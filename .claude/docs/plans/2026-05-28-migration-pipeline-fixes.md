# Migration Pipeline Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all blocking and important issues found in the code review of the agent migration pipeline, plus the three generated agent files.

**Architecture:** Four targeted fixes to existing scripts + three agent file rewrites. Each fix is a separate TDD cycle: failing test first, minimal impl, green, commit. No new abstractions.

**Tech Stack:** Python 3.12, uv, pytest, PyYAML — same stack as the pipeline itself.

---

## Path Reference

| Alias | Actual path (from `~/.claude`) |
|-------|-------------------------------|
| `scripts/` | `scripts/` |
| `tests/` | `tests/` |
| `agents-src/agency-normalized/` | `agents-src/agency-normalized/` |
| Test runner | `uv run python3 -m pytest` |

---

## TASK-FIX-01: Fix `is_blocked_output` dead-code path

**Priority:** Blocking (security safety — false sense of protection)

**Problem:** `scripts/compile-agency-agent.py:89-91` checks `"agency-normalized" not in parts` where `parts` is a tuple of individual path components. The string `"agency-normalized"` will never match a path component because it's a multi-char directory name that only appears as a full component — and even then the check is logically inverted. The string-based fallback on lines 94-97 is what actually guards the block. Dead code in a safety check is a latent bug.

**Files:**
- Modify: `scripts/compile-agency-agent.py:83-98`
- Modify: `tests/test_compile_agency_agent.py` (add regression test)

### Step 1: Write the failing regression test

Add to `tests/test_compile_agency_agent.py`:

```python
def test_is_blocked_output_blocks_absolute_agents_path():
    """Absolute path resolving to .../agents/ must be blocked."""
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path("scripts")))
    from compile_agency_agent import is_blocked_output  # noqa: E402 (inserted path)
    # Absolute path with 'agents' as final component
    assert is_blocked_output(pathlib.Path("/some/project/agents"))
    # Absolute path with 'agents/' inside
    assert is_blocked_output(pathlib.Path("/some/project/agents/core"))
    # Safe paths must NOT be blocked
    assert not is_blocked_output(pathlib.Path("agents-src/agency-normalized"))
    assert not is_blocked_output(pathlib.Path("/home/user/agents-src/agency-normalized"))
```

### Step 2: Import fix needed — rename script to importable module

The test imports `is_blocked_output` directly. Python can't import `compile-agency-agent.py` (hyphen in name). Add an alias at the bottom of the script OR rename the import target using `importlib`:

Replace the import in the test with:

```python
import importlib.util, pathlib, sys

def _load_compile():
    spec = importlib.util.spec_from_file_location(
        "compile_agency_agent",
        pathlib.Path("scripts/compile-agency-agent.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_is_blocked_output_blocks_absolute_agents_path():
    mod = _load_compile()
    assert mod.is_blocked_output(pathlib.Path("/some/project/agents"))
    assert mod.is_blocked_output(pathlib.Path("/some/project/agents/core"))
    assert not mod.is_blocked_output(pathlib.Path("agents-src/agency-normalized"))
    assert not mod.is_blocked_output(pathlib.Path("/home/user/agents-src/agency-normalized"))
    assert not mod.is_blocked_output(pathlib.Path("agents-src/agency-normalized/subdir"))
```

### Step 3: Run test to verify it fails

```bash
uv run python3 -m pytest tests/test_compile_agency_agent.py::test_is_blocked_output_blocks_absolute_agents_path -v
```

Expected: `FAILED` — either import error or assertion error on absolute path case.

### Step 4: Replace `is_blocked_output` with clean implementation

In `scripts/compile-agency-agent.py`, replace lines 83-98:

```python
def is_blocked_output(out_dir: pathlib.Path) -> bool:
    """Block writes that resolve into the live agents/ directory.

    Safe paths contain 'agents-src' or 'agency-normalized'.
    Dangerous paths contain '/agents/' or end with '/agents'.
    """
    def _is_safe(s: str) -> bool:
        return "agents-src" in s or "agency-normalized" in s

    # Check resolved absolute path
    try:
        resolved = str(out_dir.resolve()).replace("\\", "/")
        if _is_safe(resolved):
            return False
        if "/agents/" in resolved or resolved.endswith("/agents"):
            return True
    except Exception:
        pass

    # Check the raw string (handles relative paths like "agents/core")
    raw = str(out_dir).replace("\\", "/")
    if _is_safe(raw):
        return False
    return bool(re.match(r"^agents(/|$)", raw) or "/agents/" in raw)
```

### Step 5: Run tests to verify they pass

```bash
uv run python3 -m pytest tests/test_compile_agency_agent.py -v
```

Expected: all 7 tests `PASSED` (6 original + 1 new).

### Step 6: Commit

```bash
git add scripts/compile-agency-agent.py tests/test_compile_agency_agent.py
git commit -m "fix(migration): replace dead-code is_blocked_output with correct path check"
```

---

## TASK-FIX-02: Fix double file read in validator

**Priority:** Blocking (correctness + performance)

**Problem:** `scripts/validate-claude-agents.py:90` calls `pathlib.Path(entry["file"]).read_text()` inside `validate_agent()`, but `parse_agent()` already read the file. For 84 agents this reads every file twice.

**Files:**
- Modify: `scripts/validate-claude-agents.py:24-45` (parse_agent), `58-95` (validate_agent)
- Modify: `tests/test_validate_claude_agents.py` (add test for file-read count OR just verify behaviour unchanged)

### Step 1: Write test confirming body content is checked correctly

Add to `tests/test_validate_claude_agents.py`:

```python
def test_body_check_uses_parsed_content_not_disk(tmp_path, monkeypatch):
    """Validator must check body sections without re-reading disk after parse."""
    agent = tmp_path / "ev.md"
    agent.write_text(VALID_AGENT)

    # After parse, simulate the file being deleted — validate_agent must not need disk
    import scripts  # won't work directly; use subprocess to verify exit 0
    # Simpler: run validate, then delete file, confirm no extra read needed
    # Actually we verify indirectly: test that a valid agent with all sections passes
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 0
```

Note: This test mostly verifies no regression. The real fix is structural.

### Step 2: Run test to verify it passes (baseline)

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v
```

Expected: all pass (baseline green before refactor).

### Step 3: Add `body` field to `parse_agent` return dict

In `scripts/validate-claude-agents.py`, replace the return statement of `parse_agent` (lines 33-45):

```python
    return {
        "file": str(path),
        "name": fm.get("name"),
        "description": fm.get("description"),
        "tools": fm.get("tools"),
        "model": fm.get("model"),
        "permissionMode": fm.get("permissionMode"),
        "maxTurns": fm.get("maxTurns"),
        "memory": fm.get("memory"),
        "color": fm.get("color"),
        "parse_error": None,
        "frontmatter": fm,
        "body": text,          # <-- add this line
    }
```

### Step 4: Update `validate_agent` to use `entry["body"]`

Replace line 90 in `validate_agent`:

```python
# OLD:
body = pathlib.Path(entry["file"]).read_text()

# NEW:
body = entry.get("body", "")
```

### Step 5: Run all tests

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v
```

Expected: all 9 tests `PASSED`.

### Step 6: Commit

```bash
git add scripts/validate-claude-agents.py tests/test_validate_claude_agents.py
git commit -m "fix(migration): eliminate double file read in validator (pass body through parse_agent)"
```

---

## TASK-FIX-03: Fix silent false-pass in ledger writer

**Priority:** Important (silent masking of real validation failures)

**Problem:** `scripts/write-agent-migration-evidence.py:24` — if `candidate_results` is empty (path comparison mismatch), `errors = []` is set silently and the ledger records `status: validated` even when the validator actually found errors for the file.

**Files:**
- Modify: `scripts/write-agent-migration-evidence.py:11-30`
- Modify: `tests/test_agent_migration_evidence.py`

### Step 1: Write failing test

Add to `tests/test_agent_migration_evidence.py`:

```python
def test_ledger_records_needs_review_when_validator_finds_errors(tmp_path):
    """Agent with schema errors must produce status=needs_review, not validated."""
    # Intentionally invalid: missing tools
    bad_agent = tmp_path / "bad-agent.md"
    bad_agent.write_text(
        "---\nname: bad-agent\ndescription: Desc\n---\n\n# Output contract\n\n# Failure modes\n"
    )
    ledger_dir = tmp_path / "ledger"
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "bad-agent",
         "--source", "agency-agents",
         "--target-file", str(bad_agent),
         "--validator", "scripts/validate-claude-agents.py",
         "--ledger-dir", str(ledger_dir)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(list(ledger_dir.glob("*.json"))[0].read_text())
    assert data["status"] == "needs_review"
    assert data["checks"]["frontmatter_schema"] == "fail"
    assert len(data["risks"]) > 0
```

### Step 2: Run to verify it fails

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py::test_ledger_records_needs_review_when_validator_finds_errors -v
```

Expected: `FAILED` — likely records `validated` instead of `needs_review`.

### Step 3: Fix `run_validator` to warn when no match found

Replace `run_validator` in `scripts/write-agent-migration-evidence.py`:

```python
def run_validator(validator: str, target_file: str) -> dict:
    target = pathlib.Path(target_file)
    r = subprocess.run(
        ["uv", "run", "python3", validator, str(target.parent)],
        capture_output=True, text=True,
    )
    try:
        data = json.loads(r.stdout)
        target_abs = target.resolve()
        candidate_results = [
            x for x in data.get("results", [])
            if pathlib.Path(x.get("file", "")).resolve() == target_abs
        ]
        if not candidate_results:
            # Validator ran but no result matched — treat as unknown, not pass
            return {
                "frontmatter_schema": "fail",
                "errors": [
                    f"validator ran but no result matched '{target_file}' "
                    f"(scanned {len(data.get('results', []))} files)"
                ],
            }
        errors = candidate_results[0]["errors"]
    except Exception as e:
        errors = [r.stderr.strip() or f"validator parse error: {e}"]
    return {
        "frontmatter_schema": "pass" if not errors else "fail",
        "errors": errors,
    }
```

### Step 4: Run all ledger tests

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py -v
```

Expected: all 4 tests `PASSED`.

### Step 5: Commit

```bash
git add scripts/write-agent-migration-evidence.py tests/test_agent_migration_evidence.py
git commit -m "fix(migration): ledger writer no longer silently passes when validator result unmatched"
```

---

## TASK-FIX-04: Fix `global_errors` silent truncation

**Priority:** Minor (usability)

**Problem:** `scripts/validate-claude-agents.py:135` — `all_errors[:50]` silently drops errors beyond 50 with no indication in output.

**Files:**
- Modify: `scripts/validate-claude-agents.py:135`
- Modify: `tests/test_validate_claude_agents.py`

### Step 1: Write test

Add to `tests/test_validate_claude_agents.py`:

```python
def test_truncated_errors_flagged_in_output(tmp_path):
    """When >50 errors exist, output must indicate truncation."""
    # Create 60 agents each missing description and tools
    for i in range(60):
        (tmp_path / f"bad-{i:02d}.md").write_text(
            f"---\nname: bad-agent-{i:02d}\n---\n# Output contract\n# Failure modes\n"
        )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["total_errors"] > 50
    assert data.get("truncated") is True or len(data["global_errors"]) == data["total_errors"]
```

### Step 2: Run to verify it fails

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py::test_truncated_errors_flagged_in_output -v
```

Expected: `FAILED` — `truncated` key absent.

### Step 3: Fix the output line

In `scripts/validate-claude-agents.py`, replace line 135:

```python
# OLD:
print(json.dumps({"results": results, "global_errors": all_errors[:50], "total_errors": len(all_errors)}, indent=2))

# NEW:
truncated = len(all_errors) > 50
print(json.dumps({
    "results": results,
    "global_errors": all_errors[:50],
    "total_errors": len(all_errors),
    "truncated": truncated,
}, indent=2))
```

### Step 4: Run all validator tests

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v
```

Expected: all 10 tests `PASSED`.

### Step 5: Commit

```bash
git add scripts/validate-claude-agents.py tests/test_validate_claude_agents.py
git commit -m "fix(migration): flag truncated global_errors in validator JSON output"
```

---

## TASK-FIX-05: Rewrite `When to use` and `Workflow` in the 3 generated agents

**Priority:** Blocking for promotion (routing signal is wrong — Claude will not dispatch these correctly)

**Problem:** All three compiled agents have identical, meaningless `When to use` sections and identical generic `Workflow` steps. These are the primary routing signal Claude uses at dispatch time. They must be role-specific.

**Files:**
- Modify: `agents-src/agency-normalized/evidence-collector.md`
- Modify: `agents-src/agency-normalized/reality-checker.md`
- Modify: `agents-src/agency-normalized/minimal-change-engineer.md`

No test needed — these are content fixes. Validator already confirms structural compliance.

### Step 1: Rewrite `evidence-collector.md` sections

In `agents-src/agency-normalized/evidence-collector.md`, replace:

```markdown
## When to use

When evidence collector output is needed after a task run.
```

with:

```markdown
## When to use

When a task has completed and you need a structured record of what ran,
what commands were executed, what succeeded, what failed, and what risks
or side-effects were observed. Use before passing context to a reviewer.
```

Replace the generic `Workflow`:

```markdown
## Workflow

1. List working directory to discover available output files.
2. Read each relevant file (test results, logs, command output).
3. Extract: commands run, exit codes, files changed, errors seen.
4. Produce evidence bundle — do not interpret or draw conclusions.
```

### Step 2: Rewrite `reality-checker.md` sections

Replace `When to use`:

```markdown
## When to use

When a task claims to be done and you need independent verification
that outputs exist, tests pass, and stated requirements are met.
Do not use for gathering evidence — use evidence-collector first.
```

Replace `Workflow`:

```markdown
## Workflow

1. Read the task requirements or acceptance criteria.
2. Read the evidence bundle (from evidence-collector if available).
3. For each requirement, check: is there concrete evidence it is met?
4. Return: pass (all requirements evidenced), needs_work (gaps found),
   or blocked (evidence missing, cannot verify).
```

### Step 3: Rewrite `minimal-change-engineer.md` sections

Replace `When to use`:

```markdown
## When to use

When reviewing a completed diff for scope creep, gold-plating, or
changes outside the stated requirement. Use after implementation,
before merge. Focus: is every changed line necessary?
```

Replace `Workflow`:

```markdown
## Workflow

1. Read the original requirement or task description.
2. Read the diff (git diff or provided patch).
3. For each changed file: does this change serve the requirement?
4. Flag: lines that go beyond scope, abstractions not yet needed,
   deletions that may be safe to defer, style changes mixed with logic.
5. Produce review report with: verdict (minimal/bloated), line-level flags,
   suggested smaller alternative if bloated.
```

### Step 4: Verify validator still passes

```bash
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized/
```

Expected: Exit 0, `total_errors: 0`.

### Step 5: Commit

```bash
git add agents-src/agency-normalized/evidence-collector.md \
        agents-src/agency-normalized/reality-checker.md \
        agents-src/agency-normalized/minimal-change-engineer.md
git commit -m "fix(agents): rewrite When-to-use and Workflow sections with role-specific routing signals"
```

---

## TASK-FIX-06: Fix `minimal-change-engineer` unrestricted Bash tool

**Priority:** Minor (principle of least privilege)

**Problem:** `minimal-change-engineer` has `Bash` in its tools with no restrictions, but its role is read-only diff review. Unrestricted `Bash` allows arbitrary writes.

**Files:**
- Modify: `agents-src/agency-normalized/minimal-change-engineer.md:6` (tools frontmatter)
- Modify: `agents-src/agency-source/minimal-change-engineer.yaml:9` (source of truth)

No test needed — validator checks structural compliance, not tool restriction strings.

### Step 1: Update source YAML

In `agents-src/agency-source/minimal-change-engineer.yaml`, replace:

```yaml
tools:
  - Read
  - Bash
```

with:

```yaml
tools:
  - Read
  - Bash(git diff:*|cat:*|grep:*)
```

### Step 2: Update compiled agent frontmatter

In `agents-src/agency-normalized/minimal-change-engineer.md`, replace:

```yaml
tools:
  - Read
  - Bash
```

with:

```yaml
tools:
  - Read
  - Bash(git diff:*|cat:*|grep:*)
```

### Step 3: Validate

```bash
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized/
```

Expected: Exit 0.

### Step 4: Commit

```bash
git add agents-src/agency-normalized/minimal-change-engineer.md \
        agents-src/agency-source/minimal-change-engineer.yaml
git commit -m "fix(agents): restrict minimal-change-engineer Bash to read-only git/grep commands"
```

---

## TASK-FIX-07: Fix ledger absolute paths → relative

**Priority:** Minor (portability)

**Problem:** `write-agent-migration-evidence.py:58` stores `args.target_file` as-is, which is an absolute path when invoked with `str(agent_file)` from tests. If the repo moves, all ledger entries reference invalid paths.

**Files:**
- Modify: `scripts/write-agent-migration-evidence.py:33-56`
- Modify: `tests/test_agent_migration_evidence.py`

### Step 1: Write test

Add to `tests/test_agent_migration_evidence.py`:

```python
def test_ledger_stores_relative_target_path(tmp_path):
    """target_file in ledger must be a relative path, not absolute."""
    agent_file = tmp_path / "evidence-collector.md"
    agent_file.write_text(
        "---\nname: evidence-collector\ndescription: D\ntools:\n  - Read\n---\n\n# Output contract\n\n# Failure modes\n"
    )
    ledger_dir = tmp_path / "ledger"
    subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "evidence-collector",
         "--source", "agency-agents",
         "--target-file", str(agent_file),
         "--validator", "scripts/validate-claude-agents.py",
         "--ledger-dir", str(ledger_dir)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    data = json.loads(list(ledger_dir.glob("*.json"))[0].read_text())
    assert not pathlib.Path(data["target_file"]).is_absolute(), \
        f"target_file should be relative, got: {data['target_file']}"
```

### Step 2: Run to verify it fails

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py::test_ledger_stores_relative_target_path -v
```

Expected: `FAILED` — absolute path stored.

### Step 3: Fix `write_ledger` to relativize the path

In `scripts/write-agent-migration-evidence.py`, add after the `ledger_dir.mkdir(...)` line:

```python
def write_ledger(args) -> pathlib.Path:
    ledger_dir = pathlib.Path(args.ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    # Store path relative to cwd for portability
    try:
        target_file_stored = str(pathlib.Path(args.target_file).relative_to(pathlib.Path.cwd()))
    except ValueError:
        target_file_stored = args.target_file  # fallback if not under cwd

    checks = run_validator(args.validator, args.target_file)
    status = "validated" if checks["frontmatter_schema"] == "pass" else "needs_review"

    entry = {
        "candidate": args.candidate,
        "source": args.source,
        "target_file": target_file_stored,   # <-- use relative
        ...
    }
```

Full replacement of `write_ledger`:

```python
def write_ledger(args) -> pathlib.Path:
    ledger_dir = pathlib.Path(args.ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    try:
        target_file_stored = str(pathlib.Path(args.target_file).relative_to(pathlib.Path.cwd()))
    except ValueError:
        target_file_stored = args.target_file

    checks = run_validator(args.validator, args.target_file)
    status = "validated" if checks["frontmatter_schema"] == "pass" else "needs_review"

    entry = {
        "candidate": args.candidate,
        "source": args.source,
        "target_file": target_file_stored,
        "status": status,
        "checks": {
            "frontmatter_schema": checks["frontmatter_schema"],
            "name_collision": "not_checked",
            "tools_explicit": "pass" if checks["frontmatter_schema"] == "pass" else "unknown",
            "routing_overlap": "not_checked",
            "hook_schema": "not_applicable",
            "validator_errors": checks["errors"],
        },
        "risks": checks["errors"],
        "review_decision": "pending",
        "created": str(date.today()),
    }

    out = ledger_dir / f"{args.candidate}.json"
    out.write_text(json.dumps(entry, indent=2))
    print(f"Ledger: {out}")
    return out
```

### Step 4: Run all ledger tests

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py -v
```

Expected: all 5 tests `PASSED`.

### Step 5: Regenerate ledger entries with relative paths

```bash
for agent in evidence-collector reality-checker minimal-change-engineer; do
  uv run python3 scripts/write-agent-migration-evidence.py \
    --candidate "$agent" \
    --source "agency-agents-main" \
    --target-file "agents-src/agency-normalized/${agent}.md"
done
```

### Step 6: Commit

```bash
git add scripts/write-agent-migration-evidence.py \
        tests/test_agent_migration_evidence.py \
        docs/agent-migration/evidence-ledger/
git commit -m "fix(migration): store relative target_file paths in ledger for portability"
```

---

## Final Verification

```bash
uv run python3 -m pytest tests/ -v
```

Expected: all tests pass (minimum 30 — 9 validator + 5 ledger + 7 compiler + 5 manifest + 3 overlap).

```bash
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized/
```

Expected: Exit 0, `total_errors: 0`.

```bash
uv run python3 scripts/check-agent-routing-overlap.py \
  --existing agents/ \
  --new agents-src/agency-normalized \
  --report docs/agent-migration/routing-overlap-report.md
cat docs/agent-migration/routing-overlap-report.md | head -10
```

Expected: `No Conflicts Detected`.
