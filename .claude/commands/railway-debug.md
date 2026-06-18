---
description: Diagnose and fix Railway deployment failures — build errors, nixpacks, missing deps
allowed-tools: Bash, Read, Edit, Glob, Grep
---

## Context
Railway deployments fail silently or with cryptic build errors. This skill reads the latest deployment logs, identifies the root cause, and fixes it.

## Your Task

Diagnose and fix the Railway deploy failure.

### Steps

1. **Check current deploy status + read the RIGHT logs**
   ```bash
   railway status
   railway deployment list -s <service>        # find the FAILED deployment ID
   railway logs <FAILED_DEPLOY_ID> -b -s <service> --lines 200   # build log
   railway logs <FAILED_DEPLOY_ID> -d -s <service> --lines 200   # deploy/runtime log
   ```
   - **CRITICAL: `railway logs` with no deployment ID defaults to the last SUCCESSFUL deploy** — so you read the stale, healthy log and conclude "build is fine". Always pass the FAILED deployment ID explicitly (`railway deployment list` shows status per ID).
   - **Auth dead (`invalid_grant` / "run railway login again")?** Browser login may not complete in this environment. Use a project token inline: `RAILWAY_TOKEN=<token> railway ...`. Note: a shell `export` does NOT persist across separate Bash tool calls, and an already-running Railway **MCP** process can't see a newly-set token — so pass it inline on each CLI call, or restart the MCP. Remind the user to **rotate** any token pasted in plaintext afterwards.
   - If not linked: pass `-s <service>` (and `-p`/`-e`) explicitly instead of `railway link`.

2. **Read the build log carefully** — look for:
   - `Rollup failed to resolve import "X"` → missing dep in `package.json` (not devDependencies)
   - `npm ci` failures → lockfile out of sync, run `npm install` locally and commit
   - Nixpacks phase errors (setup/install/build/start) → check `nixpacks.toml`
   - `COPY . /app` + build failure → file in `.dockerignore` that shouldn't be
   - Memory/timeout → chunk size, lazy imports needed

3. **Cross-check with local build AND a clean-env start**
   ```bash
   npm run build 2>&1 | tail -30
   # simulate Railway's no-secret start: run the prod entry with a BARE env
   env -i PATH="$PATH" HOME="$HOME" PORT=8123 NODE_ENV=production node dist/server.cjs &
   ```
   - If local build passes but Railway fails → environment difference (env vars, **Node version**, dep resolution). A local `npm run build` masks a fresh-`npm ci` failure because your `node_modules` already has the platform binaries — confirm with `npm ci --dry-run` (lockfile sync) and check which **node version** Railway used in the build log vs local.
   - The clean-env start catches an **import-time** crash (a module that reads a secret at import and throws when it's missing) that your local `.env` hides. If `/api/health` still answers with a bare env, the start path is fine and the failure is build/healthcheck-side.

4. **Fix root cause** — common fixes:
   - Missing dep: `npm install <pkg> --save` (not --save-dev)
   - Node version mismatch: check `.nvmrc` vs `nixpacks.toml` `nodejs_20`
   - Space in path causing nixpacks cache error: rename dir or update `.dockerignore`
   - `three` / large lib not in deps: move from devDependencies to dependencies
   - **Builder default drift (Nixpacks → node 18):** `railway.json` `"builder": "NIXPACKS"` makes Railway use Nixpacks, which **defaults to node 18**. Node 18 + a fresh `npm ci` trips the npm optional-deps bug (npm/cli#4828) so native bindings go missing — classic symptom: `Cannot find native binding ... @tailwindcss/oxide` while loading `vite.config.ts`, build exit 1. Fix: set `"builder": "RAILPACK"` (node 22 default) **and/or** pin `"engines": { "node": "22.x" }` in `package.json` so any builder selects node 22 explicitly. Compare the failed-vs-last-good build logs' node version to confirm a builder/node change is the regression.
   - **Isolate the regression by timeline:** `railway deployment list` → find the last SUCCESS and the first FAIL; `git log --since/--until` the window between their timestamps. The single config/dep delta in that window is almost always the cause (here: the commit that added `railway.json` with NIXPACKS).

5. **Commit and push fix**, then verify:
   ```bash
   railway logs --tail 50
   ```

### Guardrails
- NEVER force push to fix a deploy — fix the actual build error
- If nixpacks.toml exists, check it before touching package.json
- `npm ci` requires an up-to-date `package-lock.json` — if changed locally, commit the lockfile too
- Space in directory name breaks nixpacks cache — check `features/plan/` paths
- **Read the FAILED deploy's logs, not the default (last-SUCCESS) ones** — pass the failed deployment ID explicitly.
- **Prefer RAILPACK over NIXPACKS** for Node apps (node 22 vs Nixpacks' node 18), or pin `engines.node`. A `railway.json` builder override silently changes the node version.
- **Verify the fix on the LIVE artifact**, not just "deploy SUCCESS": re-pull the new build log (correct builder/node, no `EBADENGINE`/native-binding error) AND `curl https://<domain>/api/health` → 200. (Pairs with `/deploy-verify`.)
- A `railway.json` healthcheck (`healthcheckPath`) means an **external HTTP probe** — confirm the server binds `0.0.0.0`, not `localhost`, or the probe fails and the deploy is marked failed after retries.

---
*Generated by /reflect-skills from 3 session patterns; enhanced with Railway builder/node-version, failed-deploy-log, clean-env-repro, and token-auth guardrails (2026-06-18 retro).*
