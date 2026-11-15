# MFA recovery and break-glass runbook

**Status:** DRAFT / NOT APPROVED  
**Phase:** 02 — P02-T09 / EDU-0029  
**Required approvers:** named Human Security Owner + named Product/School Authority  
**Open decisions:** OD-001 (authorities), OD-008 (scope), OD-011 (retention)

This document defines the minimum control process. It does not authorize an
operator, enable a production account, or replace human approval. Real student
data and production credentials are outside the current authorization.

## 1. Preconditions before activation

- Name two independent Recovery Approvers and one Security Incident Owner.
- Record their identities, backup contacts, working hours and escalation path in
  an access-controlled system outside the application repository.
- Configure an approved encrypted secret store; MFA secrets, recovery codes and
  emergency credentials must never be stored in Markdown, tickets, chat or logs.
- Approve identity-proofing factors, maximum recovery duration, notification
  recipients, audit retention and the scope allowed for an emergency account.
- Exercise the procedure with synthetic accounts and preserve the signed result.

Until these preconditions are approved, MFA recovery and break-glass activation
are **blocked**. Login verifies TOTP when an already provisioned account has MFA
enabled, but no self-service enrollment or recovery bypass is authorized.

## 2. Normal MFA recovery

1. The requester opens a recovery case; the case ID becomes the correlation ID.
2. An operator verifies the account is not suspended and records the reason,
   requested scope and expected completion time without copying credentials.
3. Two different Recovery Approvers independently validate identity using the
   approved factors. Knowledge of email, password or student information alone
   is insufficient.
4. The first approver proposes recovery; the second approves. Requester,
   proposer and approver must be different people.
5. Revoke every active session and invalidate unused recovery material before
   issuing a single-use, hashed, time-limited recovery challenge.
6. Require a new MFA enrollment and successful challenge before restoring admin
   access. Do not allow a permanent “MFA disabled” state for admin roles.
7. Notify the account owner and Security Incident Owner through an independent
   channel. Unexpected recovery is treated as an incident.
8. Close the case only after audit/outbox delivery is confirmed and both
   approvers sign the evidence record.

Target controls pending human approval: recovery challenge lifetime at most 15
minutes, one use, five failed attempts, and no extension—issue a new approved
case instead. These values are proposals, not binding OD decisions.

## 3. Break-glass procedure

Break-glass is for an active incident where normal named-admin access cannot
restore a critical service in time. It is not a shortcut for ordinary support.

1. Incident Owner declares severity, affected service and expiry time.
2. Two Recovery Approvers authorize activation and the smallest necessary scope.
3. Activate a dedicated, normally disabled emergency identity. Never share or
   rename a normal admin account for this purpose.
4. Use two-person credential custody and approved MFA. No single custodian may
   possess every factor.
5. Set an automatic expiry and deny self-extension, self-approval, role grants
   outside the incident scope, audit mutation and retention changes.
6. Stream security/audit events to the segregated audit worker and alert the
   Security Incident Owner on login, denial, grant, write and logout.
7. On expiry or containment: revoke sessions, disable the identity, rotate every
   exposed factor and verify the runtime role still cannot alter source audit.
8. Complete a post-incident review within the human-approved interval. Record
   commands, affected records, approvals, evidence hashes and corrective tasks.

## 4. Mandatory abort conditions

Stop and escalate when either approver is unavailable; identity proof conflicts;
scope or expiry is missing; audit/outbox is unavailable; the request asks to
delete evidence; a credential would be copied to chat/repo/logs; or the action
depends on an unresolved OD value with material security impact.

## 5. Evidence checklist

- Case/correlation ID, reason, severity, requested and granted scope.
- Requester, two approvers and operator identities with timestamps.
- Session revocation, activation, expiry and deactivation events.
- Audit/outbox identifiers and segregated-delivery confirmation.
- Credential rotation confirmation without secret values.
- Negative test result for stale session, self-approval, scope escape and audit
  modification.
- Post-incident findings, owners and due dates.

## 6. Current implementation boundary

The local Phase 02 implementation provides hashed server sessions, TOTP login
verification, transactional audit/outbox, stale-grant checks and DB-level audit
immutability. It does **not** yet provide encrypted MFA enrollment, recovery
challenge storage, emergency account activation, notification delivery or named
human custody. Those controls must not be simulated as production-ready.
