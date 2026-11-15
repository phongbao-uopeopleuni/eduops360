---
name: timetable-cpsat
description: Implement CP-SAT timetable constraints with truthful solver status and independent validation.
---

# timetable-cpsat

**Group:** `thuc-thi`  
**Trigger:** Implement CP-SAT timetable constraints with truthful solver status and independent validation.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Snapshot real-time interval inputs: teacher, class/group, room, slots, holidays and approved lessons.
2. Validate feasibility bounds and domain-specific hard constraints before solver.
3. Build CP-SAT model, soft objective and bounded queue jobs, distinguish feasible/optimal/unknown/infeasible.
4. Independently validate every returned schedule for collisions and completeness before draft save.
5. Benchmark datasets and support minimal-change partial repair; publish only through approval.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
