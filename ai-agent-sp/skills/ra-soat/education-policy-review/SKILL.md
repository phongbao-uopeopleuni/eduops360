---
name: education-policy-review
description: Verify school assessment or calendar rules against official legal documents with effective dates.
---

# education-policy-review

**Group:** `ra-soat`  
**Trigger:** Verify school assessment or calendar rules against official legal documents with effective dates.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Collect exact document identifiers, sources, effective dates, amendments and transitional provisions.
2. Determine grade, school year, subject, assessment type and scope; preserve ambiguity.
3. Produce policy matrix and concrete test vectors approved by domain SME.
4. No automatic activation or result change based solely on AI extraction.
5. Attach source links, review signature and policy snapshot to task.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
