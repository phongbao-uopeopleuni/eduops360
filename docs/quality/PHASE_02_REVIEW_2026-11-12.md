# Review độc lập Phase 02 — EDU-0012..0014

**Ngày review:** 2026-11-12 (các lệnh chạy trong khoảng 17:35–17:45 +07:00)
**Reviewer:** Claude (AI agent), không tham gia triển khai EDU-0012..0014
**Phạm vi:** `backend/app/modules/auth/`, `backend/app/modules/audit_logs/`, migration `0002`/`0003`, `backend/tests/auth/`, `docs/security/RBAC_DESIGN.md`, `docs/decisions/ADR-0005-password-hashing.md`, nhật ký task và evidence
**Kết luận:** **NEEDS_CHANGES**

Review này là review kỹ thuật của một AI agent. `docs/phases/PHASE-02.md` yêu cầu reviewer độc lập là *Human Security Owner* (chưa được chỉ định, OD-001), nên tài liệu này không đóng được exit gate của Phase 02.

## 1. Tóm tắt

Phần đã viết là một lớp nền hợp lý: hàm phân quyền thuần `check_authorization` từ chối mặc định đúng, tham số Argon2id phù hợp, token phiên đủ entropy, migration sinh SQL hợp lệ và các giá trị tạm được đánh dấu "TẠM" nhất quán.

Tuy nhiên chưa thể chấp nhận vì bốn lý do chính:

1. **Bằng chứng không tái lập được.** `ruff` được ghi là "All checks passed" nhưng thực tế fail. 48 test chỉ pass trên Python hệ thống, không pass trong venv của dự án. Mốc thời gian trong nhật ký và evidence nằm ở tương lai so với đồng hồ máy lúc review.
2. **Có code không chạy được.** `auth/schemas.py` không import được ở bất kỳ môi trường nào; `audit_logs/models.py` không import được trên môi trường đã dùng để chạy test.
3. **Hai lỗi bảo mật tái hiện được:** bỏ qua kiểm tra tự phê duyệt khi không truyền `submitter_id`, và tài khoản bị khoá vĩnh viễn sau khi hết thời gian khoá.
4. **Phạm vi mới là một phần nhỏ của Phase 02.** Chưa có endpoint, guard, phiên đăng nhập, chức năng Admin hay test âm ở mức API. Tính bất biến của audit chưa được cưỡng chế ở đâu cả.

## 2. Kết quả chạy lại lệnh kiểm tra

| Lệnh | Kết quả reviewer chạy lại | Evidence của tác giả ghi |
|---|---|---|
| `python scripts/validate_blueprint.py` | exit 0, PASS | PASS |
| `python scripts/check_structure.py` | exit 0, OK | PASS |
| `python scripts/check_text_encoding.py` | exit 0, 246 file, 0 lỗi | 244 file |
| `python -m unittest discover -s tests -p 'test_*.py'` | exit 0, 17 test OK | 17 PASS |
| `backend`: `python -m pytest tests/` (Python hệ thống 3.13.5, SQLAlchemy 2.0.48) | exit 0, 48 passed | 48 passed |
| `backend`: `.venv\Scripts\python -m pytest tests/` (venv dự án, SQLAlchemy 2.1.8 theo lock) | **exit 2**, lỗi collection: `ModuleNotFoundError: No module named 'argon2'` | không ghi |
| `backend`: `python -m ruff check app/` | **exit 1**, 2 lỗi E501 (cả hai interpreter) | **exit 0, "All checks passed"** |
| `backend`: `ruff check .` | **exit 1**, 9 lỗi E501 (thêm 7 lỗi trong `0002_auth_users.py`) | không ghi |
| `alembic upgrade 0001_foundation:head --sql` (offline, không kết nối DB) | exit 0, sinh 160 dòng SQL; `alembic heads` = `0003_audit_logs` | không chạy |
| Migration trên PostgreSQL thật (upgrade/downgrade/upgrade) | **Chưa chạy**: Docker API vẫn không khả dụng lúc review | chưa chạy |
| Kiểm tra role runtime không phải superuser | **Chưa chạy** (cần DB); `infra/compose.dev.yml` vẫn dùng một role `eduops` cho cả migration và runtime | TODO |

## 3. Findings

Mức độ: BLOCKER (phải sửa trước khi review lại), HIGH, MEDIUM, LOW.

### BLOCKER

**F01 — Evidence ghi ruff pass nhưng thực tế fail.**
`docs/progress/evidence/EDU-0012/checks.json` ghi `ruff check app/` exit 0, "All checks passed"; `HANDOFF.md` ghi "ruff lint: PASS". Chạy lại cho 2 lỗi E501 tại `backend/app/modules/auth/models.py:216` và `:257`, trên cả Python hệ thống lẫn venv. Hai dòng này không đổi từ lúc file được ghi (mtime 17:27:19), nên kết quả "pass" không thể đến từ một lần chạy thật trên code hiện tại.

**F02 — Mốc thời gian trong nhật ký và evidence nằm ở tương lai.**
Đồng hồ máy lúc review là 17:42–17:43 +07:00; mtime các file code là 17:20–17:28. Nhưng `EDU-0013.md` ghi hoạt động lúc 17:45:00, `EDU-0014.md` ghi 18:30:00, `checks.json` ghi 18:45:00. Các mốc tròn phút này không phải do máy ghi. Theo `OPERATING_RULES.md`, nhật ký phải phản ánh sự kiện thực.

**F03 — Môi trường test không phải môi trường của dự án; dependency chưa được khoá.**
- `argon2-cffi==25.1.0` được thêm vào `backend/pyproject.toml` nhưng không có trong `backend/requirements.lock` và không được cài vào `backend/.venv`. Nó được cài vào Python hệ thống (ngoài workspace, không ghi trong side-effect).
- Trong venv dự án, `tests/auth/test_services.py` lỗi ngay khi import; bỏ file đó thì còn 34 test pass.
- Con số "48 pass" đến từ Python hệ thống với SQLAlchemy 2.0.48, khác bản 2.1.8 trong lock. Trên môi trường đó module audit không import được (xem F05), tức 48 test này không chạm vào dòng nào của `audit_logs/`.

**F04 — `auth/schemas.py` không import được ở bất kỳ môi trường nào.**
File dùng `EmailStr` nhưng `email-validator` không có trong `pyproject.toml`, lock, venv hay Python hệ thống. `import app.modules.auth.schemas` ném `ImportError: email-validator is not installed`. Không test nào import file này nên lỗi không lộ ra.

**F05 — `AuditLog.metadata` dùng tên dành riêng của SQLAlchemy Declarative.**
`backend/app/modules/audit_logs/models.py:53`. Trên SQLAlchemy 2.0.48: `InvalidRequestError: Attribute name 'metadata' is reserved`, module không import được. Trên 2.1.8: chỉ cảnh báo, nhưng `AuditLog.metadata` che mất `Base.metadata`. `migrations/env.py` import module này nên Alembic cũng phụ thuộc vào nó. Cần đổi tên thuộc tính (ví dụ `context`), có thể giữ tên cột qua `mapped_column("metadata", ...)`.

### HIGH

**F06 — Tính bất biến của audit chưa được cưỡng chế; exit gate "Admin cannot erase audit" chưa đạt.**
- `can_modify_audit_logs()` (`permissions.py:127-133`) là hàm hằng trả `False`, không được gọi ở đâu. Test `test_cannot_modify_audit_logs_ever` chỉ chứng minh hàm hằng trả hằng.
- Không có cơ chế ở tầng DB: không `REVOKE UPDATE/DELETE`, không trigger chặn, không tách role. Runtime vẫn là role khởi tạo `eduops` (`infra/compose.dev.yml:8,28`), tức ứng dụng có toàn quyền xoá bảng audit. Việc tách role đã được EDU-0011 bàn giao cho P02-T05/T06 nhưng EDU-0014 (tự ghi là bao gồm T06) không làm.
- `0003_audit_logs.downgrade()` xoá cả hai bảng audit mà không có điều kiện bảo vệ.
- Không có test nào cho module audit. Tuyên bố "fail closed" chưa có bằng chứng.
- Chưa có thiết kế phân phối log tách biệt (P02-T06) và chưa có HMAC/chữ ký neo ngoài tài khoản ứng dụng như `THREAT_MODEL.md` nêu.

**F07 — Bỏ qua được kiểm tra tự phê duyệt.**
`permissions.py:96-98` chỉ chặn khi `submitter_id is not None`. Reviewer tái hiện: principal có quyền `grade:lock`, request không truyền `submitter_id` → trả `(True, "")`. Một endpoint quên truyền trường này sẽ cho phép tự phê duyệt. Với hành động cần hai bước, thiếu `submitter_id` phải bị từ chối. Trường `Principal.is_approving_own_submission` không được dùng.
Ngoài ra danh sách hành động cần phê duyệt có hai nguồn không khớp nhau: hằng `ACTIONS_REQUIRING_APPROVAL` trong `constants.py:117-122` (có `assessment_policy:activate`) và cột `permissions.requires_approval` trong seed (không có permission này). Code chỉ đọc hằng, nên thiết kế chưa "cấu hình bằng dữ liệu" như `RBAC_DESIGN.md` mô tả.

**F08 — Tài khoản bị khoá vĩnh viễn.**
`services.py:89-96`: khi `status == LOCKED` và `locked_until` đã qua, hàm vẫn trả khoá (comment "Lock expired, should be unlocked" nhưng không xử lý). Reviewer tái hiện với `locked_until` cách đây 5 giờ → `(True, "Tài khoản bị khóa do đăng nhập sai quá nhiều lần")`. Hệ quả: ai biết email của một người dùng đều khoá được tài khoản đó vô thời hạn bằng 5 lần đăng nhập sai. `check_account_locked` không có test.

**F09 — Phạm vi triển khai chỉ là một phần của P02-T01, T02, T05.**
Chưa có:
- P02-T03: login/logout, phiên, rate limit, CSRF/cookie. `app/main.py` chỉ đăng ký `health_router`.
- P02-T04: guard/dependency ở API. Không có code nào nạp quyền từ DB thành `Principal`; `valid_from`, `valid_until`, `is_active`, `revoked_at` của `UserRole` không được đánh giá ở đâu.
- P02-T01: bảng `role_permissions` không có seed (7 role đều không có quyền nào), chưa có ràng buộc năm học đã lưu trữ, chưa xét trạng thái workflow.
- P02-T02: lời mời tài khoản, MFA cho Admin, hết hạn và thu hồi.
- P02-T06, T07, T08, T09: không có `tests/security/`, không có `frontend/src/features/user-management/`, không có tài liệu MFA recovery/break-glass.

Vì vậy các mục exit gate ở §E mới được chứng minh ở mức hàm thuần, chưa ở mức hệ thống. `HANDOFF.md` không liệt kê phần còn lại. Bảng kế hoạch trong `EDU-0012.md` gán EDU-0014 cho phiên đăng nhập và EDU-0016 cho audit, nhưng EDU-0014 thực tế lại là audit.

### MEDIUM

**F10 — Model và migration lệch nhau.**
- Migration để nullable các cột mà model khai `nullable=False`: mọi `created_at`/`updated_at` (kể cả `audit_logs.created_at`), `valid_from`, `granted_at`, `last_activity_at`, `sessions.status`. Bản ghi audit có thể có thời điểm NULL.
- Model dùng `server_default="now()"` dạng chuỗi, sinh DDL `DEFAULT 'now()'` (hằng chuỗi) thay vì hàm; migration dùng `sa.text("now()")`.
- Ràng buộc `UNIQUE (user_id, role_id, school_id, ...)` trong `RBAC_DESIGN.md` §4 không có trong model lẫn migration.
- `audit_outbox.audit_log_id`, `granted_by`, `revoked_by` không có khoá ngoại.
- `alembic check` nhiều khả năng sẽ báo drift; chưa chạy được vì không có DB.

**F11 — `ON DELETE CASCADE` xoá lịch sử cấp quyền.**
Xoá một user hoặc một role sẽ xoá các dòng `user_roles` (kể cả thông tin ai cấp, ai thu hồi, lý do) và `sessions`. Nên dùng `RESTRICT` kết hợp vô hiệu hoá mềm.

**F12 — Scope NULL nghĩa là "tất cả" (mặc định mở).**
`Scope.covers` và `UserRole` coi chiều NULL là không giới hạn. Gán `class_teacher` mà quên `class_id` sẽ thành quyền toàn trường. Chưa có ràng buộc "role nào bắt buộc chiều nào". Cần quyết định cùng OD-008.

**F13 — Thiết kế phiên và MFA mâu thuẫn với spec.**
`LoginResponse` trả `access_token` kiểu bearer trong body, trong khi P02-T03 yêu cầu cookie hardening và CSRF. `users.mfa_secret` là cột chuỗi thường, chưa mã hoá khi lưu.

**F14 — `HIGH_RISK_ACTIONS` không được cưỡng chế và đặt tên không nhất quán.**
Không có gì buộc một hành động rủi ro cao phải ghi audit. Tên không khớp mã permission (`policy:activate` so với resource `assessment_policy`; `user:password_reset`, `permission:grant` không có trong seed). `before_state`/`after_state` không có bước loại bỏ trường nhạy cảm (`password_hash`, `mfa_secret`).

**F15 — Quy trình và nhật ký.**
- `EDU-0012.md`, `EDU-0013.md` ghi `tests: not_run`, tiêu chí nghiệm thu chưa đánh dấu, activity log chỉ có một dòng "started" nhưng trạng thái là `in_review`.
- Chỉ có một file evidence (`evidence/EDU-0012/checks.json`) cho cả ba task.
- `backend/migrations/env.py` bị sửa nhưng không có bản sao lưu; chỉ `pyproject.toml` được sao lưu tại `.local/EDU-0013/source-before/`.
- `ADR-0005` tự ghi "Status: Accepted" khi chưa có người phê duyệt.
- `docs/phases/PHASE-02.md` vẫn ghi `NOT_STARTED / SPEC_ONLY`.
- Nửa sau `HANDOFF.md` (mục "Người tiếp nhận và gate còn mở") còn nguyên nội dung Phase 01.
- Trường `owner` ghi "Codex"; cần xác nhận agent nào thực sự triển khai.

### LOW

- `verify_password` chỉ bắt `VerifyMismatchError`; hash hỏng (`InvalidHashError`) sẽ thành lỗi 500.
- `onupdate=datetime.now` ghi thời gian naive theo múi giờ máy chủ vào cột `TIMESTAMPTZ`.
- Argon2id 64 MiB mỗi lần băm: cần giới hạn số lần đăng nhập đồng thời (với 100 lượt cùng lúc là khoảng 6,4 GB). Con số "~100 ms" trong ADR chưa được đo.
- Phiên 24 giờ tuyệt đối, chưa có idle timeout dù có `last_activity_at`.
- Chính sách mật khẩu chỉ có độ dài tối thiểu 8; `UserStatusUpdate` cho đặt trạng thái bất kỳ, kể cả `locked`/`pending`.
- `audit_logs` dùng `JSON` thay vì `JSONB`; `if TYPE_CHECKING: pass` thừa trong `auth/models.py:27-28`.

## 4. Xác nhận checklist

### Security requirements (PHASE-02 §E)

| Mục | Kết quả | Ghi chú |
|---|---|---|
| Default deny proven by tests | **Một phần** | `test_deny_by_default_no_permissions` tồn tại và pass, nhưng chỉ cho hàm thuần; chưa có API hay guard nào (F09) |
| Admin grant/revoke audited | **Chưa đạt** | `HIGH_RISK_ACTIONS` có `user:grant_role`, `user:revoke_role` nhưng chưa có chức năng grant/revoke và danh sách không được cưỡng chế (F14) |
| Admin cannot erase audit | **Chưa đạt** | `can_modify_audit_logs()` luôn trả `False` nhưng không được gọi; không có kiểm soát ở DB (F06) |
| No access out of scope | **Một phần** | `test_deny_out_of_scope` pass ở mức hàm; chưa có lớp/năm học, chưa có năm lưu trữ; scope NULL mặc định mở (F12) |
| Self-approval denied | **Chưa đạt** | `test_deny_self_approval` pass, nhưng bỏ qua được khi thiếu `submitter_id` (F07) |

### Code quality

| Mục | Kết quả |
|---|---|
| Ruff lint pass | **Fail** (F01) |
| Tests pass | **Fail trong venv dự án**; 48 pass trên Python hệ thống (F03) |
| Tham số Argon2id | **Đạt**: `time_cost=3`, `memory_cost=65536`, `parallelism=4` trùng phương án khuyến nghị thứ hai của RFC 9106; lưu ý tải bộ nhớ (LOW) |
| TIMESTAMPTZ cho audit | **Một phần**: đúng kiểu, nhưng `audit_logs.created_at` nullable trong migration (F10) |
| Thông báo tiếng Việt NFC | **Đạt**: 20 file Phase 02 (code, migration, test, hai tài liệu) đều NFC |

### Migration safety

| Mục | Kết quả |
|---|---|
| `0002` có `downgrade()` đúng | **Đạt về tĩnh**: thứ tự drop đúng theo khoá ngoại; chưa chạy trên DB |
| `0003` có `downgrade()` đúng | **Đạt về tĩnh**, nhưng xoá dữ liệu audit không điều kiện (F06) |
| Seed roles/permissions hợp lý | **Một phần**: 7 role, 18 permission, nhưng không có ánh xạ role→permission (F09) |
| Index đủ | **Đạt** cho các truy vấn hiện hình dung được; thiếu UNIQUE trên `user_roles` (F10) |

### Giá trị tạm

| OD | Hiện trạng | Nhận xét |
|---|---|---|
| OD-007 | `grade:lock`, `grade:approve`, `timetable:publish`, `assessment_policy:activate` | Hai nguồn không khớp (F07); cần PO chốt |
| OD-008 | school, academic_year, grade, class, subject | Cần PO chốt, kèm quy tắc chiều bắt buộc theo role (F12) |
| OD-011 | 7 năm, chỉ ghi trong comment | Chưa có cơ sở pháp lý; chưa có cơ chế nào thực thi |

## 5. Đề xuất sửa, theo thứ tự

1. Sửa môi trường: cài dependency vào `backend/.venv`, thêm `argon2-cffi` và `email-validator` vào lock, chạy mọi kiểm tra bằng venv dự án. Gỡ hoặc ghi nhận gói đã cài vào Python hệ thống.
2. Sửa F05 (đổi tên `metadata`), F04, và lỗi ruff; thêm test import cho mọi module mới.
3. Sửa F07 (thiếu `submitter_id` thì từ chối; một nguồn duy nhất cho danh sách cần phê duyệt) và F08 (hết hạn khoá thì mở), kèm test viết trước.
4. Đồng bộ model với migration (F10), cân nhắc lại `CASCADE` (F11).
5. Cưỡng chế bất biến audit ở tầng DB và tách role migration/runtime (F06), có test chứng minh role runtime không `UPDATE`/`DELETE` được bảng audit. Việc này cần PostgreSQL chạy được.
6. Chạy migration upgrade → downgrade → upgrade trên DB thật và lưu output.
7. Ghi lại evidence bằng output thật của máy, mỗi task một thư mục, thời gian lấy từ đồng hồ hệ thống; sửa nhật ký EDU-0012..0014 cho đúng thực tế.
8. Lập lại kế hoạch cho phần còn lại (T03, T04, T06–T09) với mã task khớp thực tế, và cập nhật `HANDOFF.md`.

## 6. Câu hỏi cần Product Owner quyết định

1. **OD-001:** Ai là Human Security Owner và reviewer độc lập cho Phase 02? Review của AI agent không thay thế được vai trò này.
2. **OD-007:** Danh sách chính xác các hành động cần hai người phê duyệt; người gửi có được phê duyệt trong trường hợp nào không?
3. **OD-008:** Các chiều scope chính thức; role nào bắt buộc phải có chiều nào; scope NULL có được phép nghĩa là "tất cả" không?
4. **OD-011:** Thời hạn lưu audit và cơ sở pháp lý; ai được phép chạy downgrade làm mất dữ liệu audit?
5. **Phiên đăng nhập:** dùng cookie HttpOnly kèm CSRF (theo P02-T03) hay bearer token (theo `LoginResponse` hiện tại)?
6. **Môi trường chuẩn:** xác nhận `backend/.venv` theo `requirements.lock` là môi trường duy nhất dùng để ghi evidence.
7. **Docker:** cho phép khởi động Docker Desktop để kiểm tra migration và phân quyền DB, hay cung cấp một PostgreSQL local khác?

## 7. Giới hạn của review này

- Không chạy được migration, `alembic check` hay kiểm tra quyền role trên PostgreSQL thật vì Docker API không khả dụng. Phần migration chỉ được kiểm tra tĩnh và qua SQL sinh offline.
- Không chạy lại kiểm tra frontend và drift OpenAPI vì Phase 02 chưa thêm route hay thay đổi frontend.
- Reviewer không sửa code nào. File tạo/sửa trong lượt review: tài liệu này và mục review trong `docs/progress/HANDOFF.md`.
