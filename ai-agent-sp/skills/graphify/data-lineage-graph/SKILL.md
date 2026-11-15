---
name: data-lineage-graph
description: Document data lineage across CSV, student enrollment, scores, analytics and ML.
---

# data-lineage-graph

**Group:** `graphify`  
**Trigger:** Document data lineage across CSV, student enrollment, scores, analytics and ML.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Identify data producer, schema version, transformation, destination, retention and actor.
2. Draw ER/flowchart for year scoping and policy snapshot dependencies.
3. Highlight where personal data crosses trust boundaries and where normalization occurs.
4. Check that model features have as_of cutoff and no future labels.
5. Publish diagram, table of source fields and validation results.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
