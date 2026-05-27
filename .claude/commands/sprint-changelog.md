---
description: Generate or extend a CHANGELOG.md `## [Unreleased] - YYYY-MM-DD — <Sprint Name>` block from a range of git commits, following the project's established structure (Features / Refactoring / Database / Tests / Notes).
allowed-tools: Read, Edit, Bash
---

## Context

When a sprint phase ships, the user wants a CHANGELOG entry that:

- Sits at the top of `CHANGELOG.md` above any prior `[Unreleased]` block
- Uses the header pattern `## [Unreleased] - YYYY-MM-DD — <Sprint Name>` (with optional `(Phases A–D complete)` qualifier)
- Has these sections in order, each only if non-empty: `### Features` · `### Refactoring / removed` · `### Database` · `### Tests` · `### Notes`
- Each Features bullet starts with **bold-monospace** (file/feature name in backticks) followed by an em-dash and a 2–4 sentence description that includes the audit-finding number or task ID in parentheses where applicable
- Tests section reports the running suite total (`Full suite: N/N`)
- Notes section lists: implementation plan path, any pending follow-ups, any deferred items

The user's pattern is: ship a sprint phase → run /full-review → re-run on the next batch → eventually ask for the CHANGELOG to be updated. Sometimes mid-sprint they want a "(Phases 1+2 partial)" rename → "(Phases 1+2+3 complete)" promotion when the phase finishes. The skill handles both cases.

## Your Task

Write or update the CHANGELOG entry for a completed sprint phase, given a sprint name and (optionally) a commit range.

## Steps

### 1. Resolve inputs

Required from user invocation or follow-up prompt:
- **Sprint name** — e.g. "Stripe Integration Rebuild", "Backend Hardening Sprint", "Dashboard sprint TASK-1.x"
- **Commit range** — `<base>..HEAD` or two SHAs. If omitted, use the commits since the last `## [Unreleased]` header in the existing CHANGELOG.

If the user wants to extend an existing entry (e.g. promote `(Phases 1+2 partial)` → `(Phases 1+2+3 complete)`), detect that and offer to rename the header instead of inserting a new block.

Today's date is the `YYYY-MM-DD` value — use the system date, never an old date carried over.

### 2. Inspect the commits

```bash
git log <base>..HEAD --oneline
git log <base>..HEAD --stat | head -200
```

For each commit:
- Conventional-commit prefix (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`, `perf:`)
- Files touched (especially: `*.sql` migrations, `supabase-schema.sql`, `server.mjs`, components, test files)
- Body text — pull audit-finding numbers (`#7`, `Task 12`, `TASK-1.4`) for cross-reference

### 3. Group commits into sections

| Commit prefix | Section | Notes |
|---|---|---|
| `feat:` | Features | One bullet per logical capability, not per commit. Bundle related commits. |
| `fix:` (security/correctness) | Features | If it closes an audit finding, it goes in Features with the fix-prefix. |
| `fix:` (cosmetic, build) | Bug Fixes | Only create this section if you have ≥2 of these. |
| `refactor:`, `chore:` (deletion of dead code) | Refactoring / removed | Bundle deletions. |
| Touches `supabase-migrations/*.sql` | Database | One bullet per migration. |
| Touches `*.test.*` only | Tests | Aggregate counts: "N new tests across M files. Suite: X/X." |
| `docs:` | Notes | Plan-doc commits, audit-doc commits → reference paths. |

If a commit appears in multiple buckets, put it in the most user-facing one (Features beats Refactoring).

### 4. Generate the entry

Header:

```markdown
## [Unreleased] - <YYYY-MM-DD> — <Sprint Name> (<Phase qualifier>)
```

Phase qualifier examples (use what's appropriate):
- `(Phases A–D complete)` — fully done
- `(Phases 1 + 2 + 3 partial)` — multi-phase WIP
- omit — single-phase sprint

For each Features bullet, follow this structure:

```markdown
- **<Capability name>** (`<primary file or path>`) — <2–4 sentence prose>. Closes audit finding #<N> / TASK-<id>.
```

Concrete prose patterns to mirror (from prior entries in this repo):

> **Stripe webhook state machine + dedup** (`supabase-migrations/20260507_stripe_events.sql` + `server/services/stripeEvents.service.mjs` + `server.mjs`) — every webhook event ID is INSERTed into a new `stripe_events` table before any side-effect. Duplicate event IDs (Stripe retry storm, replay) hit the `23505` unique-violation path and the handler returns `{ received: true, dedup: true }` without re-running tier updates.

> **Idempotency keys on every Stripe write** — `stripe.customers.create` calls scope by user; `stripe.checkout.sessions.create` uses a day-windowed key. Rage-clicks no longer create parallel customers or duplicate sessions.

Tone: **active voice, present tense, name the mechanism + the consequence**. Avoid "We added X" / "This change makes Y". Lead with the noun.

For Tests section:

```markdown
### Tests
- N new server-side tests covering: <comma-separated topics with counts>. M existing tests migrated to <new shape>. Full suite: <total>/<total>.
```

For Notes section, include in this order:
1. Implementation plan path (e.g. `docs/plans/<date>-<feature>.md`)
2. Audit-findings ledger summary (e.g. "14 of 17 findings closed; 1 covered by adjacent infra; 2 deferred")
3. Migrations applied vs. pending
4. Any deferred follow-ups with single-line scope description

### 5. Insert into CHANGELOG.md

Read `CHANGELOG.md` to find the current top entry. Insert the new block immediately above it, leaving exactly ONE blank line between the new block and the prior `## [Unreleased]`. Never delete or modify the prior entry's content unless the user explicitly asked for a phase-qualifier rename.

If the user is *promoting* an existing partial entry (`(Phases 1+2 partial)` → `(Phases 1+2+3 complete)`):
1. Edit the existing header text only
2. Append new bullets to the existing sections (don't create a duplicate block)
3. Bump the test counts in `### Tests` to current
4. Update `### Notes` to drop "pending Tasks N–M" if all closed

### 6. Show diff + commit

```bash
git diff CHANGELOG.md | head -60
```

Confirm the diff shows: header rename or insertion, new bullets, refreshed counts, no deletion of prior content.

If the user has ungranted commit autonomy: stage and commit with the message:

```
docs(changelog): <Sprint Name> (<phase qualifier>)

<2–3 sentences summarising what shipped. Reference commit range
"<base>..<head>" once. Mention audit findings closed if applicable.>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Otherwise: present the diff and wait for the user to commit themselves (matches the `/ship` workflow).

## Guardrails

- **Date is always today** (system date). Never copy-paste an old date from a prior entry; that breaks "what shipped when" forensics.
- **Don't auto-insert empty sections.** If there are no `Database` commits in the range, skip the section entirely. Empty `### Database` headers are noise.
- **Don't summarize commits one-per-bullet** — bundle related ones. A 3-commit feature ("introduce table" + "add helper" + "wire helper into route") is ONE Features bullet, not three.
- **Don't quote raw commit hashes in user-facing prose.** They go in commit-message bodies, not in the CHANGELOG entry. Path references (`server.mjs:341`) are fine.
- **Preserve the user's existing prose style.** If prior entries use bold-monospace headers, German+English mixed, em-dashes, do the same. Read 2-3 prior entries before writing.
- **Tests count goes up, never down.** If your range deletes some tests (dead-component cleanup), state explicitly: "Full suite drops from X → Y (deletion of N dead tests)."
- **Audit-finding numbers are gold.** If the commit body cites `#5` / `TASK-1.4` / `STRIPE-REG-007`, surface that in the bullet. They're the only way reviewers later trace cause-and-effect.

## Anti-patterns

- "Add CHANGELOG entry for the recent commits" — too vague, will produce a generic diff.
- Copy-pasting commit subject lines as bullets — those are written for git log, not for users.
- Linking to GitHub URLs in CHANGELOG — paths and commit hashes already give the link via `git log`.
- Including "Tested on Chrome / Safari / iPhone" — that belongs in the PR body, not CHANGELOG.

---
*Generated by /reflect-skills from ~6 CHANGELOG entries written across the 2026-05-06 backend hardening + 2026-05-07 Stripe rebuild sprints, all following the same Features/Refactoring/Database/Tests/Notes structure*
