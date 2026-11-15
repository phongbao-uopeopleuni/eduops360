---
name: csv-import-pipeline
description: Implement a safe and idempotent student CSV import workflow.
---

# csv-import-pipeline

**Group:** `thuc-thi`  
**Trigger:** Implement a safe and idempotent student CSV import workflow.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Start with reviewed versioned template and preflight permissions.
2. Decode strict UTF-8/BOM, validate CSV schema/row length/NFC/date/student-code/text.
3. Stage rows; compare school+student identity+year/class; produce explicit conflict preview.
4. Confirm create/update mode, commit in transaction and audit batch with counts/checksums.
5. Test duplicate replay, invalid bytes, huge file limits, 0-leading IDs and rejected formula exports.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
