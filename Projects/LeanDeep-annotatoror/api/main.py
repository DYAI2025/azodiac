from fastapi import FastAPI
import json
from pathlib import Path
from .schemas import MarkerRegistry

app = FastAPI(title="LeanDeep Annotator 5.0")

REGISTRY_PATH = Path("build/markers_normalized/marker_registry.json")

@app.on_event("startup")
async def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r') as f:
            data = json.load(f)
            app.state.registry = MarkerRegistry(**data)
            print(f"✅ Registry loaded with {len(app.state.registry.atos)} ATOs")
    else:
        print("⚠️ No registry found. Run normalization tool first.")
        app.state.registry = MarkerRegistry()

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "5.0",
        "markers_loaded": len(app.state.registry.atos)
    }
