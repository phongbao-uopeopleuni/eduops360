# Current handoff — Phase 01/02 human acceptance

## Latest remediation — EDU-0068, 2026-11-16

- User priority is bug/documentation closeout. A67-F01/F02/F03 and UI49-F01 have
  implementations and regressions; **in review**, no independent closure claimed.
  Runtime Uvicorn access/exception logs are protected, domain constructors reject
  mutable/untyped values, and brand/text links have 44px minimum hit targets.
- Implementation commit `bdcf508`; PR #11 merged under explicit user instruction
  into the PR #10 head branch as `1307b42`. It is **not in main**; upstream PRs
  #1–10 remain open and main requires independent approval. No self-approval,
  branch-protection bypass, phase acceptance or deployment occurred.
- Fail-first backend: 12 failed / 19 passed. Final: backend host 132/20 skipped;
  isolated disposable PostgreSQL full suite **152 passed / no skips**; frontend
  24 unit, targeted browser 1, root 28. Contracts/static/security gates pass.
- README migration role, fonts, architecture worker status, traceability and
  next-agent guidance are corrected. EDU-0067 docs/probe are included in the Git
  closeout. All 44 historical raw logs remain local/ignored; EDU-0068 manifest
  retains hashes and numeric outcomes only, not an unsafe raw-log upload.
- No new feature, schema, dependency or production deployment. See EDU-0068
  for actual commit/push/PR evidence. Independent EDU-0046/0048 review, R42-F02
  decision, MFA custody, operational audit archive and human acceptance remain.

## Latest audit and completion refresh — EDU-0067, 2026-11-16

- Current progress is in `PROJECT_STATUS.md`: **0/12 phases formally accepted**;
  Phase 03–10 first-task slices are not complete feature modules. Existing PRs
  #1–10 remain OPEN. Earlier rows below are historical, including pre-Git claims
  and superseded kickoff restrictions; read their dates and later exceptions.
- Residual report: `docs/quality/RESIDUAL_BUG_AUDIT_2026-11-16.md`.
  **A67-F01 P2 OPEN:** Uvicorn default access/error logs still expose raw query
  and exception detail despite sanitized `eduops.http` events. **A67-F02/F03 P3
  OPEN:** latent immutability/year/filter constructor validation gaps, no current
  API/solver/query consumers. Synthetic real-Uvicorn probe reproduces all cases.
- Fresh baseline: backend 115 passed / 20 PostgreSQL skipped, frontend 24 passed,
  root 28 passed; lint/types/OpenAPI/security scanner/runtime dependency audit and
  governance checks pass. Existing PR #10 CI green for d488bc0; this audit's
  document/probe edits are local, no new hosted run claimed.
- R42-F02, UI49-F01, independent EDU-0046/0048 closure, MFA/archive operation and
  human acceptance remain open. No code correction or self-approval in this audit.
- Next: fix runtime log disclosure, complete eligible independent review/policy
  decisions, then resume remaining master-data tasks under the documented gates.

**Status:** `P11-T01/T02/T03A ENVIRONMENT + CI + LOCAL OBSERVABILITY / IN_REVIEW UNDER CONDITIONAL KICKOFF; PHASE 10 AND EARLIER DEBT STILL OPEN`.

Start at EDU-0066, then EDU-0065..0060 and earlier stacked tasks. The user explicitly requested processing the remaining tasks. P11-T03A is limited to local privacy-preserving HTTP request logging because Phase 10 remains unaccepted. Do not provision observability infrastructure, access credentials, run migrations against a real system, deploy or begin P11-T03B..T09 automatically.

## Conditional P11-T03A kickoff EDU-0066 — 2026-11-16

- Added a server-generated request correlation ID to one sanitized HTTP completion event: method, matched route template, status and duration only. Query, body, headers/cookies, tokens, student data, IP/user-agent and exception detail are excluded.
- Existing transactional audit log remains separate and fail-closed; operational logging failure cannot alter an HTTP response.
- Published the boundary for metrics/tracing exporters, alerts, queue/worker health, backup/disk/archive monitoring and signal thresholds as `NOT IMPLEMENTED`/`NOT APPROVED` pending named owners and infrastructure.
- No metrics or trace exporter, dashboard, alert channel, worker/queue, storage, credential, environment, migration, release or deployment was created. EDU-0066 is stacked on PR #9 and remains `in_review`.

## Conditional P11-T02 kickoff EDU-0065 — 2026-11-16

- Existing CI already runs backend/frontend lint, types, unit/E2E, OpenAPI, UTF-8 and Compose `alembic check`; EDU-0065 adds a sanitized tracked-secret scan, frontend runtime dependency audit and offline `alembic upgrade --sql head` dry-run.
- Added a path-scoped ML evaluation workflow. It does not run for today’s documentation-only ML contract; when future ML source/test/evaluator changes, it fails closed unless `backend/tests/machine_learning/` and `scripts/evaluate_ml_models.py --check` exist and pass.
- No dependency version, secret, cloud credential, infrastructure, database, artifact release or deployment is created. EDU-0065 is stacked on PR #8 and remains `in_review`.

## Conditional P11-T01 kickoff EDU-0064 — 2026-11-15

- Published local/synthetic-staging/production separation rules and prohibited all cross-environment data, credentials, keys, stores and service identities.
- Defined minimum roles for edge, API runtime, migrator, audit/domain workers, backup/restore and CI deployment, with fail-closed secrets/TLS/migration behavior.
- Recorded human gates for ownership, hosts/DNS, secret manager, lawful basis, retention, RPO/RTO, incident response, backup/restore, monitoring, UAT and release.
- No `.env` value, credential, certificate, cloud account, domain, infrastructure config, container, migration, release or deployment was created. EDU-0064 is stacked on PR #7 and remains `in_review`.

## Conditional P10-T01 kickoff EDU-0063 — 2026-11-15

- Selected one measurable operational target: 14 days before an approved grade-submission deadline, estimate whether a student-subject-term record will remain incomplete at the deadline.
- Intended use is a private authorized human review queue with manual completeness fallback. Ability/grade/discipline/teacher evaluation and autonomous action are prohibited.
- Published entity grain, prediction/label time, positive/negative/unsupported states, leakage boundary, mistake costs, abstention and approval gates in `docs/ml/PREDICTION_TARGET_V1.md`.
- No data, label materialization, feature, dataset, model, dependency, notebook, job, endpoint or prediction was created. EDU-0063 is stacked on PR #6 and remains `in_review`.

## Conditional P09-T01 kickoff EDU-0062 — 2026-11-15

- Scope is limited to an immutable chart input with x/y/group/filter roles, required academic-year scope, optional subject scope and a small approved aggregate-variable catalog.
- Direct student identifiers and PII fields are denied; unknown variables fail closed. Role-specific suitability is checked before any query exists.
- Fail-first collection exited `1`; final targeted tests pass `11`; backend host passes `112` with `20` isolated-PostgreSQL tests skipped. Ruff, OpenAPI, root governance and encoding gates pass.
- No database query, aggregation, minimum group-size policy, statistical calculation, chart renderer, export, frontend or cache is part of this slice.
- EDU-0062 is stacked on PR #5 and must remain `in_review`; Phase 08 and earlier debt remain open.

## Conditional P08-T01 kickoff EDU-0061 — 2026-11-15

- Published `LEGAL_SOURCE_REGISTRY_V1.md` for Government legal metadata/signed files, Ministry corroboration and the national legal database.
- Government pages require source attribution. No official public API/rate contract was confirmed; automated rate and concurrency are therefore zero for every source.
- Automated access to `vbpl.vn` returned `403` during preflight and was not bypassed. It remains manual-only until an approved integration exists.
- No connector, credential, job, archive, extraction, search, RAG or policy activation was implemented. EDU-0061 is stacked on PR #4 and remains `in_review`.

## Conditional P07-T01 kickoff EDU-0060 — 2026-11-15

- Official Government metadata confirms `27/2020/TT-BGDĐT` for primary assessment and `22/2021/TT-BGDĐT` for lower/upper secondary assessment.
- `89/2026/TT-BGDĐT`, issued 2026-10-16 and effective 2026-12-01, amends both. At the 2026-11-15 review date it is not yet effective; activation is blocked pending signed-text diff and Domain SME review.
- Published `docs/requirements/ASSESSMENT_POLICY_SOURCE_REVIEW_2026-11-15.md` with applicability boundaries, uncertainties and blank human gates. No calculation, schema, endpoint, UI or grade mutation was added.
- EDU-0060 is stacked on PR #3 and remains `in_review`; Phase 06 and earlier debt remain open.

## Conditional P06-T01 kickoff EDU-0059 — 2026-11-15

- Scope is limited to a self-contained, immutable scheduling-input projection for one school/year: teaching assignments, classrooms, class/group loads, weekly slots and holiday closures.
- Fail-first collection exited `1` before the module existed. Final targeted tests pass `4`; backend host passes `101` with `20` isolated-PostgreSQL tests skipped; Ruff, OpenAPI, root governance and encoding gates pass.
- No feasibility bound, collision constraint, soft objective, OR-Tools dependency, solver status, worker/job, post-solve validator, timetable draft/UI, publication or benchmark is part of this slice.
- EDU-0059 is stacked on EDU-0058/PR #2 so the Phase 05 dependency remains visible. It must remain `in_review` until an independent Domain SME/Performance QA reviewer acts.
- Phase 05 and all earlier debt remain open; P06-T02..T10 stay gated.

## Conditional P05-T01 kickoff EDU-0058 — 2026-11-15

- Scope is limited to immutable pure-domain values for schedule template school/year ownership, locale-neutral weekday, AM/PM session and per-slot start/end `TIME` values.
- Fail-first collection exited `1` before the module existed. Final targeted tests pass `4`; backend host passes `97` with `20` isolated-PostgreSQL tests skipped; Ruff, OpenAPI, root governance and encoding gates pass.
- No overlap/duration/legal-limit rule, holiday, make-up day, persistence, migration, endpoint, OpenAPI, UI, audit write or scheduling solver is part of this slice.
- EDU-0058 is stacked on the open EDU-0057 branch so its review dependency is explicit. It must remain `in_review` until an independent Domain SME/QA reviewer acts.
- Phase 04 and all earlier debt remain open; P05-T02..T09 stay gated.

## Conditional P04-T01 kickoff EDU-0057 — 2026-11-15

- Published the existing synthetic `students_import_template.csv` as CSV v1 without changing its bytes. The Vietnamese guide fixes the eight ASCII headers, field rules and SHA-256 `7cabce06705ed7935aad934ae5a2883975fe9900352465b3354da15f6f33d235`.
- This is documentation/template scope only. No schema, migration, database, endpoint, contract, UI, import, export or production behavior was added.
- Phase 03 is not accepted. P04-T02..T09 remain gated, including strict upload processing, NFC staging, DB/reference checks, preview/confirm, idempotency, safe export and rollback tests.
- EDU-0057 is implementer-authored and may move only to `in_review`; it needs an independent reviewer.

## Git bootstrap EDU-0055 — 2026-11-15

- Initialized Git on `main` and connected `origin` to `https://github.com/phongbao-uopeopleuni/eduops360.git` under explicit user authorization.
- Bootstrap commit `446c0a871854fb8236361801f8a19a7fdd8df5c3` was pushed and verified at `origin/main`. The GitHub repository is public and owned by `phongbao-uopeopleuni`; visibility was not changed.
- `.env*`, `.local`, virtualenv, dependencies, caches, build and test-result directories were excluded. Import audit found no forbidden staged environment file, ignored artifact, file over 20 MB or high-confidence secret match.
- First foundation run exposed a clean-checkout `.local` defect. EDU-0056 fixed it; replacement foundation run 43700379144 and governance/blueprint run 43700379165 are green on `d8012da`.
- `main` protection now requires strict `foundation`, `governance` and `blueprint-check` contexts, a pull request with one approval, stale-review dismissal, last-push approval, linear history and resolved conversations; force-push and deletion are denied. Admin enforcement is enabled after the final bootstrap documentation push.
- Existing whitespace in historical Markdown/evidence makes `git diff --cached --check` exit `2`; those audit artifacts were not bulk-rewritten.

## Conditional P03-T01 kickoff EDU-0054 — 2026-11-15

- User instruction superseded the EDU-0053 stop only for a narrow Phase 03 kickoff while retaining all Phase 02 items as debt. No Phase 02 approval ledger entry was created.
- Added `backend/app/modules/academic_years/domain.py` with pure rules for date windows, term containment, minimal forward-only state transitions, active-year conflict, archived read-only behavior, exact school/year scope, revision conflict and explicit IANA timezone validation.
- Fail-first: targeted collection exited `2` because the module did not exist. Final: `15 passed`; full host backend `93 passed, 20 skipped`; Ruff and OpenAPI drift checks pass.
- No model, migration, repository, endpoint, contract, frontend, seed or database write. P03-T02..T09 remain unstarted. EDU-0054 is `in_review` and needs a reviewer other than Codex.
- Phase 02 debt is unchanged: EDU-0046/0048 re-review, R42-F02 decision, UI49-F01, OD-001/003/007/008/011, MFA custody, archive/retention and human acceptance.

## Phase 03 prerequisite recheck EDU-0053 — 2026-11-15

- A fresh check found no signed Phase 01/02 acceptance and no approval-ledger change. Root governance checks remain green (`24` tests), but this is technical evidence only.
- Codex is not eligible to re-review its own EDU-0046/0048 remediation or fix UI49-F01 that it discovered. R42-F02 and OD/MFA/archive items still require the named human authorities.
- The pre-existing dev stack at `5173/58080/55440` was observed and left untouched. No Phase 03 module, migration, API, UI, seed or database write was created.
- Result: **`Phase 03 NOT STARTED — prerequisite not met`**. P03-T01 and P03-T02..T09 remain unstarted.

## Closeout EDU-0034..0041 — 2026-11-14

- EDU-0034 re-reviewed Claude's EDU-0032 remediation: `PASS_WITH_NOTES`, no new P1/P2.
- EDU-0035..0039 remediated infrastructure/test safety, rate limits/CORS/idle timeout, TOTP replay, invitation lifecycle/Admin UI/real-backend E2E and historical evidence claims.
- EDU-0040 local gate: backend host `77 passed, 18 skipped`; isolated PostgreSQL `95 passed`; frontend `22 passed`; Playwright `8 passed`; Alembic head `0008`; contract/static/build/governance checks pass.
- EDU-0041 contains F01..F22 disposition, decision briefs explicitly marked `NOT APPROVED`, reviewer eligibility for every `in_review` task and a blank approval ledger.
- Still blocked: OD-001/003/007/008/011, dependency lock hashes, encrypted MFA custody/enrollment/recovery, external audit archive/retention/anchor and human acceptance. Do not start Phase 03 from this handoff alone.

## Independent review EDU-0042 — 2026-11-14 (added by reviewer, not an acceptance)

- Claude reviewed Codex EDU-0034..0041. Report: `docs/quality/EDU-0034-0041_INDEPENDENT_REVIEW_2026-11-14.md`; evidence with exact commands/exit codes: `docs/progress/evidence/EDU-0042/verification.json`.
- All counts above were reproduced: host 77/18, isolated PostgreSQL 95, frontend 22, Playwright 8 including the real-auth path, root 24, head `0008`, `0008 ↔ 0007` roundtrip clean. The Phase 01 technical gate holds.
- **Phase 02 result: `NEEDS_CHANGES`.** The status line at the top of this file is contested for Phase 02:
  - **R42-F01 (P1).** The A0102-F01 target-privilege rule is checked only when a reset or invitation token is issued. A token issued while the target was unprivileged remains redeemable after the target is granted more rights, so a `user:password_reset`-only or `user:create`-only actor can take over the promoted account (reproduced live).
  - **R42-F02 (P2).** The TẠM per-IP window (50 failures/60 s) returns 429 to correct logins of other accounts behind the same peer address.
  - P3: R42-F03..F05.
- Claude must not fix these: it is this round's reviewer and implemented the EDU-0032 F01 design. A different actor fixes them in a separate task with live regressions, then an actor other than the fixer re-reviews. R42-F02 needs a Security Owner decision on threshold, trusted proxy and blocking semantics.
- Phase 01/02 remain NOT ACCEPTED; OD-001/003/007/008/011 remain OPEN. Do not start Phase 03.
- Next-agent prompt (EDU-0043): `docs/progress/NEXT_AGENT_PROMPT.md` now directs Codex, as a remediation actor distinct from this reviewer, to fix R42-F01 and R42-F03..F05 with live fail-first regressions. It also asks for a `NOT APPROVED` decision brief for R42-F02 and for the acceptance package to be updated truthfully. Re-review must be by an actor other than Codex. The previous EDU-0041 reviewer prompt is preserved in `docs/progress/evidence/EDU-0043/`.

## UI restyle EDU-0044 — 2026-11-14 (implementer, `in_review`)

- Frontend restyled to the user's Minimalist SaaS spec (copy: `docs/requirements/UI_STYLE_MINIMALIST_SAAS_2026-11-14.md`): indigo tokens, self-hosted Be Vietnam Pro + Inter, top navbar, pill buttons, soft cards, Overview hero/roadmap. Behaviour, labels and API are unchanged; light/dark is kept.
- Gates: frontend static checks, 22 unit, build, 9 Playwright including a new font/layout test (360–1280 px). Evidence and before/after screenshots: `docs/progress/evidence/EDU-0044/`.
- Deliberate deviations from the spec, to be confirmed by an independent design/a11y reviewer (not Claude): Be Vietnam Pro replaces Poppins, which has no Vietnamese glyphs; the dark theme is derived; scroll-reveal is omitted.
- Task ID note: EDU-0044 is used by this task, so the Codex remediation prompt's tasks start at the next free ID.

## Next-agent prompt EDU-0045 — 2026-11-14 21:50

- `docs/progress/NEXT_AGENT_PROMPT.md` is rewritten as one consolidated prompt. It replaces the unexecuted EDU-0043 prompt, which is preserved in `docs/progress/evidence/EDU-0045/`.
- Work queue, in order: A fix R42-F01 (P1); B decision brief for R42-F02 (P2); C fix R42-F03..F05 (P3); D independent review of the EDU-0044 UI restyle; E update the acceptance package and HANDOFF.
- A–D must be done by an agent other than Claude, because Claude found R42 and implemented EDU-0032/0044. Re-review must be by an actor other than the fixer.
- Fresh host numbers at 21:49: backend 77 passed / 18 skipped, ruff clean, root 24, frontend 22 unit, encoding 418/0, head `0008`. No dev servers running; Docker Desktop running.

## Remediation/review EDU-0046..0050 — 2026-11-14 22:21

- **EDU-0046 — R42-F01:** Codex added redemption-time recheck of the issuer's current purpose-specific global permission and coverage of all target grants. Fail-first RA/RB returned vulnerable 204; after fix targeted 2 passed and final PostgreSQL suite reached 98 passed. Task is `in_review`; Codex cannot close its own remediation. Denied token is not consumed, and issuer suspended/locked semantics remain a Security Owner question.
- **EDU-0047 — R42-F02:** `docs/security/R42-F02_LOGIN_RATE_LIMIT_DECISION_BRIEF.md` compares A disable, B threshold/semantics, C trusted proxy and D progressive delay. It is `NOT APPROVED`; no limiter policy code changed. P2 remains open and the no-password-oracle invariant is mandatory.
- **EDU-0048 — R42-F03..F05:** limiter eviction scan is bounded to 64 windows; tracked `scripts/seed_real_auth_e2e.py` writes synthetic credentials only under `.local`; `PLAYWRIGHT_REQUIRE_REAL_AUTH=1` fails when fixture variables are absent; EDU-0040 received an append-only 14-file correction. Final real-backend Playwright: 9 passed. Task awaits a reviewer other than Codex.
- **EDU-0049 — independent UI review:** `docs/quality/EDU-0044_UI_REVIEW_2026-11-14.md` is `NEEDS_CHANGES`. UI49-F01 P2 measured `.brand` at 36 px and `.text-link` at 25.6 px high versus the 44 px touch minimum. Codex did not edit UI; another actor may fix, then a different actor from the fixer re-reviews. The Be Vietnam Pro/dark/no-reveal deviations were accepted.
- **EDU-0050 final local gates:** governance/structure pass, final encoding 446/0, root 24, Ruff 57 formatted files, host 78 passed/20 skipped, PostgreSQL 98 passed, migration head 0008/no drift, frontend 22 + static/API/build, Playwright 9 with real-auth session revoked, OpenAPI synchronized.
- Side-effect warning: the first disposable real-auth fixture used an email domain rejected by Pydantic; its Playwright failure artifact contained the synthetic password, and Codex accidentally printed that local error context. It was not a user/production credential. Fixture and test artifact must be deleted at teardown; this remains recorded in EDU-0048 evidence.
- Next actor is Claude: re-review EDU-0046/0048; fix UI49-F01 in a separate task if accepting it; never decide R42-F02/OD items or mark a phase accepted. Prompt: `docs/progress/NEXT_AGENT_PROMPT.md` (EDU-0050).

## User-requested theme adjustment EDU-0051 — 2026-11-15 09:11

- The default theme is now light; invalid and legacy `system` preferences resolve to light. Dark mode remains available through one 44 px sun/moon icon toggle with a dynamic Vietnamese accessible name.
- Restrained warm-orange tokens appear only as background tint/glow on the hero, alternate sections, app pages and footer. Indigo remains the action/CTA colour; routes, API behavior and auth flows are unchanged.
- Fail-first evidence reproduced 2 unit failures and the absent icon button. Final frontend gates pass with 24 unit tests; external-local Chrome suite reports 9 passed and 1 real-auth test skipped because no disposable credential fixture was supplied.
- Evidence: `docs/progress/evidence/EDU-0051/`, including light/dark full-page screenshots. Local UI/API/DB remain running for the user's visual review.
- EDU-0051 does **not** close UI49-F01. Codex authored that finding and cannot self-review its disposition; the original brand/text-link touch-target work still belongs to another fixer/reviewer chain. Phase 01/02 status and all decision blockers are unchanged.

## Gate-aware Phase 03 prompt EDU-0052 — 2026-11-15 09:20

- `docs/progress/NEXT_AGENT_PROMPT.md` now gives the next agent two explicit modes: close eligible Phase 01/02 gates when acceptance is absent, or start only P03-T01 after real Phase 02 acceptance evidence exists.
- Current state still selects the first mode: Phase 01/02 are `NOT ACCEPTED`; R42-F02, independent re-reviews, UI49-F01, OD/MFA/archive and human approvals remain open. The prompt does not interpret the request to start the next phase as acceptance.
- If the prerequisite is later satisfied, the first Phase 03 slice is deliberately limited to school/year/term constraints and state transitions. It excludes migrations, student CRUD, CSV, UI, seed, scheduling and P03-T02..T09 to prevent over-engineering.
- The previous remediation prompt is preserved byte-for-byte at `docs/progress/evidence/EDU-0052/NEXT_AGENT_PROMPT.previous.md`.

The sections below are retained as historical audit/remediation context. Where counts or status differ, EDU-0050 and the current acceptance package above take precedence.

## Independent audit EDU-0031 — 2026-11-14 (added by reviewer, not an acceptance)

- AI independent technical/security audit result: **NEEDS_CHANGES**. Report: `docs/quality/PHASE_01_02_INDEPENDENT_AUDIT_2026-11-14.md`; evidence with exact commands/exit codes: `docs/progress/evidence/EDU-0031/verification.json`.
- Test counts above were reproduced, but live probes on an isolated PostgreSQL found 2 P1 (A0102-F01 password-reset/suspend without target-privilege bound → takeover of a more privileged admin; A0102-F02 User-Agent > 500 chars rolls back lockout counter and failed-login audit) and 6 P2 (F03–F08).
- The status line above is the implementer's claim; it is contested by this audit until a separate remediation task fixes F01–F08 with regression tests and the Human Security Owner reviews.
- Correction to "Reproduction" below: EDU-0024..0030 evidence JSON does not contain exact commands or exit codes (A0102-F17); EDU-0031 evidence does.
- Phase 01/02 remain NOT ACCEPTED; OD-001/007/008/011 remain OPEN.

## Remediation EDU-0032 — 2026-11-14 (implementer, `in_review`, not an acceptance)

- Separate remediation actor fixed A0102-F01..F08 with minimal changes; journal `docs/progress/tasks/EDU-0032.md`, evidence `docs/progress/evidence/EDU-0032/verification.json` (exact commands, exit codes) and `changes.diff` (no Git, so the diff is the change record).
- Failing-first: 12 regressions failed on the unfixed code and pass after (5 host, 6 live PostgreSQL, 1 Vitest). Gates after fix: backend host 74 passed / 14 skipped, isolated PostgreSQL 18 88 passed, ruff clean, `alembic check` clean (no migration), OpenAPI unchanged, frontend 20 unit + typecheck/lint/format/api/build, 7 Chrome E2E with external servers.
- Policy values introduced are **TẠM / fail-closed**, not decisions: F01 target-privilege rule (OD-008), F05 lockout keeps existing sessions (Security Owner), F06 no self-grant and delegated validity capped (OD-007/008), F07 Argon2 concurrency 4 (OD-004). Pending accounts can no longer be suspended or activated via the status endpoint.
- Next actor: an independent reviewer (not EDU-0031's or EDU-0032's session) re-reviews F01–F08, then the Human Security Owner decides. Still open: P3 F09–F22 (F10 re-invite/cancel now more relevant), real-backend Admin E2E.
- Next-agent prompt (EDU-0033): `docs/progress/NEXT_AGENT_PROMPT.md` now directs Codex to re-review EDU-0032, fix P3 findings that need no human decision, close Phase 01 local gates and prepare a Phase 01/02 acceptance and OD decision package. It grants isolated Docker use, no Git, and no acceptance authority. The previous prompt is preserved in `docs/progress/evidence/EDU-0033/`.

## Current evidence

- Database/audit boundary: EDU-0024, migration `0004`, three DB roles and live immutability/rollback tests.
- Authentication/account lifecycle: EDU-0025 plus migration `0005`/`0007`; hardened cookie/CSRF, invitation and password reset.
- Authorization/Admin: EDU-0026/0027; DB-loaded scoped grants and typed Admin console.
- Negative verification: EDU-0028 and EDU-0030; 72 host backend tests, 7 live PostgreSQL integration tests, 19 frontend unit tests and 7 Chrome E2E tests.
- Governance: EDU-0029 MFA recovery/break-glass draft; not approved or active.

## Decisions and blockers

- OD-001: name Human Security Owner, independent reviewer and Git maintainer.
- OD-007: approve two-person action/workflow policy.
- OD-008: approve authoritative role-to-permission and scope matrix. Global role mappings remain intentionally unseeded.
- OD-011: approve audit retention/archive delivery and production migration/downgrade authority.
- Approve encrypted MFA secret custody, recovery authorities and notification channel before enabling enrollment/recovery.
- Accept Phase 01 prerequisite before formal Phase 02 acceptance.
- `D:\eduops360` is not a Git repository; commit/push/PR/merge/hosted-CI evidence is unavailable.

## Next authorized actions

1. Human Security Owner reviews the package and records findings/decision without asking the implementer to self-approve.
2. Product Owner resolves OD-001/007/008/011; Security/DB owners convert approved values into a reviewed migration/configuration task.
3. Implement encrypted MFA enrollment/recovery and archive delivery only after those approvals, then rerun the same gates.
4. Do not start Phase 03 until the user accepts this audit and the formal prerequisite/gates are addressed.

## Reproduction

Exact commands and side effects are in `docs/progress/evidence/EDU-0030/verification.json`. All DB tests use an isolated disposable PostgreSQL instance and synthetic identities only.
