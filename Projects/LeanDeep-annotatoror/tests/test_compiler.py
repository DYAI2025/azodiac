import pytest
import json
import yaml
from pathlib import Path
from api.schemas import MarkerRegistry, ATOSignal

def test_registry_validation():
    data = {
        "atos": [
            {
                "id": "ATO_TEST",
                "pattern": "test",
                "description": "test description",
                "vad": {"valence": 0.5, "arousal": 0.5, "dominance": 0.5}
            }
        ]
    }
    registry = MarkerRegistry(**data)
    assert len(registry.atos) == 1
    assert registry.atos[0].id == "ATO_TEST"

def test_registry_default_vad():
    data = {
        "atos": [
            {
                "id": "ATO_TEST",
                "pattern": "test",
                "description": "test description"
            }
        ]
    }
    registry = MarkerRegistry(**data)
    assert registry.atos[0].vad.valence == 0.0

def test_registry_invalid_data():
    data = {
        "atos": [
            {
                "id": "ATO_TEST",
                # missing pattern
                "description": "test description"
            }
        ]
    }
    with pytest.raises(Exception):
        MarkerRegistry(**data)

def test_compiler_output_exists():
    path = Path("build/markers_normalized/marker_registry.json")
    assert path.exists()
    with open(path, 'r') as f:
        data = json.load(f)
        assert "atos" in data
        assert len(data["atos"]) > 0
