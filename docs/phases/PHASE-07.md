# PHASE-07 — Grade 1–12 examination rules & integrity

**Status:** P07_T01_RESEARCHED_IN_REVIEW / PHASE_06_DEBT_OPEN
**Implementers:** Examination Domain Agent / Backend Agent  
**Independent reviewer:** Domain SME / Security QA  
**Prerequisite:** PHASE-06 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

**Conditional kickoff exception — 2026-11-15:** the user explicitly instructed
the agent to proceed through Phase 07. Because Phase 06 is not accepted, this
exception is limited to P07-T01 manual source identification and applicability
uncertainty. No grading rule is activated. P07-T02..T09, schemas, APIs, UI and
grade mutations remain gated. Evidence: EDU-0060.

## A. Purpose and implementation boundaries
Grade 1–12 examination rules & integrity; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Policy-versioned rules`
- `Gradebook`
- `Approval workflow`
- `Historical correctness`

## C. Detailed execution steps
1. **P07-T01:** Verify official education assessment sources manually for school types/years in Phase 07; record applicability and uncertainty; automated source sync follows in Phase 08. Research brief published in EDU-0060; Domain SME approval pending.
2. **P07-T02:** Model subjects, choice/elective, assessment types, numeric vs remark outcomes for each grade and subject.
3. **P07-T03:** Build effective-dated policy snapshot, require domain expert approval before activation.
4. **P07-T04:** Implement pure functions for numeric rules, explicit rounding rules, completeness checks and edge cases.
5. **P07-T05:** Implement grade-entry API scoped by user/class/subject/term, revision check and transaction.
6. **P07-T06:** Create draft→submitted→reviewed→approved→locked workflow and controlled reopening flow.
7. **P07-T07:** Implement audit for every significant change, old/new, reason, actor, policy version.
8. **P07-T08:** Design student/class/gradebook UIs, import point data with validation and error preview.
9. **P07-T09:** Test primary remarks, compulsory numeric inputs, rounding, missing scores, late edits and policy-year historical reproducibility.

## D. Where files belong
- `backend/app/modules/examinations/`
- `frontend/src/features/examinations/`
- `docs/requirements/`

## E. Verification and exit gate
- [ ] No unsupported general GPA for primary school
- [ ] Locked grades reject unauthorized edit
- [ ] History replays same result under original policy
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
