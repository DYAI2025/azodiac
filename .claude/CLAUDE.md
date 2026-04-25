- Add to memory always

## Multi-Agent Coordination Patterns

- Use Claude Code's Task tool to spawn ALL agents concurrently in ONE message
- MCP tools (swarm_init, agent_spawn) are for coordination setup only, not actual agent execution
- Batch ALL TodoWrite operations (5-10+ todos minimum) in single calls
- Execute file operations, memory stores, and agent spawns in parallel within single messages
- Never spawn agents across multiple messages - this breaks parallel coordination

## VPS & Docker

- If Docker pulls fail with "connection reset" on VPS, disable IPv6: `sysctl -w net.ipv6.conf.all.disable_ipv6=1`
- ARM64 Docker images (from Mac M1/M2) won't run on AMD64 servers - pull directly on target or use `--platform linux/amd64`

## SSH

- Keys with passphrase can't be used non-interactively. Remove passphrase with `ssh-keygen -p` or create new key with `-N ""`

## Vibe Kanban

- Use `PORT` env variable (not `--port` flag) to set port: `Environment=PORT=3000` in systemd service
- Needs `npx vibe-kanban` to run both backend and frontend together

## DYAI VPS (srv1308064.hstgr.cloud)

- Vibe Kanban: https://kanban-jet-seven-ashy.vercel.app/ (Vercel deployment)
- Active agents: Perr00bot, Marvin, OpenClaw
- SSH (root): `ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud`
- SSH (moltbot): `ssh moltbot@srv1308064.hstgr.cloud` (no key needed, default key works)
- Resources: 8GB RAM, 96GB disk (Ubuntu 24.04, x86_64)
- Git repo: /opt/agent-zero-data (remote: DYAI2025/agent-zero)
- Memory sync cronjob: every 15min via /opt/agent-zero-data/scripts/memory-sync.sh

## Claude-Flow

- Install BOTH npm and Homebrew versions: `npm install -g claude-flow@alpha` + `brew install claude-flow`
- Settings.json hooks call `npx claude-flow@alpha`, so npm version required even if Homebrew installed
- Corrupted npx cache causes ENOTEMPTY errors - fix with `rm -rf ~/.npm/_npx/[dir] && npm cache clean --force`

## Process Management

- MCP servers (claude-mem, chroma-mcp) spawn orphan processes that don't cleanup on session exit
- Zombie processes (0% CPU) accumulate over time and consume RAM
- Use `/claude-process-manager` to audit and cleanup zombies across all machines
- Prevention: Need systemd services with timeouts or cron job for cleanup

## Tailscale Network

- Linux PC Berlin: dyai@100.103.64.33 (Tailscale)
- Direct SSH bypasses user mapping: `ssh root@100.103.64.33` or `ssh dyai@100.103.64.33`
- Selina web UI: http://100.103.64.33:3000
- EvermemOS location: /home/dyai/EverMemOS (MongoDB on port 27017, credentials: admin/memsys123)

## Git & Project Setup

- `.gitignore`: `dir/` blocks ALL children including negations — use `dir/*` + `!dir/allowed/` pattern instead
- Skills universally useful across projects → create as global (`~/.claude/commands/`), not project-local

## Development Principles

- Nothing is true until it runs. What doesn't work should fail visibly so we can fix it
- No masking errors, no hiding, no empty promises - only delivery and transparency

## Proactive Decision-Making (Decision-Maker Heuristic)

**Core Rule:** When I identify a clearly better solution while working, implement it without asking

**Apply when:**
- Obvious improvements during tasks (fixing A reveals trivial fix for B → do both)
- Testing my assumptions (before complex solution, test if simple one works)
- Cleanup of direct consequences (removing service → also remove its configs)
- Optimization of requested solutions (user asks for A, B is objectively better → do B, explain why)

**Never apply to:**
- Destructive changes outside scope
- Architectural decisions
- Business logic changes
- Unclear trade-offs

**Decision Test:** "If I asked user 'Soll ich X auch machen?', would they say 'Ja klar'?"
- Yes → Do it proactively, document in summary
- Maybe → Ask first
- No → Don't do it

**Examples from practice:**
- User: "Fix auth errors" → I tested API without token first (worked!) → Removed token requirement instead of complex Vercel CLI setup
- User: "Fix Task Runner" → Also cleaned dead nginx configs routing to removed services
- Post-task: Recognized debugging pattern → Proposed `/service-troubleshoot` skill during `/reflect-skills`

**Goal:** Entlaste User durch intelligente Eigeninitiative. Positiv überraschen statt nachfragen.

See `~/.claude/commands/decision-maker.md` for detailed framework and examples.

@RTK.md

@/Users/benjaminpoersch/claude/browser-harness/SKILL.md
