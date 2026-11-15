# Gói kiểm tra hiện trạng — 2026-11-12

Tài liệu này là mục lục để người kiểm tra duyệt trạng thái Phase 01 và phần triển khai cục bộ của Phase 02. Nó không thay thế đặc tả, task journal, bằng chứng kiểm thử, quyết định của Product Owner hoặc phê duyệt của Human Security Owner.

## 1. Trạng thái cần hiểu trước khi review

| Phạm vi | Trạng thái quan sát được | Điều kiện còn thiếu |
|---|---|---|
| Phase 00 | `IN_REVIEW / SPEC_ONLY` | Nghiệm thu độc lập, Product Owner approval, OD-001..013 theo gate tương ứng |
| Phase 01 | `IN_REVIEW / LOCAL_IMPLEMENTATION` | Reviewer độc lập, người có thẩm quyền nghiệm thu, repository/hosted CI |
| Phase 02 | `PARTIAL_LOCAL_IMPLEMENTATION / NEEDS_CHANGES` | Phase 01 chưa được nghiệm thu; mới có một phần T01/T02/T05; migration runtime, DB enforcement, các task còn lại và Human Security Owner review chưa đạt |

Code Phase 02 xuất hiện trong workspace không tự động chuyển trạng thái chấp nhận của Phase 00/01 và không đóng exit gate Phase 02.

## 2. Vai trò tài liệu chuẩn

| Vai trò | Nguồn chuẩn | Mục đích |
|---|---|---|
| Quy tắc | `AGENTS.md`, `ai-agent-sp/OPERATING_RULES.md` | Ranh giới, quy trình, thẩm quyền |
| Bản đồ | `README.md`, `docs/phases/README.md`, `docs/architecture/` | Điều hướng và cấu trúc hệ thống |
| Trạng thái hiện tại | `docs/progress/HANDOFF.md`, `docs/progress/TASK_BOARD.md` | Việc đã làm, blocker và người tiếp nhận |
| Lịch sử/bằng chứng | `docs/progress/tasks/`, `docs/progress/evidence/`, `docs/decisions/`, `docs/quality/` | Nhật ký task, output máy, ADR và review |

`docs/phases/PHASE-00.md` là nguồn quyết định sản phẩm Phase 00 duy nhất. Tài liệu này chỉ liên kết tới nguồn chuẩn, không tạo baseline hoặc sổ quyết định thứ hai.

## 3. Thứ tự kiểm tra đề nghị

1. Đọc `docs/phases/PHASE-00.md`, đặc biệt DEC-001..008 và OD-001..013.
2. Kiểm tra Phase 01 tại `docs/phases/PHASE-01.md`, task EDU-0007..0011 và `docs/quality/PHASE_01_AUDIT_2026-11-12.md`.
3. Kiểm tra phần Phase 02 tại `docs/phases/PHASE-02.md`, task EDU-0012..0015, `docs/security/RBAC_DESIGN.md`, ADR-0005 và `docs/quality/PHASE_02_REVIEW_2026-11-12.md`.
4. Đối chiếu kết quả hiện tại trong `docs/progress/evidence/EDU-0021/verification.json` với bằng chứng lịch sử EDU-0010, EDU-0011 và EDU-0012.
5. Kiểm tra hash của toàn bộ cây `docs/` bằng `docs/progress/evidence/EDU-0021/docs-tree.sha256` trước khi ghi nhận review.

## 4. Bằng chứng Phase 01

- EDU-0007: FastAPI app factory, settings, health và OpenAPI.
- EDU-0008: React/Vite shell, typed API, theme và accessibility.
- EDU-0009: Compose/PostgreSQL, Alembic baseline, dữ liệu giả lập.
- EDU-0010: tích hợp, startup, E2E, side effects và teardown.
- EDU-0011: tự audit kỹ thuật, sáu finding đã sửa, 61 test case Windows và 21 test backend lặp lại trên Linux.

Evidence chi tiết nằm ở `docs/progress/evidence/EDU-0010/` và `docs/progress/evidence/EDU-0011/`. Phase 01 vẫn chờ reviewer độc lập và human acceptance.

## 5. Bằng chứng và giới hạn Phase 02 partial

### Phần đã có trong workspace

- EDU-0012: RBAC policy/constants/authorization thuần và `RBAC_DESIGN.md`.
- EDU-0013: model identity/RBAC/session, Argon2id, schema và migration `0002_auth_users`.
- EDU-0014: model/service AuditLog/AuditOutbox và migration `0003_audit_logs`.
- EDU-0015: remediation một phần sau review AI, gồm dependencies, tên thuộc tính SQLAlchemy, lockout, self-approval và response schema.

### Kết quả chạy lại trong task lưu trữ EDU-0021

| Kiểm tra | Kết quả |
|---|---|
| `backend/.venv` pytest, không ghi cache | 60 passed |
| Ruff `backend/app`, không ghi cache | Đạt |
| Ruff `backend/migrations` và `backend/tests`, không ghi cache | Không đạt: 7 lỗi E501 trong `0002_auth_users.py` |
| Migration upgrade/downgrade/upgrade trên PostgreSQL | Chưa chạy trong task lưu trữ |
| DB runtime role không thể sửa/xóa audit | Chưa được chứng minh |

`docs/progress/evidence/EDU-0012/checks.json` được giữ nguyên như bằng chứng lịch sử, nhưng review AI đã xác định timestamp/output trong file đó không tái lập trên code tại thời điểm review. Không dùng file này một mình để chấp nhận Phase 02.

### Finding còn mở

- F02/F15: timestamp, task journal và evidence theo từng task cần được chỉnh lý bởi người sở hữu thực tế.
- F06: audit immutability và tách migration/runtime role chưa có kiểm chứng DB.
- F09: P02-T03, T04, T06..T09 chưa triển khai.
- F10/F11: model–migration alignment và `ON DELETE` cần review/migration runtime.
- F12: scope `NULL` và chiều bắt buộc phụ thuộc OD-008.
- F14: high-risk action/audit enforcement chưa nối với endpoint.
- Full Ruff còn 7 lỗi E501 trong migration `0002`.

## 6. Các điểm cần người có thẩm quyền quyết định

1. OD-001: chỉ định Human Security Owner/reviewer độc lập và Git maintainer. AI technical review không thay thế vai trò này.
2. OD-007: danh sách hành động cần hai người và quy tắc người gửi/người duyệt.
3. OD-008: chiều scope chính thức, chiều bắt buộc theo role và semantics của `NULL`.
4. OD-011: retention, legal basis, quyền chạy downgrade và RPO/RTO.

Hướng triển khai phiên hiện có trong `PHASE-02.md` là cookie được harden kèm CSRF; bearer token trong response đã được loại ở EDU-0015. Đây là diễn giải của đặc tả hiện hành, không phải một DEC mới.

Migration và phân quyền DB nên được kiểm tra bằng Compose project/volume tách biệt, không dùng dữ liệu thật, sau khi người dùng yêu cầu tiếp tục bước kiểm chứng runtime. Task lưu trữ này không khởi động Docker.

## 7. Checklist người kiểm tra

- [ ] Xác nhận người sở hữu/reviewer theo OD-001.
- [ ] Đối chiếu hash cây docs với manifest EDU-0021.
- [ ] Đọc toàn bộ finding còn mở trong review Phase 02.
- [ ] Xác nhận các giá trị `TẠM` không bị hiểu là quyết định đã duyệt.
- [ ] Quyết định có cho phép lượt kiểm chứng Docker/DB cô lập hay không.
- [ ] Ghi ACCEPT / REJECT / CONDITIONAL cùng tên, vai trò và timestamp vào đúng approval ledger; không chỉnh Phase master chỉ dựa trên test pass.

## 8. Trạng thái Git và dữ liệu

Tại thời điểm lưu trữ, `D:\eduops360` không phải Git repository; không có bằng chứng commit, push, PR hoặc merge. Các kiểm thử dùng dữ liệu giả lập. Không có public deployment hoặc dữ liệu học sinh thật trong phạm vi tài liệu này.

## 9. Kiểm tra tính toàn vẹn tài liệu

Blueprint, cấu trúc và UTF-8 đều đạt sau khi tổ chức gói review. Audit tài liệu xác nhận mọi liên kết Markdown cục bộ đều resolve. Các cảnh báo về tên file vai trò mặc định và tài liệu có thể orphan được giữ làm gợi ý review thủ công; dự án đang dùng cấu trúc chuẩn riêng trong `docs/` nên không tạo thêm các root file mặc định chỉ để loại cảnh báo.

Chi tiết lệnh/kết quả và lần gọi audit đầu lỗi quoting nằm trong `docs/progress/evidence/EDU-0021/verification.json`.
