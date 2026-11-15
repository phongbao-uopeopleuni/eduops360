# Independent review — EDU-0032 remediation

**Reviewer:** Codex, independent of the Claude implementation in EDU-0032  
**Date:** 2026-11-14  
**Conclusion:** `PASS_WITH_NOTES`  
**Authority:** technical review only; this is not Phase 01/02 acceptance and does not approve any open OD.

## Scope

This review checked the A0102-F01..F08 remediation recorded in EDU-0032. Product source was not changed during the review. The reviewer read `changes.diff`, traced the affected authorization/session/audit paths, ran the full backend suite against an isolated PostgreSQL 18 database, and reran copies of the EDU-0031 probes with expectations updated for the remediated behavior.

## Result by finding

| Finding | Result | Independent evidence |
|---|---|---|
| A0102-F01 | PASS | Reset and status change by an actor that does not cover the target's permissions return 403. Coverage includes every active, unrevoked, unexpired target grant, including a grant whose start time is in the future. |
| A0102-F02 | PASS | Eight failed logins with a 612-character User-Agent return 401, leave the account locked at five attempts, and write eight bounded audit records. Every application audit path goes through the shared 500-character bound. |
| A0102-F03 | PASS_WITH_NOTE | `pending → active` returns 409 and the invitation remains usable. The Admin still receives the bearer invitation token for delivery; misuse of that token is the already-disclosed Security Owner decision, not a bypass of the fixed status transition. |
| A0102-F04 | PASS | Concurrent consumer B waits for A and then receives `ACCOUNT_TOKEN_INVALID`; sequential reuse is also denied. `populate_existing=True` refreshes the locked identity-map row. |
| A0102-F05 | PASS | Five failed attempts lock the account but an existing session still receives 200; a new login is denied. Suspended users remain denied and suspension revokes sessions. |
| A0102-F06 | PASS | Self-grant is denied; omitted validity is capped to the delegator; validity beyond that cap is denied; expiry/reload prevents later delegation. The per-permission latest-expiry calculation prevents an A→B→A cycle from extending authority, and revocation/expiry is observed on the next request because grants are loaded from the database each time. |
| A0102-F07 | PASS | Argon2 runs in bounded worker threads. Ten concurrent failed logins kept liveness latency at 11.2 ms maximum in this run. AnyIO's capacity limiter is scoped per event loop; cancellation cannot leak a token because the non-abandoned worker completes before release. The temporary concurrency value still requires OD-004 confirmation. |
| A0102-F08 | PASS_WITH_NOTE | Live PostgreSQL regressions now cover F01–F06 and router lockout; obsolete helper tests/code were removed. The real backend + PostgreSQL browser path was explicitly left open in EDU-0032 and remains required in the next lifecycle/E2E task. |

No new P1 or P2 finding was found. Therefore the reviewer does not create a remediation blocker for another actor.

## Cross-cutting checks

- All direct `Session.user_agent` writes and every audit call are bounded by the session constructor helper or `write_audit_in_transaction()`.
- Invitation and password-reset acceptance audit records preserve the authenticated issuing actor in `extra_data.issued_by`; the token holder is still recorded as the action actor.
- Unknown permission values fail closed in delegation checks.
- The runtime role cannot read `alembic_version`; migration is at `0007_account_tokens (head)` and `alembic check` reports no new operations.
- The 100-file product/config snapshot taken before review remained byte-identical after review.

## Verification

| Check | Result |
|---|---|
| Backend host suite | 74 passed, 14 skipped |
| Backend PostgreSQL suite | 88 passed |
| Ruff | all checks passed |
| OpenAPI drift | contract matches FastAPI |
| Frontend typecheck/lint/format/API check | passed |
| Frontend unit | 20 passed |
| Governance | blueprint/structure/encoding/student sample/root unittest passed |
| PostgreSQL probe | F01–F07 remediated behavior reproduced |

Detailed outputs are under `docs/progress/evidence/EDU-0034/`.

## Notes carried forward

The review also reproduced the expected open P3 state: the in-memory limiter can evict a blocked key; wildcard CORS with credentials is accepted; an expired invitation cannot be reissued; the migrator is a database superuser; and a real backend browser test is missing. These are not regressions in EDU-0032 and are handled by later tasks. OD-001/003/007/008/011, MFA custody, archive/retention, and all temporary policy values remain unapproved.

