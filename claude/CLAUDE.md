# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A curated collection of Claude Code skill repositories, plugin ecosystems, and reference materials. Each subdirectory is an independent project (usually cloned from GitHub). The git repo at this level only tracks `.claude/` contents — all subdirectories are untracked.

## Repository Map

### Plugin ecosystems & learning systems
| Directory | What It Is |
|-----------|-----------|
| `superpowers-main/` | Subagent-driven development workflow plugin (obra/superpowers) |
| `homunculus-main/` | Instinct-based learning plugin — observes, learns patterns, evolves |
| `claude-reflect/` | Self-learning system — captures corrections via hook queue, `/reflect` promotes them to CLAUDE.md / reusable skills |
| `antigravity-awesome-skills-main/` | Skill collection including Loki Mode (autonomous startup builder) |
| `Agent-Skills-for-Context-Engineering/` | Skill authoring patterns and examples |
| `awesome-claude-code-main/` | Curated list of Claude Code resources, CLAUDE.md examples |
| `awesome-claude-skills-master/` | Community skill directory |
| `skills-vercel-main/` | Vercel-deployed skill registry |
| `SwiftUI-Agent-Skill/` | SwiftUI agent skill (iOS 26 / Swift 6.2, twostraws) |

### Memory / context infrastructure
| Directory | What It Is |
|-----------|-----------|
| `engram/` | Persistent memory for AI coding agents — agent-agnostic Rust single binary |
| `UnseveredMemory/` | Persistent AI memory framework |
| `OneContext-main/` | Context management tool |
| `jcodemunch-mcp/` | MCP server for code compression/analysis |

### Agent runtimes & bridges
| Directory | What It Is |
|-----------|-----------|
| `openfang/` | "The Agent Operating System" — Rust, ~137K LOC across 14 crates |
| `nanoclaw-main/` | WhatsApp/Telegram → Claude agent bridge (Node.js + containers) |
| `autoclaude/` | Autoresearch tool |
| `claude-health/` | Health-check / monitoring utility |
| `claude-canvas/` | Canvas-style UI for Claude |
| `claude-code-voice-skill/` | Voice input skill |
| `claude-island/` | Island-based Claude environment |

### Dev tooling & CLIs
| Directory | What It Is |
|-----------|-----------|
| `CLI-tokenreducter-master/` | RTK — Rust CLI proxy for LLM token reduction (60-90% savings) |
| `Backlog.md-main/` | Task management via Backlog.md MCP |
| `chartli/` | Terminal chart-rendering CLI (ascii/spark/bars/braille/svg) |
| `gitHub-reofetcher/` | GitHub repo fetcher |
| `youtube-fetcher/` | YouTube → Markdown fetcher |
| `scraper/` | `claude-code-skill-scrapling` — scraping skill |
| `Uncodixfy/` | Skill for reversing minified/obfuscated code |

### Design / landingpage assets
| Directory | What It Is |
|-----------|-----------|
| `Bazodiac/` | Next.js + shadcn/ui landingpage template (BaZi project) |
| `fonttrio/` | 49 curated font pairings for shadcn/ui projects |
| `extracted-effects/` | Reusable Canvas effects extracted from Bazodiac (vanilla JS, GSAP optional) |
| `claude2/` | Page design project (shaders/WebGL) |
| `Claude-Ads/` | Ads audit and optimization skills |

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

## Compiled Rust projects

Two compiled Rust projects live here. Both are standalone — `cd` in before running cargo.

### RTK (`CLI-tokenreducter-master/`)
Snapshot-tested with `insta`.

```bash
cargo build --release          # Build
cargo test --all               # All tests
cargo test --ignored           # Integration tests (requires installed binary)
cargo insta review             # Review snapshot changes
```

### openfang (`openfang/`)
Multi-crate workspace (~14 crates, 1.7k+ tests). Standard cargo workflow; see its own `README.md` / `docs/` for agent/runtime specifics.
