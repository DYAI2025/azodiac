# Skilldex Architecture

## Project Classification

| Dimension | Value |
|-----------|-------|
| Scale | 1 user, 1000+ skills, ~1400 index entries |
| Team | Solo developer |
| Timeline | Built, iterating |
| Domain | Search & categorization (read-heavy, zero writes at runtime) |
| Constraints | Must feel instant (<100ms), no dependencies beyond bash+fzf+jq |

**Classification: CLI Tool / Solo / Lightweight** — simplest possible architecture.

---

## Architecture Overview

```
+-----------------------------------------------------------+
|                     SKILLDEX SYSTEM                        |
|                                                           |
|  +-------------+    +--------------+    +------------+    |
|  |  SKILL DIRS  |--->|  CATEGORIZER  |--->|   CACHE    |   |
|  |  (source of  |    |  (build-time) |    |  (TSV, ~1s |   |
|  |   truth)     |    |              |    |   cold)    |   |
|  +-------------+    +--------------+    +-----+------+   |
|                                               |          |
|  +-------------+    +--------------+          |          |
|  |  RULES.json  |--->|  Keyword     |----------+          |
|  |  OVERRIDES   |--->|  Matcher     |                    |
|  +-------------+    +--------------+                    |
|                                                           |
|  +----------------------------------------------------+  |
|  |                  PRESENTATION                       |  |
|  |  +----------+  +------------+  +--------------+    |  |
|  |  | fzf TUI  |  | Claude API |  | Direct grep  |    |  |
|  |  | (terminal)|  | (in-session)|  | (scripting)  |    |  |
|  |  +----------+  +------------+  +--------------+    |  |
|  +----------------------------------------------------+  |
|                          |                                |
|                          v                                |
|                   /skill <name>                           |
+-----------------------------------------------------------+
```

---

## ADR-001: TSV Cache as Index Format

### Context
1019 skills, each with a SKILL.md. Need to search by purpose across 10 categories x 3 subcategories. Must feel instant.

### Options

| Option | Pros | Cons | Speed |
|--------|------|------|-------|
| **A: TSV flat file** | Zero deps, grep/awk native, ~25ms search | No schema validation | **25ms** |
| B: SQLite | Proper queries, FTS5 | Extra dep, overkill for 1K rows | ~50ms |
| C: JSON index | Structured, jq queryable | jq startup ~30ms, parse overhead | ~80ms |

### Decision: **TSV flat file**

### Rationale
- 1400 lines is trivially small — no database needed
- `grep` + `awk` + `fzf` are the fastest possible pipeline for this size
- Cache rebuilds in ~12s (cold), serves in ~25ms (warm)
- Any POSIX shell can read it

### Trade-offs Accepted
- No schema enforcement (offset by simple 3-column format)
- No incremental updates (offset by fast full rebuild)

### Revisit Trigger
- If skills exceed 10,000 or need full-text search across SKILL.md content

---

## ADR-002: Hybrid Categorization (Keywords + Overrides)

### Context
Skills need to be categorized by purpose. Names and descriptions contain semantic hints (`fastapi-pro` -> Code, `pentest-commands` -> Security). But some skills are ambiguous or multi-purpose.

### Options

| Option | Pros | Cons |
|--------|------|------|
| A: Manual tagging | Perfect accuracy | Doesn't scale, 1000+ skills to tag |
| B: Pure keyword matching | Zero maintenance, auto-adapts | Misclassifications, no multi-category |
| **C: Keywords + manual overrides** | Auto-categorizes 80%, manual for edge cases, multi-category | Two files to maintain |
| D: LLM-based classification | Semantic understanding | Slow, expensive, non-deterministic |

### Decision: **C — Hybrid (keywords + overrides)**

### Rationale
- `skilldex-rules.json` handles 816/1019 skills automatically via keyword patterns
- `skilldex-overrides.json` fixes the ~200 that fall through or need multi-category placement
- New skills auto-categorize on next run — zero maintenance for well-named skills
- Override format `"skill": [["Cat","Sub"], ...]` enables multi-category

### Trade-offs Accepted
- ~200 skills in "Other/Uncategorized" until manually overridden
- Keyword rules can match too broadly (e.g., `-pro` catches non-code skills)

---

## ADR-003: Three Presentation Layers

### Context
fzf TUI doesn't work in non-interactive shells (Claude Code's Bash tool). Need multiple access paths.

### Decision: Three interfaces sharing one cache

| Interface | Context | How |
|-----------|---------|-----|
| **fzf TUI** | User's terminal | `~/.claude/bin/skilldex.sh` — arrow keys, preview, fuzzy search |
| **Claude API** | In Claude Code session | `grep -i <query> ~/.claude/skilldex-cache.tsv` — Claude searches for you |
| **Slash command** | `/skilldex` | Triggers TUI or falls back to in-session search |

### Rationale
- Single source of truth (cache TSV) with multiple readers
- No code duplication — all interfaces read the same file
- Graceful degradation: TUI -> grep fallback -> manual browse

---

## Component Details

### 1. Skill Source (Read-Only)

```
~/.claude/skills/          # symlink -> skills-unified/
  +-- fastapi-pro/
  |   +-- SKILL.md         # frontmatter: name, description
  +-- kubernetes-architect/
  |   +-- SKILL.md
  +-- ... (1019 dirs)
```

**Contract:** Each skill is a directory with optional `SKILL.md`. Name = directory name. Description = `description:` field in frontmatter.

### 2. Categorizer (Build-Time Only)

```
Input:  skills/ + rules.json + overrides.json
Output: skilldex-cache.tsv

Pipeline:
  1. Scan all skill dirs -> build name+description index
  2. Apply overrides (highest priority, multi-category)
  3. Grep keywords against index (bulk, per-keyword)
  4. Remaining -> "Other/Uncategorized"
  5. Deduplicate + sort -> write cache
```

**Cache invalidation:** Skill count changed OR rules/overrides newer than cache -> full rebuild.

### 3. Cache Format

```tsv
_count	1019                          # header: invalidation key
Agents	Memory	agent-memory-systems  # Category\tSub\tSkill
Agents	Memory	context-management
Agents	Multi-Agent	ai-agents-architect
Code	Debugging	debug
Code	Debugging	error-detective
Code	Writing	fastapi-pro           # same skill can appear in
Deploy	Cloud	aws-skills            # multiple categories
...
```

### 4. Category Taxonomy

```
10 Categories x 3 Subcategories = 30 slots

Planning     -> Project Planning, Architecture, Brainstorming
Code         -> Writing, Review, Debugging
Testing      -> Unit & E2E, Performance, Security Tests
Deploy       -> CI/CD, Cloud, Container
Security     -> Audit, Pentest, Hardening
Automation   -> SaaS Tools, Workflows, Bots
Content      -> Writing, Marketing, SEO
Data         -> Databases, Pipelines, ML & AI
Research     -> Analysis, Deep Research, Docs
Agents       -> Multi-Agent, Swarm, Memory
```

---

## Performance Profile

| Operation | Time | Notes |
|-----------|------|-------|
| Cold cache build | ~12s | Scans 1019 dirs, greps ~200 keywords |
| Warm cache read | <25ms | fzf reads 1400-line TSV |
| fzf keystroke | <5ms | Native C, no shell overhead |
| Skill activation | <1s | Claude loads SKILL.md |

**Bottleneck:** Cold build (12s) — acceptable since it runs only when skills change.

---

## Extensibility Points

| What | How | Effort |
|------|-----|--------|
| Add new skill | Drop dir in `skills/` -> auto-categorized on next run | Zero |
| Fix categorization | Edit `skilldex-overrides.json` | 1 line |
| Add category | Edit `skilldex-rules.json` + keywords | 5 min |
| New presentation | Read `skilldex-cache.tsv` with any tool | Trivial |

---

## File Map

```
~/.claude/
  bin/skilldex.sh              # Main script (executable)
  skilldex-rules.json          # Keyword -> category mapping
  skilldex-overrides.json      # Manual overrides (multi-category)
  skilldex-cache.tsv           # Generated cache (gitignored)
  commands/skilldex.md         # /skilldex slash command
  skills/skilldex/SKILL.md     # Self-registration as skill
  docs/architecture/           # This document
```

---

## Validation

- [x] Requirements: fast purpose-based skill finding
- [x] Constraints: bash+fzf+jq only, <100ms search
- [x] Each decision has trade-off analysis (3 ADRs)
- [x] Simpler alternatives considered (rejected SQLite, LLM classification)
- [x] ADRs written for significant decisions
- [x] Solo developer — complexity budget respected
