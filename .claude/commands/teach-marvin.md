---
description: Train Marvin (VPS cron agent) with new tasks and patterns
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
---

## Context
Marvin is the cron-based agent on the DYAI VPS (srv1308064.hstgr.cloud) that runs automated tasks. He manages memory syncs, bot training, and maintenance jobs. This skill helps you teach Marvin new workflows and patterns.

## Your Task

Add new cron jobs, scripts, or workflows to Marvin's repertoire on the VPS.

### Steps

1. **Connect to VPS**
   ```bash
   ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud
   ```

2. **Ask User What to Teach**
   Use AskUserQuestion to clarify:
   - What task should Marvin learn?
   - How often should it run? (cron schedule)
   - What's the script/command?
   - Where should logs go?

3. **Locate Marvin's Configuration**
   ```bash
   ssh root@srv1308064.hstgr.cloud "crontab -l"
   ```

   Check existing scripts:
   ```bash
   ssh root@srv1308064.hstgr.cloud "ls -la /opt/agent-zero-data/scripts/"
   ```

4. **Create New Script (if needed)**
   ```bash
   # Create script on VPS
   ssh root@srv1308064.hstgr.cloud "cat > /opt/agent-zero-data/scripts/NEW_TASK.sh << 'EOF'
   #!/bin/bash
   # Description: [What this does]

   # Your script here

   EOF
   chmod +x /opt/agent-zero-data/scripts/NEW_TASK.sh"
   ```

5. **Test Script Manually**
   ```bash
   ssh root@srv1308064.hstgr.cloud "/opt/agent-zero-data/scripts/NEW_TASK.sh"
   ```

6. **Add to Crontab**
   ```bash
   # Add new cron job
   ssh root@srv1308064.hstgr.cloud "(crontab -l 2>/dev/null; echo '*/15 * * * * /opt/agent-zero-data/scripts/NEW_TASK.sh >> /var/log/marvin/NEW_TASK.log 2>&1') | crontab -"
   ```

7. **Verify Crontab**
   ```bash
   ssh root@srv1308064.hstgr.cloud "crontab -l | grep NEW_TASK"
   ```

8. **Create Log Directory (if needed)**
   ```bash
   ssh root@srv1308064.hstgr.cloud "mkdir -p /var/log/marvin && chmod 755 /var/log/marvin"
   ```

### Common Training Patterns

**Memory Sync Task:**
```bash
*/15 * * * * /opt/agent-zero-data/scripts/memory-sync.sh >> /var/log/marvin/memory-sync.log 2>&1
```

**Health Check Task:**
```bash
0 * * * * /opt/agent-zero-data/scripts/health-check.sh >> /var/log/marvin/health.log 2>&1
```

**Zombie Cleanup Task:**
```bash
0 */6 * * * /opt/agent-zero-data/scripts/zombie-cleanup.sh >> /var/log/marvin/zombies.log 2>&1
```

**Bot Training Workflow:**
```bash
0 2 * * * /opt/agent-zero-data/scripts/train-bots.sh >> /var/log/marvin/training.log 2>&1
```

### Cron Schedule Reference

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday=0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)

Examples:
*/15 * * * *  - Every 15 minutes
0 * * * *     - Every hour
0 2 * * *     - Daily at 2am
0 */6 * * *   - Every 6 hours
```

### Script Template

```bash
#!/bin/bash
set -euo pipefail

# Description: [What this script does]
# Author: Taught by Claude Code
# Date: $(date +%Y-%m-%d)

LOG_FILE="/var/log/marvin/$(basename $0 .sh).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting $(basename $0)"

# Your task logic here

log "Completed $(basename $0)"
```

### Guardrails
- **Always test scripts manually** before adding to crontab
- **Use absolute paths** in cron jobs (no relative paths)
- **Redirect output** to logs (`>> /var/log/marvin/task.log 2>&1`)
- **Set permissions** on scripts (`chmod +x`)
- **Create log directories** before first run
- **Use `set -euo pipefail`** in bash scripts for safety
- **Never edit crontab directly** - use `(crontab -l; echo ...) | crontab -`

### View Marvin's Logs

```bash
# Recent logs
ssh root@srv1308064.hstgr.cloud "tail -50 /var/log/marvin/*.log"

# Follow live logs
ssh root@srv1308064.hstgr.cloud "tail -f /var/log/marvin/memory-sync.log"

# Search logs
ssh root@srv1308064.hstgr.cloud "grep -r 'ERROR' /var/log/marvin/"
```

### Remove a Task

```bash
# List current cron jobs
ssh root@srv1308064.hstgr.cloud "crontab -l"

# Remove specific job
ssh root@srv1308064.hstgr.cloud "crontab -l | grep -v 'TASK_NAME' | crontab -"
```

### Advanced: Multi-Step Workflows

For complex workflows, create a master script that orchestrates multiple tasks:

```bash
#!/bin/bash
# Master workflow script

/opt/agent-zero-data/scripts/step1-collect.sh
/opt/agent-zero-data/scripts/step2-process.sh
/opt/agent-zero-data/scripts/step3-deploy.sh
```

---
*VPS-specific skill for training Marvin cron agent*
