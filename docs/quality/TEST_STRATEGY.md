# Quality Strategy, Bug Taxonomy and Evidence

## Pyramid by responsibility
1. Static: formatting/lint/typecheck, dependency and secret scan, encoding check.
2. Unit: grading functions, permission functions, time interval overlap, CSV parser, solver constraint helpers.
3. Integration: API↔PostgreSQL/worker/outbox and migrations (isolated seeded DB).
4. Contract: OpenAPI generation, generated TypeScript client, backward compatibility checks.
5. E2E: login, role restrictions, CSV preflight/confirm, schedule conflict and publication, grades audit, legal search.
6. Nonfunctional: accessibility, performance under benchmark dataset, fault injection, backup restore, authorized security testing.

## Bug workflow
`reported → triaged → reproducible → root_cause_identified → fixed → verified → released` or `blocked/deferred` with reason. P0: confidential-data leak, grade integrity breach, widespread outage. P1: core workflow unusable. P2: degraded or workaround. P3: cosmetic.

## Reproduction artifact
- Environment/build/commit SHA/branch; actor/permission/school/year; inputs (synthetic and anonymized); exact steps; expected/actual; UTC event time; request/correlation ID; sanitized logs/traces/screenshots; suspected area; minimal reproducer; rollback recommendation.
- Security proof uses redacted secrets and fake students, no production records in Git.

## Completion criteria
- A test fails on pre-fix behavior and passes after fix, except where non-deterministic root cause documented.
- Targeted regression suite + relevant integration/e2e pass with output saved to PR or task evidence.
- No change to app-scope modules outside owner without review; audit unaffected; no undocumented migrations.

## Reproducible real-auth browser gate

The real-auth Playwright path uses only a migrated, disposable PostgreSQL database and a synthetic user. Set `EDUOPS_TEST_MIGRATOR_DSN` without printing it, then run:

```powershell
backend\.venv\Scripts\python.exe scripts\seed_real_auth_e2e.py --output .local\real-auth-e2e.json
$fixture = Get-Content .local\real-auth-e2e.json -Raw | ConvertFrom-Json
$env:PLAYWRIGHT_REAL_AUTH_EMAIL = $fixture.email
$env:PLAYWRIGHT_REAL_AUTH_PASSWORD = $fixture.password
$env:PLAYWRIGHT_REQUIRE_REAL_AUTH = '1'
npm run test:e2e --prefix frontend
```

`PLAYWRIGHT_REQUIRE_REAL_AUTH=1` makes missing fixture variables fail rather than skip. When the backend is served over isolated plain HTTP, set `EDUOPS_SESSION_COOKIE_SECURE=false` **only on that disposable local backend process**; never carry it to HTTPS/staging/production. The helper refuses to write credentials outside ignored `.local/`; delete its output and the disposable database during teardown.

## Edge-case suite
- timezone 00:00 is valid, empty time is null; DST-aware other-zone support; inclusive holiday range; teacher/room actual-interval overlap; two Admins race; same student different year; CSV formula/leading zeros/NFC/NFD/UTF-8 BOM; solver FEASIBLE vs INFEASIBLE vs UNKNOWN; invalid/missing ML target; legal document supersession.
