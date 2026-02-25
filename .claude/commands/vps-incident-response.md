---
description: VPS security incident response — investigate, contain, eradicate suspicious processes
allowed-tools: Bash, Read, AskUserQuestion
---

## Context

The DYAI VPS (srv1308064.hstgr.cloud) is internet-facing and has been compromised before (SSH brute-force → cryptominer). This skill provides a systematic incident response workflow.

SSH: `ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud`

## Arguments

`$ARGUMENTS` — Optional: suspicious PID, process name, or "full-scan" for proactive check.

## Your Task

Investigate and remediate a security incident on the VPS. Follow every step — skipping steps caused a miner to respawn last time.

### Phase 1: Detection

Identify suspicious processes:
```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud '
  echo "=== HIGH CPU (>50%) ===";
  ps aux --sort=-%cpu | awk "NR<=1 || \$3>50" | head -10;
  echo;
  echo "=== SUSPICIOUS LOCATIONS ===";
  # Binaries in /tmp, /var/tmp, /dev/shm — almost always malware
  find /tmp /var/tmp /dev/shm -type f -perm -u+x 2>/dev/null;
  echo;
  echo "=== RANDOM-NAME BINARIES ===";
  find /tmp /var/tmp -name "[0-9]*" -type f 2>/dev/null;
  echo;
  echo "=== STRIPPED ELF BINARIES ===";
  find /tmp /var/tmp /dev/shm -type f -exec file {} \; 2>/dev/null | grep -i "elf.*stripped"
'
```

**Red flags:**
- Binary with random numeric name in /tmp or /var/tmp
- ELF executable, statically linked, stripped
- High CPU usage with no stdin/stdout (→ /dev/null)
- Outbound connection to unknown IP on high port
- Process owned by unexpected user

### Phase 2: Investigation

For each suspicious process, gather forensics **BEFORE killing**:

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud '
  PID=SUSPICIOUS_PID;
  echo "=== PROCESS DETAILS ===";
  ps -p $PID -o pid,user,pcpu,pmem,rss,lstart,args --no-headers;
  echo;
  echo "=== FILE INFO ===";
  ls -la /proc/$PID/exe 2>/dev/null;
  file /proc/$PID/exe 2>/dev/null;
  md5sum /proc/$PID/exe 2>/dev/null;
  echo;
  echo "=== NETWORK CONNECTIONS ===";
  ss -tnp | grep $PID;
  echo;
  echo "=== OPEN FILES ===";
  ls -la /proc/$PID/fd 2>/dev/null | head -20;
  echo;
  echo "=== PARENT PROCESS ===";
  cat /proc/$PID/status 2>/dev/null | grep PPid;
  echo;
  echo "=== COMPROMISED USER ===";
  USER=$(ps -p $PID -o user --no-headers);
  echo "User: $USER";
  id $USER;
  crontab -u $USER -l 2>/dev/null;
  echo;
  echo "=== AUTH LOG (recent logins) ===";
  grep "$USER" /var/log/auth.log 2>/dev/null | grep -iE "accepted|failed|password changed" | tail -20;
  echo;
  echo "=== SSH KEYS ===";
  cat /home/$USER/.ssh/authorized_keys 2>/dev/null;
  echo;
  echo "=== PERSISTENCE MECHANISMS ===";
  ls -laR /home/$USER/.config/systemd/ 2>/dev/null;
  find /home/$USER -name "*.service" -o -name "agetty" 2>/dev/null;
'
```

**Document the attack chain:**
- Entry point (SSH brute-force? Vulnerable service?)
- Timeline (auth.log timestamps)
- Persistence (crontab? systemd user units? config files?)
- Network (mining pool IP/port? C2 server?)

### Phase 3: Containment & Eradication

**CRITICAL: Kill ALL processes for the compromised user, not just the miner.**
Last time we only killed the miner binary but left the spawner process running — it respawned a new miner within hours.

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud '
  COMPROMISED_USER=USERNAME;

  echo "=== KILLING ALL PROCESSES ===";
  pkill -9 -u $COMPROMISED_USER;
  sleep 1;
  ps -u $COMPROMISED_USER --no-headers 2>/dev/null && echo "WARNING: processes still running" || echo "All processes killed";

  echo;
  echo "=== REMOVING MALWARE ===";
  # Remove ALL executable files in temp dirs owned by user
  find /tmp /var/tmp /dev/shm -user $COMPROMISED_USER -type f -delete 2>/dev/null;
  echo "Temp files removed";

  echo;
  echo "=== REMOVING PERSISTENCE ===";
  crontab -r -u $COMPROMISED_USER 2>/dev/null;
  echo "Crontab cleared";
  rm -rf /home/$COMPROMISED_USER/.config/systemd/ 2>/dev/null;
  echo "Systemd user config removed";

  echo;
  echo "=== TERMINATING USER SESSION ===";
  loginctl terminate-user $COMPROMISED_USER 2>/dev/null;
  echo "Session terminated";

  echo;
  echo "=== LOCKING ACCOUNT ===";
  passwd -l $COMPROMISED_USER;
  usermod -s /usr/sbin/nologin $COMPROMISED_USER;
  rm -f /home/$COMPROMISED_USER/.ssh/authorized_keys;
  echo "Account locked, shell=nologin, SSH keys removed";
'
```

**Ask user:** Delete user entirely? (`userdel -r USERNAME && rm -rf /home/USERNAME`)

### Phase 4: Verification

```bash
ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud '
  echo "=== VERIFY CLEANUP ===";
  echo "Processes:"; ps -u COMPROMISED_USER 2>/dev/null || echo "  None";
  echo "Temp files:"; find /tmp /var/tmp /dev/shm -user COMPROMISED_USER 2>/dev/null || echo "  None";
  echo "Crontab:"; crontab -u COMPROMISED_USER -l 2>/dev/null || echo "  None";
  echo "Account:"; grep COMPROMISED_USER /etc/passwd;
  echo;
  echo "=== SYSTEM RESOURCES ===";
  free -m | head -3;
  echo;
  echo "=== REMAINING SUSPICIOUS ===";
  find /tmp /var/tmp /dev/shm -type f -perm -u+x 2>/dev/null;
'
```

### Phase 5: Hardening

Suggest these mitigations to user:

1. **Disable password auth for SSH:**
   ```bash
   # /etc/ssh/sshd_config:
   PasswordAuthentication no
   ```

2. **Install fail2ban:**
   ```bash
   apt install fail2ban -y
   systemctl enable fail2ban
   ```

3. **Audit all user accounts:**
   ```bash
   grep -v nologin /etc/passwd | grep -v /bin/false
   ```

4. **Remove unnecessary users** (ask user first!)

### Guardrails

- **NEVER kill processes without investigating first** — document the attack chain
- **Kill ALL user processes, not just the miner** — spawner processes respawn miners
- **Check for MULTIPLE persistence mechanisms** — crontab + systemd + SSH keys + hidden scripts
- **Always verify after cleanup** — run Phase 4 to confirm eradication
- **Don't delete users without asking** — they might be legitimate accounts
- **Save forensic evidence** — MD5 hash of malware, auth.log excerpts, network connections

### Known Attack Patterns

**Cryptominer (observed Feb 2026):**
- Entry: SSH brute-force (weak password on `claude` user)
- Binary: Stripped ELF in `/var/tmp/[random-digits]` (3.2MB)
- Persistence: `@reboot` crontab → `/home/USER/.config/systemd/agetty` (disguised ELF dropper)
- Network: Outbound TCP to mining pool on high port
- Behavior: 100-180% CPU, 2+ GB RAM, stdin/stdout/stderr → /dev/null
- Timeline: Login → deploy (15 seconds) → change password → exit

---
*Generated by /reflect-skills from cryptominer incident response (Feb 2026)*
