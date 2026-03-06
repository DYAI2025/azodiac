---
description: Interactive skill finder - search and activate skills by purpose
allowed-tools: [Bash, Skill]
---

## Context
The user wants to find and activate a skill from 1000+ installed skills.

## Your Task
1. Run the skilldex TUI: `~/.claude/bin/skilldex.sh`
2. The script outputs the skill invocation command (e.g. `/skill fastapi-pro`)
3. Execute the output as a Skill tool call

If fzf is not installed, run `brew install fzf` first.
If the user cancels (Esc), acknowledge and do nothing.
