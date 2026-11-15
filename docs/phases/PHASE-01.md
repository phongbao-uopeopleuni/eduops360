# PHASE-01 — App foundations, shared design & API contracts

**Status:** IN_REVIEW / LOCAL_IMPLEMENTATION  
**Implementers:** Tech Lead / Frontend Agent / Backend Agent  
**Independent reviewer:** QA Agent  
**Prerequisite:** PHASE-00 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

Local implementation was started on the user's 2026-11-12 instruction, recorded in EDU-0007..0010. Evidence and outstanding independent review are tracked in `docs/progress/HANDOFF.md`. Phase 00 acceptance and OD ownership retain their recorded pending status.

## A. Purpose and implementation boundaries
App foundations, shared design & API contracts; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `React + Vite + TypeScript shell`
- `FastAPI modular app skeleton`
- `OpenAPI client generation`
- `Light/Dark theme tokens`

## C. Detailed execution steps
1. **P01-T01:** Create `frontend/` package and Vite entry, strict TS config, router, layout and feature folder convention.
2. **P01-T02:** Create `backend/` pyproject, FastAPI app factory/router registry, Pydantic settings and health endpoint.
3. **P01-T03:** Set PostgreSQL development container; Alembic revision scaffolding; no real school data.
4. **P01-T04:** Write base OpenAPI contract and generate TypeScript client into frontend/shared/api/generated.
5. **P01-T05:** Implement white-first academic design tokens, Vietnamese-friendly font fallback, system/light/dark persistence.
6. **P01-T06:** Add UTC-aware date/time utilities and `YYYY-MM-DD` handling without accidental timezone conversions.
7. **P01-T07:** Create synthetic fixture generator and deterministic seed; document local start/stop and secret placeholders.
8. **P01-T08:** Add formatting, lint, typecheck, API smoke and encoding tests in CI.
9. **P01-T09:** Benchmark developer startup and document known local dependency versions.

## D. Where files belong
- `frontend/src/`
- `backend/app/`
- `contracts/openapi.json`
- `infra/compose.dev.yml`

## E. Verification and exit gate
- [x] Frontend and backend can start independently
- [x] OpenAPI client matches backend schema
- [x] Light/Dark snapshots and UTF-8 fixtures pass
- [x] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [x] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.

## H. Local implementation evidence — 2026-11-12

| Planned step | Implementation / evidence |
|---|---|
| P01-T01 | EDU-0008, React/Vite strict TypeScript, router and feature folders |
| P01-T02 | EDU-0007, factory/settings/health, Windows-compatible API entry point |
| P01-T03 | EDU-0009, PostgreSQL Compose and Alembic `0001_foundation` |
| P01-T04 | EDU-0007/0008, generated OpenAPI/types and drift checks |
| P01-T05 | EDU-0008, persistent themes, Vietnamese font, palette contrast and screenshots |
| P01-T06 | EDU-0007/0008, calendar date/UTC helpers and regression cases |
| P01-T07 | EDU-0009, deterministic 2k/10k synthetic CSV with existing preflight validation |
| P01-T08 | EDU-0010, local checks and `.github/workflows/foundation-check.yml` |
| P01-T09 | EDU-0010, independent startup measurement with runtime versions |

Exact local commands/results and remaining gates are linked from `docs/progress/tasks/EDU-0010.md`. The hosted CI run, independent review and human acceptance are pending.

## I. Fresh local exit-gate verification — 2026-11-14

EDU-0040 repeated the complete local gate after the Phase 02 remediation work. Backend host tests passed (`77 passed, 18 skipped`); the isolated PostgreSQL suite passed (`95 passed`); frontend unit tests passed (`22 passed`); and Playwright passed all 8 browser paths, including a real login/CSRF logout against the isolated backend and database. Startup, OpenAPI/client drift, formatting, lint, build, UTF-8, structure and migration checks also passed. The detailed command ledger is `docs/quality/PHASE_01_LOCAL_GATE_2026-11-14.md`.

This closes the five local technical checkboxes above only. Phase 01 remains `IN_REVIEW`: the directory has no Git/hosted-CI evidence, OD-001 has not named the independent reviewer/authority, and Codex cannot independently approve work it implemented.

## J. Git and hosted-CI update — 2026-11-15

EDU-0055 initialized and pushed the repository to `https://github.com/phongbao-uopeopleuni/eduops360` on `main`. EDU-0056 fixed the first clean-checkout CI defect. Hosted foundation run `43700379144` and governance run `43700379165` pass on commit `d8012da9fc33bafa2d17e7ca81d0fecc996bf585`, including the `foundation`, `governance` and `blueprint-check` contexts. Protected `main` requires those checks plus a pull request and one approval.

This supersedes only the earlier “no Git/hosted-CI evidence” statement. Phase 01 remains `IN_REVIEW`: the repository is public, independent reviewer/authority assignments and human acceptance remain open, and green CI is not acceptance.
