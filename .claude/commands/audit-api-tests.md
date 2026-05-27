---
description: Audit FastAPI acceptance tests for vacuous-pass patterns — tests that "pass" without actually exercising the endpoint.
allowed-tools: Read, Bash, Grep
---

## Context

A common, hard-to-spot bug class: an API acceptance test that
"passes" without actually exercising the endpoint under test. The
test reports green; the endpoint is broken; CI is happy.

The canonical failure mode looks like this:

```python
def test_endpoint_accepts_my_value():
    r = client.post("/api/something", json={"some_field": value})
    assert r.status_code != 422
```

If `/api/something` doesn't exist (wrong prefix, wrong method,
silent route refactor), the response is 404 — and `404 != 422`
satisfies the assertion. The test passes for the wrong reason and
masks the real defect.

This skill catches that pattern by static analysis of test files
plus runtime route comparison.

Real example from a FuFirE session that motivated this skill:
`tests/test_time_standard_acceptance.py::test_chart_accepts_time_standard`
posted to `/api/chart` (the actual route is `/chart`), used field
`birth_local` (the model expects `local_datetime`), and asserted
only `status_code != 422`. Every call returned 404 and the
assertion silently passed for all three variants
(CIVIL/LMT/TLST), masking a Critical bug where the underlying
Pydantic `Literal` was never widened. Cost: shipped to production
before catch.

## Your Task

Audit one test file (or the whole `tests/` directory) for the
vacuous-pass pattern. Report findings; do not auto-fix.

### Steps

1. **Resolve scope.** Ask the user (or read from invocation arg)
   which test file(s) to audit. Default: `tests/test_*.py` filtered
   to files mentioning `TestClient` or `client.post` /
   `client.get` / etc.

2. **Static scan for the loose-assertion antipattern.** Grep for
   assertions whose only check is inequality against a single
   status code:

   ```bash
   grep -nE 'assert\s+r\.status_code\s*!=\s*[0-9]+' "$FILE"
   grep -nE 'assert\s+response\.status_code\s*!=\s*[0-9]+' "$FILE"
   ```

   Flag each hit. For each, capture:
   - The full assertion line + 3 lines of context.
   - The `client.<method>("<path>", …)` call immediately above.
   - Whether a *positive* assertion (`== 200`, `== 201`, etc.) also
     appears in the same test function.

   A test that asserts only `!= N` (no positive assertion, no
   companion `!=` against the common "route absent" codes 404 / 405
   / 503) is the high-risk shape.

3. **Runtime route comparison.** For each `client.<method>("<path>",
   …)` hit, verify the path exists in the FastAPI app's route
   table:

   ```bash
   uv run python -c "
   from <your_app_module> import app
   paths = {r.path for r in app.routes if hasattr(r, 'path')}
   import sys
   for p in sys.argv[1:]:
       print(p, 'EXISTS' if p in paths or any(p.startswith(x.rstrip('{').rstrip('/')) for x in paths) else 'MISSING')
   " "$path1" "$path2" …
   ```

   For project FuFirE the app module is `bazi_engine.app`. Adapt
   per project.

   Any `MISSING` is a high-confidence vacuous test.

4. **Pydantic field-name mismatch check (optional but high-value).**
   For each `client.post("<path>", json={…})` call:
   - Find the Pydantic request model that backs that endpoint
     (grep router files for `@router.post("<path>", ...)` and the
     argument type annotation).
   - Compare the JSON payload's keys against the model's declared
     fields. Any key in the payload that isn't a field of the model
     is silently dropped or causes a different 422; that's a
     warning sign even if the test happens to pass.

5. **Negative-companion check.** For a positive test asserting
   "value X is accepted", a companion test should exist asserting
   "value Y is rejected with 422". Without the negative test,
   silently-ignored Pydantic types (e.g. a `str` field that should
   be `Literal[...]`) wouldn't be caught. Report tests without a
   discoverable companion.

6. **Report.** Group findings as:

   ```
   API TEST AUDIT — <file>
   
   🔴 Critical (vacuous tests — route not reachable):
   - test_X (line 42): posts to /api/foo which is NOT in app.routes
   
   🟡 Important (loose assertions — could hide regressions):
   - test_Y (line 88): asserts only `!= 422`; would pass on 404/500
   - test_Z (line 120): no negative companion for a positive Literal test
   
   🟢 Minor (style):
   - test_W (line 200): payload field 'birth_local' not in BaziRequest
   ```

   No auto-fixes. The user invokes `/review-fix-cycle` (or fixes
   manually) on the findings.

### Guardrails

- **Do not modify any code.** This is a read-only audit. Findings
  feed into a separate fix step the user controls.
- **Don't flag tests that use the `!=` pattern as part of a
  multi-assertion check.** If `assert r.status_code != 422` is
  followed by `assert r.json()["pillars"]["year"] == "JiaChen"`,
  the second assertion implicitly exercises the endpoint — the
  first is fine. Only flag tests where the inequality is the
  *terminal* assertion in the test body.
- **App-module discovery must be best-effort.** Many projects use
  `app/main.py` or `src/app/__init__.py` or a factory function. If
  the runtime route check can't import the app, fall back to
  static analysis only and note the limitation explicitly.
- **Routes with path parameters (e.g. `/users/{id}/chart`) need
  prefix matching, not exact match,** for the runtime comparison.
- **Skip files that don't use `TestClient`** (e.g. unit tests for
  pure functions) — they're outside this skill's scope.

---

*Generated by /reflect-skills from session pattern: a Critical
production bug shipped behind a vacuous `!= 422` assertion that
masked an unreachable route AND a not-actually-widened Pydantic
Literal. Caught only by a later /review-fix-cycle invocation. This
skill aims to catch the same class proactively.*
