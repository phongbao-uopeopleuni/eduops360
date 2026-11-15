# System overview

Frontend (React/TypeScript) → HTTP/OpenAPI → Backend (FastAPI modular monolith) → PostgreSQL.
Independent worker processes perform CP-SAT timetable solving, ML analysis, legal-document synchronization.
A central auth/RBAC policy, academic year context, error monitoring and audit trail apply across modules.

**Boundary:** `frontend` never directly accesses the database; `backend` never ships secrets to browsers. Each module owns its service API. Cross-module changes require contracts and tests.
