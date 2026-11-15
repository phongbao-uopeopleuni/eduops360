---
name: incident-triage
description: Triage runtime incidents and preserve traceability of failures.
---

# incident-triage

**Group:** `giam-sat`  
**Trigger:** Triage runtime incidents and preserve traceability of failures.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Classify severity by CIA impact; identify affected year/school/role/time window.
2. Preserve redacted logs/traces/DB snapshots with access controls; correlate request IDs.
3. Contain first (block affected operation, rate-limit, pause worker) under authority; document side effects.
4. Create minimal reproduction and assign owning module, test plan, remediation and rollback.
5. Close only after verification plus incident report with lessons and owner approval.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
