# ⚠️ DEPRECATED DIRECTORY

**STOP:** This directory is not the active codebase. 
Please switch to: `/Users/benjaminpoersch/Projects/LeanDeep-annotator/`

---

# GEMINI.md — LeanDeep Annotator (Instructional Context)

This document provides essential context and instructions for AI agents working within the LeanDeep Annotator project.

## Project Overview

**LeanDeep 5.0** is a deterministic, regex-based semantic annotation layer designed for psychological and conversational pattern detection. It operates with a four-layer hierarchy, processing text to detect manipulation patterns, attachment styles, conflict dynamics, and emotional states—all without an LLM dependency.

### Core Architecture: The Four-Layer Hierarchy
1.  **ATO (Atomic Signals):** Low-level regex triggers.
2.  **SEM (Semantic Blends):** Combinations of atomic signals into semantic markers.
3.  **CLU (Cluster Intuitions):** Aggregations of semantic markers into psychological clusters.
4.  **MEMA (Meta-Markers):** High-level interpretive markers based on clusters and dynamics.

### Key Technologies
- **Language:** Python 3.12+
- **API Framework:** FastAPI (REST API at `localhost:8420`)
- **Agent Integration:** FastMCP (Model Context Protocol server)
- **Data Modeling:** Pydantic V2
- **Testing:** Pytest
- **Frontend:** HTML/JS with Chart.js (Analysis Playground)

## Directory Layout

- `api/`: Core FastAPI application (detection engine, persona system, dynamics, API endpoints).
- `build/`:
    - `markers_rated/`: **Source of Truth** for marker definitions (YAML).
    - `markers_normalized/`: Generated JSON registry used by the engine at runtime.
- `tools/`: Pipeline scripts for normalization, schema enrichment, and evaluation.
- `eval/`: Gold corpus datasets and evaluation metrics.
- `tests/`: Automated test suite (Pytest).
- `docs/`: Technical specifications and roadmap.

## Building and Running

### Development Environment
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the API
```bash
# Start the FastAPI server
python3 -m uvicorn api.main:app --port 8420 --reload
```
- **Playground:** [http://localhost:8420/playground](http://localhost:8420/playground)
- **API Docs:** [http://localhost:8420/docs](http://localhost:8420/docs)

### Running the MCP Server
```bash
# Run the MCP server for AI agent integration
fastmcp run mcp_server.py
```

### Running Tests
```bash
# Execute the full test suite
pytest
```

### Building the Marker Registry
```bash
# Normalize YAML markers and compile into the registry
python3 tools/normalize_schema.py
```

## Development Conventions

1.  **Marker Source of Truth:** NEVER edit `build/markers_normalized/marker_registry.json` directly. Always modify the YAML files in `build/markers_rated/1_approved/` (or relevant rating folders) and run the normalization script.
2.  **No LLM Dependency:** The core detection engine must remain deterministic and regex-based. Do not introduce LLM calls into the base annotation layer.
3.  **VAD Congruence:** Emotion scoring uses a Valence, Arousal, Dominance (VAD) model. Ensure any changes to emotion detection align with the established VAD scoring logic in `api/engine.py`.
4.  **Testing Requirement:** New features or marker updates should be accompanied by corresponding tests in the `tests/` directory to maintain the high reliability of the deterministic engine.

---
*Note: This configuration was generated based on the sibling directory `LeanDeep-annotator`, which contains the active codebase.*
