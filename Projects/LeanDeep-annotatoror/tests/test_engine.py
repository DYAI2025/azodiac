import pytest
from api.schemas import MarkerRegistry, ATOSignal, SEMMarker, VADWeights
from api.engine import DetectionEngine

@pytest.fixture
def registry():
    return MarkerRegistry(
        atos=[
            ATOSignal(id="ATO_POS", pattern="good|great", description="pos", vad=VADWeights(valence=0.8)),
            ATOSignal(id="ATO_NEG", pattern="bad|terrible", description="neg", vad=VADWeights(valence=-0.8))
        ],
        sems=[
            SEMMarker(id="SEM_MIXED", description="mixed", logic="AND", constituent_atos=["ATO_POS", "ATO_NEG"])
        ]
    )

@pytest.fixture
def engine(registry):
    return DetectionEngine(registry)

def test_ato_detection(engine):
    result = engine.analyze("Life is good and great")
    assert len(result.atos) == 2
    assert result.atos[0].id == "ATO_POS"
    assert result.vad_score.valence == 0.8

def test_vad_aggregation(engine):
    result = engine.analyze("This is good but also bad")
    # (0.8 + -0.8) / 2 = 0.0
    assert result.vad_score.valence == 0.0

def test_sem_and_logic(engine):
    result = engine.analyze("It is good and bad")
    assert any(s.id == "SEM_MIXED" for s in result.sems)

def test_sem_logic_fail(engine):
    result = engine.analyze("It is just good")
    assert len(result.sems) == 0

def test_empty_text(engine):
    result = engine.analyze("")
    assert len(result.atos) == 0
    assert result.vad_score.valence == 0.0
