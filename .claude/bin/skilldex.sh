#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$HOME/.claude/skills"
RULES="$HOME/.claude/skilldex-rules.json"
OVERRIDES="$HOME/.claude/skilldex-overrides.json"
CACHE="$HOME/.claude/skilldex-cache.tsv"

# --- Check fzf ---
if ! command -v fzf &>/dev/null; then
  echo "fzf not found. Install with: brew install fzf" >&2
  exit 1
fi

# --- Cache check ---
skill_count=$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
cache_valid=false

if [[ -f "$CACHE" ]]; then
  cached_count=$(head -1 "$CACHE" | cut -f2)
  if [[ "$cached_count" == "$skill_count" ]] \
     && [[ "$CACHE" -nt "$RULES" ]] \
     && [[ ! -f "$OVERRIDES" || "$CACHE" -nt "$OVERRIDES" ]]; then
    cache_valid=true
  fi
fi

# --- Build index if cache invalid ---
if [[ "$cache_valid" == "false" ]]; then
  tmpfile=$(mktemp)
  skill_index=$(mktemp)
  matched_skills=$(mktemp)

  echo -e "_count\t$skill_count" > "$tmpfile"

  # Step 1: Build skill index (name + description per line)
  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    [[ "$skill_name" == "*" ]] && continue
    desc=""
    if [[ -f "$skill_dir/SKILL.md" ]]; then
      desc=$(sed -n 's/^description: *"\{0,1\}\(.*\)"\{0,1\}$/\1/p' "$skill_dir/SKILL.md" | head -1)
    fi
    printf '%s\t%s\n' "$skill_name" "$skill_name $desc" >> "$skill_index"
  done

  # Step 2: Apply overrides first
  if [[ -f "$OVERRIDES" ]]; then
    jq -r '
      to_entries[] | select(.key != "_comment") |
      .key as $skill |
      .value[] |
      $skill + "\t" + .[0] + "\t" + .[1]
    ' "$OVERRIDES" 2>/dev/null | while IFS=$'\t' read -r skill cat sub; do
      printf '%s\t%s\t%s\n' "$cat" "$sub" "$skill" >> "$tmpfile"
      echo "$skill" >> "$matched_skills"
    done
  fi

  # Step 3: For each keyword rule, grep matching skills in bulk
  jq -r '
    to_entries[] | select(.key != "_meta") |
    .key as $cat |
    .value.subs | to_entries[] |
    .key as $sub |
    .value[] |
    . + "\t" + $cat + "\t" + $sub
  ' "$RULES" | while IFS=$'\t' read -r kw cat sub; do
    # grep keyword against skill index, extract skill names
    matches=$(grep -i "$kw" "$skill_index" 2>/dev/null | cut -f1 || true)
    [[ -z "$matches" ]] && continue
    while read -r skill_name; do
      [[ -z "$skill_name" ]] && continue
      # Skip if already handled by override
      if [[ -s "$matched_skills" ]] && grep -qx "$skill_name" "$matched_skills" 2>/dev/null; then
        continue
      fi
      printf '%s\t%s\t%s\n' "$cat" "$sub" "$skill_name" >> "$tmpfile"
    done <<< "$matches"
  done

  # Step 4: Find unmatched skills
  all_skills=$(cut -f1 "$skill_index" | sort)
  categorized=$(tail -n +2 "$tmpfile" | cut -f3 | sort -u)
  uncategorized=$(comm -23 <(echo "$all_skills") <(echo "$categorized"))
  while read -r skill_name; do
    [[ -z "$skill_name" ]] && continue
    printf '%s\t%s\t%s\n' "Andere" "Unsortiert" "$skill_name" >> "$tmpfile"
  done <<< "$uncategorized"

  # Deduplicate and sort
  head -1 "$tmpfile" > "$CACHE"
  tail -n +2 "$tmpfile" | sort -u >> "$CACHE"
  rm -f "$tmpfile" "$skill_index" "$matched_skills"
fi

# --- fzf selection ---
selection=$(tail -n +2 "$CACHE" \
  | awk -F'\t' '{printf "%s > %s > %s\n", $1, $2, $3}' \
  | fzf \
      --header="Skilldex | Tippen zum Suchen | Enter = Skill laden | Esc = Abbrechen" \
      --preview="cat $SKILLS_DIR/{3}/SKILL.md 2>/dev/null | head -50" \
      --preview-window=right:50%:wrap \
      --delimiter=" > " \
      --no-multi \
      --layout=reverse \
      --border \
      --prompt="Skill suchen: " \
  || true)

if [[ -n "$selection" ]]; then
  skill=$(echo "$selection" | awk -F' > ' '{print $NF}' | tr -d ' ')
  echo "/skill $skill"
fi
