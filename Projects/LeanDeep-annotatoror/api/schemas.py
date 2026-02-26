from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class VADWeights(BaseModel):
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0

class ATOSignal(BaseModel):
    id: str
    pattern: str
    description: str
    vad: VADWeights = Field(default_factory=VADWeights)

class SEMMarker(BaseModel):
    id: str
    description: str
    logic: Literal["AND", "OR", "SEQUENCE"] = "OR"
    constituent_atos: List[str]
    vad_multiplier: float = 1.0

class CLUCluster(BaseModel):
    id: str
    label: str
    markers: List[str]
    description: str

class MEMAMarker(BaseModel):
    id: str
    name: str
    description: str
    clusters_required: List[str]
    dynamics_logic: str

class MarkerRegistry(BaseModel):
    atos: List[ATOSignal] = Field(default_factory=list)
    sems: List[SEMMarker] = Field(default_factory=list)
    clus: List[CLUCluster] = Field(default_factory=list)
    memas: List[MEMAMarker] = Field(default_factory=list)
