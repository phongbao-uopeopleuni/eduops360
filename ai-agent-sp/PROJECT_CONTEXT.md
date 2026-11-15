# EduOps 360 — Canonical Project Context v2.1

Goal: secure Vietnam Grades 1–12 academic/examination administration web app with timetable CP-SAT, document provenance, analytics and ML decision support. Stage: Phase 01 local foundation is implemented; Phase 02 local IAM/RBAC/session/audit/Admin package is ready for independent review through EDU-0030. Neither phase is formally accepted. Current evidence: `docs/progress/HANDOFF.md`. Phase 02 remains gated by the unaccepted Phase 01 prerequisite, OD-001/007/008/011, Human Security Owner review, approved role activation, encrypted MFA custody and audit archive operation. Stack: Frontend React + TypeScript (Vite); Backend Python FastAPI; PostgreSQL; OR-Tools workers planned for their owning phases; Docker Linux local environment. Frontend/backend are separate root folders.

Read `docs/requirements/SRS_MASTER.md` for requirement IDs; `docs/phases/README.md` for release sequence; `docs/roles/README.md` for role accountability; `ai-agent-sp/skills/REGISTRY.md` for repeatable procedures. See README for check commands and `docs/progress/` for evidence.

Product design: white-first Scientific Minimalism, minimal science line motifs, high-contrast fonts, light/dark mode, Vietnamese UTF-8. Production student data is NOT available or authorized in this starter. All tasks are planned until verified; no code execution/commit/push/merge success may be inferred from prose.

## Confirmed Product Owner decisions (2026-11-12)
Read `docs/phases/PHASE-00.md` before starting any feature. Single-school MVP (future extensibility); Grade 1–12; **Student + CSV → Timetable → Examination**; 2k–10k students and 20–100 users; minimal academic records; configurable validated schedules; two-step sensitive approvals; local Docker then staging with synthetic data.

Open questions and gating decisions: `docs/phases/PHASE-00.md`. Any proposed defaults are NOT confirmed business requirements. Phase 00 is in review, not accepted; use EDU-0005 for traceability.
