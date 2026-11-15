# Canonical Skill Registry — 7 groups

All 27 new canonical v2.0 skills live ONLY under `ai-agent-sp/skills/<group>/<slug>/SKILL.md`. Do not maintain duplicated SOP per vendor. A tool may need explicit instructions or an adapter to load from this nonstandard location; automatic native discovery is **not guaranteed**. Root AGENTS.md and CLAUDE.md reference the same canonical location.

| Group | Skill | When to apply |
| --- | --- | --- |
| lap-ke-hoach | `spec-to-tasks` | Convert an EduOps domain requirement into atomic implementation tasks and acceptance criteria. |
| lap-ke-hoach | `architecture-decision` | Record an architecture decision when choosing a framework, schema boundary, solver approach or cross-module contract. |
| lap-ke-hoach | `handoff-planning` | Prepare a precise next-agent handoff for partially finished work or blocked tasks. |
| ra-soat | `cross-module-code-review` | Review changes for ownership violations, duplicated business rules, API mismatch and dependency cycles. |
| ra-soat | `security-cia-review` | Review proposed changes for CIA, authz, audit integrity and privacy risk. |
| ra-soat | `migration-review` | Review SQLAlchemy/Alembic migrations and rollback for data correctness and deployment safety. |
| ra-soat | `education-policy-review` | Verify school assessment or calendar rules against official legal documents with effective dates. |
| kiem-thu | `test-strategy` | Create a risk-based test matrix for a feature or phase. |
| kiem-thu | `regression-debugger` | Reproduce, isolate and fix a reported bug across UI, API, DB and worker. |
| kiem-thu | `playwright-e2e` | Design and run browser end-to-end testing for authenticated EduOps workflows. |
| kiem-thu | `unicode-regression` | Protect Vietnamese Unicode and file encoding across import/export/API/UI/report flows. |
| kiem-thu | `performance-profiling` | Measure and diagnose API, SQL, scheduling and analytics performance. |
| giam-sat | `observability-pipeline` | Design and validate application logs, tracing, metrics and alert pipeline. |
| giam-sat | `audit-trail-verification` | Verify all high-risk actions produce immutable, attributable audit evidence. |
| giam-sat | `incident-triage` | Triage runtime incidents and preserve traceability of failures. |
| graphify | `architecture-graph` | Generate and review architecture/dependency diagrams from documented source of truth. |
| graphify | `data-lineage-graph` | Document data lineage across CSV, student enrollment, scores, analytics and ML. |
| thuc-thi | `frontend-feature` | Implement an isolated accessible frontend feature with typed API and role-aware UI. |
| thuc-thi | `backend-feature` | Implement a modular FastAPI feature with validated service and repository layers. |
| thuc-thi | `csv-import-pipeline` | Implement a safe and idempotent student CSV import workflow. |
| thuc-thi | `timetable-cpsat` | Implement CP-SAT timetable constraints with truthful solver status and independent validation. |
| thuc-thi | `assessment-engine` | Implement versioned education assessment calculations and controlled grade changes. |
| thuc-thi | `database-workflow` | Implement consistent DB model and migration for one owned module. |
| thuc-thi | `api-contract-sync` | Keep FastAPI OpenAPI and generated TypeScript types synchronized. |
| trien-khai | `release-gate` | Prepare an audited and approved production deployment package. |
| trien-khai | `backup-restore-drill` | Verify database/object-store and audit recovery in isolated environment. |
| trien-khai | `rollback-and-hotfix` | Execute an approved hotfix/rollback plan with verified state. |

## Selecting one or more skills
- Start with `lap-ke-hoach/spec-to-tasks` for new requirements.
- Use `thuc-thi/<feature>` for implementation; combine `kiem-thu/` and `ra-soat/` before review.
- Use `giam-sat` when investigating live errors, `graphify` for architecture/data lineage, `trien-khai` only with explicit deployment authority.
- Keep `SKILL.md` focused on a workflow, not a personality. Tools and model names may change; this registry remains the source of truth.

## Based on uploaded `skills-main.zip`
This repository reviewed Anthropic example skill categories `skill-creator`, `webapp-testing`, `frontend-design`, `doc-coauthoring`, `mcp-builder`, `xlsx`. No upstream source code, scripts, or fonts were copied into this starter; the original package is a reference only. License terms must be checked before integrating any upstream asset later.
