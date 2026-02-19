---
description: End-to-end service debugging and repair workflow
allowed-tools: [Bash, Read, Grep, AskUserQuestion]
---

## Context
When a service on a remote system (VPS, server) is not working as expected, this skill provides a systematic debugging and repair workflow. It combines health monitoring, service discovery, root cause analysis, hypothesis testing, and verification.

## Your Task

Debug and repair a malfunctioning service using scientific methodology: observe, hypothesize, test, fix, verify.

### Steps

1. **Understand the Problem**

   Ask user:
   - What service is having issues?
   - What are the symptoms? (not responding, errors, wrong behavior)
   - When did it start?
   - Any recent changes?

2. **Phase 1: Observation & Health Check**

   Use `/nexus-health` or equivalent to gather facts:
   ```bash
   # Check service status
   ssh USER@HOST "systemctl status SERVICE_NAME --no-pager"

   # Check process status
   ssh USER@HOST "ps aux | grep SERVICE_NAME | grep -v grep"

   # Check logs for errors
   ssh USER@HOST "journalctl -u SERVICE_NAME --since '1 hour ago' | grep -i error | tail -50"
   ssh USER@HOST "tail -100 /path/to/service/logs/*.log"
   ```

   **Look for:**
   - Error messages
   - Authentication failures (401, 403)
   - Connection timeouts
   - Resource issues (out of memory, disk full)
   - Missing dependencies

3. **Phase 2: Service Discovery & Context**

   Use `/remote-service-discovery` to understand the ecosystem:
   ```bash
   # What's listening?
   ssh USER@HOST "netstat -tulpn | grep LISTEN"

   # What's the service topology?
   ssh USER@HOST "ps aux | grep -E '(SERVICE|RELATED)' | grep -v grep"

   # Configuration
   ssh USER@HOST "cat /path/to/service/config.json"
   ssh USER@HOST "cat /path/to/service/.env"
   ```

4. **Phase 3: Root Cause Analysis**

   Based on observations, form hypotheses:

   **Common patterns:**
   - **401/403 errors** → Auth problem OR API doesn't need auth
   - **Connection refused** → Service down OR firewall OR wrong port
   - **Timeout** → Service overloaded OR network issue
   - **"Command not found"** → Binary not installed OR not in PATH
   - **"Permission denied"** → File permissions OR user permissions

   **CRITICAL: Test your assumptions before fixing!**

5. **Phase 4: Hypothesis Testing**

   **DON'T FIX YET!** Test your hypothesis first.

   Example: "401 Unauthorized" errors
   ```bash
   # Hypothesis 1: Token expired → Need new token
   # Hypothesis 2: API doesn't need auth → Remove token

   # TEST FIRST:
   ssh USER@HOST "curl -s https://api.example.com/endpoint"
   # If this works → API doesn't need auth!
   # If this fails → API needs auth
   ```

   Example: "Service not responding"
   ```bash
   # Hypothesis 1: Service crashed
   # Hypothesis 2: Service running but on wrong port

   # TEST:
   ssh USER@HOST "ps aux | grep service"  # Is it running?
   ssh USER@HOST "netstat -tulpn | grep PORT"  # Is it listening?
   ```

   **Occam's Razor:** Test the simplest hypothesis first.

6. **Phase 5: Fix Implementation**

   Based on confirmed hypothesis, implement fix:

   **Config change:**
   ```bash
   ssh USER@HOST "cat > /path/to/config << 'EOF'
   # Updated config
   EOF"
   ```

   **Service restart:**
   ```bash
   ssh USER@HOST "systemctl restart SERVICE_NAME"
   # OR
   ssh USER@HOST "pkill -f SERVICE_NAME && cd /path && nohup ./start.sh &"
   ```

   **Install missing dependency:**
   ```bash
   ssh USER@HOST "npm install -g PACKAGE"
   ```

   **Fix permissions:**
   ```bash
   ssh USER@HOST "chmod 755 /path/to/script.sh"
   ```

7. **Phase 6: Verification**

   **Confirm the fix worked:**
   ```bash
   # Check process is running
   ssh USER@HOST "ps aux | grep SERVICE | grep -v grep"

   # Check logs for success
   ssh USER@HOST "tail -20 /path/to/service.log"

   # Test endpoint
   ssh USER@HOST "curl -s http://localhost:PORT/health"

   # Monitor for errors (30 seconds)
   ssh USER@HOST "timeout 30 tail -f /path/to/service.log"
   ```

8. **Document the Fix**

   Provide summary:
   ```
   Problem: [What was broken]
   Root Cause: [Why it was broken]
   Hypothesis Tested: [What you tested]
   Solution: [What you changed]
   Verification: [How you confirmed it works]
   ```

### Guardrails

**Test Before Fix:**
- NEVER implement a fix without testing the hypothesis first
- A 30-second test can save hours of debugging
- Example: Test API without auth before getting new token

**Occam's Razor:**
- Prefer simple solutions over complex ones
- "Token expired" might actually be "token not needed"
- "Service down" might actually be "service on different port"

**Understand Before Acting:**
- Read logs completely before jumping to conclusions
- 401 doesn't always mean "need authentication"
- Connection refused doesn't always mean "service down"

**Systematic Approach:**
```
1. Observe (gather facts)
2. Hypothesize (form theories)
3. Test (verify theories)
4. Fix (implement solution)
5. Verify (confirm it works)
```

**Document Learnings:**
- If the fix was non-obvious, update CLAUDE.md
- If it's a recurring pattern, consider creating a new skill
- Share knowledge with VPS Claude instance

### Common Troubleshooting Patterns

**Pattern: Authentication Errors (401/403)**
```bash
# DON'T: Immediately get new token
# DO: Test if auth is actually needed
curl -s https://api.example.com/endpoint
# If it works → Remove auth requirement
# If it fails → Then get new token
```

**Pattern: Service Not Responding**
```bash
# Check in order:
1. Is process running? (ps aux)
2. Is it listening on expected port? (netstat)
3. Is port accessible? (curl localhost:PORT)
4. Are there errors in logs? (tail logs)
5. Is firewall blocking? (iptables -L)
```

**Pattern: "Command Not Found"**
```bash
# Check:
1. Is it installed? (which COMMAND)
2. Is it in PATH? (echo $PATH)
3. Is it installed for the right user? (su - USER -c 'which COMMAND')
4. Does it need npm/pip/etc? (npm list -g | grep PACKAGE)
```

**Pattern: Configuration Issues**
```bash
# Verify:
1. Config file exists (ls -la /path/to/config)
2. Config is valid JSON/YAML (cat config | jq . OR yamllint)
3. Environment variables set (printenv | grep VAR)
4. Permissions correct (ls -la config)
```

### Advanced: Multi-Service Dependencies

When service A depends on service B:
```bash
# 1. Check dependency graph
ps aux | grep -E '(SERVICE_A|SERVICE_B)'

# 2. Test B first
curl http://localhost:B_PORT/health

# 3. Check A's connection to B
ssh USER@HOST "grep -r 'SERVICE_B' /path/to/A/logs/"

# 4. Verify network connectivity
ssh USER@HOST "nc -zv localhost B_PORT"
```

### Example: Today's Kanban Task Runner Fix

**Problem:** Task Runner not fetching tasks from board

**Phase 1 - Observation:**
- Logs showed: "401 with token, retrying without auth"
- Service running (PID 1569296)
- 401 errors repeating every 15 seconds

**Phase 2 - Service Discovery:**
- Task Runner: localhost:3004
- Kanban API: https://kanban-jet-seven-ashy.vercel.app
- Token in .env.local: VERCEL_OIDC_TOKEN (expired Feb 11)

**Phase 3 - Root Cause Hypotheses:**
1. Token expired → Need new token
2. Token misconfigured → API doesn't need auth

**Phase 4 - Hypothesis Testing:**
```bash
curl https://kanban-jet-seven-ashy.vercel.app/api/columns
→ 200 OK + full data!
```
**Result:** API is PUBLIC, doesn't need auth!

**Phase 5 - Fix:**
- Remove VERCEL_OIDC_TOKEN from .env.local
- Set KANBAN_API_TOKEN=""
- Restart task-runner.js

**Phase 6 - Verification:**
- Logs show: "Column IDs resolved"
- First task processing: ✅
- No more 401 errors: ✅

**Key Learning:** 401 doesn't always mean "need token" - test the API first!

---
*Generated by /reflect-skills from VPS troubleshooting session*
