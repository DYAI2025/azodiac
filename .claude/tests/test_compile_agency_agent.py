"""Tests for scripts/compile-agency-agent.py"""
import subprocess
import pathlib
import re

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
    r = subprocess.run(args, capture_output=True, text=True,
                       cwd="/Users/benjaminpoersch/.claude")
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
        assert section.lower() in body.lower(), f"Missing section: {section}"


def test_compiler_refuses_to_write_to_agents_dir(tmp_path):
    src = tmp_path / "ev.yaml"
    src.write_text(AGENCY_SOURCE)
    r = subprocess.run(
        ["uv", "run", "python3", SCRIPT,
         "--source", str(src), "--candidate", "evidence-collector",
         "--out", "agents/core"],
        capture_output=True, text=True,
        cwd="/Users/benjaminpoersch/.claude"
    )
    assert r.returncode != 0
    assert "blocked" in r.stderr.lower() or "forbidden" in r.stderr.lower()


def test_no_secrets_in_output(tmp_path):
    source_with_secret = AGENCY_SOURCE + "\ntoken: ghp_supersecret123\n"
    _, outfile = _compile(tmp_path, source_with_secret)
    body = outfile.read_text()
    assert "ghp_supersecret" not in body
    assert "supersecret" not in body
