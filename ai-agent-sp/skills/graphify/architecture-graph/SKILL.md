---
name: architecture-graph
description: Generate and review architecture/dependency diagrams from documented source of truth.
---

# architecture-graph

**Group:** `graphify`  
**Trigger:** Generate and review architecture/dependency diagrams from documented source of truth.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Read architecture and owner map; list nodes/edges and trust boundaries.
2. Draw Mermaid flowchart with UI→API→domain→DB, queue/worker, audit and security flow.
3. Validate diagrams match real code and ADRs; label assumptions and unbuilt components.
4. Save source `.mmd` or Markdown Mermaid; no decorative false runtime metrics.
5. Link diagram to phase and updated change journal.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
