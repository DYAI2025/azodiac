---
description: Access unified agent memories from EvermemOS via REST API
allowed-tools: [Bash, Read, Grep, AskUserQuestion]
---

## Context

EvermemOS runs on the Linux PC in Berlin (Tailscale: `100.103.64.33`) and exposes a REST API at `http://100.103.64.33:8003`. It collects agent memories from all AI agents (Perr00bot, Marvin, OpenClaw, Selina, nexus) and stores them in MongoDB + Elasticsearch. Selina web UI is available at `http://100.103.64.33:3000`.

**Note:** Port 8000 on that machine is LPrint (printer service), NOT EvermemOS. Always use port **8003**.

Known user_ids with data: `selina`, `ben`. Others may have 0 memories.

## Your Task

Connect to EvermemOS to retrieve and search agent memories across all connected AI agents.

### Step 1: Verify API Access

```bash
curl -s --connect-timeout 5 http://100.103.64.33:8003/health
```

Expected: `{"status":"healthy","timestamp":"...","message":"System running normally"}`

If API is unreachable, fall back to SSH:
```bash
ssh -o ConnectTimeout=5 dyai@100.103.64.33 "curl -s http://localhost:8003/health"
```

If both fail, inform the user that EvermemOS is unavailable and stop.

### Step 2: Query Agent Memories

Ask user what they want to search for, then use the appropriate endpoint.

**IMPORTANT:** The API uses JSON request bodies, not query parameters.

**Search by keyword (BM25):**
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "query": "SEARCH_TERM", "retrieve_method": "keyword", "top_k": 20}'
```

**Semantic search (vector):**
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "query": "SEARCH_TERM", "retrieve_method": "hybrid", "top_k": 20}'
```

Retrieve methods: `keyword` (BM25), `vector` (semantic), `hybrid` (both), `rrf` (fusion), `agentic` (LLM-guided multi-round)

**Fetch memories by type** (`profile`, `episodic_memory`, `foresight`, `event_log`):
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "memory_type": "episodic_memory", "limit": 20}'
```

**Fetch all recent memories:**
```bash
curl -s -X GET http://100.103.64.33:8003/api/v1/memories \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "limit": 20}'
```

### Memory Field Reference

Each memory type returns different fields:
- **episodic_memory**: `title`, `summary`, `participants`, `key_events`, `start_time`
- **event_log**: `atomic_fact`, `event_type`, `parent_type`, `timestamp`
- **foresight**: `content` (prediction text about future behavior)
- **profile**: `profiles[].profile_data.implicit_traits[]` (each: `trait`, `description`, `evidence`)

### Step 3: Filter and Present Results

- Format memory retrieval results clearly
- Show which agent/user the memory came from
- Include timestamps and memory type
- Group related memories together
- Offer to save important findings to local memory

### Step 4: Integration with Local Memory

After retrieving relevant memories from EvermemOS, ask the user if important findings should be saved locally. If yes, add to `~/.claude/projects/-Users-benjaminpoersch/memory/MEMORY.md` with attribution:

```markdown
## From EvermemOS (Agent: AGENT_NAME, Date: YYYY-MM-DD)

[Retrieved memory content]
```

### SSH Fallback

If the REST API is down, use SSH to query MongoDB directly:

```bash
# Check if EvermemOS service is running
ssh dyai@100.103.64.33 "ps aux | grep -i evermem"

# Check which port EvermemOS is on
ssh dyai@100.103.64.33 "ss -tlnp | grep python3"

# Query MongoDB directly
ssh dyai@100.103.64.33 "mongosh --quiet -u admin -p memsys123 --authenticationDatabase admin evermemos --eval 'db.memories.find({}).limit(10).toArray()'"

# Search MongoDB by content
ssh dyai@100.103.64.33 "mongosh --quiet -u admin -p memsys123 --authenticationDatabase admin evermemos --eval 'db.memories.find({\$text: {\$search: \"SEARCH_TERM\"}}).limit(10).toArray()'"
```

### Troubleshooting

**API returns connection refused on port 8003:**
- EvermemOS process may have stopped: `ssh dyai@100.103.64.33 "ps aux | grep evermem"`
- Check if port 8003 is listening: `ssh dyai@100.103.64.33 "ss -tlnp | grep 8003"`
- Restart: `ssh dyai@100.103.64.33 "cd /home/dyai/EverMemOS && source .venv/bin/activate && nohup python3 src/run.py --host 0.0.0.0 --port 8003 > evermemos-api.log 2>&1 &"`

**Accidentally hitting port 8000 (LPrint):**
- Port 8000 is LPrint (printer service), not EvermemOS
- Always use port 8003 for EvermemOS API

**API returns empty results:**
- Verify user_id is correct (known: `selina`, `ben`)
- Try broader search terms
- Check if memories exist: fetch with limit 5 first

**SSH connection fails:**
- Verify Tailscale is connected: `tailscale status`
- Try direct IP: `ssh dyai@100.103.64.33`
- Run `/tailscale-connect` to fix Tailscale issues
- Run `/vps-ssh-setup` to configure SSH access

**MongoDB auth fails:**
- Credentials: admin/memsys123, authDB: admin
- DB name: evermemos, port: 27017

---
*Updated: Uses REST API on port 8003 with JSON request bodies. Port 8000 is LPrint, not EvermemOS.*
