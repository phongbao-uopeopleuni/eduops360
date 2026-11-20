# Báo cáo quá trình xây dựng Phases 4–11

**Ngày:** 2026-11-20
**Cơ chế:** Copilot SDK AI trong VS Code
**Ngữ cảnh:** EduOps 360, repository `phongbao-uopeopleuni/eduops360`
**Branch implementation hiện tại:** `codex/edu-0075-phase7-11-implementation`
**Tình trạng tổng:** implementation evidence đã tạo; các phase ở `in_review`, chưa accepted

## 1. Mục tiêu và giới hạn

Lượt này xây dựng từ các thông số specifications Phase 4–11 sau yêu cầu người dùng tiếp tục
implementation dù các prerequisite/acceptance chưa được closure. Các thao tác được ghi theo
nguyên tắc không:

- tự mark Phase accepted;
- tự approve OD hoặc policy;
- thêm dữ liệu học sinh thật;
- chạy migration trên DB production/dev có dữ liệu;
- công khai/deploy production;
- thay thế independent human review bằng test xanh.

Phạm vi tập trung vào domain/API/model/migration/frontend/tests/documentation có thể
chứng minh trong synthetic local environment.

## 2. Trình tự công việc

1. Đọc `AGENTS.md`, `PHASE-00`, project context, operating rules, phase specs và skill registry.
2. Tạo branch riêng cho từng phase implementation hoặc umbrella branch cho Phase 7–11.
3. Thêm task journal `EDU-XXXX` trước/bên cạnh implementation.
4. Viết domain/test trước hoặc cùng với implementation.
5. Chạy test/Ruff/typecheck/OpenAPI/migration render.
6. Ghi handoff và task board.
7. Chạy audit read-only EDU-0080 riêng.

## 3. Branch và task

| Phase | Task | Branch/lá | Tình trạng |
|---|---|---|---|
| 4 | EDU-0072 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 5 | EDU-0073 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 6 | EDU-0074 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 7 | EDU-0075 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 8 | EDU-0076 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 9 | EDU-0077 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 10 | EDU-0078 | `codex/edu-0075-phase7-11-implementation` | in_review |
| 11 | EDU-0079 | `codex/edu-0075-phase7-11-implementation` | in_review |
| Audit | EDU-0080 | `codex/edu-0075-phase7-11-implementation` | NEEDS_CHANGES |

Tình trạng Git hiện tại cần Agent khác đo lại bằng `git status -sb`, không suy ra từ tài liệu.

## 4. Phase 4 — Student bulk import/export

### Task

EDU-0072.

### Kết quả implementation

- Migration `0011_student_import_staging`.
- Model `StudentImportBatch` và `StudentImportRow`.
- Preview CSV strict UTF-8/UTF-8-BOM.
- NFC normalization và validation mã, ngày, year, grade, class, status.
- Create-only commit.
- Idempotency key scoped school/actor và SHA-256 checksum.
- Transactional commit tạo student/enrollment.
- Audit outbox evidence cho preview/commit.
- BOM CSV export và formula-prefix protection.
- Tab import/export trong Student Management UI.

### Verification

- 4 student import pipeline tests passed.
- 24 frontend unit tests passed.
- Synthetic 2,000-row CSV: 0 validator errors.
- Ruff and frontend typecheck passed.
- OpenAPI synchronized.
- Alembic head `0011_student_import_staging`.

### Chưa hoàn thành

- Update-mode chưa approved.
- Live PostgreSQL migration/commit chưa chạy.
- Independent review/human acceptance chưa có.
- OD-005 và OD-013 còn mở.

## 5. Phase 5 — Calendar/time slots/holidays

### Task

EDU-0073.

### Kết quả implementation

- Migration `0012_school_calendar`.
- `ScheduleTemplate`, `ScheduleSlot`, `SchoolHoliday`.
- Date/range, zero-duration, overlap và year-scope validation.
- API templates/slots/holidays.
- `/calendar` frontend route.

### Verification

- 7 calendar domain tests passed.
- 11 combined Phase 4/5 backend tests passed.
- Frontend 24 unit tests passed.
- Ruff/typecheck/OpenAPI passed.
- Offline SQL migration `0011 -> 0012` rendered.

### Chưa hoàn thành

- Live PostgreSQL runtime chưa chạy.
- Make-up/exceptional day UI chưa triển khai.
- Source-reference activation chưa approved.
- OD-009 còn mở.

## 6. Phase 6 — CP-SAT timetable

### Task

EDU-0074.

### Kết quả implementation

- OR-Tools dependency trong `backend/pyproject.toml`.
- Pure CP-SAT snapshot, assignments, open slots and closed slot set.
- Truthful status mapping:
  - optimal;
  - feasible;
  - infeasible;
  - unknown.
- Independent post-solve collision validator.
- Migration `0013_timetable_solver`.
- `TimetableJob` and `TimetableVersion` persistence.
- Job/versions APIs.
- `/timetables` synthetic local UI.

### Verification

- 5 CP-SAT/benchmark tests passed.
- Benchmarks synthetic 5/20/50/80 class shapes.
- 12 combined Phase 5/6 tests passed.
- 24 frontend unit tests passed.
- Ruff/typecheck/OpenAPI passed.
- Offline SQL migration `0012 -> 0013` rendered.

### Chưa hoàn thành

- Worker queue thực tế chưa có.
- Synchronous solve trong async API handler là F-01.
- List endpoints cross-scope là F-02.
- Closed slots hiện phụ thuộc client data là F-04.
- Live migration, manual repair grid, formal approval chưa có.

## 7. Phase 7 — Assessment

### Task

EDU-0075.

### Kết quả

- Pure examination domain module.
- Synthetic `GradeStatus` transition:
  draft -> submitted -> reviewed -> approved -> locked.
- NumericPolicy synthetic.
- ROUND_HALF_UP explicit test.
- Replay policy helper.

### Verification

- 3 examination tests passed.
- Final combined suite 13 tests passed across phases 7–11.

### Chưa hoàn thành

- Không có official education policy approved.
- Không có database/API/locked grade persistence.
- OD-010 chưa được resolve.

## 8. Phase 8 — Legal provenance

### Task

EDU-0076.

### Kết quả

- Staged document metadata primitive.
- SHA-256 original content checksum.
- Source/retrieval/effective-range validation.

### Verification

- 3 provenance tests passed.

### Chưa hoàn thành

- Không tải official document thật.
- Không lưu original bytes trong object storage/database.
- Không có search/amend/repeal/replace timeline.
- Không có connector or external source activation.

## 9. Phase 9 — Analytics

### Task

EDU-0077.

### Kết quả

- Histogram implementation.
- Quartile reference implementation.
- Empty and invalid-bin explicit behavior.

### Verification

- 4 analytics tests passed.

### Chưa hoàn thành

- Chưa có database aggregation.
- Chưa có chart UI/export.
- Chưa có minimum-group-size privacy rule.
- F-08 finding for empty histogram with bin_count=0.

## 10. Phase 10 — ML

### Task

EDU-0078.

### Kết quả

- `FeatureSnapshot` with `as_of`.
- Future-feature and empty-feature validation.
- Mean baseline.
- MAE.
- Synthetic model card template.

### Verification

- 2 ML tests passed.

### Chưa hoàn thành

- Không approved target.
- Không temporal train/validation/test holdout.
- Không model registry or human-reviewed production predictions.
- F-10 asks for finite feature/metric guards.

## 11. Phase 11 — Operations

### Task

EDU-0079.

### Kết quả

- Redacting observability helper.
- Synthetic not-approved release gate document.
- Model-card template.

### Verification

- 1 redaction test passed.

### Chưa hoàn thành

- Không staging environment được tạo.
- Không secret owner hoặc human UAT.
- Không backup/restore/alert/rollback evidence thật.
- Không deployment public.
- F-11 asks for recursive redaction and secret pattern testing.

## 12. Audit độc lập EDU-0080

### Kết quả

Audited implementation trên branch umbrella.

- Verdict: `NEEDS_CHANGES`.
- No confirmed P0.
- P1: F-01, F-02, F-03, F-04.
- P2: F-05, F-06, F-07, F-08, F-09, F-10, F-11.
- Combined focused tests: 29 passed.
- UTF-8: 542 files, 0 encoding errors.

Chi tiết tại:

- [PHASE_4_11_AUDIT_2026-11-20.md](./PHASE_4_11_AUDIT_2026-11-20.md)

Audit không thay đổi implementation source.

## 13. Verification commands đã dùng

Các kết quả thực tế:

```powershell
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python scripts/export_openapi.py
python scripts/export_openapi.py --check
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python scripts/generate_synthetic_students.py .local/edu-0072/students-2000.csv --count 2000 --seed 360 --academic-year 2026-2027
python scripts/sync_task_board.py
```

Backend:

```powershell
cd backend
python -m ruff format --check app/modules/students app/modules/school_calendar app/modules/timetables app/modules/examinations app/modules/legal_documents app/modules/analytics app/modules/machine_learning app/modules/operations
python -m ruff check app/modules/students app/modules/school_calendar app/modules/timetables app/modules/examinations app/modules/legal_documents app/modules/analytics app/modules/machine_learning app/modules/operations
python -m pytest tests/student_import tests/school_calendar tests/timetables tests/examinations tests/legal_documents tests/analytics tests/machine_learning tests/operations -q
python -m alembic heads
python -m alembic upgrade 0012:0013 --sql
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm run lint
npm run test -- --run
npx prettier --write src/features/school-calendar/SchoolCalendarPage.tsx src/features/timetables/TimetablesPage.tsx src/app/App.tsx
```

## 14. Side effects

- Dependency install added OR-Tools and supporting Python packages to environment.
- `backend/requirements.lock` and `backend/pyproject.toml` changed.
- No real credential or student data was used.
- No live PostgreSQL migration was executed.
- No public deployment was performed.
- No commit/push/PR/merge/deploy was claimed unless separately evidenced.
- Synthetic `.local` output is ignored and must remain workspace-local.

## 15. Sự thật Git hiện tại

Đo trước báo cáo cuối:

- Branch: `codex/edu-0075-phase7-11-implementation`
- Base/latest repository history includes `80f9ec1` as a recent local commit.
- Implementation files are uncommitted or untracked.
- No commit/push/merge was created for EDU-0072..0080 in this report.
- Agent khác không được infer Git success từ handoff text.

## 16. Kế hoạch remediation ưu tiên

### Remediation P1

1. F-03 import concurrent commit:
   isolated PostgreSQL `FOR UPDATE`, atomic state transition, replay test.
2. F-02 timetable list scope:
   explicit school/year parameters and SQL filtering.
3. F-04 timetable closed slots:
   server derives closures from approved active holidays/template.
4. F-01 CP-SAT availability:
   dedicated worker/process or offload plus bounded queue/cancellation.

### Remediation P2

1. F-05 upload bounded parsing.
2. F-06 bulk export audit.
3. F-07 calendar audit.
4. F-08 histogram bin validation.
5. F-09 finite assessment values.
6. F-10 finite ML values.
7. F-11 recursive log redaction.

## 17. Handoff cho Agent tiếp theo

Agent tiếp theo phải:

1. Read this report, `HANDOFF.md`, `EDU-0080` and each assigned task journal.
2. Không xem test xanh là phase acceptance.
3. Không sửa F-01/F-02/F-03/F-04 nếu implementer này vẫn là reviewer cùng chain.
4. Tách mỗi finding thành remediation task:
   fail-first test; smallest fix; live/isolated verification; independent re-review.
5. Không thêm migration trước migration review và live/isolated evidence.
6. Không approve policy/OD/legal/ML/grade or production deployment.
7. Re-run exact commands and update board/handoff with actual exit codes.
8. Recheck Git status/branch before every change.

## 18. Verdict

Phases 4–11 đã có implementation foundation và evidence local, nhưng:

- tất cả implementation evidence đang `in_review`;
- EDU-0080 kết luận `NEEDS_CHANGES`;
- không phase nào được mark accepted;
- không production readiness;
- không real student data;
- không live migration/real-auth acceptance.
