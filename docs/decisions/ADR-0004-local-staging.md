# ADR-0004 — Local Docker before synthetic staging

**Date:** 2026-11-12  
**Status:** Accepted as product requirement

## Decision
- Begin with frontend/backend/PostgreSQL/worker services under reproducible local Docker Compose.
- Second environment: staging with **synthetic** school and student fixtures only, separate credentials/databases/storage.
- Enforce configuration through secrets management or local untracked `.env`, not `VITE_` variables or checked-in credentials.
- No internet-facing real-person-data system until threat modeling, independent security review, backup restore testing, legal/privacy and explicit release approval.

## Verification
Service health checks, API smoke test, database migration, CI scans and recovery exercise before external staging.
