---
name: rollback-and-hotfix
description: Execute an approved hotfix/rollback plan with verified state.
---

# rollback-and-hotfix

**Group:** `trien-khai`  
**Trigger:** Execute an approved hotfix/rollback plan with verified state.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Determine impacted release, root cause, data migration state and security impact.
2. Prepare minimal fix or rollback with test, deploy and monitoring checks.
3. Require approval; avoid force pushes or database deletion outside approved runbook.
4. Document original/final commit, deployment version, schema impact and observed service recovery.
5. Reopen incident if evidence insufficient and add regression test before closure.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
