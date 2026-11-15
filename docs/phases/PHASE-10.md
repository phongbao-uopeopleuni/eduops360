# PHASE-10 — Educational ML lab and careful predictive use

**Status:** NOT_STARTED / SPEC_ONLY  
**Implementers:** ML Agent / Domain SME  
**Independent reviewer:** Independent ML QA / Security  
**Prerequisite:** PHASE-09 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

## A. Purpose and implementation boundaries
Educational ML lab and careful predictive use; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Feature snapshots`
- `Training pipeline`
- `Model card`
- `Human reviewed warnings`

## C. Detailed execution steps
1. **P10-T01:** Choose one measurable target with a pre-declared prediction time and intended use.
2. **P10-T02:** Create `as_of` feature snapshots only from information known at prediction time.
3. **P10-T03:** Define leakage-aware temporal train/validation/test, student grouping and independent cohort holdout.
4. **P10-T04:** Build baseline models (mean/linear/logistic) before RandomForest/XGBoost/NN experimentation.
5. **P10-T05:** Optimize appropriate MAE/RMSE or precision/recall/calibration; no optimistic metrics on training data.
6. **P10-T06:** Test subgroup performance, missingness, model stability, fairness proxies and distribution drift.
7. **P10-T07:** Write model card: intended use, sources, constraints, evaluation, privacy and no-autonomous-decision rule.
8. **P10-T08:** Expose predictions with uncertainty, as-of, model version and human review; no official grading decisions.
9. **P10-T09:** Enable monitoring, manual disable/rollback, retrain only with authorized historical data.

## D. Where files belong
- `backend/app/modules/machine_learning/`
- `backend/app/jobs/ml_jobs.py`
- `docs/ml/`

## E. Verification and exit gate
- [ ] No future labels leak into features
- [ ] Benchmark against baseline and report uncertainty
- [ ] Human decides support actions; no automatic ability labels
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
