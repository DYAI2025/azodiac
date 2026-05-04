---
name: omni-architecture-brief-engine
description: creates editable single-file html architecture visualizations, ai-agent-ready markdown dev briefs, and optional live api health overlays from software, product, api, workflow, data, or agent architectures. use when users ask to visualize architecture, edit endpoints, live-check endpoints, color nodes red yellow green by runtime health, redirect flows, modify components, export architecture markdown, generate dev briefs, produce arc42 lite snapshots, or turn architecture changes into precise coding-agent instructions.
---

# Omni Architecture Brief Engine

## Overview

Transform architecture context into an editable browser-based architecture model. Always treat the visualization as a working interface for change capture, not only as documentation.

The skill has four required outputs when applicable:
1. a normalized architecture model with nodes, edges, flows, endpoints, schemas, notes, constraints, and change log;
2. a single-file HTML editor that visualizes the architecture and supports targeted editing;
3. a delta markdown development brief describing exactly what the user edited;
4. a full architecture markdown snapshot in a stable arc42-lite plus OpenAPI-style structure, including `## 10. Architecture Flows` for service-to-service calls;
5. when requested, a live API health overlay that marks nodes, endpoint rows, and edges as `red`, `yellow`, `green`, or `unknown`.

## When to apply

Apply this skill when the user asks for any of the following:
- visualize, map, document, inspect, or edit an architecture;
- create an editable architecture diagram, architecture editor, or architecture operating tool;
- change endpoints, reroute API paths, redirect flows, rewrite component boundaries, or adjust dependencies;
- export edits as markdown, tickets, implementation instructions, or dev briefs;
- generate full architecture snapshots for AI development agents;
- run or prepare live API health checks for documented endpoints;
- mark architecture nodes or endpoints red, yellow, or green based on runtime calls;
- onboard a coding agent with precise architecture context.

Do not apply it to static diagrams that explicitly require no editing, no export, and no implementation brief.

## Core contract

1. **Model first.** Extract or infer a canonical `architecture.json` model before generating UI or markdown.
2. **Visualize second.** Render nodes and edges as an editable architecture canvas.
3. **Track every edit.** No edit may be silent. Every change must enter `changes[]` with before/after data.
4. **Export two views.** Separate the delta brief from the full snapshot.
5. **Make briefs executable.** Write markdown so a coding agent can change exactly the affected component, route, edge, schema, or flow.
6. **Stay architecture-neutral.** Do not assume a specific domain such as Bazodiac, astrology, SaaS, microservices, or web apps unless the user's context provides it.
7. **Keep live calls server-mediated.** Do not put secrets or unrestricted arbitrary URL probing into the HTML. Use the health-check server contract in `references/live-api-health-check.md` and the deployment guide in `docs/DEPLOY_HEALTHCHECK_VPS.md`.

## Required model shape

Use the schema in `references/architecture-model.md`. Minimum viable model:

```json
{
  "project": { "name": "Project", "domain": "software", "repo": "", "timestamp": "ISO-8601" },
  "nodes": [],
  "edges": [],
  "changes": []
}
```

Represent each relevant architecture component as a node. Represent user journeys, API calls, data flows, event links, ownership links, deployment links, or risk-control links as edges.

## Workflow

### 1. Ingest architecture context

Accept any combination of:
- prose architecture description;
- codebase or repo summary;
- OpenAPI/spec fragments;
- user-flow descriptions;
- product modules;
- endpoint lists;
- existing diagrams;
- uploaded HTML editor exports;
- existing `architecture.json` snapshots.

Extract components, endpoints, data objects, dependencies, flows, risks, constraints, and unresolved assumptions. If the context is incomplete, continue with explicit assumptions rather than blocking unless the target architecture cannot be identified at all.

### 2. Normalize to nodes and edges

For each node, capture:
- stable `id` in kebab-case;
- `label`, `type`, `icon`, `x`, `y`;
- `detail.title`, `detail.subtitle`, `detail.tags`;
- `detail.flow[]` for runtime/user/process steps;
- `detail.apis[]` for endpoints;
- `detail.schemas` for request/response/data models;
- `detail.notes`, `detail.constraints`, `detail.risks`.

For each edge, capture:
- `from`, `to`, `style`, `label`, `relation`, and optional protocol/data description;
- for service-to-service calls, also capture `method`, `path`, `description`, and `critical` when inferable.

Use deterministic IDs and stable ordering. Sort nodes by user-flow order when known, otherwise by dependency layer and then by label.

### 3. Generate editable HTML

When the user asks for an editor or visualization, generate a single-file HTML artifact using either:
- `scripts/generate_architecture_editor.py`, or
- a direct HTML answer/artifact if the environment requires inline output.

The HTML must include:
- node/edge canvas;
- zoom/reset and pan interaction;
- detail panel per node;
- edit mode;
- editing for node title/subtitle/tags/notes;
- add/edit/delete for flow steps;
- add/edit/delete for API routes;
- optional `CHECK LIVE API` button that calls a server-mediated probe endpoint and applies red/yellow/green status classes;
- add/edit/delete or reroute for edges;
- add/delete nodes;
- local save/load/import/export JSON;
- export delta dev brief as markdown;
- export full architecture snapshot as markdown.

Use `references/editor-behavior.md` for exact behavior. For live API status overlays, use `references/live-api-health-check.md` and the deployment guide in `docs/DEPLOY_HEALTHCHECK_VPS.md`, along with the OpenAPI Action schema in `references/custom-gpt-action-openapi.yaml`.

### 4. Add live API health checking when requested

When the user asks to call live APIs, validate endpoints, or color nodes by health:
1. Generate or preserve endpoint probe metadata in `detail.apis[]`: `method`, `path` or `url`, optional `headers`, `query`, `body`, `expectedStatus`, and `expectedResponse.requiredJsonPaths`.
2. Keep secrets out of the HTML model. Put tokens, base URLs, and host allowlists on the server.
3. Use the JavaScript function `callLiveApiHealthCheck(serverUrl, options)` embedded by `scripts/generate_architecture_editor.py`.
4. Expect the health-check server to expose `POST /probe-architecture` using the contract in `references/custom-gpt-action-openapi.yaml`.
5. Apply statuses exactly: `red` = functionally broken; `yellow` = reachable but partial request/response/contract problem; `green` = full pass; `unknown` = not checked.
6. If no server URL exists, return the server properties needed instead of pretending the HTML can securely probe arbitrary APIs alone.

### 5. Convert edits to a dev brief

When edits exist, produce a markdown brief using the contract in `references/export-contracts.md`.

The brief must answer:
- what changed;
- where it changed;
- why the change matters;
- which components, endpoints, schemas, flows, and tests are affected;
- exact implementation instructions;
- exact acceptance criteria;
- migration or backwards-compatibility notes;
- verification commands or test targets when inferable.

Do not write vague instructions such as "update the API". Specify the route, method, component, before/after state, and expected behavior.

### 6. Export full architecture snapshot

When the user asks for full export, architecture documentation, current state, onboarding context, or `EXPORT-ALL-STATES`, produce the fixed arc42-lite plus OpenAPI-style markdown snapshot:

1. Header block
2. Table of Contents
3. Introduction & Goals
4. Constraints
5. Context & Scope
6. Solution Strategy
7. Building Block View
8. Runtime View - User Flows
9. API Reference
10. Module Catalogue
11. Glossary
12. Architecture Flows

The rendered markdown heading for the final flow section must be exactly `## 10. Architecture Flows`, even though the internal outline above lists it after the glossary. Preserve this heading for compatibility with downstream healthcheck and flow-testing tools.

The flow section must:
- include only real service-to-service calls;
- exclude internal Ollama calls, static file accesses, filesystem reads, UI-only edges, and documentation edges;
- list `Source`, `Target`, `Method`, `Path`, `Description`, and `Critical` for every flow;
- sort flows by source, then target, then path;
- mark critical runtime flows with `Critical: true`.

### 7. Prepare coding-agent handoff

For Codex, Claude Code, Gemini CLI, Cursor, Aider, or another coding agent:
- include a short task title;
- include affected files if known;
- include search terms if affected files are unknown;
- include exact before/after endpoint paths;
- include impacted schemas and contracts;
- include test expectations;
- state explicit non-goals.

## Output format

Choose the smallest complete output that satisfies the request.

### For architecture editor generation

Return:
1. `architecture.json` if requested or useful;
2. generated `.html` file or complete HTML block;
3. brief usage instructions;
4. live API health-check server requirements if endpoint probing was requested;
5. uncertainty notes if assumptions were needed.

### For changed architecture handoff

Return:
1. `# Development Brief` markdown;
2. `## Change Summary`;
3. `## Surgical Edit Instructions`;
4. `## Affected Architecture Objects`;
5. `## Acceptance Criteria`;
6. `## Verification Plan`;
7. `## Non-Goals`.

### For full snapshot

Return only the fixed snapshot structure from `references/export-contracts.md`, unless the user explicitly asks for commentary.

## Quality rules

- Make all IDs stable and deterministic.
- Make markdown diffable: stable section order, stable table columns, sorted endpoints.
- Preserve before/after values for every edit.
- Avoid domain-specific labels unless provided by the user.
- Do not invent repo paths, server URLs, credentials, or test commands. If unknown, write `Unknown - search required` and include likely search terms or required deployment properties.
- Separate facts from assumptions in exports.
- Prefer Mermaid diagrams in markdown snapshots and SVG/HTML canvas in the editor.

## Examples

### Example 1 - endpoint reroute

User: "Move the daily summary endpoint from `/api/daily/summary` to `/api/summary/daily` and make the dashboard use it."

Expected behavior:
- locate the dashboard node and daily-summary route;
- record a modify change with before/after path;
- update edge or dependency labels if needed;
- export a dev brief naming the route, component, consumers, tests, and compatibility decision.

### Example 2 - full architecture export

User: "Export the current architecture for a new coding agent."

Expected behavior:
- emit the full arc42-lite snapshot;
- include Mermaid context and building block diagrams;
- include all modules, all edges, all flows, all endpoints;
- keep section order fixed.

### Example 3 - visual architecture editor

User: "Visualize this agent architecture and make it editable."

Expected behavior:
- normalize the agent architecture to nodes and edges;
- generate a single-file HTML editor;
- ensure edit mode can modify nodes, flows, APIs, and edges;
- include exports for markdown dev brief and full architecture snapshot.
