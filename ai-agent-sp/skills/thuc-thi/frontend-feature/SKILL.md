---
name: frontend-feature
description: Implement an isolated accessible frontend feature with typed API and role-aware UI.
---

# frontend-feature

**Group:** `thuc-thi`  
**Trigger:** Implement an isolated accessible frontend feature with typed API and role-aware UI.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Read owning feature route/page/hook and SRS; inspect generated OpenAPI client.
2. Build page and local components, use shared primitives, no direct SQL or secrets in browser.
3. Implement loading, empty, error, permission denied and conflict states; use light/dark tokens.
4. Add unit and E2E tests incl Vietnamese/keyboard and API contract cases.
5. Run TS typecheck/lint/tests, review diff and update task evidence.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
