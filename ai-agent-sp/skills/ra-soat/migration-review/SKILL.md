---
name: migration-review
description: Review SQLAlchemy/Alembic migrations and rollback for data correctness and deployment safety.
---

# migration-review

**Group:** `ra-soat`  
**Trigger:** Review SQLAlchemy/Alembic migrations and rollback for data correctness and deployment safety.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Map added/altered fields to SRS and existing rows, UUID/FK/tenant scopes.
2. Assess NULL/default/index, unique constraints, historical data and lock time.
3. Run migration on isolated seeded DB and test rollback where reversible.
4. Inspect performance/query plan and concurrent write implications.
5. Block destructive production migration without approval, backup and explicit recovery steps.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
