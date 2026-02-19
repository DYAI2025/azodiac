---
description: Audit and manage Claude processes across all machines
allowed-tools: [Bash, Read, AskUserQuestion]
---

## Context
You are auditing Claude Code processes across multiple machines (local Mac, VPS, Linux PC Berlin) to understand what's running, measure resource consumption, and manage processes.

## Your Task

Find, analyze, and manage Claude-related processes on local and remote systems.

### Steps

1. **Define Scope**
   Ask user which machines to audit:
   - **Local** (current Mac)
   - **VPS** (srv1308064.hstgr.cloud)
   - **Linux PC Berlin** (dyai@100.103.64.33 via Tailscale)
   - **All machines**

2. **Audit Local Machine**

   **Find Claude Processes:**
   ```bash
   ps aux | grep -E '(claude|claude-code|npx.*claude)' | grep -v grep
   ```

   **Detailed Process Info:**
   ```bash
   ps -eo pid,ppid,user,%cpu,%mem,vsz,rss,tty,stat,start,time,command | grep -E '(claude|claude-code)' | grep -v grep
   ```

   **Analyze Each Process:**
   For each Claude process found:
   - **PID:** Process ID
   - **Purpose:** Main process, subagent, background task, etc.
   - **CPU %:** Current CPU usage
   - **Memory %:** RAM usage
   - **VSZ/RSS:** Virtual/Resident memory size
   - **Runtime:** How long it's been running
   - **Command:** Full command line

3. **Categorize Claude Processes**

   **Main Claude Code Process:**
   - Usually runs as `claude` or `node ...claude-code...`
   - Parent of subagents

   **Subagents:**
   - Spawned by Task tool
   - Named like `agent-aprompt_suggestion-xyz`
   - Check: `ls ~/.claude/projects/*/subagents/` for active subagent sessions

   **Background Processes:**
   - Hooks (TTS, etc.)
   - MCP servers
   - npx executions

4. **Measure Resource Consumption**

   **Total Claude Resource Usage:**
   ```bash
   ps aux | grep -E '(claude|claude-code)' | grep -v grep | awk '{cpu+=$3; mem+=$4} END {print "Total CPU: " cpu "%, Total Memory: " mem "%"}'
   ```

   **Top Resource Consumers:**
   ```bash
   ps aux | grep -E '(claude|claude-code)' | grep -v grep | sort -nrk 3 | head -10
   ```

5. **Audit Remote Machines**

   For each remote machine, execute same analysis via SSH:

   **VPS:**
   ```bash
   ssh root@srv1308064.hstgr.cloud "ps aux | grep -E '(claude|openclaw|npx.*claude)' | grep -v grep"
   ```

   **Linux PC Berlin:**
   ```bash
   ssh root@100.103.64.33 "su - dyai -c 'ps aux | grep -E (claude|openclaw|seline) | grep -v grep'"
   ```

6. **Present Audit Report**

   Create summary table:

   ```
   ═══ CLAUDE PROCESS AUDIT ═══

   Machine: MacBook (Local)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [Process 1]
   PID:      12345
   Purpose:  Main Claude Code process
   CPU:      5.2%
   Memory:   2.3% (450 MB)
   Runtime:  2h 15m
   Command:  /usr/bin/claude code
   Status:   Active

   [Process 2]
   PID:      12389
   Purpose:  Subagent (prompt_suggestion)
   CPU:      0.1%
   Memory:   0.5% (98 MB)
   Runtime:  15m
   Command:  node ...subagent...
   Status:   Active

   Total Local Usage:
   - CPU: 5.3%
   - Memory: 2.8%
   - Processes: 2

   Machine: VPS (srv1308064.hstgr.cloud)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [No Claude processes found]

   Machine: Linux PC Berlin (100.103.64.33)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [Process 1]
   PID:      98765
   Purpose:  OpenClaw agent
   CPU:      1.2%
   Memory:   3.4% (680 MB)
   Runtime:  1d 5h
   Command:  openclaw agent
   Status:   Active

   Total Across All Machines:
   - Processes: 3
   - Total CPU: 6.5%
   - Total Memory: 6.2%
   ```

7. **Process Management Options**

   Ask user what to do:
   - **Monitor** - Continue monitoring
   - **Kill specific process** - Terminate by PID
   - **Kill all subagents** - Clean up finished subagents
   - **Kill zombie processes** - Processes using 0% CPU for >1h
   - **Restart main process** - Kill and restart Claude Code

### Process Categories & Actions

**Safe to Kill:**
- Zombie subagents (0% CPU, completed tasks)
- Old background processes (>24h runtime, 0% activity)
- Duplicate processes (multiple main processes)

**Risky to Kill (Ask First):**
- Main Claude Code process (user's active session)
- Active subagents (running tasks)
- Processes with high CPU (actively working)

**Never Kill Without Warning:**
- The current Claude session (would interrupt this conversation)

### Kill Commands

**Kill by PID:**
```bash
kill -9 PID
```

**Kill all Claude subagents (local):**
```bash
pkill -9 -f "claude.*subagent"
```

**Kill all Claude subagents (remote):**
```bash
ssh USER@HOST "pkill -9 -f 'claude.*subagent'"
```

**Find and kill zombies:**
```bash
ps aux | grep -E '(claude|openclaw)' | grep -v grep | awk '$3 == 0.0 {print $2}' | xargs kill -9 2>/dev/null
```

### Guardrails
- **Never kill current session** without explicit user request
- **Warn before killing main process** - disrupts active work
- **Show process details** before killing - let user verify
- **Check if process is parent** - killing parent kills children
- **Confirm remote kills** - harder to recover from mistakes

### Common Scenarios

**Scenario 1: Too many subagents**
- Check: `ls ~/.claude/projects/*/subagents/ | wc -l`
- Many finished subagents accumulate over time
- Safe to kill all with 0% CPU

**Scenario 2: High memory usage**
- Identify top consumers
- Check if processes are stuck (same CPU % over time)
- Kill stuck processes

**Scenario 3: Orphaned processes**
- Parent process died but children still running
- Look for ppid pointing to non-existent process
- Safe to clean up

**Scenario 4: Multiple main processes**
- User may have multiple Claude windows open
- Verify which is current session (by PID or terminal)
- Kill others if desired

### Advanced Analysis

**Track resource usage over time:**
```bash
while true; do
  echo "=== $(date) ==="
  ps aux | grep -E '(claude|openclaw)' | grep -v grep | awk '{printf "%-8s %5.1f%% %5.1f%% %s\n", $2, $3, $4, $11}'
  sleep 5
done
```

**Find long-running processes:**
```bash
ps -eo pid,etime,command | grep -E '(claude|openclaw)' | grep -v grep
```

**Memory breakdown:**
```bash
ps -eo pid,rss,command | grep -E '(claude|openclaw)' | grep -v grep | awk '{sum+=$2} END {print "Total: " sum/1024 " MB"}'
```

---
*Generated by /reflect-skills from user request for multi-machine Claude process management*
