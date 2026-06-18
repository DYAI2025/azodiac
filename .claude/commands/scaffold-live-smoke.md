---
description: Scaffold a flag-gated, real-boundary LIVE SMOKE for a provider/boundary that verifies the live integration with its real secret — opt-in (never in CI), with a FAIL-LOUD contract-drift guard, a secret-hygiene self-check, dry-run + inject-drift modes that prove the guard bites, and an adversarial-verify step before any not-real→real claim. Use when a code path against an external boundary (provider API, payment/POD/LLM/email service, internal route) exists but has only mock/sample evidence and you need real-boundary proof, or when the user asks to "write a live smoke / real-boundary smoke / boundary verification harness".
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

## Context

The point of a live smoke is to **verify the assembled, deployed system against the real boundary with its real injected secret** — green unit tests and a passing readiness gate do not prove that. Bugs that only surface with the real secret/config (a stray control char in a stored key, a config-schema mismatch, a missing env-wiring, a stale model slug, a key stored under the wrong env var) are invisible to local runs that use clean/mock values. A live smoke hits the real URL, exercises the real auth path, and reads the runtime shape.

But a single green smoke also *hides* defects — so the pattern is not "call the API and print OK". It is a structured harness with guards that can go RED on their own, plus an independent adversarial check before any "this is now real" claim.

This pattern originated in the **Sizhu middleware** project (codename Bazzi Middleware Console), where it is codified as verification rule **P7** and supported by **P6** (secret-ref indirection). Concrete examples there: `scripts/smoke/fufire-live-smoke.ts`, `scripts/smoke/fufire-location-probe.ts` (the adversarial probe), `scripts/smoke/openrouter-live-smoke.ts`, `scripts/smoke/lgq-live-smoke.ts`; opt-in npm scripts `smoke:fufire`, `probe:fufire-location`, `smoke:openrouter`, `smoke:lgq`; evidence flipped only in `docs/reality/<feature>.evidence.jsonl`. Treat those as *one project's instantiation* of the pattern, not as required paths — the guards are the value, the locations are local convention.

## Your Task

Scaffold a new flag-gated live smoke for the boundary the user names (a provider/API/route). **First adapt to the project**, then mirror its closest existing smoke. Never invent a shape if one already exists.

### Step 0 — Discover the project's conventions (do this before writing anything)

Don't assume the Sizhu layout. Inspect the repo and adapt:

- **Existing smokes?** Look for prior live/real-boundary smokes and copy their skeleton.
  ```bash
  ls scripts/smoke 2>/dev/null; ls scripts/ 2>/dev/null
  # NB: grep does NOT brace-expand inside --include; pass each glob separately.
  grep -rIl --include='*.ts' --include='*.js' --include='*.py' --include='*.sh' --include='*.go' --include='*.rb' \
    -E 'live[-_ ]?smoke|real[-_ ]?boundary|RUN_.*_SMOKE|inject[-_]?drift' . 2>/dev/null | grep -v node_modules
  ```
  If found, **mirror that structure, naming, and flag convention** — consistency beats this skill's defaults.
- **No existing smokes?** Create a smokes home that fits the project's layout and test-script convention: e.g. `scripts/smoke/` for a Node/TS repo, `tests/smoke/` or `scripts/smoke/` for Python, a `Makefile` target, etc. Match the repo's language and runner (don't introduce `tsx` into a Python repo, or `pytest` into a pure-Node one).
- **How are scripts invoked?** `package.json` scripts, a `Makefile`, `justfile`, `pyproject.toml` `[tool.*.scripts]`, a `bin/` dir, or just `node/tsx/python <file>`. Add the smoke entrypoint **the same way the project already runs scripts**.
- **Is there a verification/reality-ledger or evidence convention?** (e.g. `docs/reality/*.evidence.jsonl`, a traceability matrix, a `docs/verification*.md`.) If yes, plan to record evidence there *but do not flip a not-real→real status yourself* — that is the user's call. If the project has **no** such ledger, skip it; the smoke is still valuable on its own. Do not manufacture a P-rule / ledger ceremony a project doesn't have.
- **Where do secrets/env vars live and how are they read?** Find the env loading (`.env`, `process.env`, `os.environ`, a config module) and the **exact var that holds the boundary's key**. Watch for **secret-ref indirection**: some codebases read `process.env[ process.env.<PROVIDER>_API_KEY_SECRET_REF || "<DEFAULT_REF>" ]` — i.e. the key lives under the var that the *ref* names, not under the bare `<PROVIDER>_API_KEY`, and defaults can be asymmetric across providers. Resolve which var actually holds the key; **if you can't determine it, ask — never guess the var name.**

### Step 1 — Identify the boundary + its real secret

Confirm: the provider, the real endpoint/URL, the auth scheme, and exactly which env var holds the key (resolving any secret-ref indirection from Step 0). State the resolved var name back to the user before scaffolding.

### Step 2 — Build the opt-in entrypoint (never in CI)

A single entrypoint guarded by an explicit env flag (e.g. `RUN_<X>_SMOKE=1`) or an explicit subcommand, so it **never runs in the normal test suite** (`npm test` / `pytest` / `go test`). A disabled reality-test is RED (un-run), not a silent pass — make "did not run" visibly distinct from "passed". If the project runs the file through its test runner, exclude it from the default glob.

### Step 3 — Implement the three required guards

These are the substance of the pattern. All three are mandatory.

- **Contract-drift guard — FAIL LOUD.** Assert the live response shape matches exactly what the downstream consumer/interpreter assumes (required fields, types, enum values, status codes, the slice you actually read). On any divergence: non-zero exit + a clear diagnostic naming the field that drifted. **Never** synthesize, default, or swallow a fake-success. If the boundary changed, the smoke must scream — that is the whole point.
- **Secret-hygiene self-check.** Assert the resolved key value never appears anywhere in the smoke's stdout/stderr/log/artifacts. Log only the host (and maybe a key *length* or last-4 if needed), never the key itself. This guard runs even in dry-run.
- **Dry-run + inject-drift modes.**
  - `--dry-run` (or `RUN_..._SMOKE` unset + a `DRY_RUN` flag): exercises every guard **without** the live network call, using a canned good response. Proves the harness wiring works offline.
  - `--inject-drift`: feeds a deliberately-divergent response into the contract-drift guard and asserts the guard **BITES** (the smoke goes RED / non-zero). This proves the guard is not decoration. If `--inject-drift` passes green, the guard is broken — treat that as a failure of the smoke itself.

### Step 4 — Wire the runner + document the env

- Add the entrypoint the way the project runs scripts (Step 0): e.g. `"smoke:<x>": "tsx scripts/smoke/<x>-live-smoke.ts"` in `package.json`, a `make smoke-<x>` target, or a documented `python -m ...` invocation.
- Document the **exact** env vars (the opt-in flag + the secret-ref var that truly holds the key) in the smoke's header comment and, if the project has one, its deployment/ops doc. Note any indirection and asymmetric defaults so the next person doesn't mis-wire the live secret.

### Step 5 — Prove the guards offline (do this yourself)

Run `--dry-run` and `--inject-drift` and confirm: dry-run is green, inject-drift is RED, secret-hygiene passes. **Do not run the live call yourself** unless the user provides the real secret and explicitly asks — the live call is the user's to trigger.

### Step 6 — Adversarial verify before any "it's real" claim

When a live PASS does happen, do **not** immediately record it as proof. Re-check it with an independent lens or a discriminating probe — a second endpoint, a different field, a value-level sanity check that a fake/cached/wrong-tenant response would fail (the Sizhu `fufire-location-probe.ts` is one example of such a probe). A single green smoke has been observed to PASS while adversarial lenses refuted the underlying claim. Only after the independent check survives should the boundary be considered verified — and **only the user flips a not-real→real status** in whatever evidence/ledger the project uses.

## Guardrails

- **Opt-in / not CI.** Gate on an explicit flag or subcommand; never let it run in the default test suite. "Disabled" must read as RED (un-run), never as a footnote that looks green.
- **Never echo the secret.** Log host only; the secret-hygiene self-check must assert this and run in dry-run too.
- **One green smoke is not proof.** The contract-drift guard, the inject-drift counter-test, and the Step-6 adversarial check are all mandatory — not optional polish.
- **Resolve secret-ref indirection.** If the project reads keys by an indirection var, the real key must live under the var the ref *names*; mis-wiring is invisible to clean unit tests and only a live smoke catches it. Ask if the var is ambiguous.
- **Don't rewrite the production path to "make it testable."** The smoke provides *evidence*; the path stays as it is. A RED-for-confidence item usually needs evidence, not new code.
- **Don't impose ceremony the project lacks.** If there's no reality ledger / P-rule framework, skip it — the guarded smoke stands on its own. If there is one, record evidence there but leave the not-real→real flip to the user.
- **Verify, don't trust self-reports.** Confirm the smoke actually ran and the guards actually fired (read the exit codes / output), rather than assuming. (Mind piped exit codes: `cmd | tail` reports `tail`'s status, not `cmd`'s — use `PIPESTATUS`/`$?` on the real process.)
- **Account/quota failure ≠ code defect — and ≠ real-boundary evidence.** A real call can fail for *account* reasons: `402` (no credits/billing), `429` (rate-limit / free-tier throttle), `401/403` (key scope). That is NOT a code bug — but it ALSO means the boundary was **not** verified. Do not flip the evidence to `real-boundary` unless the real call **actually executed and returned a usable response**; if it 402/429'd, the evidence stays `integration`, and you **surface the account blocker** (no laundering an unmade call into "real"). Note the exact status + provider message so the user can act (top up credits / add an own provider key / wait out the limit).
- **Discover the live model/endpoint from the provider catalog — don't hardcode a slug.** Before routing a smoke to a specific model/route, query the provider's live catalog (e.g. OpenRouter `GET /api/v1/models`) and pick a currently-present id; a hardcoded slug goes stale silently (P7 origin: a stale `-preview` model slug). Make it overridable by env (e.g. a free-tier model) so the path can be exercised without paid credits.

---
*Globalized by /reflect-skills from Sizhu middleware session patterns (the project-local `scaffold-live-smoke` + its P6/P7 verification conventions and 3+ existing live smokes). Project-specific paths/rules above are cited as the originating example, not as requirements — adapt to the host project.*
