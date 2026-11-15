---
name: observability-pipeline
description: Design and validate application logs, tracing, metrics and alert pipeline.
---

# observability-pipeline

**Group:** `giam-sat`  
**Trigger:** Design and validate application logs, tracing, metrics and alert pipeline.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Identify API, worker, DB and external connectors and correlation IDs.
2. Classify audit vs security vs error logs, redact personal data and tokens.
3. Set measurable alert triggers for error rate, queue wait, backups, disk, auth failures.
4. Test event delivery, failure isolation and alert routing with synthetic events.
5. Publish dashboard queries, alert runbook, retention and unknowns.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
