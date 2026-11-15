# Bug debugging playbook — from symptom to verified fix

**Goal:** never stop at a cosmetic UI patch when the root cause is a backend/date/DB bug.

## Standard procedure
1. Receive incident and label `P0/P1/P2/P3`; determine which school, year and role are affected.
2. Freeze relevant release metadata: commit SHA, branch, API/DB migration version, timestamp with time zone.
3. Reproduce using sanitized synthetic fixture. Capture expected/actual behavior and exact request_id.
4. Use **frontend** browser console + network panel for payload/status/caching/context.
5. Use **backend** router/service logs, tracing and permission decision. Avoid raw PII in evidence.
6. Use **database** EXPLAIN, row revision, unique constraints and FKs. Never edit production data as a debugging shortcut.
7. Check **workers/queue** for timeouts, retries, duplicate jobs and solver/model version.
8. Identify minimal root cause; write failing test that reproduces failure before fix where practicable.
9. Fix in owning module, not by duplicating logic elsewhere; verify authorization and regressions.
10. Run tests on expected matrix, compare artifacts/outputs, log fix evidence and rollback plan.
11. Independent reviewer validates risk; merge/deploy only with authority and verified Git record.
12. Close incident with root-cause classification, prevention and linked tests.

## High-risk scenarios
| Symptom | First suspects | Required verification |
|---|---|---|
| Time shows `00:00` unexpectedly | nullable→zero coercion; JS Date parsing; session timezone | raw DB type, API payload, UI format utility, valid midnight case |
| Wrong academic year data | stale global state, omitted API year scope, cache key bug | authorized year_id, API SQL scope, two-tab switching |
| Excel Vietnamese mojibake | UTF-8/BOM confusion, legacy encoding guess, missing font | input bytes, strict decode, NFC, rendered font coverage |
| Two overlapping lessons | time interval logic, teacher/group scope, unchecked manual save | intersecting time ranges across all resources, published/draft policy |
| Student code lost leading zero | CSV read as numeric, Excel autocast | textual column in template, canonical DB TEXT, export roundtrip |
| Grade edit history missing | transaction split from audit, retry, faulty worker | transactional outbox and immutable archive proof |
| Solver reports no schedule | timeout mislabeled impossible; bad assignments or capacity | CP-SAT status and feasibility precheck, independent validator |
| Unexplained ML prediction jump | future-label leakage, model drift, changed joins | feature as_of and temporal split, model/version metrics |
