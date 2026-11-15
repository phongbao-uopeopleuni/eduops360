---
name: backup-restore-drill
description: Verify database/object-store and audit recovery in isolated environment.
---

# backup-restore-drill

**Group:** `trien-khai`  
**Trigger:** Verify database/object-store and audit recovery in isolated environment.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Document RPO/RTO objectives and components to restore, including encryption keys/secrets handling.
2. Create test backup containing only synthetic data and archived document fixtures.
3. Restore to separate isolated database/storage; verify integrity hashes, FK counts and permissions.
4. Test point-in-time/rollback and recovery from failed migration; measure timings.
5. Write signed drill report and unresolved risks; no production restore without approval.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
