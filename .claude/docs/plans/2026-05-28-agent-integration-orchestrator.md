# Agent Integration Orchestrator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a validated, reversible migration pipeline that compiles Agency-agent definitions into Claude-Code-conformant subagent Markdowns, with schema validation, evidence ledger, and review gate before any agent lands in `agents/`.

**Architecture:** Agency source → curated manifest → compiler → schema validator → routing-overlap check → evidence ledger → review gate → accepted agents in `agents/`. Nothing reaches `agents/` without explicit `accepted` status. Intermediate output lives in `agents-src/agency-normalized/`.

**Tech Stack:** Python 3.12 (uv), pytest, PyYAML, plain Markdown/JSON, bash hooks

---

## Path Reference (this repo = `~/.claude`)

| Plan path | Actual path |
|-----------|-------------|
| `.claude/agents/` | `agents/` |
| `config/claude/commands/agileteam.md` | `commands/agileteam.md` |
| Python runner | `uv run python3` |
| Test runner | `uv run python3 -m pytest` |

---

## Safety Rules (non-negotiable)

- No writes to `agents/` until candidate status = `accepted`
- No changes to `~/.claude` global config (we ARE `~/.claude` — no writes outside this repo)
- No `bypassPermissions`, no `--no-verify`, no `push --force`, no commits to `main` directly
- Ledger entries are never deleted; mark `reverted` instead

---

## TASK-001: Repo Discovery (read-only inventory)

**Goal:** Inventory every agent Markdown in the repo. No writes.

**Files:**
- Create: `scripts/validate-claude-agents.py`
- Create: `tests/test_validate_claude_agents.py`

### Step 1: Write the failing test for `--inventory-only`

```python
# tests/test_validate_claude_agents.py
import subprocess, json, pathlib

SCRIPT = "scripts/validate-claude-agents.py"

def test_inventory_only_exits_zero(tmp_path):
    """--inventory-only on a dir with one valid agent exits 0 and emits JSON."""
    agent = tmp_path / "good-agent.md"
    agent.write_text(
        "---\nname: good-agent\ndescription: Does good things\ntools:\n  - Read\n---\n\n# Good Agent\n"
    )
    result = subprocess.run(
        ["uv", "run", "python3", SCRIPT, "--inventory-only", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert len(data["agents"]) == 1
    assert data["agents"][0]["name"] == "good-agent"

def test_inventory_only_reports_missing_frontmatter(tmp_path):
    bad = tmp_path / "no-fm.md"
    bad.write_text("# Just a markdown file\n")
    result = subprocess.run(
        ["uv", "run", "python3", SCRIPT, "--inventory-only", str(tmp_path)],
        capture_output=True, text=True
    )
    assert result.returncode == 0  # inventory-only never exits 1
    data = json.loads(result.stdout)
    assert data["agents"][0]["parse_error"] is not None
```

### Step 2: Run test to verify it fails

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py::test_inventory_only_exits_zero -v
```

Expected: `FAILED` — `ModuleNotFoundError` or `FileNotFoundError`

### Step 3: Write minimal `validate-claude-agents.py` (inventory mode only)

```python
#!/usr/bin/env python3
"""Claude Code agent schema validator and inventory tool."""
import argparse, json, pathlib, re, sys
import yaml  # uv add pyyaml if needed

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

def parse_agent(path: pathlib.Path) -> dict:
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {"file": str(path), "name": path.stem, "parse_error": "no frontmatter"}
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"file": str(path), "name": path.stem, "parse_error": str(e)}
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
    }

def collect_agents(root: pathlib.Path) -> list[dict]:
    agents = []
    for p in sorted(root.rglob("*.md")):
        # skip non-agent files (no frontmatter with name:)
        entry = parse_agent(p)
        if entry.get("parse_error") is None and entry.get("name") is None:
            continue  # not an agent file
        agents.append(entry)
    return agents

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Directory to scan")
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()

    root = pathlib.Path(args.path)
    agents = collect_agents(root)

    if args.inventory_only:
        print(json.dumps({"agents": agents}, indent=2))
        sys.exit(0)

    # Validation mode — TASK-002 adds this
    print("Validation mode not yet implemented", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 4: Run test to verify it passes

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v
```

Expected: `PASSED`

### Step 5: Run inventory on real repo

```bash
uv run python3 scripts/validate-claude-agents.py --inventory-only agents/ | uv run python3 -m json.tool | head -60
```

Expected: JSON with all agent entries, no crash.

### Step 6: Commit

```bash
git add scripts/validate-claude-agents.py tests/test_validate_claude_agents.py
git commit -m "feat(migration): add agent inventory scanner (read-only)"
```

---

## TASK-002: Schema Validator

**Goal:** Extend the script with full validation mode. Exits 1 on schema errors.

**Files:**
- Modify: `scripts/validate-claude-agents.py`
- Modify: `tests/test_validate_claude_agents.py`

### Step 1: Write failing tests for validation rules

```python
# append to tests/test_validate_claude_agents.py

VALID_AGENT = """\
---
name: evidence-collector
description: Collects and structures evidence from task runs for downstream review.
tools:
  - Read
  - Bash
model: sonnet
permissionMode: default
maxTurns: 20
memory: project
color: blue
---

# Evidence Collector

## Mission
Collect evidence.

## When to use
After a task run.

## When not to use
During active coding.

## Tools and permissions
Read-only evidence files.

## Workflow
1. Read outputs.

## Evidence required
Task output files.

## Output contract
JSON evidence bundle.

## Failure modes
Missing output files.

## Escalation
Notify orchestrator.
"""

def test_valid_agent_passes(tmp_path):
    (tmp_path / "evidence-collector.md").write_text(VALID_AGENT)
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True
    )
    assert r.returncode == 0, r.stdout + r.stderr

def test_missing_description_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ntools:\n  - Read\n---\n# body\n"
    )
    r = subprocess.run(["uv", "run", "python3", SCRIPT, str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "description" in r.stdout

def test_missing_tools_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ndescription: Desc\n---\n# body\n"
    )
    r = subprocess.run(["uv", "run", "python3", SCRIPT, str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "tools" in r.stdout

def test_name_with_spaces_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad agent\ndescription: Desc\ntools:\n  - Read\n---\n# body\n"
    )
    r = subprocess.run(["uv", "run", "python3", SCRIPT, str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1

def test_bypass_permissions_blocked(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ndescription: Desc\ntools:\n  - Read\npermissionMode: bypassPermissions\n---\n# body\n"
    )
    r = subprocess.run(["uv", "run", "python3", SCRIPT, str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "bypassPermissions" in r.stdout

def test_body_sections_required(tmp_path):
    """Body must contain Output contract and Failure modes sections."""
    (tmp_path / "bad.md").write_text(
        "---\nname: missing-sections\ndescription: Desc\ntools:\n  - Read\n---\n# body only\n"
    )
    r = subprocess.run(["uv", "run", "python3", SCRIPT, str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 1
    assert "Output contract" in r.stdout or "Failure modes" in r.stdout
```

### Step 2: Run to verify they fail

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v -k "not inventory"
```

Expected: all new tests `FAILED`

### Step 3: Add validation logic to the script

Replace `main()` validation section in `scripts/validate-claude-agents.py`:

```python
ALLOWED_MODELS = {"sonnet", "opus", "haiku", "inherit", None}
ALLOWED_PERMISSIONS = {"default", "acceptEdits", "readOnly", None}
ALLOWED_MEMORY = {"none", "project", "user", "local", None}
ALLOWED_COLORS = {"red","orange","yellow","green","blue","purple","pink","cyan","white","black", None}
KEBAB_RE = re.compile(r"^[a-z][a-z0-9\-]+$")
REQUIRED_BODY_SECTIONS = ["Output contract", "Failure modes"]

def validate_agent(entry: dict) -> list[str]:
    errors = []
    if entry.get("parse_error"):
        return [f"parse_error: {entry['parse_error']}"]
    
    name = entry.get("name")
    if not name:
        errors.append("name: missing")
    elif not KEBAB_RE.match(name):
        errors.append(f"name: '{name}' must be kebab-case")

    if not entry.get("description"):
        errors.append("description: missing or empty")

    if not entry.get("tools"):
        errors.append("tools: missing — must be explicit list (not inherited)")

    pm = entry.get("permissionMode")
    if pm == "bypassPermissions":
        errors.append("permissionMode: bypassPermissions is blocked without explicit approval")
    elif pm not in ALLOWED_PERMISSIONS:
        errors.append(f"permissionMode: '{pm}' not in allowed values {ALLOWED_PERMISSIONS}")

    if entry.get("model") not in ALLOWED_MODELS:
        errors.append(f"model: '{entry.get('model')}' not allowed")

    if entry.get("memory") not in ALLOWED_MEMORY:
        errors.append(f"memory: '{entry.get('memory')}' not in {ALLOWED_MEMORY}")

    if entry.get("color") not in ALLOWED_COLORS:
        errors.append(f"color: '{entry.get('color')}' not in allowed values")

    # body section check
    body = pathlib.Path(entry["file"]).read_text()
    for section in REQUIRED_BODY_SECTIONS:
        if section.lower() not in body.lower():
            errors.append(f"body: missing section '{section}'")

    return errors

def check_duplicates(agents: list[dict]) -> list[str]:
    seen, errors = {}, []
    for a in agents:
        n = a.get("name")
        if n and n in seen:
            errors.append(f"name: '{n}' duplicated in {a['file']} and {seen[n]}")
        elif n:
            seen[n] = a["file"]
    return errors
```

Replace the validation block in `main()`:

```python
    # Validation mode
    all_errors = check_duplicates(agents)
    results = []
    for agent in agents:
        errs = validate_agent(agent)
        results.append({"file": agent["file"], "name": agent.get("name"), "errors": errs})
        all_errors.extend([f"{agent['file']}: {e}" for e in errs])
    
    print(json.dumps({"results": results, "total_errors": len(all_errors)}, indent=2))
    sys.exit(1 if all_errors else 0)
```

### Step 4: Run all validator tests

```bash
uv run python3 -m pytest tests/test_validate_claude_agents.py -v
```

Expected: all `PASSED`

### Step 5: Validate real agents directory (expect some issues — that's OK)

```bash
uv run python3 scripts/validate-claude-agents.py agents/ 2>&1 | head -40
```

Expected: JSON report, non-zero exit likely (existing agents predate these rules).

### Step 6: Commit

```bash
git add scripts/validate-claude-agents.py tests/test_validate_claude_agents.py
git commit -m "feat(migration): add schema validator with TDD tests"
```

---

## TASK-003: Migration Manifest

**Goal:** Create `docs/agent-migration/curated-agents.yaml` with pilot batch of 3 candidates.

**Files:**
- Create: `docs/agent-migration/curated-agents.yaml`
- Create: `tests/test_migration_manifest.py`

### Step 1: Write failing test

```python
# tests/test_migration_manifest.py
import yaml, pathlib

MANIFEST = pathlib.Path("docs/agent-migration/curated-agents.yaml")

def test_manifest_is_valid_yaml():
    data = yaml.safe_load(MANIFEST.read_text())
    assert data is not None

def test_manifest_has_required_fields():
    data = yaml.safe_load(MANIFEST.read_text())
    assert "batch_id" in data
    assert "mode" in data
    assert data["mode"] == "review-only"
    assert "candidates" in data

def test_manifest_has_exactly_three_pilot_candidates():
    data = yaml.safe_load(MANIFEST.read_text())
    assert len(data["candidates"]) == 3

def test_no_candidate_is_auto_accepted():
    data = yaml.safe_load(MANIFEST.read_text())
    for c in data["candidates"]:
        assert c["status"] == "pending", f"{c['target_name']} must start as pending"

def test_all_candidates_have_required_fields():
    data = yaml.safe_load(MANIFEST.read_text())
    required = {"source_name", "target_name", "target_type", "tools_policy", "status", "priority"}
    for c in data["candidates"]:
        missing = required - set(c.keys())
        assert not missing, f"{c.get('target_name')} missing fields: {missing}"
```

### Step 2: Run to verify fail

```bash
uv run python3 -m pytest tests/test_migration_manifest.py -v
```

Expected: `FileNotFoundError`

### Step 3: Create the manifest

```yaml
# docs/agent-migration/curated-agents.yaml
batch_id: pilot-001
mode: review-only
target_scope: project
source_repo: agency-agents-main
created: "2026-05-28"

candidates:
  - source_name: Evidence Collector
    target_name: evidence-collector
    target_type: subagent
    priority: 1
    tools_policy: read-evidence
    status: pending
    notes: "Collects structured evidence from task outputs. Read-only role."

  - source_name: Reality Checker
    target_name: reality-checker
    target_type: subagent
    priority: 2
    tools_policy: read-evidence
    status: pending
    notes: "Checks claims against available evidence. Read-only role."

  - source_name: Minimal Change Engineer
    target_name: minimal-change-engineer
    target_type: subagent
    priority: 3
    tools_policy: diff-review
    status: pending
    notes: "Reviews diffs for scope bloat. Suggests smaller alternatives."
```

### Step 4: Run tests to verify they pass

```bash
uv run python3 -m pytest tests/test_migration_manifest.py -v
```

Expected: all `PASSED`

### Step 5: Commit

```bash
git add docs/agent-migration/curated-agents.yaml tests/test_migration_manifest.py
git commit -m "feat(migration): add pilot migration manifest (3 candidates, all pending)"
```

---

**CHECKPOINT — Stop here for Phase 1 review.**

Run full test suite: `uv run python3 -m pytest tests/ -v`

Open MISSINGs at this point:
- Exact Agency-agent source file paths (needed for TASK-004 compiler)
- Source content for evidence-collector, reality-checker, minimal-change-engineer from agency-agents-main

---

## TASK-004: Agent Compiler

**Goal:** Compile an Agency-agent definition into a normalized Claude-Code Markdown. Writes only to `agents-src/agency-normalized/`, never to `agents/`.

**Files:**
- Create: `scripts/compile-agency-agent.py`
- Create: `agents-src/agency-normalized/` (directory)
- Create: `tests/test_compile_agency_agent.py`

### Step 1: Write failing tests

```python
# tests/test_compile_agency_agent.py
import subprocess, pathlib, re
import yaml

SCRIPT = "scripts/compile-agency-agent.py"
NORMALIZE_DIR = pathlib.Path("agents-src/agency-normalized")

AGENCY_SOURCE = """\
name: Evidence Collector
description: |
  Collects evidence from task outputs and builds structured records.
persona: You are a meticulous evidence gatherer...
tools_guidance: You only need to read files. No writes.
"""

def _compile(tmp_path, source_text, candidate="evidence-collector", extra_args=None):
    src = tmp_path / "evidence-collector.yaml"
    src.write_text(source_text)
    out = tmp_path / "out"
    out.mkdir()
    args = ["uv", "run", "python3", SCRIPT,
            "--source", str(src),
            "--candidate", candidate,
            "--out", str(out)]
    if extra_args:
        args.extend(extra_args)
    r = subprocess.run(args, capture_output=True, text=True)
    return r, out / f"{candidate}.md"

def test_compiler_produces_output_file(tmp_path):
    r, outfile = _compile(tmp_path, AGENCY_SOURCE)
    assert r.returncode == 0, r.stderr
    assert outfile.exists()

def test_output_has_valid_frontmatter(tmp_path):
    _, outfile = _compile(tmp_path, AGENCY_SOURCE)
    text = outfile.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, "No frontmatter found"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == "evidence-collector"
    assert fm.get("tools") is not None

def test_name_is_kebab_case(tmp_path):
    _, outfile = _compile(tmp_path, AGENCY_SOURCE)
    fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---", outfile.read_text(), re.DOTALL).group(1))
    assert re.match(r"^[a-z][a-z0-9\-]+$", fm["name"])

def test_required_body_sections_present(tmp_path):
    _, outfile = _compile(tmp_path, AGENCY_SOURCE)
    body = outfile.read_text()
    for section in ["Output contract", "Failure modes", "When to use", "When not to use"]:
        assert section.lower() in body.lower(), f"Missing: {section}"

def test_compiler_refuses_to_write_to_agents_dir(tmp_path):
    src = tmp_path / "ev.yaml"
    src.write_text(AGENCY_SOURCE)
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--source", str(src), "--candidate", "evidence-collector",
         "--out", "agents/core"],
        capture_output=True, text=True
    )
    assert r.returncode != 0
    assert "blocked" in r.stderr.lower() or "forbidden" in r.stderr.lower()

def test_no_secrets_in_output(tmp_path):
    source_with_secret = AGENCY_SOURCE + "\ntoken: ghp_supersecret123\n"
    _, outfile = _compile(tmp_path, source_with_secret)
    body = outfile.read_text()
    assert "ghp_supersecret" not in body
    assert "supersecret" not in body
```

### Step 2: Run to verify fail

```bash
uv run python3 -m pytest tests/test_compile_agency_agent.py -v
```

Expected: `FAILED` — script missing

### Step 3: Create minimal compiler

```python
#!/usr/bin/env python3
"""Compile an Agency-agent YAML into a normalized Claude-Code subagent Markdown."""
import argparse, pathlib, re, sys
import yaml

BLOCKED_OUTPUT_PATHS = {"agents/", "agents-src/agency-normalized/../agents/"}
SECRET_PATTERNS = re.compile(r"(ghp_|sk-|token\s*[:=]\s*\S+|password\s*[:=]\s*\S+)", re.IGNORECASE)

TEMPLATE = """\
---
name: {name}
description: {description}
tools:
{tools_block}
model: sonnet
permissionMode: default
maxTurns: 20
memory: project
color: blue
---

# {title}

## Mission

{mission}

## When to use

{when_to_use}

## When not to use

Not applicable until validated and accepted.

## Tools and permissions

{tools_narrative}

## Workflow

1. Read available evidence or diff.
2. Analyze against stated criteria.
3. Produce structured output.

## Evidence required

Prior task outputs must exist in working directory.

## Output contract

Structured Markdown report with: summary, findings list, confidence, recommendation.

## Failure modes

- Missing input files → report `blocked: missing_evidence`
- Ambiguous scope → report `needs_clarification`

## Escalation

Return `blocked` status to orchestrator with reason.
"""

def kebab(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def scrub_secrets(text: str) -> str:
    return SECRET_PATTERNS.sub("[REDACTED]", text)

def compile_agent(source_path: pathlib.Path, candidate: str, out_dir: pathlib.Path) -> pathlib.Path:
    # Block writes to live agents/ dir
    out_str = str(out_dir).rstrip("/") + "/"
    if "agents/" in out_str and "agency-normalized" not in out_str and "agents-src" not in out_str:
        print(f"BLOCKED: output path '{out_dir}' resolves to live agents directory", file=sys.stderr)
        sys.exit(1)

    raw = yaml.safe_load(source_path.read_text()) or {}
    name = kebab(candidate)
    title = raw.get("name", candidate)
    description = scrub_secrets(str(raw.get("description", f"Migrated from agency-agents: {title}")).strip())
    mission = scrub_secrets(str(raw.get("persona", raw.get("description", "TBD"))).strip())
    tools_narrative = str(raw.get("tools_guidance", "Explicit tools listed in frontmatter only.")).strip()
    tools_list = raw.get("tools", ["Read"])

    tools_block = "\n".join(f"  - {t}" for t in tools_list)

    content = TEMPLATE.format(
        name=name,
        title=title,
        description=description,
        tools_block=tools_block,
        mission=mission,
        when_to_use=f"When {title.lower()} is needed after a task run.",
        tools_narrative=tools_narrative,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}.md"
    out_file.write_text(content)
    return out_file

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    outfile = compile_agent(pathlib.Path(args.source), args.candidate, pathlib.Path(args.out))
    print(f"Generated: {outfile}")

if __name__ == "__main__":
    main()
```

### Step 4: Run tests

```bash
uv run python3 -m pytest tests/test_compile_agency_agent.py -v
```

Expected: all `PASSED`

### Step 5: Validate compiled output

```bash
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized/
```

Expected: Exit 0 (or report specific gaps to fix in compiler template).

### Step 6: Commit

```bash
git add scripts/compile-agency-agent.py agents-src/ tests/test_compile_agency_agent.py
git commit -m "feat(migration): add agent compiler (writes only to agents-src/agency-normalized)"
```

---

## TASK-005: Evidence Ledger Writer

**Goal:** Each compiled candidate produces a JSON ledger entry in `docs/agent-migration/evidence-ledger/`.

**Files:**
- Create: `scripts/write-agent-migration-evidence.py`
- Create: `docs/agent-migration/evidence-ledger/` (directory)
- Create: `tests/test_agent_migration_evidence.py`

### Step 1: Write failing tests

```python
# tests/test_agent_migration_evidence.py
import subprocess, json, pathlib, tempfile

SCRIPT = "scripts/write-agent-migration-evidence.py"

def test_writes_valid_json_ledger(tmp_path):
    agent_file = tmp_path / "evidence-collector.md"
    agent_file.write_text(
        "---\nname: evidence-collector\ndescription: Desc\ntools:\n  - Read\n---\n\n# Output contract\n\n# Failure modes\n"
    )
    ledger_dir = tmp_path / "ledger"
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "evidence-collector",
         "--source", "agency-agents",
         "--target-file", str(agent_file),
         "--validator", "scripts/validate-claude-agents.py",
         "--ledger-dir", str(ledger_dir)],
        capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr
    entries = list(ledger_dir.glob("*.json"))
    assert len(entries) == 1
    data = json.loads(entries[0].read_text())
    assert data["candidate"] == "evidence-collector"
    assert data["status"] in {"generated", "validated", "needs_review"}

def test_ledger_contains_required_fields(tmp_path):
    agent_file = tmp_path / "reality-checker.md"
    agent_file.write_text("---\nname: reality-checker\ndescription: D\ntools:\n  - Read\n---\n# Output contract\n# Failure modes\n")
    ledger_dir = tmp_path / "ledger"
    subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "reality-checker", "--source", "agency-agents",
         "--target-file", str(agent_file), "--validator", "scripts/validate-claude-agents.py",
         "--ledger-dir", str(ledger_dir)],
        capture_output=True
    )
    data = json.loads(list(ledger_dir.glob("*.json"))[0].read_text())
    required = {"candidate", "source", "target_file", "status", "checks", "risks", "review_decision", "created"}
    assert required.issubset(set(data.keys()))

def test_ledger_json_is_valid(tmp_path):
    agent_file = tmp_path / "minimal-change-engineer.md"
    agent_file.write_text("---\nname: minimal-change-engineer\ndescription: D\ntools:\n  - Read\n---\n# Output contract\n# Failure modes\n")
    ledger_dir = tmp_path / "ledger"
    subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "minimal-change-engineer", "--source", "agency-agents",
         "--target-file", str(agent_file), "--validator", "scripts/validate-claude-agents.py",
         "--ledger-dir", str(ledger_dir)],
        capture_output=True
    )
    for f in ledger_dir.glob("*.json"):
        json.loads(f.read_text())  # must not raise
```

### Step 2: Run to verify fail

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py -v
```

Expected: `FAILED`

### Step 3: Implement ledger writer

```python
#!/usr/bin/env python3
"""Write a per-candidate evidence ledger entry for agent migration."""
import argparse, json, pathlib, subprocess, sys
from datetime import date

def run_validator(validator: str, target_file: str) -> dict:
    r = subprocess.run(
        ["uv", "run", "python3", validator, str(pathlib.Path(target_file).parent)],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        candidate_results = [x for x in data.get("results", []) if target_file.endswith(x.get("file","").lstrip("./"))]
        errors = candidate_results[0]["errors"] if candidate_results else []
    except Exception:
        errors = [r.stderr.strip() or "validator parse error"]
    return {
        "frontmatter_schema": "pass" if not errors else "fail",
        "errors": errors,
    }

def write_ledger(args) -> pathlib.Path:
    ledger_dir = pathlib.Path(args.ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    checks = run_validator(args.validator, args.target_file)
    status = "validated" if checks["frontmatter_schema"] == "pass" else "needs_review"

    entry = {
        "candidate": args.candidate,
        "source": args.source,
        "target_file": args.target_file,
        "status": status,
        "checks": {
            "frontmatter_schema": checks["frontmatter_schema"],
            "name_collision": "not_checked",  # TASK-007 adds this
            "tools_explicit": "pass" if checks["frontmatter_schema"] == "pass" else "unknown",
            "routing_overlap": "not_checked",  # TASK-007 adds this
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--target-file", required=True)
    p.add_argument("--validator", default="scripts/validate-claude-agents.py")
    p.add_argument("--ledger-dir", default="docs/agent-migration/evidence-ledger")
    args = p.parse_args()
    write_ledger(args)

if __name__ == "__main__":
    main()
```

### Step 4: Run tests

```bash
uv run python3 -m pytest tests/test_agent_migration_evidence.py -v
```

Expected: all `PASSED`

### Step 5: Commit

```bash
git add scripts/write-agent-migration-evidence.py docs/agent-migration/ tests/test_agent_migration_evidence.py
git commit -m "feat(migration): add evidence ledger writer with validator integration"
```

---

## TASK-006: Generate Three Pilot Agents

**Goal:** Compile evidence-collector, reality-checker, minimal-change-engineer into `agents-src/agency-normalized/`. Write ledger. No writes to `agents/`.

**Files:**
- Create: `agents-src/agency-normalized/evidence-collector.md`
- Create: `agents-src/agency-normalized/reality-checker.md`
- Create: `agents-src/agency-normalized/minimal-change-engineer.md`
- Create: `docs/agent-migration/evidence-ledger/evidence-collector.json`
- Create: `docs/agent-migration/evidence-ledger/reality-checker.json`
- Create: `docs/agent-migration/evidence-ledger/minimal-change-engineer.json`

### Step 1: Create source YAML stubs for the three candidates

```bash
mkdir -p agents-src/agency-source
```

```yaml
# agents-src/agency-source/evidence-collector.yaml
name: Evidence Collector
description: Collects and structures evidence from task runs — sources, commands, outputs, and risks — for downstream review agents.
persona: |
  You are a meticulous evidence gatherer. You read task outputs, test results, and log files.
  You never draw conclusions. You only report what you observe.
tools_guidance: |
  Read-only. You need Read and Bash(cat|grep|ls) to gather evidence.
tools:
  - Read
  - Bash
```

```yaml
# agents-src/agency-source/reality-checker.yaml
name: Reality Checker
description: Verifies task completion claims against available evidence. Returns pass, needs_work, or blocked with specific reasons.
persona: |
  You are a skeptical verifier. You check that claims of completion are backed by evidence.
  You never accept "it should work" — only "it demonstrably works".
tools_guidance: |
  Read-only access to evidence ledger and source files.
tools:
  - Read
```

```yaml
# agents-src/agency-source/minimal-change-engineer.yaml
name: Minimal Change Engineer
description: Reviews diffs for scope bloat and unnecessary changes. Proposes the smallest change that achieves the goal.
persona: |
  You believe every line added is a liability. You find the minimal path.
tools_guidance: |
  Read diffs and source. No writes. Produce diff review report.
tools:
  - Read
  - Bash
```

### Step 2: Compile all three

```bash
for CANDIDATE in evidence-collector reality-checker minimal-change-engineer; do
  uv run python3 scripts/compile-agency-agent.py \
    --source "agents-src/agency-source/${CANDIDATE}.yaml" \
    --candidate "$CANDIDATE" \
    --out agents-src/agency-normalized
done
```

Expected: three `.md` files created in `agents-src/agency-normalized/`

### Step 3: Validate all three

```bash
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized
echo "Exit: $?"
```

Expected: Exit 0 (fix compiler template if errors appear)

### Step 4: Write evidence ledger for all three

```bash
for CANDIDATE in evidence-collector reality-checker minimal-change-engineer; do
  uv run python3 scripts/write-agent-migration-evidence.py \
    --candidate "$CANDIDATE" \
    --source agency-agents-main \
    --target-file "agents-src/agency-normalized/${CANDIDATE}.md" \
    --ledger-dir docs/agent-migration/evidence-ledger
done
```

### Step 5: Validate ledger JSON

```bash
for f in docs/agent-migration/evidence-ledger/*.json; do
  uv run python3 -m json.tool "$f" > /dev/null && echo "OK: $f"
done
```

Expected: all `OK`

### Step 6: Verify nothing written to `agents/`

```bash
git diff --name-only | grep "^agents/" && echo "FAIL: wrote to live agents!" || echo "OK: agents/ untouched"
```

Expected: `OK: agents/ untouched`

### Step 7: Commit

```bash
git add agents-src/ docs/agent-migration/evidence-ledger/
git commit -m "feat(migration): generate 3 pilot agents (evidence-collector, reality-checker, minimal-change-engineer)"
```

---

## TASK-007: Routing Overlap Report

**Goal:** Heuristic keyword check — do new agents' descriptions overlap existing ones?

**Files:**
- Create: `scripts/check-agent-routing-overlap.py`
- Create: `docs/agent-migration/routing-overlap-report.md`
- Create: `tests/test_routing_overlap.py`

### Step 1: Write failing test

```python
# tests/test_routing_overlap.py
import subprocess, pathlib

SCRIPT = "scripts/check-agent-routing-overlap.py"

def test_overlap_report_is_created(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "coder.md").write_text("---\nname: coder\ndescription: Writes and fixes code.\ntools:\n  - Edit\n---\n")
    new_agents = tmp_path / "new"
    new_agents.mkdir()
    (new_agents / "evidence-collector.md").write_text(
        "---\nname: evidence-collector\ndescription: Collects evidence from task runs.\ntools:\n  - Read\n---\n"
    )
    report = tmp_path / "report.md"
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--existing", str(existing), "--new", str(new_agents), "--report", str(report)],
        capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr
    assert report.exists()

def test_overlap_report_flags_keyword_match(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "collector.md").write_text(
        "---\nname: evidence-collector\ndescription: Collects evidence after tasks.\ntools:\n  - Read\n---\n"
    )
    new_agents = tmp_path / "new"
    new_agents.mkdir()
    (new_agents / "evidence-collector2.md").write_text(
        "---\nname: evidence-collector-v2\ndescription: Collects evidence from run outputs.\ntools:\n  - Read\n---\n"
    )
    report = tmp_path / "report.md"
    subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--existing", str(existing), "--new", str(new_agents), "--report", str(report)],
        capture_output=True
    )
    text = report.read_text()
    assert "overlap" in text.lower() or "conflict" in text.lower()
```

### Step 2: Run to verify fail

```bash
uv run python3 -m pytest tests/test_routing_overlap.py -v
```

Expected: `FAILED`

### Step 3: Implement overlap checker

```python
#!/usr/bin/env python3
"""Heuristic routing overlap detector for Claude Code subagents."""
import argparse, pathlib, re
import yaml

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

def extract_descriptions(directory: pathlib.Path) -> dict[str, str]:
    result = {}
    for p in directory.rglob("*.md"):
        m = FM_RE.match(p.read_text())
        if not m:
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        if fm.get("name") and fm.get("description"):
            result[fm["name"]] = fm["description"]
    return result

def keyword_overlap_score(desc_a: str, desc_b: str) -> float:
    a_words = set(re.findall(r"\b\w{4,}\b", desc_a.lower()))
    b_words = set(re.findall(r"\b\w{4,}\b", desc_b.lower()))
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / min(len(a_words), len(b_words))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--existing", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--report", default="docs/agent-migration/routing-overlap-report.md")
    p.add_argument("--threshold", type=float, default=0.3)
    args = p.parse_args()

    existing = extract_descriptions(pathlib.Path(args.existing))
    new_agents = extract_descriptions(pathlib.Path(args.new))

    conflicts, clean = [], []

    for new_name, new_desc in new_agents.items():
        for ex_name, ex_desc in existing.items():
            score = keyword_overlap_score(new_desc, ex_desc)
            if score >= args.threshold:
                conflicts.append((new_name, ex_name, score, new_desc, ex_desc))
            else:
                clean.append((new_name, ex_name, score))

    lines = ["# Routing Overlap Report\n", f"Threshold: {args.threshold}\n"]
    if conflicts:
        lines.append(f"\n## Potential Conflicts ({len(conflicts)})\n")
        lines.append("> These are heuristic matches — human review required.\n")
        for new_name, ex_name, score, new_desc, ex_desc in conflicts:
            lines.append(f"\n### `{new_name}` ↔ `{ex_name}` (score: {score:.2f})\n")
            lines.append(f"- **New:** {new_desc.strip()}\n")
            lines.append(f"- **Existing:** {ex_desc.strip()}\n")
            lines.append("- **Action required:** Sharpen description to differentiate delegation signal.\n")
    else:
        lines.append("\n## No conflicts detected\n")
        lines.append("> Note: this is a keyword heuristic, not semantic analysis.\n")

    report = pathlib.Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("".join(lines))
    print(f"Report: {report}")

if __name__ == "__main__":
    main()
```

### Step 4: Run tests

```bash
uv run python3 -m pytest tests/test_routing_overlap.py -v
```

Expected: `PASSED`

### Step 5: Run on real agents

```bash
uv run python3 scripts/check-agent-routing-overlap.py \
  --existing agents/ \
  --new agents-src/agency-normalized \
  --report docs/agent-migration/routing-overlap-report.md
cat docs/agent-migration/routing-overlap-report.md
```

### Step 6: Commit

```bash
git add scripts/check-agent-routing-overlap.py docs/agent-migration/routing-overlap-report.md tests/test_routing_overlap.py
git commit -m "feat(migration): add routing overlap heuristic checker"
```

---

## TASK-008: Review Gate Document

**Goal:** Define the review checklist and status transitions. Document is human-readable; no code needed.

**Files:**
- Create: `docs/agent-migration/review-gate.md`

### Step 1: Write the document

```markdown
# Agent Migration Review Gate

## Status Model

pending → generated → validated → reviewed → accepted | rejected | needs-rework

No candidate transitions to `accepted` without an explicit reviewer decision.

## Review Checklist

For each candidate:

- [ ] Description is a concrete delegation signal (not generic)
- [ ] Tools are minimal for the role
- [ ] No routing overlap with existing agents (or overlap is justified with comment)
- [ ] Output contract is testable (what exactly does it produce?)
- [ ] Failure modes cover realistic scenarios
- [ ] Evidence Ledger entry exists and `frontmatter_schema: pass`
- [ ] No secrets, local paths, or hardcoded tokens in body

## Updating a Candidate's Status

Edit `docs/agent-migration/curated-agents.yaml`:

```yaml
status: accepted       # or: rejected | needs-rework
review_decision: "description is specific, tools minimal, no overlap"
reviewed_by: <name>
reviewed_at: "2026-05-28"
```

## Promoting an Accepted Candidate

Only after status = `accepted` in manifest:

```bash
cp agents-src/agency-normalized/<name>.md agents/<category>/<name>.md
uv run python3 scripts/validate-claude-agents.py agents/
git diff -- agents/
```

Never use `git add -A` — add the specific file only.
```

### Step 2: Commit

```bash
git add docs/agent-migration/review-gate.md
git commit -m "docs(migration): add review gate checklist and status model"
```

---

## TASK-009: Promote Accepted Candidates to `agents/`

**This task runs only after at least one candidate reaches `status: accepted` in the manifest.**

**Files:**
- Conditionally create: `agents/<category>/<name>.md`

### Step 1: Verify acceptance before touching `agents/`

```bash
uv run python3 - <<'PY'
import yaml
data = yaml.safe_load(open("docs/agent-migration/curated-agents.yaml"))
accepted = [c for c in data["candidates"] if c["status"] == "accepted"]
print(f"Accepted: {[c['target_name'] for c in accepted]}")
if not accepted:
    raise SystemExit("No accepted candidates — stop here.")
PY
```

### Step 2: For each accepted candidate, copy and validate

```bash
# Replace NAME and CATEGORY with actual values
cp agents-src/agency-normalized/NAME.md agents/CATEGORY/NAME.md
uv run python3 scripts/validate-claude-agents.py agents/CATEGORY/NAME.md
git diff -- agents/
```

### Step 3: Commit only the promoted file

```bash
git add agents/CATEGORY/NAME.md docs/agent-migration/evidence-ledger/NAME.json
git commit -m "feat(agents): promote NAME agent (accepted via review gate)"
```

---

## TASK-010: Extend `/agileteam` Command (optional)

**Only after at least two pilot agents are accepted.**

**Files:**
- Modify: `commands/agileteam.md`

### Step 1: Verify candidates accepted before touching command

```bash
grep -c "status: accepted" docs/agent-migration/curated-agents.yaml
```

Expected: ≥ 2

### Step 2: Add optional references (do not replace existing pipeline)

Add to `commands/agileteam.md` after the existing Tester step:

```markdown
## Optional Evidence & Quality Gates (after agents accepted)

After each task cycle, if `evidence-collector` is available:
- Invoke evidence-collector to summarize sources, commands, outputs, risks

Before marking task done, if `reality-checker` is available:
- Invoke reality-checker to verify completion claims against evidence
- Accept only `pass`; loop on `needs_work`

For Coder tasks, if `minimal-change-engineer` is available:
- Pass diff to minimal-change-engineer before committing
- Incorporate suggestions unless explicitly overridden

**Fallback:** If any of these agents are unavailable, skip that gate and continue.
```

### Step 3: Verify existing flow untouched

```bash
grep -n "evidence-collector\|reality-checker\|minimal-change-engineer" commands/agileteam.md
```

Expected: 3 references, all in the new optional section.

### Step 4: Commit

```bash
git add commands/agileteam.md
git commit -m "feat(agileteam): add optional evidence/quality gate references"
```

---

## Full Validation Suite

Run after every task group:

```bash
uv run python3 -m pytest tests/ -v
uv run python3 scripts/validate-claude-agents.py agents-src/agency-normalized
uv run python3 -m json.tool docs/agent-migration/evidence-ledger/*.json > /dev/null && echo "Ledger OK"
```

---

## Rollback Reference

| Artifact | Rollback action |
|----------|----------------|
| `agents-src/agency-normalized/*.md` | `rm agents-src/agency-normalized/<name>.md` |
| `agents/<category>/<name>.md` | `git rm agents/<category>/<name>.md` |
| `commands/agileteam.md` changes | `git checkout commands/agileteam.md` |
| `docs/agent-migration/evidence-ledger/*.json` | Do NOT delete — set `"status": "reverted"` |
| Scripts | `git rm scripts/<name>.py` |
