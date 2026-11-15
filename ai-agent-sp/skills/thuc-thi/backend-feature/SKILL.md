---
name: backend-feature
description: Implement a modular FastAPI feature with validated service and repository layers.
---

# backend-feature

**Group:** `thuc-thi`  
**Trigger:** Implement a modular FastAPI feature with validated service and repository layers.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Locate owner module, SRS and API contract; propose endpoints and data changes.
2. Add Pydantic schemas, router, scoped authorization, service and repository responsibilities.
3. Enforce transaction and audit/outbox for critical writes; explicit status codes/errors.
4. Add unit + integration + authz negative tests and generate OpenAPI for frontend.
5. Run tests/linters and log changes without claiming Git operations.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
