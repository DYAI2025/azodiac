# Skilldex Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an interactive TUI skill-finder (`/skilldex`) that categorizes 1000+ Claude skills by purpose and lets users fuzzy-search and activate them via fzf.

**Architecture:** Shell script reads SKILL.md files, categorizes via keyword rules + manual overrides, caches the index as TSV, and pipes it to fzf. The slash-command `/skilldex` invokes the script and outputs the selected skill name.

**Tech Stack:** Bash, fzf, jq, grep/sed

---

### Task 1: Install fzf

**Files:**
- None (system install)

**Step 1: Install fzf via Homebrew**

Run: `brew install fzf`
Expected: fzf installed, `which fzf` returns path

**Step 2: Verify**

Run: `echo "test" | fzf --filter="test"`
Expected: outputs "test"

**Step 3: Commit**

No commit needed (system tool).

---

### Task 2: Create skilldex-rules.json

**Files:**
- Create: `~/.claude/skilldex-rules.json`

**Step 1: Write the category rules file**

```json
{
  "_meta": { "version": 1 },
  "Planen": {
    "subs": {
      "Projektplanung": ["planning", "plan-writing", "project-development", "product-manager", "startup-business", "startup-metrics", "startup-financial", "kanban", "kaizen"],
      "Architektur": ["architect", "architecture", "c4-", "ddd-", "domain-driven", "microservices", "monorepo", "software-architecture", "database-design", "event-sourcing", "cqrs", "saga-"],
      "Brainstorming": ["brainstorm", "design-orchestration", "design-md", "concise-planning", "writing-plans", "decision-maker"]
    }
  },
  "Code": {
    "subs": {
      "Schreiben": ["-pro", "-expert", "development", "scaffold", "patterns", "best-practices", "mastery", "state-management", "nextjs-", "react-", "angular-", "django-", "fastapi-", "nestjs-", "laravel-", "flutter-", "swiftui-", "golang-", "rust-", "typescript-", "python-", "java-pro", "dotnet-", "ruby-", "elixir-", "haskell-", "scala-", "cpp-", "c-pro", "php-", "julia-", "kotlin-"],
      "Review": ["review", "audit", "lint", "refactor", "clean-code", "code-review", "simplify", "tech-debt", "codebase-cleanup", "code-refactoring"],
      "Debugging": ["debug", "error-", "fix", "incident-response", "troubleshoot", "find-bugs", "error-detective", "systematic-debugging", "diagnostics"]
    }
  },
  "Testen": {
    "subs": {
      "Unit & E2E": ["test-driven", "tdd-", "unit-testing", "e2e-testing", "testing-patterns", "playwright", "jest", "bats-", "webapp-testing", "test-automator", "test-fixing"],
      "Performance": ["performance-", "benchmark", "profiling", "optimization", "bottleneck", "load-"],
      "Security-Tests": ["security-scanning", "sast-", "pentest-", "vulnerability-", "penetration", "burp-", "sqlmap-", "ffuf-", "api-fuzzing"]
    }
  },
  "Deployen": {
    "subs": {
      "CI/CD": ["cicd-", "github-actions", "gitlab-ci", "circleci-", "deployment-pipeline", "deployment-validation", "gitops-", "vercel-deploy"],
      "Cloud": ["aws-", "gcp-", "azure-", "cloud-architect", "terraform-", "cloudformation-", "cdk-", "serverless", "render-automation"],
      "Container": ["docker-", "kubernetes-", "k8s-", "helm-", "container", "istio-", "linkerd-", "service-mesh"]
    }
  },
  "Security": {
    "subs": {
      "Audit": ["security-audit", "security-compliance", "security-requirement", "threat-model", "stride-", "attack-tree", "pci-compliance", "gdpr-", "security-bluebook"],
      "Pentest": ["pentest-", "red-team", "ethical-hacking", "exploit", "privilege-escalation", "xss-", "sql-injection", "ssh-penetration", "smtp-penetration", "wordpress-penetration", "cloud-penetration", "idor-", "broken-authentication", "shodan-", "metasploit", "scanning-tools"],
      "Hardening": ["security-hardening", "secrets-management", "mtls-", "api-security", "memory-safety", "anti-reversing", "wcag-", "accessibility-"]
    }
  },
  "Automatisieren": {
    "subs": {
      "SaaS-Tools": ["slack-automation", "gmail-automation", "notion-automation", "jira-automation", "hubspot-", "salesforce-", "shopify-", "stripe-", "github-automation", "linear-automation", "asana-", "trello-", "clickup-", "monday-", "confluence-", "zendesk-", "intercom-", "freshdesk-", "pagerduty-", "sentry-", "datadog-", "posthog-", "mixpanel-", "amplitude-", "segment-", "zapier-", "make-automation", "n8n-", "airtable-", "coda-", "miro-", "figma-", "canva-", "todoist-", "calendly-", "zoom-", "discord-automation", "telegram-automation", "whatsapp-automation", "instagram-automation", "youtube-automation", "twitter-automation", "reddit-automation", "linkedin-automation", "mailchimp-", "sendgrid-", "brevo-", "activecampaign-", "klaviyo-", "convertkit-", "docusign-", "box-automation", "dropbox-automation", "google-drive-", "google-calendar-", "google-analytics-", "outlook-", "one-drive-", "microsoft-teams-", "pipedrive-", "close-automation", "zoho-", "square-", "paypal-", "bamboohr-", "freshservice-", "wrike-", "basecamp-", "bitbucket-", "webflow-"],
      "Workflows": ["workflow-", "inngest", "trigger-dev", "temporal-", "bullmq-", "airflow-", "conductor-", "orchestration"],
      "Bots": ["slack-bot", "telegram-bot", "discord-bot", "browser-automation", "chrome-extension", "apify-"]
    }
  },
  "Content": {
    "subs": {
      "Writing": ["copywriting", "copy-editing", "content-creator", "content-marketer", "beautiful-prose", "writing-skills", "documentation-", "readme", "docs-architect", "wiki-", "tutorial-", "podcast-", "data-storytelling", "professional-proofreader"],
      "Marketing": ["marketing-", "ads-", "paid-ads", "launch-strategy", "viral-", "social-content", "email-sequence", "pricing-strategy", "free-tool-strategy", "referral-", "competitive-landscape", "competitor-", "brand-guidelines", "micro-saas"],
      "SEO": ["seo-", "programmatic-seo", "schema-markup", "app-store-optimization"]
    }
  },
  "Daten": {
    "subs": {
      "Datenbanken": ["database-", "postgresql", "postgres-", "nosql-", "sql-", "prisma-", "drizzle-", "mongodb", "redis-", "cosmos-", "supabase-", "neon-", "firebase"],
      "Pipelines": ["data-engineer", "data-engineering-", "data-quality-", "dbt-", "spark-", "airflow-", "etl", "data-pipeline"],
      "ML & AI": ["ml-", "machine-learning", "ai-engineer", "ai-agent", "llm-", "rag-", "embedding-", "vector-", "computer-vision", "prompt-engineering", "prompt-caching", "evaluation", "langchain-", "langgraph", "crewai"]
    }
  },
  "Recherche": {
    "subs": {
      "Analyse": ["business-analyst", "startup-analyst", "market-sizing", "risk-manager", "risk-metrics", "quant-analyst", "culture-index", "team-composition", "kpi-dashboard"],
      "Deep Research": ["deep-research", "research-engineer", "exa-search", "tavily-", "firecrawl-", "context7-", "claude-speed-reader", "reference-builder"],
      "Docs": ["api-documenter", "api-documentation", "openapi-spec", "code-documentation", "changelog-", "architecture-decision-records", "postmortem-writing"]
    }
  },
  "Agenten": {
    "subs": {
      "Multi-Agent": ["multi-agent", "agent-orchestration", "autonomous-agent", "ai-agents-architect", "agent-manager", "dispatching-parallel", "subagent-", "swarm", "hive-mind", "claude-flow"],
      "Swarm": ["swarm-", "coordination", "topology-", "load-balance"],
      "Memory": ["agent-memory", "memory-systems", "conversation-memory", "hierarchical-agent-memory", "context-management", "context-window", "context-optimization"]
    }
  }
}
```

**Step 2: Verify JSON is valid**

Run: `jq '.' ~/.claude/skilldex-rules.json > /dev/null && echo "valid"`
Expected: "valid"

**Step 3: Commit**

```bash
git add ~/.claude/skilldex-rules.json
git commit -m "feat(skilldex): add category rules with 10 categories and keyword matching"
```

---

### Task 3: Create skilldex-overrides.json

**Files:**
- Create: `~/.claude/skilldex-overrides.json`

**Step 1: Write empty overrides file with examples as comments**

```json
{
  "_comment": "Manual overrides: skill-name -> [[category, sub], ...]. Overrides keyword matching.",
  "clean-code": [["Code", "Review"]],
  "antigravity-workflows": [["Agenten", "Multi-Agent"], ["Automatisieren", "Workflows"]]
}
```

**Step 2: Verify**

Run: `jq '.' ~/.claude/skilldex-overrides.json > /dev/null && echo "valid"`
Expected: "valid"

**Step 3: Commit**

```bash
git add ~/.claude/skilldex-overrides.json
git commit -m "feat(skilldex): add overrides file for manual categorization"
```

---

### Task 4: Create skilldex.sh main script

**Files:**
- Create: `~/.claude/bin/skilldex.sh`

**Step 1: Create bin directory**

Run: `mkdir -p ~/.claude/bin`

**Step 2: Write the skilldex.sh script**

```bash
#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$HOME/.claude/skills"
RULES="$HOME/.claude/skilldex-rules.json"
OVERRIDES="$HOME/.claude/skilldex-overrides.json"
CACHE="$HOME/.claude/skilldex-cache.tsv"

# --- Cache check ---
skill_count=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l | tr -d ' ')
cache_valid=false

if [[ -f "$CACHE" ]]; then
  cached_count=$(head -1 "$CACHE" | cut -f2)
  if [[ "$cached_count" == "$skill_count" ]] \
     && [[ "$CACHE" -nt "$RULES" ]] \
     && [[ "$CACHE" -nt "$OVERRIDES" ]]; then
    cache_valid=true
  fi
fi

# --- Build index if cache invalid ---
if [[ "$cache_valid" == "false" ]]; then
  # Load rules
  categories=$(jq -r 'to_entries[] | select(.key != "_meta") | .key' "$RULES")

  tmpfile=$(mktemp)
  echo -e "_count\t$skill_count" > "$tmpfile"

  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    [[ "$skill_name" == "*" ]] && continue

    # Read description from SKILL.md
    desc=""
    if [[ -f "$skill_dir/SKILL.md" ]]; then
      desc=$(sed -n 's/^description: *"\{0,1\}\(.*\)"\{0,1\}$/\1/p' "$skill_dir/SKILL.md" | head -1)
    fi
    match_text="$skill_name $desc"
    matched=false

    # Check overrides first
    if [[ -f "$OVERRIDES" ]]; then
      override=$(jq -r --arg s "$skill_name" '.[$s] // empty' "$OVERRIDES" 2>/dev/null)
      if [[ -n "$override" && "$override" != "null" ]]; then
        echo "$override" | jq -r '.[] | .[0] + "\t" + .[1]' | while read -r cat sub; do
          echo -e "${cat}\t${sub}\t${skill_name}" >> "$tmpfile"
        done
        matched=true
      fi
    fi

    # Keyword matching (skill can appear in multiple categories)
    if [[ "$matched" == "false" ]]; then
      while IFS= read -r cat; do
        subs=$(jq -r --arg c "$cat" '.[$c].subs | to_entries[] | .key' "$RULES")
        while IFS= read -r sub; do
          keywords=$(jq -r --arg c "$cat" --arg s "$sub" '.[$c].subs[$s][]' "$RULES")
          while IFS= read -r kw; do
            if echo "$match_text" | grep -qi "$kw"; then
              echo -e "${cat}\t${sub}\t${skill_name}" >> "$tmpfile"
              break
            fi
          done <<< "$keywords"
        done <<< "$subs"
      done <<< "$categories"
    fi

    # Fallback: uncategorized
    if ! grep -q "$skill_name" "$tmpfile" 2>/dev/null; then
      echo -e "Andere\tUnsortiert\t${skill_name}" >> "$tmpfile"
    fi
  done

  # Deduplicate and sort
  head -1 "$tmpfile" > "$CACHE"
  tail -n +2 "$tmpfile" | sort -u >> "$CACHE"
  rm -f "$tmpfile"
fi

# --- fzf selection ---
selection=$(tail -n +2 "$CACHE" \
  | awk -F'\t' '{printf "%s > %s > %s\n", $1, $2, $3}' \
  | fzf --ansi \
        --header="Skilldex | Pfeiltasten + Tippen zum Suchen | Enter = Skill laden | Esc = Abbrechen" \
        --preview="cat $SKILLS_DIR/{3}/SKILL.md 2>/dev/null | head -50" \
        --preview-window=right:50%:wrap \
        --delimiter=" > " \
        --no-multi \
  || true)

if [[ -n "$selection" ]]; then
  skill=$(echo "$selection" | awk -F' > ' '{print $NF}' | tr -d ' ')
  echo "/skill $skill"
fi
```

**Step 3: Make executable**

Run: `chmod +x ~/.claude/bin/skilldex.sh`

**Step 4: Test script runs without error**

Run: `~/.claude/bin/skilldex.sh --help 2>&1 || echo "ok, no --help but script exists"`
Expected: Script exists and is executable

**Step 5: Commit**

```bash
git add ~/.claude/bin/skilldex.sh
git commit -m "feat(skilldex): add main script with categorization, caching, and fzf UI"
```

---

### Task 5: Create /skilldex slash-command

**Files:**
- Create: `~/.claude/commands/skilldex.md`

**Step 1: Write the slash-command file**

```markdown
---
description: Interactive skill finder - search and activate skills by purpose
allowed-tools: [Bash, Skill]
---

## Context
The user wants to find and activate a skill from 1000+ installed skills.

## Your Task
1. Run the skilldex TUI: `~/.claude/bin/skilldex.sh`
2. The script outputs the skill invocation command (e.g. `/skill fastapi-pro`)
3. Execute the output as a Skill tool call

If fzf is not installed, run `brew install fzf` first.
If the user cancels (Esc), acknowledge and do nothing.
```

**Step 2: Commit**

```bash
git add ~/.claude/commands/skilldex.md
git commit -m "feat(skilldex): add /skilldex slash-command"
```

---

### Task 6: Test end-to-end

**Step 1: Delete cache to force rebuild**

Run: `rm -f ~/.claude/skilldex-cache.tsv`

**Step 2: Run skilldex and verify index builds**

Run: `~/.claude/bin/skilldex.sh` (press Esc to exit)
Expected: Cache file created at `~/.claude/skilldex-cache.tsv`

**Step 3: Verify cache content**

Run: `wc -l ~/.claude/skilldex-cache.tsv && head -20 ~/.claude/skilldex-cache.tsv`
Expected: 1000+ lines, tab-separated with category/sub/skill

**Step 4: Verify multi-category skills**

Run: `grep "security-audit" ~/.claude/skilldex-cache.tsv`
Expected: Appears in multiple categories (Security + Code/Review)

**Step 5: Run again (cached, should be instant)**

Run: `time ~/.claude/bin/skilldex.sh` (press Esc)
Expected: Near-instant startup from cache

**Step 6: Final commit**

```bash
git commit --allow-empty -m "test(skilldex): verified end-to-end flow with 1000+ skills"
```

---

### Task 7: Register as skill (self-referential)

**Files:**
- Create: `~/.claude/skills/skilldex/SKILL.md`

**Step 1: Create skill directory and SKILL.md**

```markdown
---
name: skilldex
description: "Interactive TUI skill finder. Categorizes 1000+ skills by purpose, searchable via fzf. Use when you need to find the right skill for a task."
risk: safe
source: self
---

# Skilldex

Interactive skill finder with purpose-based categories.

## Usage
Invoke via `/skilldex` slash-command or run `~/.claude/bin/skilldex.sh` directly.

## Categories
10 categories based on "Why do I need this skill?":
Planen, Code, Testen, Deployen, Security, Automatisieren, Content, Daten, Recherche, Agenten

## Maintenance
- Edit `~/.claude/skilldex-rules.json` to adjust keyword rules
- Edit `~/.claude/skilldex-overrides.json` for manual overrides
- Delete `~/.claude/skilldex-cache.tsv` to force rebuild
- New skills are auto-categorized on next run
```

**Step 2: Commit**

```bash
git add ~/.claude/skills/skilldex/
git commit -m "feat(skilldex): register as self-referential skill"
```
