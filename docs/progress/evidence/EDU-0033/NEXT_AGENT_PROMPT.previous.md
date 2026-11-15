# Prompt bàn giao cho AGENT tiếp theo

Sao chép toàn bộ nội dung từ mục **Bắt đầu prompt** đến **Kết thúc prompt** cho AGENT tiếp theo.

---

## Bắt đầu prompt

Bạn là AGENT tiếp theo làm việc trên dự án **EduOps 360** tại `D:\eduops360`.

### 1. Ranh giới và thẩm quyền

- Chỉ được làm việc bên trong `D:\eduops360`. Không đọc, sửa hoặc chuyển sang dự án khác nếu người dùng chưa cho phép rõ ràng trong phiên hiện tại.
- Đây là lượt tiếp tục **Phase 02 partial**, không phải sự công nhận rằng Phase 00/01 đã được nghiệm thu.
- Không tự đánh dấu phase `accepted`, không tự phê duyệt output, không tự merge/deploy và không tuyên bố Git thành công nếu không có bằng chứng máy.
- Không dùng dữ liệu học sinh thật, production credential hoặc public deployment.
- DEC-001..008 trong Phase 00 là các quyết định đã xác nhận. OD-001..013 vẫn mở trừ khi có bằng chứng Product Owner mới trong tài liệu chuẩn.
- Các giá trị `TẠM`, suggested default hoặc comment trong code không phải quyết định đã duyệt.

### 2. Thứ tự đọc bắt buộc trước mọi thay đổi

Đọc đầy đủ, theo đúng thứ tự:

1. `AGENTS.md`
2. `docs/phases/PHASE-00.md`
3. `ai-agent-sp/PROJECT_CONTEXT.md`
4. `ai-agent-sp/OPERATING_RULES.md`
5. `docs/progress/REVIEW_PACKAGE_2026-11-12.md`
6. `docs/progress/HANDOFF.md`
7. `docs/phases/PHASE-02.md`
8. `docs/quality/PHASE_02_REVIEW_2026-11-12.md`
9. `docs/progress/tasks/EDU-0023.md`
10. `ai-agent-sp/skills/REGISTRY.md`, sau đó chỉ đọc các skill liên quan trực tiếp đến task: tối thiểu `ra-soat/migration-review`, `thuc-thi/database-workflow`, `kiem-thu/test-strategy`; dùng thêm skill khác chỉ khi phạm vi thực sự yêu cầu.
11. Các source/test/migration liên quan trực tiếp trong `backend/app/modules/auth/`, `backend/app/modules/audit_logs/`, `backend/migrations/versions/` và `backend/tests/auth/`.

Tài liệu là context và evidence, không phải bằng chứng thực thi tự động. Phải đối chiếu mọi claim với source, lệnh kiểm tra và trạng thái máy hiện tại.

### 3. Trạng thái khởi điểm cần kiểm chứng lại

Trạng thái được bàn giao, chưa được phép tin mù quáng:

- Phase 01: `IN_REVIEW / LOCAL_IMPLEMENTATION`.
- Phase 02: `PARTIAL_LOCAL_IMPLEMENTATION / NEEDS_CHANGES`.
- EDU-0012..0015 đã tạo RBAC foundation, identity schema, AuditOutbox foundation và một số remediation.
- Lần kiểm chứng gần nhất: 60 backend tests đạt trong `backend/.venv`; Ruff trên `app/` đạt; Ruff trên `migrations/ tests/` còn 7 lỗi E501 trong `0002_auth_users.py`.
- Migration Phase 02 chưa được chạy upgrade/downgrade/re-upgrade trên PostgreSQL thật.
- DB runtime role chưa được chứng minh là least privilege và chưa có bằng chứng không thể `UPDATE/DELETE` audit rows.
- Không có Git repository tại lần bàn giao gần nhất; phải kiểm tra lại bằng `git status -sb` và `git reflog -5`.
- OD-001, OD-007, OD-008 và OD-011 vẫn mở.

### 4. Task được giao: EDU-0023

Mục tiêu của lượt này là **ổn định foundation Phase 02 trước khi triển khai login/session/API guards**. Không gộp toàn bộ P02-T03..T09 vào một task.

Thực hiện theo thứ tự:

1. Kiểm tra workspace hiện tại, file mtime/hash và các thay đổi có thể do agent khác tạo. Không ghi đè thay đổi không thuộc task.
2. Chạy lại baseline bằng `backend/.venv`, không dùng Python hệ thống để ghi evidence.
3. Tạo regression/validation phù hợp trước khi sửa các finding có hành vi. Sửa bảy lỗi E501 còn lại và làm cho Ruff trên `app migrations tests` đạt.
4. Đối chiếu model với migration cho các finding F10/F11: nullable/default/FK/unique/on-delete. Chỉ sửa phần có thể xác định từ invariant bảo mật và tài liệu chuẩn. Nếu thay đổi phụ thuộc semantics của OD-008 hoặc retention/rollback của OD-011, dừng phần đó và ghi blocker cụ thể; không tự chọn default.
5. Chỉnh trạng thái ADR-0005 nếu còn tự ghi `Accepted` mà chưa có approver; dùng `Proposed` hoặc `In review` và bảo toàn lịch sử.
6. Chỉnh lý task/evidence F02/F15 bằng entry correction có timestamp thực tế. Không xóa hoặc viết lại lịch sử để làm cho evidence cũ có vẻ hợp lệ. Không bịa timestamp/actor của EDU-0012..0015.
7. Chưa triển khai login/logout/session/CSRF trong EDU-0023. Sau khi foundation ổn định và review lại, task tiếp theo mới triển khai P02-T03 theo **cookie HttpOnly được harden + CSRF**, không trả bearer token trong body.

### 5. Docker và migration runtime

- Prompt này không tự cấp quyền khởi động Docker Desktop.
- Nếu người dùng trong phiên của bạn cho phép rõ ràng, dùng một Compose project, database, network và volume audit **tách biệt**; không chạm volume local trước đó.
- Trước mọi thao tác xoá/move/teardown, resolve và kiểm tra chính xác target trong `D:\eduops360` hoặc resource Docker có project name của task.
- Khi được phép, kiểm tra tối thiểu: `0001 → 0003 → base → 0003`, `alembic current`, `alembic check`, UTF-8, role migration/runtime tách biệt, runtime role không thể sửa/xóa bảng audit.
- Sau kiểm thử phải dừng process/container do task tạo; ghi rõ image/volume/cache nào được giữ. Kiểm chứng lại cổng/process tại chỗ trước khi tuyên bố đã dừng.
- Nếu chưa được phép dùng Docker, hoàn thành phần static/offline/test không phụ thuộc Docker và bàn giao runtime migration là `not_run`.

### 6. Lệnh baseline bắt buộc

Chạy từ PowerShell, ghi nguyên command, cwd, timestamp, exit code và output đã sanitize:

```powershell
cd D:\eduops360\backend
$env:PYTHONDONTWRITEBYTECODE = '1'
.venv\Scripts\python -B -m pytest tests -q -p no:cacheprovider
.venv\Scripts\python -B -m ruff check --no-cache app migrations tests
.venv\Scripts\python -B -m alembic heads
.venv\Scripts\python -B -m alembic upgrade 0001_foundation:head --sql
```

Sau thay đổi, chạy lại các lệnh liên quan và kiểm tra governance từ thư mục gốc:

```powershell
cd D:\eduops360
python -B scripts/validate_blueprint.py
python -B scripts/check_structure.py
python -B scripts/check_text_encoding.py
python -B scripts/sync_task_board.py
```

Nếu thay đổi route/OpenAPI, phải chạy thêm contract drift và frontend type generation/check. Nếu không thay đổi interface, ghi rõ `not_applicable` thay vì giả vờ đã kiểm tra.

### 7. Quy tắc sửa file và evidence

- Dùng `apply_patch` cho chỉnh sửa file thủ công.
- Snapshot hash/mtime các file target trước thay đổi. Backup byte gốc nếu task có migration hoặc thay đổi khó rollback.
- Viết expected behavior và failure case trước implementation.
- Mỗi finding phải có: vị trí, mức độ, cách tái hiện, before/after, test và giới hạn.
- Dùng dữ liệu giả lập; không log secret. Không đưa nội dung `.env` vào evidence.
- Test/build có tạo hoặc ghi đè cache, `dist`, `test-results`, database, image hay volume thì phải kê khai đầy đủ, kể cả file gitignored và mtime-only.
- Giữ `frontend/` và `backend/` tách biệt; dùng `contracts/` khi interface thay đổi.
- Không sửa `docs/phases/PHASE-00.md` hoặc biến OD thành DEC nếu chưa có phê duyệt đúng thẩm quyền.

### 8. Điều kiện bàn giao EDU-0023

Trước khi kết thúc lượt:

- Cập nhật `docs/progress/tasks/EDU-0023.md` với changed paths, before/after, lệnh/exit code, side effects và blocker.
- Lưu evidence riêng dưới `docs/progress/evidence/EDU-0023/`.
- Cập nhật `docs/progress/HANDOFF.md` ngắn gọn, nêu ba hành động tiếp theo.
- Chạy `python -B scripts/sync_task_board.py`; không sửa tay board.
- Kiểm tra `git status -sb` và `git reflog -5`. Nếu vẫn không có repository, ghi đúng exit/error; commit/push/PR/merge đều `not_done`.
- Không tự đánh dấu Phase 02 accepted. Trạng thái task tối đa là `in_review` cho đến khi có reviewer phù hợp.
- Human Security Owner theo OD-001 vẫn phải review security gate; AI review không thay thế vai trò này.

Kết quả trả người dùng phải bắt đầu bằng outcome, nêu phần đã đạt, phần fail/not_run, file quan trọng và mọi tác dụng phụ. Không che giấu lỗi hoặc mô tả công việc partial là hoàn thành Phase 02.

## Kết thúc prompt
