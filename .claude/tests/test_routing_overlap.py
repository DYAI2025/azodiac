"""Tests for scripts/check-agent-routing-overlap.py"""
import subprocess
import pathlib

SCRIPT = "scripts/check-agent-routing-overlap.py"


def test_overlap_report_is_created(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "coder.md").write_text(
        "---\nname: coder\ndescription: Writes and fixes code.\ntools:\n  - Edit\n---\n"
    )
    new_agents = tmp_path / "new"
    new_agents.mkdir()
    (new_agents / "evidence-collector.md").write_text(
        "---\nname: evidence-collector\ndescription: Collects evidence from task runs.\ntools:\n  - Read\n---\n"
    )
    report = tmp_path / "report.md"
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--existing", str(existing), "--new", str(new_agents), "--report", str(report)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
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
        capture_output=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    text = report.read_text()
    assert "overlap" in text.lower() or "conflict" in text.lower()


def test_no_overlap_between_distinct_agents(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "coder.md").write_text(
        "---\nname: coder\ndescription: Writes and refactors source code files.\ntools:\n  - Edit\n---\n"
    )
    new_agents = tmp_path / "new"
    new_agents.mkdir()
    (new_agents / "reality-checker.md").write_text(
        "---\nname: reality-checker\ndescription: Verifies claims against evidence ledger.\ntools:\n  - Read\n---\n"
    )
    report = tmp_path / "report.md"
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--existing", str(existing), "--new", str(new_agents), "--report", str(report)],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode == 0
    text = report.read_text()
    assert "no conflicts" in text.lower() or "0)" in text
