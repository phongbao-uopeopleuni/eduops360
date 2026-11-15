# Phase 11 — Environment isolation contract v1

**Status:** `SELECTED_FOR_REVIEW / NOT APPROVED / NO DEPLOYMENT`

## Purpose and authority boundary

This contract defines the minimum boundary for local, synthetic staging and
production environments before deployable configuration is created. It does not
authorize cloud accounts, domains, credentials, secret-manager entries, TLS
certificates, database migrations, staging access or a production release.

Phase 10 is not accepted and OD-001/003/004/011 remain open. Therefore this is a
review artifact for P11-T01 only; no environment described below currently exists
because of this document.

## Environment matrix

| Boundary | Local development | Synthetic staging | Production |
| --- | --- | --- | --- |
| Data | Synthetic fixtures only | Synthetic identities and fixtures only | Real data only after lawful basis, retention and owner approval |
| Network exposure | Loopback-bound development ports | HTTPS through an approved non-production endpoint | HTTPS through an approved production endpoint after release authorization |
| Control plane | Developer-owned disposable local stack | Separate non-production account/project and operators | Separate production account/project and authorized operators |
| Database/storage | Local disposable services and named volumes | Dedicated staging database, object store, queue and backup target | Dedicated production database, object store, queue, audit archive and backup target |
| Secrets | Local ignored files or approved development store | Staging-only secret store and keys | Production-only secret store and keys |
| Identity | Local development identities | Staging-only human and service identities | Production-only named human and service identities |
| Release source | Local branch for development | Reviewed immutable artifact from protected CI | Same reviewed immutable artifact, checksum verified and explicitly authorized |

No environment may share database credentials, session/signing keys, encryption
keys, object-store credentials, queue credentials, audit-archive credentials,
backup credentials or service identities with another environment. Staging must
not be trusted by production and must not contain copied production records.

## Minimum service IAM contract

| Identity | Minimum purpose | Must not receive |
| --- | --- | --- |
| Edge/TLS gateway | Terminate approved TLS and route to the API/frontend | Database, migration, backup or business-admin rights |
| API runtime | Serve authorized application requests using the runtime DB role | Schema migration, role grant, audit deletion, backup/restore or secret-admin rights |
| Migrator job | Apply one reviewed migration in an authorized release window | Long-lived API access, business-admin identity or audit deletion |
| Audit delivery worker | Deliver append-only evidence to a segregated archive | Business-record mutation or archive deletion/retention override |
| Domain worker | Run one bounded queue workload with module-specific access | Global Admin, unrestricted database or cross-environment access |
| Backup writer | Create encrypted, integrity-checked backups | Restore, application mutation or retention-policy override |
| Restore operator/job | Restore an approved backup into an explicitly named isolated target | Unreviewed production overwrite or cross-environment source selection |
| CI deploy identity | Promote a reviewed immutable artifact to one approved environment | Runtime database credentials, unrestricted secret read or another environment |

Concrete grants, owners, expiry and emergency access remain pending human review.
Service identities are non-human, non-interactive, environment-scoped and
revocable. Production changes require attributable named operator evidence; a
shared Admin identity is not acceptable.

## Secret custody contract

- Never commit secret values, print them in logs/evidence, expose them through
  frontend `VITE_` variables or place them in tickets and task journals.
- Keep an inventory of secret *names, purpose, owner, consumer, environment,
  rotation due date and revocation evidence* without recording values.
- Inject secrets only into the authorized runtime identity and environment.
  Missing or cross-environment references must fail closed.
- Rotation must support overlap only for a reviewed bounded window, revoke the
  old value, verify consumers and preserve sanitized audit evidence.
- CI may request environment-scoped credentials through an approved short-lived
  mechanism; persistent deploy keys and secret-store administrators are not an
  assumed default.
- Custody for MFA, application signing/encryption, audit integrity anchors,
  backup encryption and third-party credentials remains `NOT APPROVED`.

No `.env` value, credential or certificate is created or inspected by P11-T01.

## TLS and endpoint contract

- External staging and production traffic is HTTPS-only. Plain HTTP is limited
  to explicitly isolated local development or private service hops approved by
  the operations/security design.
- Certificate issuance, DNS authority, approved protocol/cipher profile,
  renewal owner and expiry alert are required before an endpoint can open.
- The application must derive secure-cookie and trusted-origin behavior from an
  approved environment profile; staging exceptions must never weaken production.
- Missing/expired/untrusted certificates, unknown hostnames or insecure redirect
  targets fail closed. HSTS activation waits for confirmed production domains
  and rollback review; it is not silently enabled from this contract.
- Health endpoints expose no credentials, personal data or internal exception
  details and do not bypass authentication for privileged diagnostics.

## Required failure behavior

| Failure | Required outcome |
| --- | --- |
| Secret missing, unreadable or from another environment | Service/job does not start or privileged operation is denied |
| Runtime identity attempts migration/role grant/audit deletion | Database authorization denies it and emits sanitized security evidence |
| Audit delivery unavailable during a critical audited write | Critical write follows the approved fail-closed/outbox policy; never invent success |
| TLS or trusted-host validation fails | Request is rejected; no insecure fallback |
| Migration or immutable artifact checksum differs | Promotion stops before traffic changes |
| Backup integrity or restore target is uncertain | Restore stops; production is not overwritten |
| Monitoring/rollback/incident ownership is absent | External release remains blocked |

## Approval gates before deployable configuration

- Phase 10 accepted: `NO`.
- Product Owner, Operations Owner, Security Owner and Git/release maintainer:
  `NOT NAMED / NOT APPROVED`.
- Staging/production host, DNS, network and secret manager: `NOT SELECTED`.
- OD-004 concurrency target and OD-011 retention/RPO/RTO/incident authority:
  `OPEN`.
- Data owner, lawful basis, real-data classification and production access:
  `NOT AUTHORIZED`.
- Backup/restore, observability, security/load tests, UAT and rollback evidence:
  `NOT RUN`.

P11-T02 and later tasks may implement and verify these controls only after their
own prerequisites and authority are recorded. An AI agent cannot approve or
perform a staging/production deployment from this document.

## Review checklist

Independent Security and Operations reviewers must verify environment separation,
least privilege, secret custody, TLS ownership, CI trust, failure behavior and
rollback. Product/Data owners must approve real-data and retention boundaries.
Until then the only rollback for this task is reverting this documentation; no
runtime or infrastructure state exists to roll back.
