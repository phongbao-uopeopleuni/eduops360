# Requirement → phase → verification → evidence

| ID | Owning phase | Minimum verification | Evidence location |
| --- | --- | --- | --- |
| GOV-01 | Phase 00 | decision baseline + ADR + independent review | docs/quality/PHASE_00_ACCEPTANCE.md / EDU-0005 |
| SCALE-01 | Phase 01/11 | synthetic fixture generation + load tests; targets unverified | docs/phases/PHASE-01.md / PHASE-11.md |
| APPROVAL-01 | Phase 02/05/07 | state transition tests + actor≠approver + audit | docs/phases/PHASE-02.md / PHASE-07.md |
| ENV-01 | Phase 01/11 | compose health + staging isolation + secret scan | EDU-0040 / docs/phases/PHASE-01.md / PHASE-11.md |
| AUTH-01 | Phase 02 | unit + PostgreSQL integration + browser E2E | EDU-0025/0027/0028/0030/0038/0040 |
| AUTH-02 | Phase 02 | default-deny, scope/IDOR/escalation tests + independent review | EDU-0012/0026/0028/0032/0034 |
| YEAR-01 | Phase 03 | unit + integration + E2E per phase | EDU-0054 pure-domain unit slice; DB/API/E2E remain later Phase 03 tasks |
| YEAR-02 | Phase 03 | unit + integration + E2E per phase | EDU-0054 date/timezone/revision unit slice; DB/API/E2E remain later Phase 03 tasks |
| SIS-01 | Phase 03 | unit + integration + E2E per phase | docs/phases/PHASE-03* / task evidence |
| IMPORT-01 | Phase 04 | unit + integration + E2E per phase | docs/phases/PHASE-04* / task evidence |
| IMPORT-02 | Phase 04 | unit + integration + E2E per phase | docs/phases/PHASE-04* / task evidence |
| CAL-01 | Phase 05 | unit + integration + E2E per phase | docs/phases/PHASE-05* / task evidence |
| CAL-02 | Phase 05 | unit + integration + E2E per phase | docs/phases/PHASE-05* / task evidence |
| SCH-01 | Phase 06 | unit + integration + E2E per phase | docs/phases/PHASE-06* / task evidence |
| SCH-02 | Phase 06 | unit + integration + E2E per phase | docs/phases/PHASE-06* / task evidence |
| SCH-03 | Phase 06 | unit + integration + E2E per phase | docs/phases/PHASE-06* / task evidence |
| EXAM-01 | Phase 07 | unit + integration + E2E per phase | docs/phases/PHASE-07* / task evidence |
| EXAM-02 | Phase 07 | unit + integration + E2E per phase | docs/phases/PHASE-07* / task evidence |
| LEGAL-01 | Phase 08 | unit + integration + E2E per phase | docs/phases/PHASE-08* / task evidence |
| LEGAL-02 | Phase 08 | unit + integration + E2E per phase | docs/phases/PHASE-08* / task evidence |
| ANA-01 | Phase 09 | unit + integration + E2E per phase | docs/phases/PHASE-09* / task evidence |
| ML-01 | Phase 10 | eval + security + nonfunctional tests | docs/phases/PHASE-10* / task evidence |
| ML-02 | Phase 10 | eval + security + nonfunctional tests | docs/phases/PHASE-10* / task evidence |
| SEC-01 | Phase 02/11 | transaction/audit privilege tests + negative API/E2E | EDU-0024/0028/0030/0034/0036/0037/0038; Phase 11 evidence later |
| OPS-01 | Phase 11 | eval + security + nonfunctional tests | docs/phases/PHASE-11* / task evidence |
| UI-01 | Phase 01 | unit + integration + E2E per phase | EDU-0040 / docs/phases/PHASE-01* / task evidence |

Detailed feature tests for later phases are added as implementation proceeds.

## Phase 01 local evidence — 2026-11-12

| Requirement | Implemented verification | Evidence |
|---|---|---|
| ENV-01 | Compose health, frontend proxy smoke, real DB outage/recovery, PostgreSQL UTF8, Alembic baseline | EDU-0007/0009; `docs/progress/evidence/EDU-0010/integration.json` |
| SCALE-01 fixture slice | Deterministic 2k/10k CSV, preflight, NFC/BOM/leading-zero and overwrite protection | `tests/foundation/test_synthetic_students.py`; EDU-0009. Load benchmarks remain due Phase 11 |
| UI-01 | Theme persistence/storage failure, navigation/keyboard/mobile, light/dark palette contrast and screenshots | Frontend Vitest/Playwright; EDU-0008 |
| NFR-TIME foundation slice | Strict calendar dates, leap-year rejection and timezone-aware UTC conversion | `backend/tests/test_foundation.py`, `frontend/src/shared/lib/dates.test.ts` |
| ENV-01 contract slice | Generated OpenAPI matches backend, generated TypeScript matches OpenAPI, API 200/503/error cases | `scripts/export_openapi.py --check`, `npm run api:check`, EDU-0007/0008 |

Phase 01 remains pending independent review and acceptance.

### Fresh Phase 01 gate — 2026-11-14

EDU-0040 reran startup, backend host/live PostgreSQL suites, migrations, contracts, frontend unit/build and all 8 Playwright paths. Technical checks pass; independent review, Git/hosted CI and human acceptance remain pending. See `docs/quality/PHASE_01_LOCAL_GATE_2026-11-14.md`.

## Phase 02 local evidence — 2026-11-13

| Requirement | Implemented verification | Evidence / remaining gate |
|---|---|---|
| AUTH-01 | Argon2id; hashed session/CSRF; login/logout; one-time hashed invitation/reset with expiry/reuse denial; reset revokes sessions; provisioned TOTP verification | EDU-0025/0028/0030; encrypted MFA enrollment/recovery still blocked by approved custody and OD-001 |
| AUTH-02 | DB-loaded active/time-valid grants, default deny, explicit school/year scope, IDOR/escalation/stale-grant negative tests | EDU-0012/0026/0028; OD-008 must approve the authoritative role/scope matrix before activation |
| APPROVAL-01 | Missing submitter and self-approval deny in policy tests; current high-risk mutations audited | EDU-0015/0027/0028; OD-007 still owns exact workflow/action list |
| SEC-01 | Three least-privilege DB roles, source audit immutable to runtime/worker, transactional rollback, token/audit redaction, CSRF and rate-limit negatives | EDU-0024/0025/0028/0030; OD-011 owns external archive retention/delivery activation |
| UI Phase 02 slice | Typed Vietnamese Admin invitation/status/scoped-role console; browser confirms CSRF header and one-time token display | EDU-0027/0030; Product/Human Security review pending |

Local test success is implementation evidence only. Phase 02 remains unaccepted until its prerequisite, OD and independent human gates close.

## Phase 01/02 acceptance package — 2026-11-14

EDU-0041 maps all current gates, A0102-F01..F22, remaining OD/MFA/archive blockers and reviewer eligibility at `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`. Its conclusion is `READY_FOR_HUMAN_ACCEPTANCE`, not phase acceptance.
