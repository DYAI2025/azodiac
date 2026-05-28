"""Tests for scripts/validate-claude-agents.py"""
import subprocess
import json
import pathlib

SCRIPT = "scripts/validate-claude-agents.py"

# --- TASK-001: inventory-only tests ---

def test_inventory_only_exits_zero(tmp_path):
    agent = tmp_path / "good-agent.md"
    agent.write_text(
        "---\nname: good-agent\ndescription: Does good things\ntools:\n  - Read\n---\n\n# Good Agent\n"
    )
    result = subprocess.run(
        ["uv", "run", "python3", SCRIPT, "--inventory-only", str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
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
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["agents"][0]["parse_error"] is not None

# --- TASK-002: validation tests ---

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
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 0, r.stdout + r.stderr

def test_missing_description_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ntools:\n  - Read\n---\n# Output contract\n## Failure modes\n"
    )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    assert "description" in r.stdout

def test_missing_tools_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ndescription: Desc\n---\n# Output contract\n## Failure modes\n"
    )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    assert "tools" in r.stdout

def test_name_with_spaces_fails(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad agent\ndescription: Desc\ntools:\n  - Read\n---\n# Output contract\n## Failure modes\n"
    )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1

def test_bypass_permissions_blocked(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: bad-agent\ndescription: Desc\ntools:\n  - Read\npermissionMode: bypassPermissions\n---\n# Output contract\n## Failure modes\n"
    )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    assert "bypassPermissions" in r.stdout

def test_body_sections_required(tmp_path):
    (tmp_path / "bad.md").write_text(
        "---\nname: missing-sections\ndescription: Desc\ntools:\n  - Read\n---\n# body only\n"
    )
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    assert "Output contract" in r.stdout or "Failure modes" in r.stdout

def test_duplicate_names_fails(tmp_path):
    for i in range(2):
        (tmp_path / f"agent-{i}.md").write_text(VALID_AGENT)
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT, str(tmp_path)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 1
    assert "duplicated" in r.stdout
