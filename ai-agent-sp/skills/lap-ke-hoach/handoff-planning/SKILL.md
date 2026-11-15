---
name: handoff-planning
description: Prepare a precise next-agent handoff for partially finished work or blocked tasks.
---

# handoff-planning

**Group:** `lap-ke-hoach`  
**Trigger:** Prepare a precise next-agent handoff for partially finished work or blocked tasks.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Inspect task journal, git diff/status, CI results, actual files and open issues.
2. Differentiate done, untested, blocked, proposed, and unverified Git states.
3. List most important next 3 actions with exact paths and reproduction commands.
4. Include reviewer requirements and known failure conditions.
5. Update docs/progress/HANDOFF.md and task journal; do not invent remote status.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
