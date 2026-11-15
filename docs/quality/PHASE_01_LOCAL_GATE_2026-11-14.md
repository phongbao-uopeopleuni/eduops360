# Phase 01 local exit gate — 2026-11-14

**Result:** `TECHNICAL_GATE_PASS / HUMAN_ACCEPTANCE_PENDING`  
**Executor:** Codex, technical gate executor  
**Task:** EDU-0040  
**Environment:** Windows host plus disposable PostgreSQL 18 Compose project `eduops360-edu0034`; synthetic data only

## Scope and authority

This verification establishes the local technical state of Phase 01 after the Phase 02 remediation set. It does not accept the phase, substitute for a hosted CI run, or provide independent review of Codex-authored work. OD-001 and OD-003 remain open.

## Results

| Gate | Fresh result | Status |
|---|---|---|
| Independent startup | backend first HTTP 200 in 1.2 s on port 58098; frontend ready in 0.573 s on port 5175; both listeners absent after the benchmark | PASS |
| Backend host suite | `77 passed, 18 skipped`; skips are live-PostgreSQL tests intentionally run in the next row | PASS |
| Backend isolated PostgreSQL suite | `95 passed` | PASS |
| Migration | current/head `0008_mfa_replay_counter`; `alembic check` reports no new upgrade operations | PASS |
| Python quality | Ruff lint passes; Ruff format check reports 51 files formatted | PASS |
| API contract | FastAPI export matches `contracts/openapi.json`; generated TypeScript matches OpenAPI | PASS |
| Frontend quality | TypeScript, ESLint and Prettier checks pass; Vitest `22 passed` | PASS |
| Frontend build | Vite production build completes | PASS |
| Browser paths | Playwright `8 passed`, including real backend login, session-bound CSRF logout and signed-out reload | PASS |
| Governance/fixtures | blueprint PASS; structure OK; encoding clean; synthetic sample 3 rows/0 errors; root unittest 24 OK after the workflow regression | PASS; rerun after documentation updates required |
| Git/hosted CI | workspace is not a Git repository; no commit, push, PR or hosted-CI run can be evidenced | PENDING — OD-003/human |
| Independent acceptance | reviewer/authority is unnamed and the executor is not eligible to approve its own implementation | PENDING — OD-001/human |

## Commands

Commands were run from `D:\eduops360`; credentials were read only from the disposable `.local/EDU-0034/edu0034.env` without printing them.

```powershell
python scripts/benchmark_startup.py --output .local/EDU-0040/startup.json
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python -m unittest discover tests/foundation

Push-Location backend
.venv\Scripts\python.exe -m pytest tests -q
.venv\Scripts\python.exe -m ruff check app tests
.venv\Scripts\python.exe -m ruff format --check app tests migrations
.venv\Scripts\python.exe -m alembic current
.venv\Scripts\python.exe -m alembic heads
.venv\Scripts\python.exe -m alembic check
Pop-Location
backend\.venv\Scripts\python.exe scripts/export_openapi.py --check

Push-Location frontend
npm run typecheck
npm run lint
npm run format:check
npm run api:check
npm test
npm run build
npx playwright test
Pop-Location
```

The live backend command additionally set the three disposable `EDUOPS_TEST_*_DSN` values. The browser command used ports 58097/5176, `EDUOPS_SESSION_COOKIE_SECURE=false` for isolated HTTP only, and the synthetic `real-e2e-edu0038@example.com` fixture.

## Findings and corrections made by the gate

1. `ruff format --check` initially reported 14 Python files. The configured formatter was run mechanically across `backend/app`, `backend/tests` and `backend/migrations`; the full backend test/lint/format/contract gate then passed.
2. The startup benchmark initially selected Windows-excluded ports 18000 and 15173 and received `WinError 10013`. EDU-0040 changed the benchmark-only ports to 58098/5175; the benchmark passed and all attempted listeners were confirmed absent afterward.
3. A final workflow/source reconciliation found that `foundation-check.yml` still created the retired single `POSTGRES_PASSWORD` and attempted Alembic through the runtime container. A fail-first static regression reproduced the mismatch; the workflow now creates all three current synthetic role passwords and runs `alembic check` through the migrator service. Local Compose configuration and the regression pass; a hosted run remains pending OD-003.

Neither correction changes product policy or resolves an OD item.

## Side effects of this gate

- `frontend/dist/` was overwritten by the Vite build.
- `frontend/test-results/` was overwritten by Playwright; `.local/playwright-tmp/` and normal Python/Node caches and mtimes were updated.
- Seventeen Python files were mechanically reformatted (14 backend files and 3 root foundation tests); behavior was reverified by the host/live PostgreSQL suites and 24 root tests.
- The Phase 01 workflow and its static infrastructure regression were updated; no hosted workflow was triggered.
- No dependency was installed, no external network fetch was requested, no real student data was used, and no public service was started.

## Remaining acceptance gates

- Name an independent reviewer/security authority under OD-001 and record their review.
- Decide how Git/hosted-CI evidence is to be produced under OD-003.
- Record explicit human acceptance; until then Phase 01 remains `IN_REVIEW`.
