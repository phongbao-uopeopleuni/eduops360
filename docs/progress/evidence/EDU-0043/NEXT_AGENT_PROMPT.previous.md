# Prompt bàn giao cho reviewer/authority tiếp theo — nghiệm thu Phase 01/02

Tạo bởi EDU-0041 ngày 2026-11-14. Prompt thực thi EDU-0033 đã được sao lưu nguyên vẹn tại `docs/progress/evidence/EDU-0041/NEXT_AGENT_PROMPT.previous.md`.

## Bắt đầu prompt

Bạn là reviewer tiếp theo của EduOps 360 tại `D:\eduops360`. Mục tiêu là **review và ghi quyết định có bằng chứng**, không tự sửa finding trong cùng vòng review và không mặc định rằng `READY_FOR_HUMAN_ACCEPTANCE` đồng nghĩa với `accepted`.

### Ranh giới

- Chỉ làm trong `D:\eduops360`; đọc `AGENTS.md` trước.
- Không dùng dữ liệu thật, không public deploy, không tự tạo Git repository/commit/push/PR, không đọc/sửa `.env` thật nếu chưa được người dùng cho phép rõ.
- Chỉ DEC-001..008 là quyết định đã xác nhận. OD-001..013 và mọi giá trị `TẠM` vẫn mở.
- Reviewer không được tự sửa finding do chính vòng review này phát hiện. Tạo task remediation riêng cho actor khác.
- Không đánh dấu Phase 01/02 `accepted` nếu thiếu người có thẩm quyền, thời điểm ISO-8601, quyết định và evidence thật.

### Đọc theo thứ tự

1. `docs/phases/PHASE-00.md`, `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md`.
2. `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`.
3. `docs/quality/PHASE_01_02_INDEPENDENT_AUDIT_2026-11-14.md`.
4. `docs/quality/EDU-0032_REMEDIATION_REVIEW_2026-11-14.md`.
5. `docs/quality/PHASE_01_LOCAL_GATE_2026-11-14.md`.
6. `docs/phases/PHASE-01.md`, `docs/phases/PHASE-02.md`, `docs/quality/RELEASE_GATE.md`, `docs/quality/TRACEABILITY_MATRIX.md`.
7. Journals/evidence EDU-0032 và EDU-0034..0041; sau đó chỉ đọc skill cần thiết từ `ai-agent-sp/skills/REGISTRY.md`.

### Trạng thái phải tự kiểm chứng

- Phase 01/02: `READY_FOR_HUMAN_ACCEPTANCE / NOT ACCEPTED`.
- Gate mới nhất: backend host `77 passed, 18 skipped`; PostgreSQL cô lập `95 passed`; frontend `22 passed`; Playwright `8 passed`; Alembic head `0008`.
- F01..F11, phần replay của F12, F13..F20 và F22 đã có remediation/test. F21, MFA secret custody/encryption, dependency hashes và policy/OD vẫn blocked hoặc chưa approved.
- Thư mục hiện không phải Git repository; hosted CI chưa có.

### Việc review

1. Kiểm tra manifest/source và chạy lại gate trong EDU-0040 trên môi trường cô lập, không dùng credential hay dữ liệu thật.
2. Ưu tiên kiểm tra bypass F01/F04/F06, rate-limit F09, invitation F10, TOTP replay/migration F12, audit boundary F21 và real-auth E2E.
3. Đối chiếu từng kết luận trong acceptance package với source, test và evidence; ghi finding theo severity, cách tái hiện, tác động và owner.
4. Xác minh ma trận độc lập: không để actor review phần họ đã triển khai.
5. Human authorities quyết định OD-001/003/007/008/011, MFA custody và archive/retention. Mọi recommendation hiện tại đều `NOT APPROVED` cho đến khi được ghi quyết định thật.
6. Điền approval ledger chỉ với danh tính/thẩm quyền thật, timestamp ISO-8601 có offset và evidence. Nếu thiếu, giữ trạng thái `IN_REVIEW`.
7. Nếu có finding P0/P1/P2, kết luận `NOT_READY`, tạo task remediation cho actor khác và không bắt đầu Phase 03. Nếu không có, authority có thể ghi quyết định acceptance theo release gate.

### Đầu ra bắt buộc

- Một task journal mới, không ghi đè EDU cũ.
- Báo cáo review độc lập có lệnh, exit code, output đã sanitize và toàn bộ side effect.
- Finding ledger cập nhật và approval/decision records thật hoặc blocker rõ ràng.
- `TASK_BOARD.md` được sinh bằng script và toàn bộ governance validators đạt.
- Teardown môi trường cô lập, chứng minh không còn server/container riêng của task và không ảnh hưởng tài nguyên có trước.

## Kết thúc prompt
