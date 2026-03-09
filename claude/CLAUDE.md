# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A curated collection of Claude Code skill repositories, plugin ecosystems, and reference materials. Each subdirectory is an independent project (usually cloned from GitHub). The git repo at this level only tracks `.claude/` contents — all subdirectories are untracked.

## Repository Map

| Directory | What It Is |
|-----------|-----------|
| `superpowers-main/` | Subagent-driven development workflow plugin (obra/superpowers) |
| `homunculus-main/` | Instinct-based learning plugin — observes, learns patterns, evolves |
| `nanoclaw-main/` | WhatsApp/Telegram → Claude agent bridge (Node.js + containers) |
| `antigravity-awesome-skills-main/` | Skill collection including Loki Mode (autonomous startup builder) |
| `awesome-claude-code-main/` | Curated list of Claude Code resources, CLAUDE.md examples |
| `awesome-claude-skills-master/` | Community skill directory |
| `CLI-tokenreducter-master/` | RTK — Rust CLI proxy for LLM token reduction (60-90% savings) |
| `Backlog.md-main/` | Task management via Backlog.md MCP |
| `Agent-Skills-for-Context-Engineering/` | Skill authoring patterns and examples |
| `skills-vercel-main/` | Vercel-deployed skill registry |
| `claude-canvas/` | Canvas-style UI for Claude |
| `claude-code-voice-skill/` | Voice input skill |
| `claude-island/` | Island-based Claude environment |
| `OneContext-main/` | Context management tool |
| `UnseveredMemory/` | Persistent AI memory framework |
| `claude2/` | Page design project (shaders/WebGL) |
| `Claude-Ads/` | Ads audit and optimization skills |
| `jcodemunch-mcp/` | MCP server for code compression/analysis |
| `Uncodixfy/` | Skill for reversing minified/obfuscated code |

## Git Tracking

Only `CLAUDE.md` is tracked by git. Everything else (all subdirectory projects, `.claude/` contents) is untracked. Each subdirectory is a standalone clone.

## Working With This Repo

- Each subdirectory has its own `README.md` and often its own `CLAUDE.md` — **always read those before working in a subdirectory**
- There are no repo-wide build/test/lint commands — each project is independent
- When working in a subdirectory project, `cd` into it first so its own `CLAUDE.md` takes effect
- `.claude/homunculus/` contains observation logs (`observations.jsonl`) and learned instincts (`instincts/pending/`)
- To install a Claude Code plugin: `/plugin marketplace add <org>/<name>` then `/plugin install <plugin>@<marketplace>`

## Root-Level Scripts

- `vps-cleanup.sh` — VPS process cleanup and maintenance script

## RTK (CLI-tokenreducter-master)

The only compiled project in this collection. Rust-based, uses `insta` for snapshot testing.

```bash
cargo build --release          # Build
cargo test --all               # All tests
cargo test --ignored           # Integration tests (requires installed binary)
cargo insta review             # Review snapshot changes
```
