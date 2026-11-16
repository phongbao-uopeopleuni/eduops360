# System overview

Frontend (React/TypeScript) → HTTP/OpenAPI → Backend (FastAPI modular monolith) → PostgreSQL.
Independent workers for CP-SAT timetable solving, ML analysis and legal-document
synchronization are planned; none is implemented or deployed in the current repo.
A central auth/RBAC policy, academic year context, error monitoring and audit trail apply across modules.

This is the target architecture. Current local code exposes health and IAM/Admin
APIs; academic-year rules exist only as pure domain values. Audit/outbox and local
HTTP logs exist, but external monitoring, archive delivery and workers remain
gated. Current implementation/review evidence: `docs/progress/PROJECT_STATUS.md`.

**Boundary:** `frontend` never directly accesses the database; `backend` never ships secrets to browsers. Each module owns its service API. Cross-module changes require contracts and tests.
