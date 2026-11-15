---
name: test-strategy
description: Create a risk-based test matrix for a feature or phase.
---

# test-strategy

**Group:** `kiem-thu`  
**Trigger:** Create a risk-based test matrix for a feature or phase.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Map SRS acceptance to unit/integration/contract/E2E/security/performance tests.
2. Define synthetic fixtures, valid/invalid inputs, authorization and failure boundaries.
3. Write tests of data/time/UTF-8 and idempotency where applicable.
4. Run tests, preserve commands/logs/versions and check determinism.
5. Report coverage gaps and false-pass risks; mark unrun tests explicitly.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
