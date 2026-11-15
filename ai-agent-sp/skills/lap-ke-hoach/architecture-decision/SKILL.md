---
name: architecture-decision
description: Record an architecture decision when choosing a framework, schema boundary, solver approach or cross-module contract.
---

# architecture-decision

**Group:** `lap-ke-hoach`  
**Trigger:** Record an architecture decision when choosing a framework, schema boundary, solver approach or cross-module contract.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. State context, alternatives, tradeoffs, security/performance effect and non-goals.
2. Identify module ownership and affected agents; compare operational costs and rollback.
3. Draft ADR with decision status proposed/accepted and review authority.
4. Link ADR to affected phases/tasks and API contracts.
5. Do not change live code until decision is accepted and change task assigned.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
