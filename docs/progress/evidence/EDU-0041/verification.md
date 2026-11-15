# EDU-0041 verification and closeout evidence

Date: 2026-11-14 (Asia/Saigon)  
Workspace: `D:\eduops360`

## Technical gates

| Command/scope | Exit/result |
|---|---|
| `backend/.venv/Scripts/python.exe -m pytest tests -q` without live DSNs | exit 0; `77 passed, 18 skipped` |
| same backend suite with isolated migrator/runtime/audit-worker DSNs | exit 0; `95 passed` |
| Ruff `check` and `format --check` for backend; OpenAPI `--check` | exit 0; lint/format/contract match |
| `alembic current`, `heads`, `check` on isolated PostgreSQL | exit 0; `0008_mfa_replay_counter`; no new upgrade operations |
| frontend typecheck/lint/format/API/unit/build | exit 0; `22 passed`; Vite build complete |
| self-started Playwright on ports 58097/5176 | exit 0; `8 passed`; real-auth path included |
| startup benchmark on 58098/5175 | exit 0; backend 1.2 s, frontend 0.573 s |
| `python -m unittest discover` after CI regression | exit 0; `24 tests OK` |
| workflow DB-role regression | failed before against old workflow; exit 0 after correction |
| Compose config with three disposable role passwords | exit 0 |
| blueprint/structure/encoding/CSV validators | exit 0 on the final documentation set (see final journal row/task board) |

The executed browser JSON is preserved at `../EDU-0040/playwright-results.json`; startup JSON is at `../EDU-0040/startup.json`.

## Teardown proof

- `docker compose -p eduops360-edu0034 ... down -v --remove-orphans`: exit 0; removed only container `eduops360-edu0034-db-1`, network `eduops360-edu0034_default` and volume `eduops360-edu0034_postgres-data`.
- Exact synthetic credential file `.local/EDU-0034/edu0034.env` was deleted after its resolved path was verified inside the workspace.
- Before stopping Docker, filtered counts were 0 isolated containers, 0 isolated volumes and 0 isolated networks. Pre-existing `eduops360-local_postgres-data` and `eduops360-audit-0011_postgres-data`, 13 images and 16 unrelated containers remained.
- `docker desktop stop`: exit 0. Fresh `docker desktop status`: exit 1 with `Could not retrieve status. Is Docker Desktop running?`, confirming the initial stopped state was restored.
- Fresh listener check for 5173/5174/5175/5176/4173/8000/15173/18000/55432/55494/58095/58097/58098: `NONE`.
- Fresh process query for command lines containing `D:\eduops360`: `NONE`.
- `git status -sb` and `git reflog -5`: exit 128, `not a git repository`; no Git action was possible or attempted.

## Complete side-effect ledger

- Created/updated source, tests, migrations, contracts and documentation listed by EDU-0034..0041. `contracts/openapi.json` and generated TypeScript types were regenerated after the invitation API change.
- `frontend/dist/` was erased/rebuilt by Vite; `frontend/test-results/` was overwritten by Playwright. `.local/playwright-tmp/`, Python `__pycache__`, Pytest/Ruff/Vite caches and file mtimes were updated.
- `.local/EDU-0034/` retains sanitized baseline/probe/test logs and the synthetic E2E seeding helper; its credential file was deleted. `.local/EDU-0040/startup.json` remains. These are ignored local evidence.
- Ruff mechanically reformatted 14 backend files and 3 root foundation test files. All relevant tests were rerun after formatting.
- Docker Desktop was started for isolated PostgreSQL work, unexpectedly stopped once, then restarted. The orphaned task wrapper/child process was stopped and only the isolated DB container was recreated using its preserved disposable volume. Final teardown deleted that synthetic DB volume and Docker Desktop was stopped.
- A temporary real E2E API/Vite pair used ports 58095/5174 earlier; the full gate used 58097/5176. All were stopped. Attempts to use Windows-excluded benchmark ports 18000 and 15173 failed to bind and left no listener; benchmark ports were changed to 58098/5175.
- Two `Start-Process` attempts for Vite were rejected by host policy before execution; Vite was then run through the unified process session and stopped. One diagnostic SQL query had an ambiguous `status` reference, made no mutation, and was rerun qualified.
- One final validator command referenced nonexistent `scripts/validate_student_sample.py`, exited 2 and changed nothing; the correct `validate_students_csv.py` command then passed.
- No package/dependency install, external package-index/network request, real `.env` read/edit, real student data, public deployment, Git init/commit/push/PR or external message occurred.

## Remaining non-technical gates

OD-001/003/007/008/011, dependency hash generation authorization, MFA secret custody/encryption, archive/retention/audit anchor and human approval remain open exactly as listed in the acceptance package. No proposal was activated as an approved default.
