---
description: Display a Supabase migration SQL copy-paste-ready, generate domain-appropriate verification queries, and walk the user through applying it via the Supabase SQL Editor.
allowed-tools: Read, Bash, Glob, Grep
---

## Context

The user repeatedly applies migration files from `supabase-migrations/<date>_<feature>.sql` via Supabase Dashboard → SQL Editor. The recurring friction:
1. The SQL block is buried in a code file — they want a single copy-paste-ready chunk in chat.
2. After running the migration they don't know what to verify.
3. The `IF NOT EXISTS` / `OR REPLACE` patterns mean a successful run produces no row output, so "did it actually work?" is unclear.
4. RLS / GRANT / policy state needs to be checked separately from the table state.

This skill consolidates that workflow.

## Your Task

Given a migration file path (or the latest unapplied migration if no path is given), display the SQL ready to paste into Supabase SQL Editor, then provide tailored verification queries based on what the migration does.

## Steps

### 1. Resolve the migration file

If the user passed a path, use it. Otherwise:

```bash
ls -t supabase-migrations/*.sql 2>/dev/null | head -3
```

Ask which one if ambiguous. If only one recent unapplied migration is obvious, use it.

### 2. Read + inspect the migration

Read the file. Identify which DDL operations it performs:
- `CREATE TABLE` — flag table name, column count
- `CREATE INDEX` — flag index names
- `CREATE OR REPLACE FUNCTION` — flag function signatures
- `ALTER TABLE … ENABLE ROW LEVEL SECURITY` — flag the table
- `CREATE POLICY` / `DROP POLICY` — flag policy names + the table
- `GRANT EXECUTE` / `REVOKE EXECUTE` — flag the role(s) and function(s)

Use this list to generate the verification queries in step 4.

### 3. Display SQL copy-paste-ready

Output the migration SQL inside ONE fenced sql block. No truncation, no `[…]` ellipsis. The user must be able to triple-click to select the whole thing.

Frame with a short intro:

> Hier der vollständige SQL-Block — alles in einem zusammenhängenden Stück, direkt copy-paste-fähig in den Supabase SQL Editor:

```sql
-- file contents verbatim
```

Followed by a 2-line "Reihenfolge zum Anwenden":
1. Supabase Dashboard → SQL Editor
2. Paste → **Run**
3. Expected: `Success. No rows returned.`

### 4. Generate verification queries

Based on the operations identified in step 2, build a single SQL block titled "## Verifizierung" the user can paste into the SAME SQL Editor session. Include only the checks relevant to what the migration actually did.

Templates:

**For new tables:**
```sql
SELECT column_name, data_type FROM information_schema.columns
  WHERE table_name = '<table>' ORDER BY ordinal_position;
-- Expected: <N> columns
```

**For RLS-enabled tables:**
```sql
SELECT relname, relrowsecurity FROM pg_class WHERE relname = '<table>';
-- Expected: relrowsecurity = true
```

**For policy presence:**
```sql
SELECT polname FROM pg_policy WHERE polrelid = '<table>'::regclass;
-- Expected: <N> rows or 0 (service_role only)
```

**For new functions:**
```sql
SELECT proname, pronargs, prosecdef AS security_definer
  FROM pg_proc
  WHERE proname IN (<function names>)
  ORDER BY proname;
-- Expected: <N> functions, security_definer = <t/f as appropriate>
```

**For GRANT/REVOKE on functions:**
```sql
SELECT grantee, privilege_type
  FROM information_schema.role_routine_grants
  WHERE routine_name IN (<function names>)
  ORDER BY routine_name, grantee;
-- Expected: only postgres + service_role (no authenticated)
```

For each verification query, include the EXPECTED result inline as a comment so the user can compare without scrolling.

### 5. Optional functional smoke test

For RPCs, suggest a minimal smoke test the user can run as a single SQL block. Use a real user UUID placeholder `<YOUR_USER_UUID>` and ALWAYS add a `DELETE FROM <table> WHERE <test-key>` cleanup at the end.

Keep the smoke test concise — 3-5 statements max. Skip if the migration is purely structural.

### 6. Wait for confirmation

After displaying everything, end with:

> Sag Bescheid sobald du die Migration angewendet hast und die Verifizierung durchgelaufen ist (Zeilen-Counts wie erwartet) — dann mache ich mit dem nächsten Schritt weiter.

Do NOT proceed to wire the migration into code yet — wait for explicit "applied" / "done" / "läuft durch".

### 7. If the user reports a verification failure

Common patterns:
- **`23503` foreign key violation** during smoke test → suggest using the user's own UUID, not a placeholder
- **`42501` permission denied** during smoke test as `authenticated` role → that's the bypass-revoke working as intended; explain it's the security boundary
- **`SET LOCAL ROLE authenticated` doesn't drop privileges** in SQL Editor → explain this is a known Supabase quirk; the editor runs with elevated privileges, the real boundary is via PostgREST + RLS, not in the editor
- **Function returns expected JSON but test-fixture UUID doesn't exist in `auth.users`** → that's the FK enforcing referential integrity, not a bug. Use a real user.

## Guardrails

- NEVER apply the migration yourself, even if a Supabase MCP is available. The user's pattern is "I apply, you display + verify". Suggesting `mcp__claude_ai_Supabase__apply_migration` skips the audit trail they want.
- NEVER truncate the SQL block in display. The point is copy-paste — partial SQL is worse than useless.
- The "Expected: ..." inline comments are MANDATORY in every verification query. Without them, the user has to figure out what "right" looks like.
- If the migration does both DDL and a `GRANT`, generate verification for BOTH. Don't skip the GRANT check just because the table check passed.
- After the user confirms application, OFFER to commit a cosmetic update to `supabase-schema.sql` if you can detect drift between schema-file and migration. Don't auto-commit.

## Anti-patterns (do not do these)

- "Run this migration" — the user wants to read it first, then apply themselves
- Generating verification queries that include `\d <table>` (psql meta-command, doesn't work in Supabase SQL Editor)
- Using `SELECT 1` as a smoke test — useless, doesn't prove anything
- Suggesting the user run the migration via `supabase db push` CLI — they're explicitly using the Dashboard SQL Editor

---
*Generated by /reflect-skills from 3 Supabase migration applications across the 2026-05-06 backend hardening + 2026-05-07 Stripe rebuild sprints*
