---
name: cross-module-code-review
description: Review changes for ownership violations, duplicated business rules, API mismatch and dependency cycles.
---

# cross-module-code-review

**Group:** `ra-soat`  
**Trigger:** Review changes for ownership violations, duplicated business rules, API mismatch and dependency cycles.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Collect PR diff, SRS, module map, contract diff and task acceptance.
2. Check import boundaries (frontend→API only, backend service→repository) and role checks.
3. Verify new interfaces, migration and generated client, year scoping and error contracts.
4. List findings with severity, file path/line, reproduction and suggested smallest fix.
5. Record reviewed commit and independent sign-off, or mark blocked.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
