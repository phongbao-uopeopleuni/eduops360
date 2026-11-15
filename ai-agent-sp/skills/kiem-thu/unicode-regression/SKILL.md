---
name: unicode-regression
description: Protect Vietnamese Unicode and file encoding across import/export/API/UI/report flows.
---

# unicode-regression

**Group:** `kiem-thu`  
**Trigger:** Protect Vietnamese Unicode and file encoding across import/export/API/UI/report flows.  
**Prerequisites:** Inspect task `EDU-XXXX`, affected phase and role, real worktree/branch; read `ai-agent-sp/OPERATING_RULES.md` and relevant standards only.

## Inputs
Task objective / SRS IDs; current code or architecture docs; authorized permissions; constraints; current errors and test evidence when available.

## Execution procedure
1. Read ai-agent-sp/standards/UNICODE_UTF8.md and run strict UTF-8 scanner.
2. Test NFC/NFD, ă â ê ô ơ ư đ, BOM/no-BOM CSV, invalid byte, quoted comma and newline.
3. Ensure student code leading zero and ISO dates survive round-trip; do not normalize legal originals.
4. Test CSV formula injection in exports and text-typed XLSX alternative.
5. Capture fixture hashes and pass/fail; block corruption before DB import.

## Required outputs and acceptance
- Identify exact files changed, why each changed, interfaces affected and explicit tests/commands with true results.
- Update `docs/progress/tasks/EDU-XXXX.md` and handoff; regenerate board. Record Git SHA/remote/PR/merge individually, or `not_done`.
- Escalate school-policy approvals, real student data, credentials, destructive operations and production deployment to a human; never silently assume permission.
- Stop on unresolved critical security/assessment/temporal integrity issues; provide a minimal reproducible blocker rather than claiming completion.

## Quality checks
- Apply `docs/quality/RELEASE_GATE.md` at relevant phase and link requirement/test evidence.
- Do not duplicate this workflow into vendor-specific paths. This file in `ai-agent-sp/` is the canonical SOP.
