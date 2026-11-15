# PHASE-06 — Automatic scheduling with CP-SAT and local repair

**Status:** NOT_STARTED / SPEC_ONLY  
**Implementers:** Solver Agent / Backend Agent  
**Independent reviewer:** Domain SME / Performance QA  
**Prerequisite:** PHASE-05 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

## A. Purpose and implementation boundaries
Automatic scheduling with CP-SAT and local repair; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Solver input snapshot`
- `Constraint model`
- `Job queue`
- `Manual changes and publication`

## C. Detailed execution steps
1. **P06-T01:** Define immutable scheduling input snapshot: teaching assignments, classrooms, class/group loads, slots, holidays.
2. **P06-T02:** Pre-validate feasibility lower bounds for teacher/room/available slots, detect inconsistent assignments.
3. **P06-T03:** Model hard constraints for teacher/class/group/room date+time overlap, room capacity, required weekly lessons and closed times.
4. **P06-T04:** Model soft objectives for teacher gaps, daily balance, double periods and minimum changes on repair.
5. **P06-T05:** Implement OR-Tools CP-SAT with bounded runtime, solver status, objective value and deterministic seed where feasible.
6. **P06-T06:** Add heuristic warm start only if benchmark proves benefit; never treat hint as proof of solution.
7. **P06-T07:** Run solver via queued worker with cancellation/job status, bounded concurrency and CPU controls.
8. **P06-T08:** Implement independent post-solve validator before draft storage; report infeasible and unknown separately.
9. **P06-T09:** Create interactive grid, drag/drop edit, immediate conflict check, draft/version approve publish and local repair.
10. **P06-T10:** Benchmark 5/20/50/80-class synthetic datasets and record feasibility, runtime, changes and conflicts.

## D. Where files belong
- `backend/app/modules/timetables/`
- `backend/app/jobs/timetable_jobs.py`
- `frontend/src/features/timetables/`

## E. Verification and exit gate
- [ ] No hard violations in any accepted solution
- [ ] Timeout not mislabeled infeasible
- [ ] Published schedule immutable and prior version recoverable
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
