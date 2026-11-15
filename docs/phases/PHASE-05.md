# PHASE-05 — Calendar, time slots, holidays & temporal integrity

**Status:** NOT_STARTED / SPEC_ONLY  
**Implementers:** Backend Agent / UX Agent  
**Independent reviewer:** Domain SME / QA  
**Prerequisite:** PHASE-04 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

## A. Purpose and implementation boundaries
Calendar, time slots, holidays & temporal integrity; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Add Slot editor`
- `Holiday ranges`
- `Effective school calendar`
- `Temporal tests`

## C. Detailed execution steps
1. **P05-T01:** Model schedule templates per school, year and day-of-week with AM/PM and per-slot start/end.
2. **P05-T02:** Implement Add Slot, Insert Break, edit start/end, reorder, duplicate and weekday override.
3. **P05-T03:** Validate non-null time, zero-duration rejection, actual interval overlap and applicable legal daily limits.
4. **P05-T04:** Model one-day/multi-day/partial-day/recurring holidays and school/multi-class scopes.
5. **P05-T05:** Implement make-up and exceptional teaching day without overwriting default weekly calendar.
6. **P05-T06:** Calculate upcoming affected timetable entries and require preview before holiday activation.
7. **P05-T07:** Add audit, approvals and source legal reference for official holidays.
8. **P05-T08:** Test inclusive ranges, AM/PM partial closures, time-zone conversion, midnight valid vs missing null.
9. **P05-T09:** Expose calendar API consumed by schedule solver; version templates per academic year.

## D. Where files belong
- `backend/app/modules/school_calendar/`
- `frontend/src/features/school-calendar/`
- `tests/e2e/`

## E. Verification and exit gate
- [ ] No schedule in approved closure window
- [ ] Add Slot validation detects overlapping time
- [ ] Year-specific holidays do not leak across years
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
