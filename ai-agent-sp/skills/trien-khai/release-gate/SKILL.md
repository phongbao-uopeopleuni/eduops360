---
name: release-gate
description: Prepare an audited and approved production deployment package.
---

# release-gate

**Group:** `trien-khai`  
**Trigger:** Prepare an audited and approved production deployment package.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Identify release commit, SRS coverage, open incidents, CI evidence and migration plan.
2. Validate secrets, MFA, backup, rollback, audit archive and monitoring alerts in staging.
3. Require human operations/security/business approvals and schedule downtime if applicable.
4. Record exact release commands/versions/health checks and rollback trigger; do not deploy without authorization.
5. Update task+release records only after confirmed outcomes.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
