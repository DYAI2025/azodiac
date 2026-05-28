"""Tests for docs/agent-migration/curated-agents.yaml"""
import pathlib
import yaml

MANIFEST = pathlib.Path(__file__).parent.parent / "docs/agent-migration/curated-agents.yaml"


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
