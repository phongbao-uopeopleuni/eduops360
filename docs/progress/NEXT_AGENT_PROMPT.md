# Agent handoff tiếp theo — remediation và audit closure

## 1. Mục tiêu

Tiếp tục EduOps 360 bằng thứ tự:

1. Remediate P1 từ EDU-0080.
2. Re-run isolated/live evidence cần thiết.
3. Cập nhật audit bằng actor độc lập với fixer.
4. Chỉ sau đó mới xem xét gate hoặc tiếp tục implementation mới.

Không tự mark phase accepted.

## 2. Phải đọc trước

1. `AGENTS.md`
2. `docs/phases/PHASE-00.md`
3. `ai-agent-sp/PROJECT_CONTEXT.md`
4. `ai-agent-sp/OPERATING_RULES.md`
5. `docs/quality/PHASE_4_11_BUILD_REPORT_2026-11-20.md`
6. `docs/quality/PHASE_4_11_AUDIT_2026-11-20.md`
7. `docs/progress/HANDOFF.md`
8. EDU-0072–EDU-0084
9. Relevant phase specs 4–11
10. Relevant skills in `ai-agent-sp/skills/REGISTRY.md`

## 3. Trạng thái đã biết

- Phase 4 implementation EDU-0072: in_review.
- Phase 5 implementation EDU-0073: in_review.
- Phase 6 implementation EDU-0074: in_review.
- Phase 7 implementation EDU-0075: in_review.
- Phase 8 implementation EDU-0076: in_review.
- Phase 9 implementation EDU-0077: in_review.
- Phase 10 implementation EDU-0078: in_review.
- Phase 11 implementation EDU-0079: in_review.
- EDU-0080 audit: NEEDS_CHANGES.
- EDU-0083 F-03 remediation: implemented, in_review.
- EDU-0084 F-02 remediation: implemented, in_review.
- EDU-0085 F-04 prerequisite: blocked pending Product Owner decisions.
- Current implementation umbrella branch:
  `codex/edu-0075-phase7-11-implementation`.

Trạng thái Git, commit, remote, PR và live processes phải được đo lại.

## 4. P1 remediation queue

### EDU-0080-F03 — import concurrent commit (implemented; independent review pending)

EDU-0083 now selects the batch with `FOR UPDATE` and refreshes the state before checking
committed replay. A synthetic two-session PostgreSQL regression passed three consecutive
runs; `tests/student_import` passed 5 tests. The implementer must not mark the audit finding
closed: a different actor must review the change and its live evidence.

### EDU-0080-F02 — timetable list scope (implemented; independent review pending)

EDU-0084 adds optional school/year filters to both job/version list endpoints, enforces the
requested scope, and filters SQL. The live two-school/three-year test and the six-test
timetable suite passed; OpenAPI and frontend types are synchronized. A different actor must
review the fix before the audit finding is closed.

### EDU-0080-F04 — server-derived closed slots (blocked; do not implement yet)

EDU-0085 records why implementation stopped: holiday status has no approved state or
approval workflow, and the schema permits multiple active schedule templates per
school/year while job requests contain no template ID. Do not assume `active` means
`approved`, select a template implicitly, or move to F-01 until an authorized Product Owner
decision is recorded in canonical Phase 00.

Decisions required: (1) whether active holidays are approved for solver use or a separate
approval workflow is required; (2) whether one active template is guaranteed per
school/year or each job must explicitly select an active template, including fail-closed
behavior for none/multiple.

### EDU-0080-F01 — CP-SAT availability

- Keep queued after F-04; do not skip the unresolved P1 blocker.
- move solve outside async request event loop;
- use bounded worker/process/queue;
- preserve queued/running/failed/cancelled status;
- test responsive health during long solve;
- do not auto-publish result.

### Completed implementation still awaiting independent review

- F-03 import commit serialization — EDU-0083; two-session PostgreSQL regression passed.
- F-02 timetable list scope — EDU-0084; two-school/year PostgreSQL regression passed.

Do not treat passing tests as audit closure or phase acceptance.

## 5. P2 queue

Remediate or record explicit blocker:

- F-05 bounded import upload/chunking;
- F-06 bulk export audit;
- F-07 calendar/holiday audit;
- F-08 histogram bin_count validation;
- F-09 finite assessment values;
- F-10 finite ML features/metrics;
- F-11 recursive depth-bounded redaction.

## 6. Ranh giới

- Không truy cập hoặc copy `.env*`, real credentials hoặc production data.
- Không chạy DB test trên shared/dev EduOps database.
- Không thay đổi OD or school policy values.
- Không activate official grade/legal/ML policy.
- Không public deploy, merge, production migration or force-push.
- Không mark accepted based on test pass.
- Một finding per task unless tightly coupled.
- Implementer cannot re-review own P1 remediation.

## 7. Verification tối thiểu

Run from repository root:

```powershell
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python scripts/export_openapi.py --check
python scripts/sync_task_board.py
git --no-pager status -sb
```

Backend:

```powershell
cd backend
python -m ruff format --check app tests
python -m ruff check app tests
python -m pytest tests/student_import tests/school_calendar tests/timetables tests/examinations tests/legal_documents tests/analytics tests/machine_learning tests/operations -q
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm run lint
npm run test -- --run
npm run api:check
npm run build
```

Live database work:

```text
Only use isolated PostgreSQL with synthetic data.
Record project, container/volume, migration current/head,
upgrade/downgrade/roundtrip and teardown.
```

## 8. Handoff bắt buộc

Each remediation task must contain:

- exact actor/role;
- fail-first evidence;
- changed files;
- exact commands and exit codes;
- live/hosted/isolation evidence;
- Git branch/commit/push/PR/merge fields;
- unresolved findings and blockers;
- independent reviewer identity/eligibility;
- no claim of human acceptance.

## 9. Stop conditions

Stop and report if:

- live DB is unavailable or shared;
- finding requires policy/authority not approved;
- migration is irreversible or lacks rollback review;
- source/test evidence conflicts;
- same actor would implement and self-review;
- real data or credentials are encountered.
