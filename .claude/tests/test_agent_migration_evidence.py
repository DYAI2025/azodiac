"""Tests for scripts/write-agent-migration-evidence.py"""
import json
import subprocess
import pathlib

SCRIPT = "scripts/write-agent-migration-evidence.py"

VALID_AGENT_BODY = (
    "---\nname: {name}\ndescription: D\ntools:\n  - Read\n---\n\n# Output contract\n\n# Failure modes\n"
)


def _write_ledger(tmp_path, name, extra_args=None):
    agent_file = tmp_path / f"{name}.md"
    agent_file.write_text(VALID_AGENT_BODY.format(name=name))
    ledger_dir = tmp_path / "ledger"
    args = [
        "uv", "run", "python3", SCRIPT,
        "--candidate", name,
        "--source", "agency-agents",
        "--target-file", str(agent_file),
        "--validator", "scripts/validate-claude-agents.py",
        "--ledger-dir", str(ledger_dir),
    ]
    if extra_args:
        args.extend(extra_args)
    r = subprocess.run(args, capture_output=True, text=True,
                       cwd="/Users/benjaminpoersch/.claude")
    return r, ledger_dir


def test_writes_valid_json_ledger(tmp_path):
    r, ledger_dir = _write_ledger(tmp_path, "evidence-collector")
    assert r.returncode == 0, r.stderr
    entries = list(ledger_dir.glob("*.json"))
    assert len(entries) == 1
    data = json.loads(entries[0].read_text())
    assert data["candidate"] == "evidence-collector"
    assert data["status"] in {"generated", "validated", "needs_review"}


def test_ledger_contains_required_fields(tmp_path):
    _, ledger_dir = _write_ledger(tmp_path, "reality-checker")
    data = json.loads(list(ledger_dir.glob("*.json"))[0].read_text())
    required = {"candidate", "source", "target_file", "status", "checks", "risks", "review_decision", "created"}
    assert required.issubset(set(data.keys()))


def test_ledger_json_is_valid(tmp_path):
    _, ledger_dir = _write_ledger(tmp_path, "minimal-change-engineer")
    for f in ledger_dir.glob("*.json"):
        json.loads(f.read_text())  # must not raise


def test_ledger_records_needs_review_when_validator_finds_errors(tmp_path):
    """Agent with schema errors must produce status=needs_review, not validated."""
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
    assert data["status"] == "needs_review", f"Expected needs_review, got {data['status']}"
    assert data["checks"]["frontmatter_schema"] == "fail"
    assert len(data["risks"]) > 0


def test_ledger_fails_when_validator_result_unmatched(tmp_path):
    """Silent false-pass: validator returns results with no entry for the target path → must record fail.

    The bug (pre-fix): candidate_results is empty → errors=[] → status='validated'
    even though the target file was never actually checked.

    We reproduce this by providing a custom validator that always returns results
    for a DIFFERENT file path (never for target_file), so candidate_results is empty.
    """
    ghost_agent = tmp_path / "ghost-agent.md"
    ghost_agent.write_text(
        "---\nname: ghost-agent\ndescription: Desc\n---\n\n# Output contract\n\n# Failure modes\n"
    )

    ledger_dir = tmp_path / "ledger"

    # Custom validator that returns results for a completely different file path
    # (simulates a validator that scans a different dir or uses non-resolved paths)
    custom_validator = tmp_path / "custom_validator.py"
    custom_validator.write_text(
        "import sys, json\n"
        "# Always returns a result for some OTHER file — never for the target\n"
        "print(json.dumps({'results': [{'file': '/nonexistent/other-agent.md', 'errors': []}]}))\n"
    )

    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--candidate", "ghost-agent",
         "--source", "agency-agents",
         "--target-file", str(ghost_agent),
         "--validator", str(custom_validator),
         "--ledger-dir", str(ledger_dir)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(list(ledger_dir.glob("*.json"))[0].read_text())
    # Pre-fix: status would be 'validated' (silent false-pass — empty errors from empty candidate_results)
    # Post-fix: status must be 'needs_review' with a clear diagnostic error
    assert data["status"] == "needs_review", (
        f"Expected needs_review (validator found no result for target), got {data['status']}"
    )
    assert data["checks"]["frontmatter_schema"] == "fail"
    assert any("no result matched" in str(risk) or "validator ran but" in str(risk)
               for risk in data["risks"]), f"Expected unmatched-path error in risks, got: {data['risks']}"
