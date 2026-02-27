from fastapi import FastAPI, Body
import json
from pathlib import Path
from .schemas import MarkerRegistry, AnalysisResult
from .engine import DetectionEngine

app = FastAPI(title="LeanDeep Annotator 5.0")

REGISTRY_PATH = Path("build/markers_normalized/marker_registry.json")

@app.on_event("startup")
async def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            data = json.load(f)
            registry = MarkerRegistry(**data)
            app.state.engine = DetectionEngine(registry)
            print(f"✅ Detection Engine initialized with {len(registry.atos)} ATOs")
    else:
        print("⚠️ No registry found. Run normalization tool first.")
        app.state.engine = DetectionEngine(MarkerRegistry())

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "5.0",
        "markers_loaded": len(app.state.engine.registry.atos)
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze(text: str = Body(..., embed=True)):
    """
    Perform hierarchical semantic analysis on the input text.
    """
    return app.state.engine.analyze(text)
