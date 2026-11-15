# Threat Model + CIA Controls — EduOps 360

## Assets
Student personal data, grades, assessment policies, legal evidence, user permissions, audit trails, backup images, solver and ML outputs.

## Trust boundaries
Browser/edge; edge/API; API/DB; API/queue/worker; legal source connector; object store; CI/CD credentials; monitoring stack.

## Abuse cases and mitigations
| Threat | Prevent | Detect | Test |
|---|---|---|---|
| IDOR across class/school/year | Backend RBAC+ABAC scope; default deny | denied access security logs | API 403 for out-of-scope ID |
| SQL injection in search/import | parameterized queries | failed validation | payload cases on API |
| CSV formula payload on export | neutralize spreadsheet formulas / typed XLSX | export scan | open exported fixture with hostile prefix |
| Unicode spoofing or corrupted CSV | strict decoding, NFC for names, no silent replacement | encoding errors | NFC/NFD, BOM, invalid byte test |
| Score tampering after lock | workflow state+approval+immutable audit | score change reports | 409/403 and prior value preservation |
| Audit deletion by Admin | segregated immutable archive and restricted retention | integrity checks and alerts | attempted archive deletion denied |
| Solver resource DoS | bounded jobs, worker concurrency/time limits | runtime metrics | stress test + cancel timeout |
| Legal sync malicious source content | source allowlist, no instructions from retrieved text, file validation | checksum, provenance and review | prompt-injection fixtures |
| ML leakage of future scores | as_of features and temporal split | data checks and eval logs | regression test for leakage |
| compromised deployment credential | least privilege, rotate keys, protected branch, reviews | CI/CD audit | secret scan; denied permission tests |
| stolen session or CSRF | high-entropy server session hash, Secure/HttpOnly/SameSite cookie, session-bound CSRF hash, revocation | login/logout/denial audit with request ID | missing/wrong CSRF, expiry and DB revocation tests |
| role escalation or stale grant | DB-loaded active grants on every request, scope coverage, delegation subset check | grant/revoke and denial audit | higher-role delegation, IDOR and post-revocation tests |
| MFA recovery social engineering | two independent human approvers, independent identity proof, single-use expiry, owner notification | recovery and session-revocation evidence | synthetic recovery drill; self-approval denied |
| break-glass abuse | normally disabled identity, dual custody, least scope, automatic expiry, no audit mutation | real-time security alert plus post-incident review | synthetic activation/expiry/scope-escape drill |

## CIA and incident response
- Confidentiality: encryption in transit, scoped permissions, no sensitive data in logs, production legal/privacy review.
- Integrity: revisions, FK, transactions, audit/outbox, signature/HMAC anchor outside app account, review official assessments.
- Availability: isolated worker queues, backups with restore drills, monitoring, capacity planning, rate limiting.
- Incident steps: contain -> preserve evidence -> classify severity -> investigate using correlation_id -> fix -> regression tests -> restore -> retrospective. Never delete evidence to hide a bug.

See also `docs/quality/TEST_STRATEGY.md` and relevant skills. OWASP ASVS 5.0 is a baseline, not a certification claim.
