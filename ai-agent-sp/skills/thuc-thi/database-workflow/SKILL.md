---
name: database-workflow
description: Implement consistent DB model and migration for one owned module.
---

# database-workflow

**Group:** `thuc-thi`  
**Trigger:** Implement consistent DB model and migration for one owned module.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Design FK/index/constraints with school/year scope and archiving implications.
2. Write Alembic migration and data conversion plan; preserve old values and rollback path.
3. Run isolated migration against synthetic current/old-schema data and test idempotence where applicable.
4. Evaluate concurrent writes and query performance; never bypass service layer.
5. Record migration revision/hash, reviewers and operational warnings.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
