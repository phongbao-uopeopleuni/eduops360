# EduOps 360 — PHASE 00 MASTER SPECIFICATION v2.2

> **SOURCE OF TRUTH / MUST READ FIRST**  
> Canonical path: `docs/phases/PHASE-00.md`  
> Document owner: Product Owner (business), Architecture Lead (technical)  
> Recorded: 2026-11-12 · Timezone: `Asia/Ho_Chi_Minh` (exact time not independently verified)  
> Status: **IN_REVIEW / SPEC_ONLY** — **NOT formally accepted**  
> Scope: Governance & requirements baseline only; **not** a working, deployed or security-certified application.

## 0. How every Agent must use this file

1. Open root `AGENTS.md` or `CLAUDE.md`, then **read this complete file before Phase 00 work**. Read `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md` and the assigned `EDU-XXXX` task journal.
2. Treat only **DEC-001–DEC-008** below as explicitly confirmed Product Owner decisions. Treat **OD-001–OD-013** as **OPEN**, including all proposed defaults.
3. Use the single authoritative version in this path. **Do not create another Phase 00 baseline, summary or open-decisions file**. Architecture ADRs, SRS, role cards and test evidence are supporting artifacts, not competing sources of business decisions.
4. On contradiction, stop changes affecting that decision, open an issue, cite the competing statements, and obtain Product Owner confirmation. Do not silently choose the newest document or an AI guess.
5. Before changing this file: create a task ID; log exact before/after and changed paths; update version and change history; run validations; request independent review. Only a human with authority can approve Phase 00 and authorize Git merge.
6. Maintain per-task work journals in `docs/progress/tasks/` and generate `docs/progress/TASK_BOARD.md`; the board is **operational evidence**, not an alternative specification.
7. Work in Vietnamese for business requirements and use consistent technical identifiers. All source text: strict UTF-8 without BOM; Vietnamese text NFC when appropriate. CSV for Excel can use UTF-8 BOM. No production student data in this starter.

### Document precedence (Phase 00 only)

`User-confirmed decisions → THIS FILE → approved ADRs & SRS implementation detail → AI Agent skills and task journals`. An ADR conflicting with a confirmed decision requires a Product Owner-approved change request. Do not reinterpret approvals, tests or Git state from a markdown claim.

## 1. Objective, users, and MVP boundaries

EduOps 360 is a web-based platform for academic administration and examination management in Vietnamese general education. It will serve **one school in MVP**, with a school boundary prepared for future expansion. It must model **Grades 1–12** and support **2,000–10,000 student records** with an anticipated **20–100 users** (simultaneous-vs-registered meaning still OPEN: OD-004).

**Delivery order:** Security/foundation prerequisites → **MVP-A Student Management + Bulk CSV** → **MVP-B Calendar/Timetable** → **MVP-C Examination**. Future modules include official legal-document tracking, statistics/visualization, ML decision support and AI-assisted search; they are **deferred, not canceled**.

**Non-goals of Phase 00:** implement production APIs; ingest real student data; create production accounts; run schema migrations against a real school database; deploy publicly; certify compliance; claim any Git action completed without evidence.

### Technology direction (agreed previously; implementation details reviewable)

- `frontend/`: React + TypeScript + Vite, white-first Scientific Minimalism, high-contrast Vietnamese font, Light/Dark.
- `backend/`: Python + FastAPI modular monolith; separate workers for OR-Tools CP-SAT scheduling, document synchronization and ML.
- PostgreSQL data model, OpenAPI contracts, Docker for local development; synthetic-data staging after local.
- Access control: server-enforced RBAC + scope + resource state, secure sessions and immutable/auditable change history.
- Strict UTF-8, Vietnamese NFC for appropriate text fields; CSV UTF-8 BOM output for direct Excel opening; preserve leading zeroes in identifiers.

## 2. Confirmed Product Owner decisions — authoritative

| ID | Area | **CONFIRMED decision** | Required design implication |
|---|---|---|---|
| DEC-001 | School scope | **Một trường, mở rộng sau** | `school_id` boundary in model; **no multi-school SaaS/billing UI** in MVP |
| DEC-002 | Education level | **Lớp 1–12** | Grade-aware catalog and policy engines; pilot school may operate fewer grades (OD-002) |
| DEC-003 | MVP order | **Quản lý học sinh + CSV → Thời khóa biểu → Khảo thí** | Phases 03–04 → 05–06 → 07, after foundation/security prerequisites |
| DEC-004 | Size | **2.000–10.000 HS / 20–100 người** | Synthetic fixtures to 10k; benchmark performance; concurrency meaning OPEN |
| DEC-005 | Student data | **Hồ sơ học vụ tối thiểu; mở rộng sau** | Stable ID, `student_code` TEXT, enrollment history per year; no unnecessary personal fields |
| DEC-006 | Timetable | **Mẫu theo cấp học + tùy chỉnh và validation** | Configurable hours/slots, holidays, classroom/teacher/student conflicts and hard/soft constraints |
| DEC-007 | Approval | **Phân quyền theo thao tác; hỗ trợ phê duyệt hai bước cho dữ liệu quan trọng** | Separate submission/approval permissions, state machine, server checks, audit; no self-approval by default pending policy |
| DEC-008 | Environments | **Local Docker trước → staging dùng dữ liệu giả lập** | Environment isolation, no real student datasets or production credentials in dev/staging |

### Data/temporal invariants for later implementation

- `students` identifies a person within an institution. `enrollments` records year/grade/class memberships; never recreate a student just because the academic year changes.
- School, academic year, scope and record state must be validated on the backend for every operation; frontend controls are only usability aids.
- Use `DATE` for dates, `TIME` for class periods, and `TIMESTAMPTZ` for audit events. `00:00` is a legitimate time, not a default for missing data.
- Grade computation must be policy-versioned by grade, subject, academic year and legal effective interval; not a universal formula for all grades.
- School closure/holiday periods block scheduling as hard constraints; published schedules must be versioned, not silently overwritten.

## 3. Roadmap and phase gates

| Phase | Deliverable | Minimum exit evidence |
|---|---|---|
| 00 | Governance, 8 decisions, 13 open questions, ownership, acceptance | Independent review + Product Owner approval; test/evidence and Git truthfulness |
| 01 | Working local frontend, backend, PostgreSQL, Docker, OpenAPI skeleton | Startup + health endpoint + frontend/API contract test |
| 02 | Login, IAM, RBAC, scope checks, audit trail | Negative access tests, session security tests, audit consistency |
| 03 | Academic year, school, class, student, enrollment master | DB relationships + historical/year transition tests |
| 04 | CSV upload, staging, preview, validation, import, rollback and audit | UTF-8/BOM/NFC/duplicate tests; transactional import |
| 05 | Timeslots, sessions, holidays, academic calendars | Interval and exception overlap tests |
| 06 | CP-SAT timetable, conflict validation, approval & publish | No hard conflicts, no silent missing periods, solver status tests |
| 07 | Grade 1–12 assessment engine, gradebook and approvals | Education domain SME legal review + fixed-input regression tests |
| 08 | Official legal-document sync, archive, effectiveness history and search | Provenance, legal relations, historical query tests |
| 09 | Statistical analytics and chart builder | Reproducible aggregation/visualization tests |
| 10 | ML experiment/prediction assistant | Leakage, temporal holdout, calibration/baseline and fairness evaluation |
| 11 | Security, load, backup/restore, monitoring and deployment readiness | Threat-model review, measured performance, RPO/RTO and release authorization |

**Release rule:** Security/performance/backup gates relevant to an earlier MVP pilot apply before that pilot; they must not be postponed merely because Phase 11 is numbered later.

## 4. Roles, responsibility and approval

| Role | Primary responsibility | Phase 00 task ownership | Can approve own output? |
|---|---|---|---|
| Human Product Owner | Scope, priorities, final business acceptance | DEC register, Phase 00 acceptance | Only as authorized business approver; cannot replace independent review |
| Business Analyst | Requirements, traceability, acceptance language | P00-T01/T02/T06 | No |
| Architecture Lead | Boundaries, ADR consistency, API ownership | P00-T03/T07 | No sole acceptance of own changes |
| Security / Privacy Reviewer | IAM/CIA, security risks, audit/privacy controls | P00-T04 | Independent reviewer required |
| DBA / Data Lead | Identifiers, year scope, data consistency | P00-T03 | No |
| DevOps / Maintainer | Local/staging plan, CI, repository permissions | P00-T05 | Merge only when authorized |
| QA / Governance Reviewer | Independent test evidence, contradiction and regression checks | P00-T09/T11 | Can review, not unilaterally accept business scope |
| AI Agent (Claude/Codex/other) | Implement assigned task with named role and bounded file ownership | P00-T08/T10, as assigned | **Never self-approve, self-merge or invent verification** |

**Assignments are role placeholders:** named human architecture reviewer, school/domain authority and Git merge maintainer are **OPEN (OD-001)**. Brand of AI model grants no authorization.

## C. Detailed execution steps

Execute in order; each entry is a task with required actions and evidence. Do not turn a proposed default into a confirmed requirement.

| Task | Owner | Procedure (in order) | Files / output | Completion evidence |
|---|---|---|---|---|
| P00-T01 | BA | Read 8 user answers → compare DEC-001..008 → mark confirmed only | This file §2 | All 8 preserved accurately |
| P00-T02 | PO + BA | Fix MVP-A/B/C sequence → list exclusions → align roadmap | This file §§1,3; `ADR-0001/0002` | No premature ML/legal in MVP |
| P00-T03 | Architect + DBA | Diagram school/year/student/enrollment boundary → identify key foreign-key/scope constraints → review with SME | `docs/architecture/DOMAIN_DATA_MODEL.md` | Consistent identities and history |
| P00-T04 | Security + BA | Define actor, role, action, scope, resource state → two-step transitions and audit evidence → negative cases | `ADR-0003`; SRS/traceability | No frontend-only authorization; no silent log deletion |
| P00-T05 | DevOps + Architect | Design Docker local and isolated synthetic staging → secrets policy → release checkpoints | `ADR-0004`; `infra/` plan | No live data/keys in fixtures |
| P00-T06 | BA + QA | Catalog OD-001..013 → assign gate phase → list defaults as suggestions only | This file §5 | Every unknown has phase/owner |
| P00-T07 | Architect | Update SRS IDs → link tests/phase → review module ownership | `SRS_MASTER.md`, `TRACEABILITY_MATRIX.md` | Traceable requirement coverage |
| P00-T08 | Agent governance | Ensure root adapters read this file → check skill registry → prohibit competing baselines | `AGENTS.md`, `CLAUDE.md`, `ai-agent-sp/` | Single-source checks |
| P00-T09 | QA | Run governance + UTF-8 + CSV + negative tests → capture command, timestamp, exit code, environment | Task evidence journal | Reproducible results, no invented PASS |
| P00-T10 | Implementer | Record before/after and paths → task status → branch/commit/push/PR/merge verified from Git | `docs/progress/tasks/EDU-XXXX.md`, generated board | No unverified Git claims |
| P00-T11 | Independent reviewer | Check every DEC and OD → inspect diffs/ADRs → report blockers and acceptance findings | `docs/quality/PHASE_00_ACCEPTANCE.md` | Reviewer different from implementer |
| P00-T12 | Human Product Owner | Read evidence + independent review → ACCEPT/REJECT/CONDITIONAL → authorize next phase | Approval ledger with timestamp | No automatic self-acceptance |

### Handoff checklist for each Agent

1. Confirm task ID, assigned role, owner files, dependencies, current branch and current Phase 00 status.
2. Read this file and only the relevant domain skill (`ai-agent-sp/skills/REGISTRY.md`); check SRS/test/ADR as applicable.
3. Write an expected behavior + failure case before implementation; identify security/UTF-8/year-scope impacts.
4. Change only authorized files; include schema/API/test changes when necessary, coordinating across `frontend/`, `backend/`, `contracts/`.
5. Run targeted tests and regressions; include command, environment, actual result and logs/links.
6. Record exact changed paths and before/after in task journal; verify Git commit/push/PR/merge individually.
7. Hand off blockers, outstanding questions and next commands; never describe unfinished work as done.

## 5. OPEN DECISIONS — not confirmed

The following proposals are **not** approved user decisions. Keep each item OPEN until the stated gate and record a PO-approved decision in §9.

### A. Blocking formal Phase 00 acceptance / Phase 01 handoff

| ID | Open question | Why it matters | Suggested default **NOT APPROVED** | Owner | Gate |
|---|---|---|---|---|---|
| OD-001 | Who is the authorized Product Owner, independent reviewer, security authority and Git merge maintainer? | Independent acceptance and source-control accountability | User as business PO; assign named reviewer and maintainer | Human PO | P00 acceptance |
| OD-002 | Pilot school is real institution or all-synthetic Grade 1–12 simulation? | School/UAT scope and campus/grade config differ | Simulated Grade 1–12 for development; architecture remains generic | Academic SME / PO | P00/P03 |
| OD-003 | New/existing GitHub repository? Branch-protection and merge authority? | Cannot prove Git/CI states without repo | New private `eduops360` repository, protected main | Git maintainer / PO | P01 kickoff |

### B. Resolve before feature implementation; do not block purely local scaffolding

| ID | Open question | Suggested default **NOT APPROVED** | Due |
|---|---|---|---|
| OD-004 | Are 20–100 registered users or concurrent sessions? | Benchmark 20 and 100 concurrent request scenarios; no unmeasured SLA | P01/P11 |
| OD-005 | Exact CSV/student fields, unique identity reconciliation and legacy formats? | Minimal code/name/DOB/year/grade/class/status, gender optional; manual conflict review | P03/P04 |
| OD-006 | Real academic-year and term dates; school/campus structure? | School-configured dates, `Asia/Ho_Chi_Minh`; no hardcoded Aug–Jul | P03 |
| OD-007 | Which actions require two-person approval? Can submitter approve? | After-lock grade edits, timetable publication and grading-policy activation require distinct approver by default | P02/P05/P07 |
| OD-008 | Exact RBAC scope: class, grade, subject, year, assignment? | Server checks role + permission + school/year/class/subject + state | P02/P03 |
| OD-009 | Scheduling priorities: double periods, special rooms, Saturday, no-class periods? | Hard constraints first, weighted preferences after SME fixtures | P05/P06 |
| OD-010 | Authoritative legal sources and effective-date validation per year/grade? | Official curated source list + human rule activation | P07/P08 |
| OD-011 | Retention, legal basis, backup RPO/RTO, production host, incident responder? | Synthetic only until reviewed; no public release | P02/P11 |
| OD-012 | Target devices and accessibility: desktop/phone editing? | Desktop-first authoring, responsive mobile read/review later | P01 |
| OD-013 | Import limit, staged import and duplicate-update mode? | Configurable file limit; mandatory preview/dry-run; resolve conflicts before commit | P04 |

### Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Wrong Grade 1–12 legal rule across years | Critical | Versioned policy with official citation and SME-approved test fixtures |
| Student duplicates/incorrect merges | High | Stable student ID, typed code, dry-run, manual reconciliation |
| Agent specification drift | High | This single Phase 00 master, root adapters, owned tasks, review |
| Solver infeasible/timeout | Medium | Prechecks, distinguish FEASIBLE/INFEASIBLE/UNKNOWN, independent validator |
| Vietnamese mojibake or leading-zero loss | Medium | Strict UTF-8/BOM, NFC, keep codes TEXT, round-trip tests |
| Overwritten grade/schedule via concurrent updates | High | Transactions, optimistic concurrency and audit outbox |
| Student data leak in staging/ML | Critical | Synthetic fixtures only, role-scoped API and exports |
| Unverified performance for 100 users | Medium | Load tests on measured environment before SLA commitment |

## 6. Source tree, module ownership and non-collision rules

```text
eduops360/
├── frontend/             # React/TypeScript only
├── backend/              # FastAPI, domain logic, workers
├── ai-agent-sp/          # Single canonical agent SOP and skills
├── contracts/            # OpenAPI-generated client contract
├── docs/
│   ├── phases/
│   │   └── PHASE-00.md    # THIS FILE: ONLY Phase 00 source of truth
│   ├── decisions/        # ADR explanations; not competing product decisions
│   ├── requirements/     # SRS and detailed feature requirements
│   ├── quality/          # Test evidence and independent review
│   └── progress/tasks/   # Append-only per-task execution evidence
├── infra/                # Docker/proxy/deployment config
├── scripts/              # Validators, task-board generation
├── AGENTS.md             # Codex adapter (pointer only)
└── CLAUDE.md             # Claude adapter (pointer only)
```

- No agent-specific fork of core specifications. No duplicate `PRODUCT_BASELINE*.md`, `OPEN_DECISIONS.md` or `PHASE00_TOM_TAT*.md` in active tree.
- One task, one branch/worktree when working in parallel; coordinate cross-boundary contracts/migrations.
- Feature business rules belong to backend domain modules. Frontend validation improves UX but cannot authorize writes.
- Tests, architectural rationale and actual Git history remain separately maintained **evidence**, not rival requirement sources.

## E. Verification and exit gate

**Phase 00 is NOT ACCEPTED until the following are evidenced:**

- [ ] P00-G01 — All 8 user-confirmed decisions match §2 and the SRS/ADR; independent reviewer signs.
- [ ] P00-G02 — MVP scope and non-goals aligned with roadmap (§§1,3).
- [ ] P00-G03 — All 13 unresolved issues have ownership and phase gate; no proposals silently treated as approved.
- [ ] P00-G04 — Named human approval/review/merge responsibility for OD-001.
- [ ] P00-G05 — Root agent adapters point to this file and only the unified `ai-agent-sp` library.
- [ ] P00-G06 — SRS requirements map to a phase and acceptance/negative tests.
- [ ] P00-G07 — Test execution logs show exact commands and PASS/FAIL, including malformed/negative cases.
- [ ] P00-G08 — Git repository/branch-protection and authorized maintainer are known (OD-003).
- [ ] P00-G09 — Task journal documents all changes; commit/push/merge fields reflect verified actions, not guesses.
- [ ] P00-G10 — Independent reviewer and Product Owner explicitly accept Phase 00 in recorded approval.

### Validation commands (from repository root)

```bash
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python scripts/sync_task_board.py
```

A passing document/governance suite proves only that the **starter documentation and validators** meet their checks. It does not prove a functioning API, user authentication, real student import, security certification or production readiness.

### Review / approval record (not yet completed)

| Field | Current value |
|---|---|
| Implementer | Architecture/BA preparation (artifact creation) |
| Independent reviewer | **NOT ASSIGNED** |
| Product Owner approval | **PENDING** |
| Decision | **IN_REVIEW** |
| Approved commit SHA / CI run | **NONE** |
| Phase 01 authorization | **NOT GRANTED** |

Reviewer: `________` · Review time ISO-8601 with offset: `________`  
Approval decision (`ACCEPTED` / `REJECTED` / `CONDITIONAL`): `________`  
Evidence link/path and signed Product Owner: `________`

## 7. Git / work log and handoff rules

Use `docs/progress/tasks/EDU-XXXX.md` for task-by-task history. Required fields: `task_id`, date/time (+07 or UTC offset), role/actor, reason, affected paths, before/after, actual test commands/results, issue, branch, commit SHA, push remote, PR URL, merged commit and approver. Generate summary via `python scripts/sync_task_board.py`; **never manually edit** the generated task board.

| Action | State for this blueprint | Evidence |
|---|---|---|
| Documentation prepared | YES (local artifact only) | Files in starter package |
| Real frontend/backend deployed | NO | None |
| Git commit | **NOT DONE** | No SHA |
| Git push | **NOT DONE** | No remote push proof |
| Pull request | **NOT CREATED** | No PR |
| Git merge | **NOT DONE** | No merge SHA |
| Production/staging deployment | **NOT DONE** | None |

No agent may claim a successful operation merely because a task file says so. Check Git state/API/CI directly before updating status. Track current bugs and blockers with exact reproduction and evidence; never erase old audit/work-log entries.

## 8. Failure, review and rollback protocol

- If new requirement conflicts with DEC-001..008: halt affected work, create a change request, impact analysis and updated ADR; obtain Product Owner confirmation before changing baseline.
- If validation fails: preserve failing evidence, find the first failing layer, fix a bounded change and run the same failing test plus regressions.
- If a Git conflict or mismatched agent output occurs: keep original branches/worktrees, review diff, resolve using agreed module ownership; do not blindly force-push or overwrite.
- If review rejects Phase 00: keep previous approved revision, mark blockers in task journal, edit this one master only and re-run acceptance.
- No database rollback is applicable in Phase 00 because real schema operations are not authorized.

## 9. Change history and future decision record

| Version | Date | Change | Git state | Approval |
|---|---|---|---|---|
| v2.1 | 2026-11-12 | Original separate product baseline, detailed plan, summary and open questions; 8 decisions confirmed | Not committed/pushed/merged | In review |
| **v2.2** | 2026-11-12 | Consolidated Phase 00 into one authoritative Markdown; removed three overlapping active specification files; aligned agent entrypoints and governance tests | Not committed/pushed/merged | **In review** |
| **v2.3** | 2026-11-20 | Added DEC-009: `SchoolHoliday.status == active` is authoritative for server-composed timetable closure. Added DEC-010: exactly one `ScheduleTemplate.status == active` is required per school/year; missing or multiple templates fail closed | Not committed/pushed/merged | Product Owner confirmed in EDU-0085; independent review pending |

**New decisions:** Append `DEC-009` onward only after documented Product Owner confirmation, with date, rationale, impacted modules, tests and reviewer. **Resolved issues:** Mark OD entries RESOLVED with exact decision ID and approval evidence; do not delete their history. All unresolved items remain OPEN.
