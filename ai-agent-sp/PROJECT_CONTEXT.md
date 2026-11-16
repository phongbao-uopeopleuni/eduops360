# EduOps 360 — Canonical Project Context v2.1

Latest correction, EDU-0068 (2026-11-16): A67-F01/F02/F03 and UI49-F01 now have
code fixes and regression evidence, pending independent review. Full disposable
PostgreSQL suite 152 passed, frontend 24, targeted browser 1 and root 28. The
EDU-0067 paragraph below records the preceding audit, not unresolved code fixes.
Historical evidence storage is indexed by the sanitized 44-log EDU-0068 manifest;
raw logs are intentionally local/ignored. Current Git details are in EDU-0068.

Goal: secure Vietnam Grades 1–12 academic/examination administration web app with timetable CP-SAT, document provenance, analytics and ML decision support. Stage verified 2026-11-16 (EDU-0067): Phase 01/02 local foundation and IAM exist with residual review/policy debt; Phase 03–10 have only narrow conditional first-task slices, and Phase 11 has environment/CI/local logging slices. None of the 12 phases is formally accepted. Current evidence: `docs/progress/PROJECT_STATUS.md`, `docs/progress/HANDOFF.md` and `docs/quality/RESIDUAL_BUG_AUDIT_2026-11-16.md`. New residual issues include default Uvicorn log disclosure and latent domain-constructor validation gaps. Phase 02 still needs EDU-0046/0048 independent re-review, approved role activation, encrypted MFA custody, audit archive operation and human acceptance. Stack: Frontend React + TypeScript (Vite); Backend Python FastAPI; PostgreSQL; OR-Tools workers remain planned. Frontend/backend are separate root folders.

Read `docs/requirements/SRS_MASTER.md` for requirement IDs; `docs/phases/README.md` for release sequence; `docs/roles/README.md` for role accountability; `ai-agent-sp/skills/REGISTRY.md` for repeatable procedures. See README for check commands and `docs/progress/` for evidence.

Product design: white-first Scientific Minimalism, minimal science line motifs, high-contrast fonts, light/dark mode, Vietnamese UTF-8. Production student data is NOT available or authorized in this starter. All tasks are planned until verified; no code execution/commit/push/merge success may be inferred from prose.

## Confirmed Product Owner decisions (2026-11-12)
Read `docs/phases/PHASE-00.md` before starting any feature. Single-school MVP (future extensibility); Grade 1–12; **Student + CSV → Timetable → Examination**; 2k–10k students and 20–100 users; minimal academic records; configurable validated schedules; two-step sensitive approvals; local Docker then staging with synthetic data.

Open questions and gating decisions: `docs/phases/PHASE-00.md`. Any proposed defaults are NOT confirmed business requirements. Phase 00 is in review, not accepted; use EDU-0005 for traceability.
