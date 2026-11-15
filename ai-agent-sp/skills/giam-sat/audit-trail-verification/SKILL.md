---
name: audit-trail-verification
description: Verify all high-risk actions produce immutable, attributable audit evidence.
---

# audit-trail-verification

**Group:** `giam-sat`  
**Trigger:** Verify all high-risk actions produce immutable, attributable audit evidence.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. List critical actions: grade edit/approve, policy activation, scope grant, schedule publish, import.
2. Trace transaction, outbox, exporter, immutable archive and independent verification key.
3. Test rollback on audit failure, tamper detection and restricted archive deletion.
4. Check timestamps UTC, actor, resource revision, before/after minimized, reason and correlation ID.
5. Write evidence and exceptions; business Admin must not be able to erase audit.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
