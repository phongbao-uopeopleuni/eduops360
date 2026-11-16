# PHASE-11 — Operations, security hardening, performance & release

**Status:** P11_T01_T02_IN_REVIEW / PHASE_10_DEBT_OPEN
**Implementers:** DevOps Agent / Security Agent / QA Lead  
**Independent reviewer:** Human Product Owner + Operations Owner  
**Prerequisite:** PHASE-10 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

**Conditional kickoff exception — 2026-11-15:** the user explicitly instructed
the agent to proceed to the next phase. Because Phase 10 is not accepted, this
exception is limited to P11-T01's review-only environment isolation contract and
P11-T02's repository-local CI gate additions. It authorizes no environment
provisioning, credential access, migration against a real system, release or
deployment. P11-T03..T09 remain gated. Evidence: EDU-0064 and EDU-0065.

## A. Purpose and implementation boundaries
Operations, security hardening, performance & release; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `CI/CD release pipeline`
- `Incident runbooks`
- `Restore drill`
- `Staging UAT`

## C. Detailed execution steps
1. **P11-T01:** Build staging and prod isolated environment configs, secrets management, minimal service IAM and TLS. Review-only boundary contract published in EDU-0064; deployable configuration and human approval remain pending.
2. **P11-T02:** Create CI gates: lint/types/tests, migration dry-run, API contract, security scans, UTF-8 and model eval when changed. EDU-0065 adds narrowly scoped repository gates; future ML implementation must provide its test/evaluator before ML code can merge.
3. **P11-T03:** Implement metrics/tracing/logs, redaction, alerts, job queue health and correlation IDs.
4. **P11-T04:** Run RLS/IDOR tests, injection cases, privilege escalation, bulk export abuse and worker DoS simulations.
5. **P11-T05:** Load test agreed datasets/concurrent roles and compare p95 to SRS target; tune DB indexes using EXPLAIN.
6. **P11-T06:** Run backup and restore drill with documented RPO/RTO targets; confirm audit archive separation.
7. **P11-T07:** Conduct human UAT (Admin, Examination Officer, Teacher), record issue fixes and sign-off.
8. **P11-T08:** Document deployment & rollback step-by-step, checksum artifacts, PR approvals, and irreversible actions.
9. **P11-T09:** Only authorized operator releases; record actual commit/push/PR/merge/deploy evidence and follow-up monitoring.

## D. Where files belong
- `infra/`
- `docs/operations/`
- `docs/quality/RELEASE_GATE.md`
- `.github/workflows/`

## E. Verification and exit gate
- [ ] No unresolved P0/P1 and known residual risks accepted
- [ ] Restore verified and monitoring actionable
- [ ] Human sign-off; version deploy/rollback reproducible
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
