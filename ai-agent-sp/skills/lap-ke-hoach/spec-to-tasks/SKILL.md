---
name: spec-to-tasks
description: Convert an EduOps domain requirement into atomic implementation tasks and acceptance criteria.
---

# spec-to-tasks

**Group:** `lap-ke-hoach`  
**Trigger:** Convert an EduOps domain requirement into atomic implementation tasks and acceptance criteria.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Read SRS ID and corresponding phase, data-flow and domain owner.
2. Map UI→API→service→repository→audit/test dependencies; flag uncertain legal details.
3. Break into tasks no larger than one coherent pull request with unique owner, file scope and test objective.
4. Add inputs/outputs, negative cases, measurable DoD and rollback expectations.
5. Publish plan as task journals; update traceability but do not claim implementation.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
