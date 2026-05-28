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
