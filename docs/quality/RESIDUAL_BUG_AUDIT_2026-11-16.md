# Residual bug audit — 2026-11-16

## Remediation update — EDU-0068, 2026-11-16

A67-F01/F02/F03 and UI49-F01 now have code fixes and regression evidence; status
is **FIX_IMPLEMENTED / IN_REVIEW**, not independent acceptance. The OPEN labels
and baseline counts below describe the earlier audit snapshot and are retained.
Fail-first backend: 12 failed / 19 passed; final targeted: 39 passed. Full isolated
PostgreSQL backend: 152 passed / no skips; frontend 24; targeted browser 1; root 28.
Current probe returns all six defect indicators `false`. Source contracts, static
checks and runtime dependency audit pass. See EDU-0068 for command/Git evidence.
R42-F02, independent EDU-0046/0048 review, MFA/archive and human acceptance remain.

Task: EDU-0067. Author: Codex, audit author; **not independent acceptance** of
Codex's previous implementations. Reviewed HEAD:
`d488bc055b0609430fe1dbf3177c427650617830` in `D:\eduops360`.
Commands ran approximately 09:22–09:25 +07:00, with final documentation checks
recorded in the task journal. Inputs: Phase 00, phase task definitions, current
source, threat model, release gate and historical findings.

## Findings reproduced in this audit

### A67-F01 — P2 OPEN: default Uvicorn logs bypass sanitized application logging

- Paths: `backend/app/__main__.py:11`,
  `backend/app/main.py:68`, `backend/app/common/observability.py`.
- Requirement: SRS `NFR-SEC`; P11-T03A confidentiality boundary.
- Preconditions: use the shipped entrypoint/default Uvicorn logging. Send a URL
  containing sensitive query data, or encounter an unhandled exception containing
  sensitive internal details. No authentication is required to trigger access logs.
- Actual: `eduops.http` is sanitized, but `uvicorn.access` separately records the
  raw query and `uvicorn.error` records the propagated exception traceback.
- Reproduction: run the checked-in synthetic probe below. Both
  `uvicorn_logs_raw_query` and `uvicorn_logs_exception_detail` return `true`.
  The probe runs actual Uvicorn/HTTP on an ephemeral loopback port and captures
  its logger records; TestClient alone misses this behavior.
- Impact: application log redaction does not protect all runtime destinations;
  query secrets or exception details can enter stderr/container logs. This does
  not demonstrate a secret leak to an HTTP client or a transactional-audit bypass.
- Minimal remediation for Backend/Operations implementer: suppress or sanitize
  default access logs; handle unexpected failures without emitting sensitive
  exception text, retaining a safe error event/request ID. Cover all shipped
  entrypoints. Add a real-server logging regression, including 500 handling.
- Status: **OPEN**, no runtime change made in this audit. The earlier
  EDU-0066 logger-liveness fix remains present but does not fix this separate path.

### A67-F02 — P3 OPEN: domain immutability stops at the dataclass boundary

- Paths: `backend/app/modules/school_calendar/domain.py:39`,
  `backend/app/modules/timetables/snapshot.py:66`.
- Requirement: P05-T01 domain values / P06-T01 immutable input snapshot.
- Actual: `ScheduleTemplate(..., slots=some_list)` accepts a mutable list;
  changing that list changes the frozen template. Snapshot checks outer tuples
  but accepts a mutable dictionary inside `teaching_assignments`, which remains
  mutable after construction.
- Probe outputs: `schedule_template_changed_through_original_list=true` and
  `snapshot_nested_element_changed=true`.
- Impact: a future caller using unvalidated runtime inputs can change a supposedly
  stable projection. These examples violate Python type annotations; there is
  currently no API/persistence/solver consumer of these types, so this is a
  latent runtime-contract defect, **not an observed production scheduling bug**.
- Minimal remediation: validate tuple collection types and their element classes
  at construction, or introduce an explicitly validated construction boundary.
  Do not add future solver/calendar business rules as part of this correction.
- Owner: Calendar/Timetable Backend implementer; review by another actor.

### A67-F03 — P3 OPEN: chart input can bypass required scope/filter validation

- Path: `backend/app/modules/analytics/chart_input.py:86`.
- Requirement: P09-T01, academic-year scope and unsuitable-variable rejection.
- Actual: `ChartInput(None, None, 'grade_level', filters=({'field': 'full_name',
  'values': ['synthetic-name']},))` constructs successfully. `academic_year_id`
  is not validated and filter elements are not required to be `ChartFilter`.
- Probe: `chart_accepts_missing_year=true` and
  `chart_accepts_unvalidated_filter=true`.
- Impact: malformed runtime construction bypasses the advertised fail-closed
  input contract. These inputs violate the annotations. No query, export, UI or
  endpoint consumes this type yet; **no live data disclosure is demonstrated**.
- Minimal remediation: enforce required UUID year/optional UUID subject and
  `ChartFilter` elements at the construction boundary; add rejection tests.
- Owner: Analytics Backend implementer; review by another actor.

## Previously known residual findings and gates

| Item | Current disposition | Evidence / next owner |
| --- | --- | --- |
| R42-F01 | Implemented remediation, independent closure still pending | EDU-0046; token redemption rechecks present in source; Codex cannot independently approve its fix |
| R42-F03..F05 | Implemented remediation, independent closure still pending | EDU-0048; saturated limiter fail-open behavior remains explicitly documented |
| R42-F02 (P2) | OPEN Security Owner decision | Shared-IP login blocking semantics/threshold/trusted proxy; do not silently change policy |
| UI49-F01 (P2) | OPEN | `.brand`/`.text-link` still lack 44px minimum hit targets; source rechecked, browser dimensions not remeasured this audit; different implementer needed per EDU-0049 |
| MFA custody / audit archive | Not operationally completed | Encrypted enrollment/recovery custody, archive retention/delivery and human approval still pending |
| Phase acceptance / OD decisions | OPEN | No signed acceptance discovered; unchanged master decisions remain authoritative |

No new P0/P1 was demonstrated in the reviewed source/probes. This is a bounded
audit, not proof that no P0/P1 exists: live PostgreSQL integration, real-backend
browser flows, load/restore and infrastructure security were not rerun locally.
The historical P1 R42-F01 must not be described as independently closed.

## Reproduction and verification

From repository root in PowerShell:

```powershell
.\backend\.venv\Scripts\python.exe docs/progress/evidence/EDU-0067/audit_probe.py
```

At 2026-11-16T09:24:43+07:00, exit 0, final probe JSON:

```json
{"chart_accepts_missing_year":true,"chart_accepts_unvalidated_filter":true,"schedule_template_changed_through_original_list":true,"snapshot_nested_element_changed":true,"uvicorn_logs_exception_detail":true,"uvicorn_logs_raw_query":true}
```

Exit 0 means the probe completed; the six `true` values are evidence of defects,
**not six passing safety tests**. Only synthetic markers were used. Settings
explicitly disable environment-file loading and database access.

| Current command | Actual result |
| --- | --- |
| `backend/.venv/Scripts/python.exe -m pytest backend/tests -q` | 115 passed, 20 skipped (isolated PostgreSQL DSNs not configured), exit 0 |
| Backend Ruff lint / format check | pass; 67 files formatted, exit 0 |
| Backend venv `scripts/export_openapi.py --check` | matches FastAPI, exit 0 |
| `npm test --prefix frontend` | 24 passed / 4 files, exit 0 |
| Frontend typecheck / lint / api:check | pass, exit 0 |
| `npm audit --prefix frontend --omit=dev --audit-level=high` | 0 runtime dependency vulnerabilities, exit 0; dev dependencies outside this check |
| `python -m unittest discover -s tests -p 'test_*.py'` | 28 passed, exit 0 |
| Secret scan / structure / blueprint | pass, exit 0; scanner is high-confidence tracked-value detection, not a full secret inventory |
| `gh pr checks 10` | existing reviewed HEAD: foundation, governance, blueprint-check pass; no CI claimed for this uncommitted audit |

No frontend build was needed or run; `dist/` was not rebuilt. Existing browser
and hosted CI evidence is historical for HEAD, not a fresh local E2E execution.

## Action order

1. Correct A67-F01 and add actual Uvicorn redaction coverage before treating
   operational logs as privacy preserving.
2. Have an eligible independent reviewer verify EDU-0046/0048. Security Owner
   resolves R42-F02 and MFA/archive policy; separate actor fixes UI49-F01.
3. Harden the narrow domain constructors (A67-F02/F03) before wiring them to
   queries, solver jobs or API boundaries.
4. Complete remaining Phase 03 master data and subsequent feature task groups
   under their documented gates. Phase numbering is not completion evidence.
