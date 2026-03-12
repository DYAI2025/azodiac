---
description: "10-second project status: tests, git state, key metrics"
allowed-tools: ["Bash", "Read", "Glob"]
---

## Your Task

Print a concise terminal-only project status covering all dimensions in one glance.

### Steps

1. **Detect project type** — Check for `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `CLAUDE.md` etc.

2. **Run ALL of these in parallel** (single message, multiple Bash calls):

   ```bash
   # Git state
   git log --oneline -3 && echo "---" && git status -s | head -5
   ```

   ```bash
   # Tests (adapt to project)
   # Python: python3 -m pytest tests/ -x -q 2>&1 | tail -3
   # Node: npm test 2>&1 | tail -5
   # Rust: cargo test 2>&1 | tail -5
   # Go: go test ./... 2>&1 | tail -5
   ```

   ```bash
   # Project-specific metrics from CLAUDE.md or config
   # e.g. marker count, endpoint count, model count
   ```

3. **Format output** as a compact status block:

   ```
   ══════════════════════════════════════
     Project Quick Status
   ══════════════════════════════════════
   Tests:       XX passed
   Last commit: abc1234 description
   Git state:   clean / N untracked
   [project-specific metrics]
   ══════════════════════════════════════
   ```

### Guardrails
- Read-only — never modify files
- Skip slow operations (full eval suites, builds)
- If tests fail, show the failure line, don't hide it
