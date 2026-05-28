# Agent Migration Review Gate

## Status Model

```
pending → generated → validated → reviewed → accepted | rejected | needs-rework
```

No candidate transitions to `accepted` without an explicit reviewer decision.

## Review Checklist

For each candidate, confirm all before setting `accepted`:

- [ ] Description is a **concrete delegation signal** — Claude can use it to decide when to route here (not generic like "helps with tasks")
- [ ] Tools are **minimal for the role** — read-only agents have no Edit/Write
- [ ] **No routing overlap** with existing agents, or overlap is justified with a comment
- [ ] **Output contract is testable** — the section says exactly what the agent produces (format, fields, conditions)
- [ ] **Failure modes** cover realistic scenarios (not just "unexpected errors")
- [ ] Evidence Ledger entry exists at `docs/agent-migration/evidence-ledger/<name>.json` with `frontmatter_schema: pass`
- [ ] **No secrets**, local paths, or hardcoded tokens in body

## Updating a Candidate's Status

Edit `docs/agent-migration/curated-agents.yaml`:

```yaml
# Example: accepting a candidate
- target_name: evidence-collector
  status: accepted
  review_decision: "description is specific delegation signal, tools read-only, no overlap detected"
  reviewed_by: <your-name>
  reviewed_at: "2026-05-28"
```

Valid status values: `pending` | `generated` | `validated` | `accepted` | `rejected` | `needs-rework`

## Promoting an Accepted Candidate

Only run this after `status: accepted` in manifest.

```bash
# 1. Verify acceptance
uv run python3 - <<'PY'
import yaml
data = yaml.safe_load(open("docs/agent-migration/curated-agents.yaml"))
accepted = [c for c in data["candidates"] if c["status"] == "accepted"]
print(f"Accepted: {[c['target_name'] for c in accepted]}")
if not accepted:
    raise SystemExit("No accepted candidates — stop here.")
PY

# 2. Copy to live agents directory (choose appropriate category subdir)
cp agents-src/agency-normalized/<name>.md agents/<category>/<name>.md

# 3. Validate the promoted file
uv run python3 scripts/validate-claude-agents.py agents/<category>/

# 4. Review diff before staging
git diff -- agents/

# 5. Commit only the promoted file — never git add -A
git add agents/<category>/<name>.md docs/agent-migration/evidence-ledger/<name>.json
git commit -m "feat(agents): promote <name> agent (accepted via review gate)"
```

## Routing Overlap Check

Before accepting, run:

```bash
uv run python3 scripts/check-agent-routing-overlap.py \
  --existing agents/ \
  --new agents-src/agency-normalized \
  --report docs/agent-migration/routing-overlap-report.md
```

Conflicts are advisory — not blockers — but require a written justification in `review_decision`.

## Current Pilot Batch Status

See `docs/agent-migration/curated-agents.yaml` for live status.
See `docs/agent-migration/routing-overlap-report.md` for latest overlap check results.
