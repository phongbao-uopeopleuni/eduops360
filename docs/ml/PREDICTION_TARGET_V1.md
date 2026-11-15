# Phase 10 — Prediction target contract v1

**Status:** `SELECTED_FOR_REVIEW / NOT APPROVED / NO MODEL`

## Target statement

At **14 calendar days before the approved grade-submission deadline**, predict
whether one `student × subject × academic term` record will still have at least
one policy-required assessment missing when the deadline is reached.

This is an operational completeness warning, not a prediction of ability,
future grade, conduct, promotion, graduation or teacher performance.

## Entity, time and label contract

| Field | Contract v1 |
| --- | --- |
| Entity grain | `school_id + academic_year_id + term_id + student_id + subject_id` |
| Prediction time (`as_of`) | Exactly 14 calendar days before the approved submission deadline, interpreted in the configured school timezone and stored as UTC |
| Positive label | At the deadline, at least one assessment required by the approved policy snapshot is absent or not in the accepted submission state |
| Negative label | At the deadline, all assessments required by the approved policy snapshot are present in the accepted submission state |
| Unsupported | No approved policy snapshot, no approved deadline, ambiguous enrollment/subject scope, or unresolved correction/reopen workflow |
| Label availability | Only after the deadline and workflow state are finalized; extraction lag remains an explicit P10-T02/P10-T03 decision |
| Prediction output | Review-queue candidate with model/version/as-of/uncertainty in later phases; no autonomous action |

The task does not materialize labels. If any required scope or policy value is
missing, the system must abstain rather than infer a label.

## Intended use

- Decision owner: authorized Examination Officer or delegated school authority.
- User action: review the completeness record, verify data/workflow problems and
  coordinate support or correction through existing approved processes.
- Fallback: the existing manual completeness report/checklist; absence or failure
  of a model must not block grade entry or change official results.
- Human override: mandatory. A prediction is a prompt to inspect evidence only.

## Prohibited use

- No automatic grade, remark, ability label, promotion, discipline or access change.
- No ranking or performance evaluation of students, teachers, classes or schools.
- No notification to students/guardians without an approved human workflow.
- No use of outcome information or events occurring after `as_of` as features.
- No real student data in development, Git, tickets, fixtures or model artifacts.
- No use of name, student code, contact details or free text as model signals.

## Stakeholder loss and mistake boundary

| Error | Cost / required handling |
| --- | --- |
| False positive | Unnecessary staff review and possible stigma; prediction must remain private, explainable and easy to dismiss |
| False negative | A missing assessment may not be surfaced early; manual completeness process remains mandatory |
| Abstention | Preferred over prediction when policy/deadline/scope/feature freshness is invalid |
| System failure | Fall back to manual report; never synthesize a score or silently mark complete |

Numeric metric thresholds and mistake budgets are **not approved in P10-T01**.
P10-T05 must predeclare precision/recall/calibration gates based on measured class
balance and stakeholder review before any model promotion.

## Leakage boundary for P10-T02

Features may be considered only if their event timestamp is at or before `as_of`
and the value was actually available to the authorized workflow then. Explicitly
forbidden examples include final deadline status, later score entries/corrections,
future attendance, future messages, post-deadline approval and any feature derived
from the label. Point-in-time join rules and feature catalog do not exist yet.

## Required slices and safeguards for later review

- Academic year, term, grade level and subject; school scope must never mix.
- Missingness/abstention rate and label delay by slice.
- False-positive/false-negative review for small or sparse cohorts.
- Fairness/proxy review before considering demographic variables.
- Dataset/model version, code SHA, snapshot ID and reproducible temporal split.

## Gates before P10-T02 or model work

- Phase 09 accepted: `NO`.
- Phase 07 assessment policy snapshot approved: `NO`.
- Submission deadline authority and workflow approved: `NO`.
- Lawful basis, retention and ML data owner approved: `NO`.
- Domain SME/Product/Security approval of this target: `PENDING`.
- Real or production dataset access: `NOT AUTHORIZED`.

Therefore v1 is a reviewable prediction contract only. It authorizes no feature
snapshot, training, evaluation, serving, monitoring or production decision.
