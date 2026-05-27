---
description: When `git push` fails with GitHub `GH013` repository-rule-violation (push protection blocked secrets), parse the rejection output, extract every bypass URL, walk the user through clicking the green "Allow secret" button, and retry the push.
allowed-tools: Bash, Read
---

## Context

GitHub's push-protection scans every push for secret-looking patterns. False positives are common when:
- Test fixtures contain synthetic secrets (e.g. `sk_live_<SYNTHETIC_FIXTURE_VALUE>`)
- Plan documents quote diff blocks containing the same fixture strings
- Secrets are in commits that previously fired the protection but were never deleted from history

The user typically:
1. Runs `/ship`, push fails with `GH013`
2. Doesn't know where the bypass URLs are in the noisy stderr
3. Doesn't know the URL opens a *form* that requires picking a reason and clicking a green button — opening the page is not enough
4. Doesn't understand which fixtures are real vs synthetic

This skill takes that whole loop down to "open the URLs I give you, click Allow, say done".

## Your Task

Resolve a push blocked by GitHub secret-protection by guiding the user through the bypass form, then retrying.

## Steps

### 1. Reproduce the rejection (if not already shown)

If the user invokes this skill *before* attempting the push, run:

```bash
git push 2>&1
```

Capture the full stderr. If the user invokes the skill *after* a failed push and the rejection output is still visible in conversation, parse the existing output instead.

### 2. Verify the failure mode is `GH013` push protection

Look for these markers in the stderr:

```
remote: error: GH013: Repository rule violations found for refs/heads/<branch>.
remote: - GITHUB PUSH PROTECTION
remote:   Resolve the following violations before pushing again
remote:     - Push cannot contain secrets
```

If those markers are absent, this is a different rejection (force-push refused, branch protection, fast-forward not allowed). **Stop and report** — this skill only handles secret-protection blocks.

### 3. Extract every bypass URL

GitHub emits one URL per *unique secret value*, not per occurrence. Multiple commits that contain the same string share a URL.

Pattern to match:

```
remote:        (?) To push, remove secret from commit(s) or follow this URL to allow the secret.
remote:        https://github.com/<org>/<repo>/security/secret-scanning/unblock-secret/<token>
```

Extract every URL. Also collect the secret type (e.g. "Stripe API Key", "Supabase JWT") and the file:line locations from the same block — this lets you verify that the matches are synthetic test fixtures and not real secrets.

### 4. Pre-flight check: are these synthetic?

For each flagged file:line, read the line and inspect the surrounding context:

```bash
sed -n '<line-3>,<line+3>p' <file>
```

Classify each match:
- **Synthetic test fixture** (predictable letters like `abcdefghij…`, in a `*test*` or `*fixture*` file, runtime concat with `'sk_' + 'live_' + ...`) → safe to bypass
- **Plan/doc quoting a fixture** (matches in `docs/plans/` or `docs/audit/`) → safe to bypass
- **Real-looking secret** (high-entropy random string, in a non-test file) → **STOP**, alert the user, do NOT bypass

If any match is unclassifiable, surface it to the user with the file:line and the secret type, and ask before continuing.

### 5. Display URLs prominently

Number them, one per line, with the secret type and a hint:

```
**URL 1: Stripe API Key** (matched in server/__tests__/fixture.test.ts:49 and docs/plans/2026-05-07-x.md:57)
https://github.com/<org>/<repo>/security/secret-scanning/unblock-secret/<token-1>

**URL 2: Stripe Webhook Secret** (matched in server/__tests__/fixture.test.ts:115)
https://github.com/<org>/<repo>/security/secret-scanning/unblock-secret/<token-2>
```

User-facing language in the language they were using (de/en).

### 6. Form-submission walkthrough

Critical: opening the URL is NOT enough. The user must:

1. Click the URL → lands on a GitHub page titled "Allow secret"
2. Scroll to the form section "Why are you bypassing this push protection?"
3. Pick one of the radio buttons: **"It's used in tests"** (best fit for synthetic fixtures) or "It's a false positive"
4. Click the **green "Allow me to push this secret"** button at the bottom
5. Repeat for every URL

State this explicitly. Many users open the page, see the secret listed, and close the tab thinking that "viewing" was the action.

### 7. Wait for "done" confirmation

Pause until the user says "done" / "submitted" / "applied" / similar. Do NOT auto-retry — give time for GitHub's rule to propagate (10-30 seconds typical).

### 8. Retry the push

```bash
git push 2>&1 | tail -5
```

- **Success** → report `<old-sha>..<new-sha>  main -> main` and stop
- **Same rejection** → the bypass form was probably not submitted. Tell the user:
  - "Bypass didn't take effect. Verify you clicked the green 'Allow' button on each URL — opening the page alone doesn't count."
  - Wait 30 seconds, retry once
  - If still failing: stop, recommend Path B (interactive rebase to remove literals) and explicitly request user approval for that path
- **Different rejection** (e.g. fast-forward refused) → stop and report the new error verbatim

### 9. After successful push

If the bypassed strings are in test fixtures, suggest a one-line follow-up commit later that breaks the contiguous literal via runtime concat:

```js
// Before — triggers GitHub secret scanning
const k = "sk_live_<SYNTHETIC_FIXTURE_VALUE>";

// After — same value at runtime, no GitHub flag
const k = 'sk_' + 'live_' + 'abcdefghijklmnopqrstuvwxyz1234567890';
```

This pre-empts the same dialog on the next push.

## Guardrails

- **NEVER bypass a real secret.** If a flagged match doesn't look like a test fixture, stop and alert the user even if the user says "just bypass it". Real keys leaking via push protection happens — the protection exists to catch this case.
- **NEVER use `git push --no-verify`** — that's a different bypass path that some repos disallow entirely and it leaves no audit trail.
- **NEVER suggest interactive rebase as the first option.** Bypass-via-URL is the lowest-risk path and matches the tool's intended workflow. Rebase is only for cases where the URL bypass isn't possible (org policy disallowing it).
- **NEVER auto-retry on the same rejection more than once.** Two failures in a row means the bypass form wasn't submitted; further retries waste time. Wait for the user.
- The bypass URLs are single-use per secret/repo. Don't paste them in commit messages or any committed artifact.

## Anti-patterns

- "I'll click the URL for you" — Claude can't, and shouldn't try via browser MCP either; the user must approve via their own GitHub session.
- "Just remove the secret from the file" — that doesn't help if the literal is still in git history. Bypass + later runtime-concat refactor is the right fix order.
- Suggesting `git filter-branch` or BFG Repo-Cleaner as a first response — both rewrite history and are massive overkill for synthetic test fixtures.

---
*Generated by /reflect-skills from the 2026-05-07 Stripe rebuild ship friction (6 user turns to resolve a single push-protection block — should have been 1)*
