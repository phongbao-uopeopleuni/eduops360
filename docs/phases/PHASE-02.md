# PHASE-02 — IAM, security baseline, audit & roles

**Status:** LOCAL_IMPLEMENTATION_IN_REVIEW / HUMAN_AND_POLICY_GATES_OPEN  
**Implementers:** Security Agent / Backend Agent  
**Independent reviewer:** Human Security Owner — not yet named (OD-001)  
**Prerequisite:** PHASE-01 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

The local implementation for P02-T01..T09 and the audit remediation are packaged under EDU-0012..0041. The technical package is `READY_FOR_HUMAN_ACCEPTANCE`, but it is not an accepted phase: Phase 01 still lacks human acceptance, OD-001/007/008/011 remain open, the authoritative role matrix is intentionally not activated, and MFA enrollment/recovery cannot be enabled without approved encrypted custody and named human authorities. Current package: `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`.

## A. Purpose and implementation boundaries

IAM, security baseline, audit & roles; implement only approved scope and use synthetic data. Unresolved OD values are fail-closed, not silently promoted to product decisions.

## B. Expected artifacts

- `Authentication sessions`
- `RBAC/ABAC scopes`
- `Audit outbox`
- `Admin console`

## C. Detailed execution steps

1. **P02-T01:** Define role permissions and resource-scoped policy matrix including archived-year restrictions.
2. **P02-T02:** Implement identity schema, password hashing policy, account invitations, MFA admin, expiry and revocation.
3. **P02-T03:** Implement login/logout/auth check with rate limits and CSRF/cookie hardening.
4. **P02-T04:** Create permission guards in API dependencies plus resource-based decisions; frontend guard only for UX.
5. **P02-T05:** Implement AuditOutbox within the same transaction as high-risk data changes.
6. **P02-T06:** Add segregated log delivery design and ensure business Admin cannot delete source audit records.
7. **P02-T07:** Implement Admin user creation, suspend, grant/revoke permissions and scope, all audited.
8. **P02-T08:** Write negative tests: role escalation, IDOR, non-admin grant, session expiry, revocation and stale cache.
9. **P02-T09:** Document threat model, MFA recovery and break-glass process requiring human approval.

## D. Where files belong

- `backend/app/modules/auth/`
- `backend/app/modules/audit_logs/`
- `frontend/src/features/user-management/`
- `docs/security/`

## E. Verification and exit gate

- [x] Default deny proven by local unit and PostgreSQL API tests.
- [x] Admin grant/revoke audited; runtime and audit worker cannot update/delete/truncate source audit.
- [x] Current Admin API denies missing school/year scope, IDOR, stale grants and role escalation.
- [x] Negative, contract, frontend and live migration tests run with synthetic data and recorded.
- [x] Task journals and evidence updated; `TASK_BOARD.md` regenerated.
- [ ] Phase 01 prerequisite accepted.
- [ ] OD-001/007/008/011 resolved by authorized owners; approved role mappings activated.
- [ ] Encrypted MFA enrollment/recovery custody and notification channel approved and implemented.
- [ ] Segregated archive delivery/retention operation approved under OD-011.
- [ ] Independent Human Security Owner and required authority approve Phase 02.

## F. Failure/rollback plan

On failed validation, do not publish. Preserve sanitized logs, isolate the defective change and use a reviewed forward/backward migration on a disposable copy first. Runtime credentials cannot run Alembic. Irreversible production migration or audit retention actions require authorized review.

## G. Suggested work breakdown / evidence

Use one EDU task per coherent feature, record exact commands/results and distinguish `in_review` from phase `accepted`. Evidence is under `docs/progress/evidence/EDU-0023` through `EDU-0030`.

## H. Local implementation matrix — 2026-11-13

| Planned step | Local implementation / review status |
|---|---|
| P02-T01 | EDU-0012/0026: deny-by-default, DB-loaded time-valid grants, scoped delegation and fail-closed global grant. OD-007/008 remain authoritative blockers; archived-year state belongs to Phase 03. |
| P02-T02 | EDU-0013/0025/0030: identity schema, Argon2id, hashed single-use invitation/reset tokens, expiry, token reuse denial and session revocation. TOTP verification works for provisioned accounts; enrollment/recovery activation remains blocked by custody approval. |
| P02-T03 | EDU-0025: login/me/logout, hashed server sessions, hardened cookies, session-bound CSRF, lockout and bounded rate limiting. |
| P02-T04 | EDU-0026: FastAPI permission dependencies reload grants from PostgreSQL; frontend is UX only. |
| P02-T05 | EDU-0014/0024/0027: audit/outbox is written in the business transaction for security mutations; failure rollback is proven live. |
| P02-T06 | EDU-0024: migrator/runtime/audit-worker DB roles and immutable source-audit boundary are proven. External archive transport and retention activation remain gated by OD-011. |
| P02-T07 | EDU-0027/0030: invite/read/activate/suspend/password-reset/role grant/revoke APIs and typed Vietnamese Admin console, with CSRF, authorization and audit. |
| P02-T08 | EDU-0028/0030: 7 live PostgreSQL integration tests plus unit/E2E coverage for CSRF, expiry, revocation, IDOR, escalation, stale grants, token reuse, audit tampering and rollback. |
| P02-T09 | EDU-0029: threat model and MFA recovery/break-glass runbook drafted; explicitly not approved or activated. |

The previous AI review at `docs/quality/PHASE_02_REVIEW_2026-11-12.md` remains historical evidence of findings before remediation. The current reconciliation is `docs/quality/PHASE_02_TECHNICAL_AUDIT_2026-11-13.md`; neither document replaces human acceptance.

## I. Audit remediation and fresh verification — 2026-11-14

- EDU-0031 independently found A0102-F01..F22. EDU-0032 fixed F01..F08; EDU-0034 independently re-reviewed that remediation as `PASS_WITH_NOTES` with no new P1/P2.
- EDU-0035..0039 fixed the technically actionable P3 findings: infrastructure/test isolation, limiter/CORS/idle expiry, TOTP replay, invitation reissue/cancel, visible Admin errors, real backend browser coverage and evidence correction.
- EDU-0040 reran the complete local gate: backend host `77 passed, 18 skipped`, isolated PostgreSQL `95 passed`, frontend `22 passed`, Playwright `8 passed`, migration head `0008`, contracts/build/validators clean.
- F21 audit integrity architecture, MFA secret custody, dependency hashes and all authoritative policy values remain explicit blockers, not silently accepted defaults. See EDU-0041 acceptance package.
