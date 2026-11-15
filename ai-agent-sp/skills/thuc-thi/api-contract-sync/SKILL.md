---
name: api-contract-sync
description: Keep FastAPI OpenAPI and generated TypeScript types synchronized.
---

# api-contract-sync

**Group:** `thuc-thi`  
**Trigger:** Keep FastAPI OpenAPI and generated TypeScript types synchronized.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Change authoritative Pydantic schema/router, add contract tests.
2. Generate OpenAPI JSON and TypeScript client by reproducible command.
3. Inspect wire field names, nullable dates, time-zone semantics, list pagination and error codes.
4. Fail CI for uncommitted generated diff or breaking changes without version plan.
5. Link contract change to both frontend/backend task owners and independent reviewer.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
