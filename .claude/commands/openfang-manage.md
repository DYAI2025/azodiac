---
description: Manage OpenFang agents, channels, and memory on the DYAI VPS
allowed-tools: Bash, Read, Edit, Write, AskUserQuestion
---

## Context

OpenFang 0.3.42 runs on DYAI VPS as `openfang.service`. Key facts learned from deployment:

- **SSH**: `ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud`
- **API**: `http://localhost:4200` — uses **both** `X-API-Key: <key>` (curl) and `Authorization: Bearer <key>` (CLI)
- **API key**: `grep "^api_key " /opt/openfang/config.toml | head -1 | sed 's/api_key = "//;s/"//'`
- **Config**: `/opt/openfang/config.toml` | **Agents**: `/opt/openfang/agents/` | **Data**: `/opt/openfang/data/`
- **Source**: `/opt/openfang/src/` (rsync target from Mac)
- **Env/secrets**: `/etc/openfang/env` (chmod 600, contains OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN)

**Known API patterns:**
- Auth: `X-API-Key` header for curl, `OPENFANG_HOME=/opt/openfang/data` for CLI
- Channels: configured via `[channels.telegram]` / `[channels.discord]` in config.toml (NOT `[telegram]`)
- Agent spawn: `POST /api/agents` with `{"manifest_toml": "<escaped toml string>"}`
- Memory KV: `PUT /api/memory/agents/{id}/kv/{key}` with `{"value": "..."}`
- Tool update: kill agent → respawn with updated manifest (PATCH doesn't update capabilities)

## Arguments

`$ARGUMENTS` — Action to perform. Examples: "list agents", "respawn zeroclaw", "add tool X to perr00bot", "check channels", "set memory key=value for zeroclaw"

## Your Task

Manage OpenFang based on the requested action. Detect intent from `$ARGUMENTS`.

---

### Action: List Agents

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "/bin/bash -s" << 'ENDSSH'
API_KEY=$(grep "^api_key " /opt/openfang/config.toml | head -1 | sed 's/api_key = "//;s/"//')
curl -s -H "X-API-Key: $API_KEY" http://localhost:4200/api/agents | python3 -c "
import json,sys
for a in json.load(sys.stdin):
    tools = a.get('capabilities',{}).get('tools',[])
    print(f\"  {a['id'][:8]}  {a['name']:20} {a['state']:10} tools={len(tools)}\")
"
ENDSSH
```

---

### Action: Respawn Agent (after manifest change)

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "/bin/bash -s" << 'ENDSSH'
API_KEY=$(grep "^api_key " /opt/openfang/config.toml | head -1 | sed 's/api_key = "//;s/"//')
AUTH="Authorization: Bearer $API_KEY"

# Get agent ID
AGENT_ID=$(curl -s -H "X-API-Key: $API_KEY" http://localhost:4200/api/agents | python3 -c "
import json,sys
for a in json.load(sys.stdin):
    if a['name'] == 'AGENT_NAME':
        print(a['id'])
")

# Kill
curl -s -X DELETE -H "$AUTH" "http://localhost:4200/api/agents/$AGENT_ID"

# Respawn from manifest
MANIFEST=$(cat /opt/openfang/agents/AGENT_NAME/agent.toml | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"manifest_toml\": $MANIFEST}" http://localhost:4200/api/agents
ENDSSH
```

**Note:** After respawn, verify tools with:
```bash
curl -s -H "X-API-Key: $API_KEY" http://localhost:4200/api/agents/NEW_ID | python3 -c "import json,sys; print(json.load(sys.stdin).get('capabilities',{}).get('tools',[]))"
```

---

### Action: Add Tool to Agent

1. Edit manifest on Mac:
   ```
   /Users/benjaminpoersch/claude/openfang/agents/AGENT_NAME/agent.toml
   ```
   Add tool name to `tools = [...]` in `[capabilities]`

2. Sync to VPS:
   ```bash
   rsync -avz --include="agents/***" --exclude="*" -e "ssh -i ~/.ssh/id_ed25519" \
     /Users/benjaminpoersch/claude/openfang/ root@srv1308064.hstgr.cloud:/opt/openfang/src/
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud \
     "cp /opt/openfang/src/agents/AGENT_NAME/agent.toml /opt/openfang/agents/AGENT_NAME/agent.toml"
   ```

3. Respawn agent (see above — PATCH does NOT update capabilities)

**Available tools** (from `GET /api/tools`):
`file_read`, `file_write`, `file_list`, `memory_store`, `memory_recall`, `web_fetch`, `shell_exec`, `agent_send`, `agent_list`, `media_transcribe`, `speech_to_text`, `text_to_speech`, `media_describe`

---

### Action: Check / Fix Channels

Check active connections:
```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "ss -tnp | grep openfang"
# 149.154.x.x = Telegram, 162.159.x.x = Discord (Cloudflare)
```

Check logs for errors:
```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "journalctl -u openfang --since '5 minutes ago' --no-pager | grep -iE '(telegram|discord|conflict|error)'"
```

If Telegram shows `409 Conflict` persistently:
```bash
# Kill zombie NanoBot if still running
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "pgrep -a nanobot && pkill -f nanobot || echo 'no nanobot'"
```

Channel config format (must use `[channels.X]`, NOT `[telegram]`):
```toml
[channels.telegram]
bot_token_env = "TELEGRAM_BOT_TOKEN"
default_agent = "perr00bot"

[channels.discord]
bot_token_env = "DISCORD_BOT_TOKEN"
default_agent = "zeroclaw"
```

---

### Action: Set/Read Agent Memory (KV)

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "/bin/bash -s" << 'ENDSSH'
API_KEY=$(grep "^api_key " /opt/openfang/config.toml | head -1 | sed 's/api_key = "//;s/"//')
AUTH="Authorization: Bearer $API_KEY"
AGENT_ID="<uuid>"  # from list agents

# Read all KV
curl -s -H "$AUTH" "http://localhost:4200/api/memory/agents/$AGENT_ID/kv"

# Set a value
curl -s -X PUT -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"value": "VALUE"}' \
  "http://localhost:4200/api/memory/agents/$AGENT_ID/kv/KEY_NAME"
ENDSSH
```

---

### Action: Restart Service

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "systemctl restart openfang && sleep 6 && curl -s http://localhost:4200/api/health"
```

After restart, agents are restored from DB automatically. Channels reconnect automatically if `[channels.X]` config is correct.

---

### Guardrails

- Always verify agent IDs with `list agents` before kill/respawn — IDs change on every respawn
- Never edit `/etc/openfang/env` directly — it contains real tokens (chmod 600)
- After config.toml changes, restart the service (`systemctl restart openfang`)
- PATCH endpoint does NOT update agent capabilities — must kill+respawn for tool changes
- The CLI (`openfang memory set`) requires `OPENFANG_HOME=/opt/openfang/data` to find the running daemon

---
*Created 2026-03-11 — source: OpenFang VPS deployment session patterns*
