---
name: regression-debugger
description: Reproduce, isolate and fix a reported bug across UI, API, DB and worker.
---

# regression-debugger

**Group:** `kiem-thu`  
**Trigger:** Reproduce, isolate and fix a reported bug across UI, API, DB and worker.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Capture sanitized report: exact actions, environment/commit, year scope, request_id and expected vs actual.
2. Reproduce using fake data; trace browser console→network→API logs→DB state→worker metrics.
3. Use smallest failing automated test; perform root-cause analysis with competing hypotheses.
4. Fix in owning module, validate security effects, rerun failing test and neighboring regression suite.
5. Write incident/task log with before-after, evidence, residual risk and rollback.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
