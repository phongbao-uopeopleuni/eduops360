# PHASE-03 — Academic year, master data & school hierarchy

**Status:** P03_T01_IMPLEMENTED_IN_REVIEW / PHASE_02_DEBT_OPEN  
**Implementers:** Backend Domain Agent / Database Agent  
**Independent reviewer:** Domain SME / QA  
**Prerequisite:** PHASE-02 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

**Conditional kickoff exception — 2026-11-15:** the user explicitly instructed the agent to continue Phase 03 while carrying the unfinished Phase 02 gates as technical debt. This does **not** mark Phase 02 accepted, approve any OD/R42/MFA/archive policy, or authorize production. The exception is limited to P03-T01 pure-domain constraints; migrations, APIs, UI and P03-T02..T09 remain gated and unstarted. Evidence: EDU-0054.

## A. Purpose and implementation boundaries
Academic year, master data & school hierarchy; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Academic year and term state machines`
- `Student identity`
- `Classes/teachers/subjects`
- `Years-scoped view`

## C. Detailed execution steps
1. **P03-T01:** Define school, academic-year and term constraints and allowed state transitions. Implemented in EDU-0054; independent review pending.
2. **P03-T02:** Create identity and enrollment schemas with immutable history, unique code per school, cross-school FK checks.
3. **P03-T03:** Migrate tables with Alembic and build scoped index strategy from real query patterns.
4. **P03-T04:** Implement API for year activation/archival, class/teacher/subject catalogs and student enrollments.
5. **P03-T05:** Use year ID from authorized request context, not browser clock; preserve tab-local selected year.
6. **P03-T06:** Add default year selection logic, archived read-only banner and time zone settings.
7. **P03-T07:** Test overlapping/invalid year windows, inactive year edit, teacher/class mismatches and race updates.
8. **P03-T08:** Seed synthetic 2,000-student dataset across Grades 1–12; no real personal data.
9. **P03-T09:** Expose E2E journeys for switching academic years without cross-year leakage.

## D. Where files belong
- `backend/app/modules/academic_years/`
- `backend/app/modules/students/`
- `frontend/src/features/academic-years/`

## E. Verification and exit gate
- [ ] Unique school-year and enrollment rules enforced
- [ ] Archived history preserved
- [ ] Year switch consistently scopes all APIs
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.

## H. P03-T01 conditional kickoff evidence — 2026-11-15

EDU-0054 adds pure-domain validation only under the user's explicit Phase 02 debt exception: strict date windows, term containment, `DRAFT → ACTIVE → ARCHIVED` transitions, one-active-year precondition, archived read-only protection, exact school/year scope, optimistic revision conflict and explicit IANA timezone validation. Fail-first collection exited `2` before the module existed; the final targeted suite passed `15` tests and the host backend suite passed `93` with `20` PostgreSQL tests skipped because no isolated test DSNs were configured.

No SQLAlchemy model, migration, repository, API, OpenAPI change, frontend, seed or database write is part of P03-T01. Database enforcement and concurrency proof remain for separately reviewed P03-T03 work. EDU-0054 is `in_review`; it does not approve Phase 02 debt or authorize P03-T02..T09 automatically.
