import yaml
import json
import os
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path so we can import api.schemas
sys.path.append(str(Path(__file__).parent.parent))

from api.schemas import MarkerRegistry, ATOSignal, SEMMarker, CLUCluster, MEMAMarker

SOURCE_DIR = Path("build/markers_rated/1_approved")
OUTPUT_FILE = Path("build/markers_normalized/marker_registry.json")

def normalize():
    print(f"🔍 Normalizing markers from {SOURCE_DIR}...")
    
    registry_data = {
        "atos": [],
        "sems": [],
        "clus": [],
        "memas": []
    }
    
    if not SOURCE_DIR.exists():
        print(f"❌ Source directory {SOURCE_DIR} does not exist.")
        return

    for yaml_file in SOURCE_DIR.glob("*.yaml"):
        print(f"📄 Processing {yaml_file.name}...")
        with open(yaml_file, 'r') as f:
            try:
                data = yaml.safe_load(f)
                if not isinstance(data, list):
                    print(f"⚠️ Skipping {yaml_file.name}: expected list at root.")
                    continue
                
                for item in data:
                    marker_id = item.get("id", "")
                    if marker_id.startswith("ATO_"):
                        registry_data["atos"].append(item)
                    elif marker_id.startswith("SEM_"):
                        registry_data["sems"].append(item)
                    elif marker_id.startswith("CLU_"):
                        registry_data["clus"].append(item)
                    elif marker_id.startswith("MEMA_"):
                        registry_data["memas"].append(item)
                    else:
                        print(f"❓ Unknown marker type for ID: {marker_id}")
            except yaml.YAMLError as exc:
                print(f"❌ YAML error in {yaml_file.name}: {exc}")
                continue

    # Validate with Pydantic
    try:
        registry = MarkerRegistry(**registry_data)
        print("✅ Validation successful.")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return

    # Save to JSON
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(registry.model_dump(), f, indent=2)
    
    print(f"🚀 Registry compiled to {OUTPUT_FILE}")

if __name__ == "__main__":
    normalize()
