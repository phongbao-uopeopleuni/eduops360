---
name: performance-profiling
description: Measure and diagnose API, SQL, scheduling and analytics performance.
---

# performance-profiling

**Group:** `kiem-thu`  
**Trigger:** Measure and diagnose API, SQL, scheduling and analytics performance.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Choose representative data shape, concurrent load and objective p95 target from SRS.
2. Capture baseline and system conditions: CPU, memory, DB pool and solver worker concurrency.
3. Use EXPLAIN ANALYZE on slow queries; trace request_id and background task wait.
4. Test with and without index/cache, verify correctness and tenant isolation.
5. Report before/after benchmark and revert if benefit not proven.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
