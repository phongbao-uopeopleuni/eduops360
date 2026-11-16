# Project progress — verified 2026-11-16

Operational progress snapshot, **not an alternative specification**. Canonical
scope/decisions: `docs/phases/PHASE-00.md`; detailed tasks: phase specifications.
Audit evidence: EDU-0067 and `docs/quality/RESIDUAL_BUG_AUDIT_2026-11-16.md`.

Latest remediation: EDU-0068, 2026-11-16. A67-F01/F02/F03 and UI49-F01 have code
fixes with regression evidence, **in review, not independently accepted**.
Full isolated synthetic PostgreSQL backend suite: 152 passed (no skips);
frontend unit: 24 passed; targeted browser hit-target test: 1 passed; root: 28.
All 44 historical raw logs remain local/ignored; a sanitized manifest preserves
their hashes and available numeric summaries, not a full raw-log backup.
In the table below, A67/UI49 references identify findings whose fixes await
independent review; they are no longer unimplemented code corrections.

**12 phases total (00–11); 0/12 formally accepted; all 12 still require exit-gate
completion or approval.** This is acceptance progress, not 0% implementation.
No reliable overall implementation percentage is claimed: phase tasks have
different sizes and several completed slices are documents rather than features.

| Phase | What exists | What remains |
| --- | --- | --- |
| 00 | Master, requirements, governance and checks | Named authorities, open decisions and signed independent/PO acceptance |
| 01 | Local React/FastAPI/PostgreSQL/Compose foundation, API contract, CI; UI49-F01 fix/Chromium regression in EDU-0068 | Independent UI review and human acceptance; full browser suite not rerun in EDU-0068 |
| 02 | Local IAM, session/CSRF, RBAC/scopes, transactional audit/outbox, Admin UI | EDU-0046/0048 independent re-review; R42-F02; role-policy approval; MFA custody; audit archive operation and acceptance |
| 03 | P03-T01 pure year/term rules (EDU-0054) | P03-T02..T09: master/student/enrollment persistence, APIs, UI and cross-year journeys |
| 04 | P04-T01 CSV v1 template/guide (EDU-0057) | P04-T02..T09: upload/staging/preview/transaction/import/export/rollback |
| 05 | P05-T01 schedule-template domain values (EDU-0058); A67-F02 guards/tests in EDU-0068 | Independent fix review; P05-T02..T09 editor, validation, holidays, exceptions, APIs |
| 06 | P06-T01 input snapshot (EDU-0059); A67-F02 nested/scalar guards/tests in EDU-0068 | Independent fix review; P06-T02..T10 feasibility/constraints/CP-SAT/worker/validation/UI/benchmarks |
| 07 | P07-T01 source research (EDU-0060) | SME confirmation and P07-T02..T09 assessment engine, gradebook, workflows and tests |
| 08 | P08-T01 legal source registry (EDU-0061) | Source integration approval and P08-T02..T09 collection/archive/extraction/search/provenance |
| 09 | P09-T01 chart-input domain (EDU-0062); A67-F03 guards/tests in EDU-0068 | Independent fix review; P09-T02..T09 scoped aggregation, privacy thresholds, chart UI/export/test/benchmark |
| 10 | P10-T01 prediction target contract (EDU-0063) | Human target approval and P10-T02..T09 features/data/evaluation/model/prediction controls |
| 11 | P11-T01 environment contract; T02 CI additions; T03A local request logs (EDU-0064..0066); A67-F01 Uvicorn privacy fix/regression in EDU-0068 | Independent fix review; deployable environment configuration; T03B signals/alerts/worker health; T04..T09 security/load/restore/UAT/release |

All conditional kickoff slices remain in review. Full student management/import,
timetable, gradebook, legal sync, analytics and ML are not end-to-end delivered.
User authorization to continue a phase has not been recorded as formal phase
acceptance. The master and its unresolved OD items remain unchanged.

GitHub checked during EDU-0067: PRs #1–10 are OPEN; none is merged. HEAD and
remote branch both `d488bc055b0609430fe1dbf3177c427650617830`; existing PR #10
checks green. That snapshot predates EDU-0068 Git closeout; check its task journal
and Git for current commit/push/PR evidence. No deployment is claimed.

Next priority: independent review of EDU-0068 and security remediation closure,
Phase 01/02 human decisions, then remaining Phase 03 master-data scope. Preserve
earlier task history when updating. R42-F02/MFA/archive operation remain gated.
