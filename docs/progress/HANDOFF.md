# Current handoff — Phase 01/02 human acceptance

**Status:** `P03-T01 IMPLEMENTED / IN_REVIEW UNDER USER DEBT EXCEPTION; PHASE 02 STILL NOT ACCEPTED`.

## Consolidated build handoff EDU-0081 — 2026-11-20

- Committed as `b86456c0890462edd867e461d98a81797e34709e` and pushed to
  `origin/codex/edu-0075-phase7-11-implementation`.
- Draft stacked PR [#15](https://github.com/phongbao-uopeopleuni/eduops360/pull/15) uses the
  open PR #14 branch as its base to avoid duplicating GitHub Pages changes.
- The first PR #15 foundation run failed on Ruff issues in Phase 3 prerequisite files.
  EDU-0082 corrected formatting, one unused import, and exception chaining, declared
  `python-multipart` in application and runtime locks, and added OR-Tools/transitive packages
  to the Docker runtime lock. Latest hosted checks pass: foundation run 44681442057 and
  governance/blueprint run 44681441925, including Compose, Alembic check, smoke and E2E.
- PR #15 remains a draft: EDU-0080 is `NEEDS_CHANGES`, and `main` requires CI, one independent
  approval after the latest push, and resolved conversations. No merge or phase acceptance occurred.
- Added a complete process report:
  [PHASE_4_11_BUILD_REPORT_2026-11-20.md](D:/eduops360/docs/quality/PHASE_4_11_BUILD_REPORT_2026-11-20.md).
- Added this agent handoff task: [EDU-0081](D:/eduops360/docs/progress/tasks/EDU-0081.md).
- Replaced the stale next-agent prompt with a remediation-first prompt in
  [NEXT_AGENT_PROMPT.md](D:/eduops360/docs/progress/NEXT_AGENT_PROMPT.md).
- The next actor should remediate EDU-0080 F-03/F-02/F-04/F-01 first, then P2 findings,
  and only then consider independent re-review.
- The report and handoff do not close audit findings or mark any phase accepted.

## Independent audit EDU-0080 — 2026-11-20

- Reviewed Phases 4–11 implementation without product source changes.
- Verdict: `NEEDS_CHANGES`; no confirmed P0.
- P1: F-01 synchronous CP-SAT event-loop blocking, F-02 timetable cross-scope listing,
  F-03 concurrent import commit race, F-04 client-controlled closed slots.
- P2: F-05 upload memory precheck, F-06 export audit, F-07 calendar audit, F-08 analytics
  bin validation, F-09 finite assessment values, F-10 finite ML values, F-11 shallow log redaction.
- Remediation and independent re-review are required; this audit is not phase acceptance.

## Phase 7–11 foundation EDU-0075..0079 — 2026-11-20

- The user authorized continuing Phases 7–11 while skipping formal accepted-phase gates.
- Added an umbrella implementation branch `codex/edu-0075-phase7-11-implementation`.
- Phase 7: policy-versioned synthetic assessment domain, forward state transitions and ROUND_HALF_UP numeric rounding.
- Phase 8: source URL, retrieval timestamp, checksum and effective-range provenance primitives.
- Phase 9: independent histogram and quartile calculations.
- Phase 10: `as_of` feature snapshots, mean baseline, MAE and synthetic model-card template.
- Phase 11: credential/redaction helper and explicit not-approved release gate record.
- Phase 7–11 remain `in_review`; no official legal policy, real student data, approved predictive target or production deployment was used.

## Phase 6 implementation EDU-0074 — 2026-11-20

- The user authorized continuing Phase 6 while skipping formal accepted-phase gates.
- EDU-0074 implementation is `in_review` on branch `codex/edu-0075-phase7-11-implementation`.
- Added OR-Tools CP-SAT snapshot, bounded solve, truthful status mapping and independent collision validation.
- Added timetable job/version persistence migration `0013_timetable_solver`, JSONB snapshots and draft versions.
- Added timetable job API and local `/timetables` UI.
- Verified 5 CP-SAT/benchmark tests including 5/20/50/80 synthetic class shapes, 12 combined Phase 5/6 tests,
  24 frontend unit tests, Ruff, frontend typecheck and OpenAPI synchronization.
- Live PostgreSQL migration, queued worker, manual repair grid, benchmark evidence and human approval remain incomplete.
- Formal Phase 5 acceptance and OD-009 remain open; no timetable is published automatically.

## Phase 5 implementation EDU-0073 — 2026-11-20

- The user authorized continuing Phase 5 while skipping formal accepted-phase gates.
- EDU-0073 implementation is `in_review` on branch `codex/edu-0075-phase7-11-implementation`.
- Added migration `0012_school_calendar`, schedule templates, AM/PM time slots and holiday ranges.
- Added overlap, zero-duration, reversed-range and academic-year-boundary validation.
- Added local calendar API and frontend route `/calendar`.
- Verified 7 calendar temporal tests, 11 combined Phase 4/5 backend tests, 24 frontend unit tests,
  Ruff, frontend typecheck, OpenAPI synchronization and offline SQL for migration `0012`.
- Live PostgreSQL migration/runtime, independent review and human acceptance remain not done.
- OD-009 and legal-holiday approval semantics remain open; no source is represented as approved.

## Phase 4 implementation EDU-0072 — 2026-11-20

- The user explicitly authorized continuing Phase 4 while skipping formal acceptance gates.
- EDU-0072 implementation is `in_review` on branch `codex/edu-0075-phase7-11-implementation`.
- Added migration `0011_student_import_staging`, staged batch/row models, strict UTF-8/BOM preview,
  create-only transactional commit, SHA-256 idempotency replay, audit writes and BOM CSV export.
- Added the import/export UI in the Student Management page.
- Verified 4 pipeline unit tests, 24 frontend unit tests, frontend typecheck/lint, Ruff,
  OpenAPI synchronization and a 2,000-row synthetic UTF-8 CSV with 0 validation errors.
- Live PostgreSQL migration/commit, independent review and human acceptance remain not done.
- OD-005 and OD-013 remain open; update mode and stricter import-limit policy are not approved.

Start at EDU-0054, then read `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`, EDU-0042 and EDU-0046..0053. The user explicitly allowed the narrow P03-T01 kickoff while carrying Phase 02 debt. Phase 01/02 remain unaccepted; do not present this exception as acceptance or automatically begin P03-T02..T09.

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
- Git initialized in EDU-0055; remote at `https://github.com/phongbao-uopeopleuni/eduops360`; `main` protected after EDU-0056. PR #14 (`codex/edu-0070-github-pages`) remains open and unmerged.

## Next authorized actions

1. Human Security Owner reviews the package and records findings/decision without asking the implementer to self-approve.
2. Product Owner resolves OD-001/007/008/011; Security/DB owners convert approved values into a reviewed migration/configuration task.
3. Implement encrypted MFA enrollment/recovery and archive delivery only after those approvals, then rerun the same gates.
4. Do not start Phase 03 until the user accepts this audit and the formal prerequisite/gates are addressed.

## Reproduction

Exact commands and side effects are in `docs/progress/evidence/EDU-0030/verification.json`. All DB tests use an isolated disposable PostgreSQL instance and synthetic identities only.


## GitHub Pages UI preview EDU-0070 — 2026-11-16

- The backend-free static preview is live at
  `https://phongbao-uopeopleuni.github.io/eduops360/`. The first successful
  deployment was run `43863545271` (#31), attempt 2, on `851f998`; current head
  `62d6beb` was subsequently deployed successfully by run `43870623064` (#33).
  GitHub deployment `7824548695` is `success`, and a fresh local probe returned
  HTTP `200` for both the HTML and its `/eduops360/assets/` JavaScript bundle.
  The user also confirmed in the browser that the public page opens.
- PR #14 (`codex/edu-0070-github-pages` → `main`) remains open and unmerged.
  Its current remote state is `BLOCKED` / `REVIEW_REQUIRED`; `main` remains at
  `c622467`. Do not self-approve, fabricate an approval, use admin bypass, or
  weaken the `main` branch rules.
- To make the requested static UI preview available without a second
  collaborator, the Pages workflow explicitly permits trusted pushes from
  `codex/edu-0070-github-pages` as a temporary deployment source, as well as
  `main`. Pull-request events remain validation-only and cannot deploy.
- Pages artifact remains limited to `frontend/dist`; no backend, PostgreSQL,
  Railway configuration, credentials, or student data are deployed.
- This does not merge PR #14, change the default branch, alter branch
  protection, or accept any project phase. After a future approved merge,
  `main` remains a deployment source.
- The separate `docs/progress/PROJECT_STATUS.md` file is absent from this
  main-based task branch; do not invent a replacement or import the unrelated
  stacked PR chain to enable Pages.
- Historical failure `43862744119` on `bf74ee1` occurred before the environment
  allowlist permitted the task branch. It is resolved and must not be reported as
  the current state. Keep the allowlist restricted to the two explicit refs;
  do not disable environment protection or select unrestricted branches.
- Current PR checks are green: Pages build/deploy, foundation, governance and
  blueprint. Deployment success does not merge PR #14, connect a backend,
  establish production readiness, or accept any project phase.

## Dangerous residual bug audit EDU-0071 — 2026-11-17

- Audit result is **NEEDS_CHANGES** on reviewed commit `62d6beb`: no confirmed
  P0, two new P1 findings and four open P2 findings. Full evidence, exact
  preconditions and minimum remediation are in
  `docs/quality/DANGEROUS_BUG_AUDIT_2026-11-17.md`.
- P1: delegated grants can remain effective after their authorizing grant is
  revoked early; concurrent grant requests can create duplicate active rows so
  revoking one row leaves the duplicate effective. Both require isolated
  PostgreSQL regression tests in a separate remediation task.
- P2: login accepts an unbounded password/body; the known shared-peer rate-limit
  denial of service remains open; the Pages deployment branch is allowed to
  publish while unprotected; all 13 workflow action references use mutable
  major tags. Policy-only and defense-in-depth items remain clearly separated.
- Verification: root 24 passed; backend host 93 passed/20 PostgreSQL skipped;
  backend Ruff/OpenAPI passed; frontend API/lint/typecheck/24 unit tests passed;
  npm audits and a 41-package OSV query returned no advisories. Docker was
  unavailable and was not started, so live concurrency proof remains pending.
- This was an audit-only task. No product code, migration, workflow, cloud
  setting or branch protection was changed; PR #14 was not merged and no phase
  was accepted. Pre-existing EDU-0070 documentation edits were preserved.
- Side effect: an initial backend scan accidentally read ignored local `.env`
  files, exposing local DB connection material only in internal tool output.
  The scan was stopped; no DB connection, data transfer or credential change
  occurred. Rotate those values if they are reused beyond local development.
- Test runs refreshed ignored pytest, Python bytecode, Ruff and Vitest caches;
  none were added to Git or deleted. The final port check was empty for the
  common project ports and the Docker service remained stopped.
