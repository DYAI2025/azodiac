# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Context

This is a personal home directory workspace (macOS, Apple Silicon) containing multiple projects, AI agent infrastructure, and skill libraries. The user communicates in both English and German.

## Directory Layout

- `Projects/` - Main development projects (30+ projects including DeepAgent, FlashDoc, BaZiEngine, claude-mem, etc.)
- `Active/` - Current work organized into `Claude-Workspace/`, `Projects-Current/`, `Quick-Access/`
- `OMNI-SKILLS/` - Extended skill library (GPT prompts, blueprint skills, automation tools)
- `claude-skills/` - Claude Code skill configurations
- `DevTools/` - IDE configs, runtimes, utilities
- `FileOrganizer/` - Python-based file watcher/organizer with dashboard (`start.sh`/`stop.sh`/`status.sh`)
- `Tools/` - Standalone tools (OpenMarkdownReader)
- `.claude/commands/` - Slash commands (skills invokable via `/command-name`)
- `.claude/skills/` and `.claude/skills-unified/` - Categorized skill definitions

## File Organization Rules

**Never save files to the home directory root.** Use appropriate subdirectories:
- New projects → `Projects/`
- Test files → within project's `/tests` folder
- Documentation → within project's `/docs` folder

## Execution Patterns

When spawning multiple agents or performing parallel operations, batch ALL related operations in a single message:
- Use Task tool to spawn all agents concurrently
- Batch all file operations together
- Batch all bash commands together

## Claude-Flow Integration

Multi-agent orchestration via `claude-flow`. Config: `claude-flow.config.json` (hierarchical topology, max 10 agents).

```bash
npx claude-flow sparc run <mode> "<task>"
npx claude-flow hive-mind spawn "<objective>"
```

Install requires BOTH npm and Homebrew: `npm install -g claude-flow@alpha` + `brew install claude-flow`. The npm version is needed because settings.json hooks call `npx claude-flow@alpha`.

## Infrastructure

### DYAI VPS (srv1308064.hstgr.cloud)
- SSH: `ssh -i ~/.ssh/id_ed25519 root@srv1308064.hstgr.cloud`
- Active agents: Perr00bot, Marvin, OpenClaw
- Git repo: `/opt/agent-zero-data` (remote: DYAI2025/agent-zero)
- Vibe Kanban: https://kanban-jet-seven-ashy.vercel.app/

### Tailscale Network
- Linux PC Berlin: `dyai@100.103.64.33`
- EvermemOS: `/home/dyai/EverMemOS` (MongoDB port 27017)

## Project-Specific Instructions

When working in a specific project, check for that project's own CLAUDE.md file which will contain project-specific build commands, architecture, and conventions.
