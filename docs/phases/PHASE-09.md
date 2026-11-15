# PHASE-09 — Statistical Analytics Studio

**Status:** NOT_STARTED / SPEC_ONLY  
**Implementers:** Data Analytics Agent / Frontend Agent  
**Independent reviewer:** QA / Examination SME  
**Prerequisite:** PHASE-08 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

## A. Purpose and implementation boundaries
Statistical Analytics Studio; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Chart builder`
- `Statistical aggregations`
- `Export charts`
- `Reporting consistency`

## C. Detailed execution steps
1. **P09-T01:** Define chart input schema (x/y/group/filter, academic_year, subject) and reject inappropriate variables.
2. **P09-T02:** Build scoped, parameterized aggregation queries with minimum group size policy for privacy.
3. **P09-T03:** Implement histogram bins and KDE where meaningful; boxplot quartiles and whiskers consistent across reports.
4. **P09-T04:** Build scatter, KDE/hist, box/swarm, heatmap, line/ECDF/violin and accessible legends.
5. **P09-T05:** Create interactive Chart Builder with column selectors, course/class/year filters and missing-value indicators.
6. **P09-T06:** Implement chart export PNG/SVG and CSV/XLSX aggregates with Unicode checks and source provenance.
7. **P09-T07:** Test with known analytical fixtures against Python statistical reference outputs.
8. **P09-T08:** Benchmark large class datasets and cache read-only aggregates safely per year and scope.
9. **P09-T09:** Ensure no charts reveal identifiable student data outside permission scope.

## D. Where files belong
- `backend/app/modules/analytics/`
- `frontend/src/features/analytics/`
- `tests/analytics/`

## E. Verification and exit gate
- [ ] Chart results match independent reference
- [ ] Filtering year/class/subject correct
- [ ] No data leakage via export or chart labels
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
