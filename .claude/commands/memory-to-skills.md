---
description: Fetch agent memories from EvermemOS and transform them into new or refined skills
allowed-tools: [Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion]
---

## Context

EvermemOS runs on the Linux PC in Berlin (Tailscale: `100.103.64.33`) and exposes a REST API at `http://100.103.64.33:8003`. It stores unified agent memories from Perr00bot, Marvin, OpenClaw, Selina, and other agents. This skill queries those memories, analyzes them for recurring patterns, and proposes new skills or refinements to existing ones in `~/.claude/commands/`.

**Note:** Port 8000 on that machine is LPrint (printer service), NOT EvermemOS. Always use port **8003**.

## Your Task

Query EvermemOS for agent memories, cross-reference with existing skills, and propose skill refinements or new skill drafts.

### Step 1: Verify API Health

```bash
curl -s --connect-timeout 5 http://100.103.64.33:8003/health
```

If the API is unreachable, fall back to SSH access:
```bash
ssh -o ConnectTimeout=5 dyai@100.103.64.33 "curl -s http://localhost:8003/health"
```

Expected response: `{"status":"healthy","timestamp":"...","message":"System running normally"}`

If both fail, inform the user that EvermemOS is unavailable and stop.

### Step 2: Determine Search Scope

Use AskUserQuestion to ask the user:
- **What topic/domain** should memories be searched for? (e.g., "debugging", "deployment", "docker", or "all recent")
- **Which user_ids** to include? Known user_ids: `selina`, `ben` (others like `perr00bot`, `marvin`, `openclaw`, `nexus` may have 0 memories)
- **Time range?** (last 7 days, 30 days, all time)

### Step 3: Fetch Memories from EvermemOS

**IMPORTANT:** The API uses JSON request bodies, not query parameters.

Search by keyword:
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "query": "TOPIC", "retrieve_method": "keyword", "top_k": 20}'
```

Search with vector similarity (semantic):
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "query": "TOPIC", "retrieve_method": "hybrid", "top_k": 20}'
```

Fetch by memory type (`profile`, `episodic_memory`, `foresight`, `event_log`):
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "memory_type": "TYPE", "limit": 50}'
```

Fetch recent memories:
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "limit": 50}'
```

If API calls fail, fall back to SSH + curl against localhost:
```bash
ssh dyai@100.103.64.33 "curl -s -X GET http://localhost:8003/api/v1/memories/search -H 'Content-Type: application/json' -d '{\"user_id\": \"USER_ID\", \"query\": \"TOPIC\", \"retrieve_method\": \"keyword\", \"top_k\": 20}'"
```

### Memory Field Reference

Each memory type has different fields:
- **episodic_memory**: `title`, `summary`, `participants`, `key_events`, `start_time`
- **event_log**: `atomic_fact`, `event_type`, `parent_type`, `timestamp`
- **foresight**: `content` (prediction text)
- **profile**: `profiles[].profile_data.implicit_traits[]` (each with `trait`, `description`, `evidence`)
- **search results**: grouped by relevance, with `scores` and `importance_scores`

### Step 4: Inventory Existing Skills

```bash
ls ~/.claude/commands/*.md
```

Read each skill file to understand what's already covered. Focus on:
- What topics/domains each skill addresses
- What patterns or workflows they encode
- Gaps where memories suggest useful automation

### Step 5: Analyze Memories → Skill Candidates

For each cluster of related memories, evaluate:

1. **Frequency** — Does this pattern appear across multiple memories/agents? Recurring patterns make strong skill candidates.
2. **Complexity** — Is the workflow multi-step enough to benefit from being encoded as a skill? Single commands don't need skills.
3. **Overlap** — Does an existing skill already cover this? If partially, it's a refinement candidate.
4. **Actionability** — Can this be turned into concrete steps? Vague observations aren't skills.

Categorize findings as:
- **New Skill** — Pattern not covered by any existing skill
- **Skill Refinement** — Existing skill could be improved with insights from memories
- **Not Actionable** — Interesting but not skill-worthy

### Step 6: Present Proposals to User

For each proposal, show:

**New Skills:**
```
PROPOSED NEW SKILL: /skill-name
Source: [agent names] — [N memories]
Pattern: [description of the recurring pattern]
Draft:
---
[full skill content]
---
```

**Refinements:**
```
PROPOSED REFINEMENT: /existing-skill-name
Source: [agent names] — [N memories]
Change: [what would be added/modified]
Diff:
  [show what lines change]
```

Use AskUserQuestion to let the user approve, modify, or reject each proposal individually.

### Step 7: Apply Approved Changes

For approved new skills:
- Write the skill file to `~/.claude/commands/SKILL_NAME.md`
- Confirm creation

For approved refinements:
- Show the exact diff before applying
- Use Edit to apply changes to the existing skill file
- Confirm the edit

### Guardrails

- **Never overwrite** an existing skill without explicit user approval
- **Always show diffs** before modifying existing skills
- **Verify API health** before any queries — don't silently fail
- **Fall back to SSH** (`ssh dyai@100.103.64.33`) if the REST API is unreachable
- **Attribute sources** — every proposal must reference which agent memories it's based on
- **Don't create trivial skills** — single-command patterns should be memory notes, not skills
- **Preserve existing skill structure** — refinements should match the style of the skill being modified

### Example Flow

```
User runs /memory-to-skills
→ API health check passes (port 8003)
→ User asks to search for "docker" memories
→ Fetches 12 memories about Docker issues from Perr00bot and Marvin
→ Finds pattern: "IPv6 causes Docker pull failures on VPS" appears 4 times
→ Checks existing skills: /vps-health mentions Docker but not IPv6 fix
→ Proposes refinement to /vps-health: add IPv6 diagnostic step
→ Also proposes new skill: /docker-troubleshoot for container debugging
→ User approves refinement, rejects new skill
→ Applies Edit to vps-health.md
→ Done
```
