---
description: Comprehensive VPS health check — OpenFang service, agents, channels, memory, disk, zombies
allowed-tools: Bash, Read, AskUserQuestion
---

## Context

The DYAI VPS (srv1308064.hstgr.cloud) runs **OpenFang** (Agent OS) as the primary service, with agents Perr00bot (Telegram) and ZeroClaw (Discord). Memory usage can creep up, zombie processes accumulate, and channels occasionally disconnect.

SSH: `ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud`
OpenFang API: `http://localhost:4200` (Bearer token in `/opt/openfang/config.toml`)
Config: `/opt/openfang/config.toml` | Data: `/opt/openfang/data/`

## Arguments

- `$ARGUMENTS` — Optional: "quick" for summary only, or specific check like "memory", "agents", "channels", "zombies"

## Your Task

Run a comprehensive health check on the VPS and report status clearly.

### Steps

1. **System Resources:**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "free -h && echo '---' && df -h / && echo '---' && uptime"
   ```

2. **OpenFang Service:**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "systemctl status openfang --no-pager | head -10 && echo '---' && curl -s http://localhost:4200/api/health"
   ```

3. **Agents (via API):**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "/bin/bash -s" << 'ENDSSH'
   API_KEY=$(grep "^api_key " /opt/openfang/config.toml | head -1 | sed 's/api_key = "//;s/"//')
   curl -s -H "X-API-Key: $API_KEY" http://localhost:4200/api/agents | python3 -c "
   import json,sys
   for a in json.load(sys.stdin):
       print(f\"  {a['name']:20} {a['state']:10} {a['model_provider']}/{a['model_name']}\")
   "
   ENDSSH
   ```

4. **Channel Connections (Telegram + Discord):**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "
   ss -tnp | grep openfang | awk '{print \$1, \$5, \$6}'
   echo '---'
   journalctl -u openfang --since '5 minutes ago' --no-pager | grep -iE '(telegram|discord|connected|conflict|error)' | tail -10
   "
   ```
   - `149.154.x.x` = Telegram, `162.159.x.x` = Discord (Cloudflare)

5. **Zombie/Orphan Processes:**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "ps aux | awk '\$8 ~ /Z/ {print}' && ps aux --sort=-%mem | head -10"
   ```

6. **Backup Cron:**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud "crontab -l 2>/dev/null && ls -lh /opt/openfang/backups/ 2>/dev/null | tail -3"
   ```

7. **Report** — Present a clear summary table:
   ```
   ┌──────────────────┬──────────┬────────────────────────────┐
   │  Component       │  Status  │  Details                   │
   ├──────────────────┼──────────┼────────────────────────────┤
   │  RAM             │  OK/WARN │  X/Y GB used (Z%)          │
   │  Disk            │  OK/WARN │  X/Y GB used (Z%)          │
   │  openfang.svc    │  UP/DOWN │  PID XXXX, uptime Xh       │
   │  perr00bot       │  UP/DOWN │  Running/Stopped           │
   │  zeroclaw        │  UP/DOWN │  Running/Stopped           │
   │  Telegram chan   │  UP/DOWN │  ESTAB / 409 Conflict      │
   │  Discord chan    │  UP/DOWN │  ESTAB / reconnecting      │
   │  Zombies         │  N found │  [details if any]          │
   │  Last backup     │  OK/MISS │  YYYY-MM-DD, Xk            │
   └──────────────────┴──────────┴────────────────────────────┘
   ```

### Guardrails

- Read-only checks only — never kill processes or restart services without asking
- If memory > 85%, flag it and suggest `/vps-process-cleanup`
- If Telegram shows `409 Conflict`, check for zombie NanoBot: `pgrep -a nanobot`
- If an agent is down, suggest respawn via API (see `/openfang-manage`)
- If OpenFang service is down: `systemctl restart openfang && sleep 6 && curl http://localhost:4200/api/health`

---
*Updated 2026-03-11 — migrated from NanoBot/OpenClaw to OpenFang; source: session patterns*
