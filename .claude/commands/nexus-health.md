---
description: Check Flow-Nexus and bot health on VPS
allowed-tools: [Bash, Read]
---

## Context
Flow-Nexus is the MCP coordination system running on the DYAI VPS. This skill monitors the health of all bots, services, and infrastructure to ensure everything is running smoothly.

## Your Task

Check system health, identify issues, and provide actionable recommendations for the VPS infrastructure.

### Steps

1. **Connect to VPS**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud
   ```

2. **System Resources Overview**
   ```bash
   ssh root@srv1308064.hstgr.cloud "df -h / && free -h && uptime"
   ```

3. **Check Running Services**

   **Agent Zero (Docker):**
   ```bash
   ssh root@srv1308064.hstgr.cloud "docker ps -a | grep agent-zero"
   ssh root@srv1308064.hstgr.cloud "curl -s http://localhost:5000/health || echo 'Agent Zero not responding'"
   ```

   **Vibe Kanban (systemd):**
   ```bash
   ssh root@srv1308064.hstgr.cloud "systemctl status vibe-kanban --no-pager"
   ssh root@srv1308064.hstgr.cloud "curl -s http://localhost:3000 -o /dev/null && echo 'Kanban: UP' || echo 'Kanban: DOWN'"
   ```

4. **Check Claude/OpenClaw Processes**
   ```bash
   ssh root@srv1308064.hstgr.cloud "ps aux | grep -E '(claude|openclaw|mcp)' | grep -v grep | wc -l"
   ```

5. **Resource Consumption Analysis**

   **CPU/Memory Top Consumers:**
   ```bash
   ssh root@srv1308064.hstgr.cloud "ps aux --sort=-%mem | head -15"
   ```

   **Zombie Processes:**
   ```bash
   ssh root@srv1308064.hstgr.cloud "ps aux | grep -E '(claude|openclaw)' | grep -v grep | awk '\$3 == 0.0 {count++} END {print count \" zombies found\"}'"
   ```

6. **Check Disk Usage**
   ```bash
   ssh root@srv1308064.hstgr.cloud "du -sh /opt/agent-zero-data /var/log /tmp 2>/dev/null | sort -hr"
   ```

7. **Check Logs for Errors**

   **Recent errors:**
   ```bash
   ssh root@srv1308064.hstgr.cloud "journalctl -u vibe-kanban --since '1 hour ago' | grep -i error | tail -20"
   ssh root@srv1308064.hstgr.cloud "docker logs agent-zero --tail 50 2>&1 | grep -i error"
   ```

8. **Check Cron Jobs (Marvin)**
   ```bash
   ssh root@srv1308064.hstgr.cloud "crontab -l"
   ssh root@srv1308064.hstgr.cloud "tail -20 /var/log/marvin/*.log 2>/dev/null"
   ```

9. **Network Connectivity**
   ```bash
   ssh root@srv1308064.hstgr.cloud "curl -s https://a0.dyai.cloud -o /dev/null && echo 'Public URL: OK' || echo 'Public URL: FAILED'"
   ssh root@srv1308064.hstgr.cloud "curl -s https://kanban.dyai.cloud -o /dev/null && echo 'Kanban URL: OK' || echo 'Kanban URL: FAILED'"
   ```

10. **Generate Health Report**

Create summary:
```
════════════════════════════════════════════════════════
FLOW-NEXUS HEALTH REPORT
VPS: srv1308064.hstgr.cloud
Time: [timestamp]
════════════════════════════════════════════════════════

SYSTEM RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Disk:   [X]% used ([Y]GB free)
Memory: [X]% used ([Y]GB free)
CPU:    [load average]
Uptime: [days]

SERVICES STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Agent Zero     - Running (Docker)
✓ Vibe Kanban    - Running (systemd)
✓ Public URLs    - Accessible
⚠ Claude Zombies - [N] processes at 0% CPU

RESOURCE CONSUMERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Top 5 processes by memory]

MARVIN CRON STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active jobs: [N]
Last memory sync: [timestamp]
Recent errors: [N]

RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• [Action items based on health check]

════════════════════════════════════════════════════════
```

### Health Thresholds

**Healthy:**
- Disk < 80% used
- Memory < 70% used
- CPU load < # of cores
- Zombies < 5
- All services responding

**Warning:**
- Disk 80-90%
- Memory 70-85%
- Zombies 5-20
- One service degraded

**Critical:**
- Disk > 90%
- Memory > 85%
- Zombies > 20
- Services down

### Quick Fixes

**Too many zombies:**
```bash
ssh root@srv1308064.hstgr.cloud "/opt/agent-zero-data/scripts/zombie-cleanup.sh"
```

**High disk usage:**
```bash
ssh root@srv1308064.hstgr.cloud "docker system prune -f"
ssh root@srv1308064.hstgr.cloud "rm -rf /tmp/* /var/log/*.log.*"
```

**Service not responding:**
```bash
# Restart Vibe Kanban
ssh root@srv1308064.hstgr.cloud "systemctl restart vibe-kanban"

# Restart Agent Zero
ssh root@srv1308064.hstgr.cloud "docker restart agent-zero"
```

### Monitoring Automation

Create a health-check cron job:
```bash
# Add to Marvin's crontab
0 * * * * /opt/agent-zero-data/scripts/health-check.sh >> /var/log/marvin/health.log 2>&1
```

Health check script template:
```bash
#!/bin/bash
set -euo pipefail

DISK_WARN=80
MEM_WARN=70
ZOMBIE_WARN=10

disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
zombies=$(ps aux | grep -E '(claude|openclaw)' | grep -v grep | awk '$3 == 0.0 {count++} END {print count+0}')

if [[ $disk_usage -gt $DISK_WARN ]] || [[ $mem_usage -gt $MEM_WARN ]] || [[ $zombies -gt $ZOMBIE_WARN ]]; then
    echo "ALERT: Disk=${disk_usage}%, Mem=${mem_usage}%, Zombies=${zombies}"
    # Add notification logic here
fi
```

### Guardrails
- **Run health checks regularly** (hourly cron job)
- **Never kill processes blindly** - verify they're zombies first
- **Check logs before restarting services** - understand root cause
- **Monitor trends over time** - one spike is normal, patterns indicate issues
- **Alert on critical thresholds** - don't wait for manual checks

---
*VPS-specific skill for Flow-Nexus health monitoring*
