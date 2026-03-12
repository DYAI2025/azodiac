---
description: Write a structured developer specification (.md) for a feature or component — requirements only, no implementation
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch
---

## Context

When planning new components (frontend, integrations, modules), write structured developer briefs — NOT implementation code.

## Your Task

Write a developer specification as a markdown file.

### Steps

1. **Understand scope** — Ask what component/feature needs a brief if not obvious from the user's message.

2. **Gather context** — Read relevant existing files:
   - `CLAUDE.md` for current project state
   - Any existing briefs or specs in `docs/`
   - API endpoints if the feature involves API integration
   - Design references if provided (zips, screenshots, URLs)

3. **Write the brief** with these sections:
   - **Product** — What this is, one paragraph
   - **Target Users** — Who uses this
   - **Goal** — What success looks like
   - **Tech Stack** — Table with recommended technologies and reasoning
   - **Design System** — Reuse existing tokens if available, or propose new ones
   - **Pages / Views** — Each page with: purpose, API endpoints, input fields, output display
   - **API Integration** — Concrete fetch examples with request/response
   - **Out of Scope** — What's explicitly excluded
   - **Acceptance Criteria** — Numbered list

4. **Save** — Write to the appropriate location (root for major specs, `docs/` for sub-features)

### Guardrails

- **Requirements only** — Never write implementation code. No components, no routes. Only the spec.
- **Reuse design tokens** — If a design system exists, reference it. Don't invent new colors.
- **Concrete API examples** — Include actual fetch calls with real endpoint URLs, not placeholders
- **If design references provided** — Analyze what fits and what needs adaptation. Be honest about gaps.
