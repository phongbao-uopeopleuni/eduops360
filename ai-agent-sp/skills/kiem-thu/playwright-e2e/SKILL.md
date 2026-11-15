---
name: playwright-e2e
description: Design and run browser end-to-end testing for authenticated EduOps workflows.
---

# playwright-e2e

**Group:** `kiem-thu`  
**Trigger:** Design and run browser end-to-end testing for authenticated EduOps workflows.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Start isolated local/staging app; use synthetic identities and stable fixtures.
2. Test login, role-scope denial, year switch, CSV import, holiday warnings and timetable edit.
3. Test keyboard navigation, Vietnamese strings, responsive view and light/dark contrast.
4. Capture video/screenshots/traces only with redacted or synthetic data.
5. Report failing locator, browser, trace and reproducible command; never claim UI tested if app not running.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
