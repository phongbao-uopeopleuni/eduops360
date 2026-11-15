# Prompt bàn giao cho Agent — đóng gate và kickoff Phase 03 có điều kiện

Tạo bởi EDU-0052; cập nhật bởi EDU-0054 sau chỉ đạo mới của người dùng. Bản trước EDU-0052 được sao lưu tại `docs/progress/evidence/EDU-0052/NEXT_AGENT_PROMPT.previous.md`.

> **Chỉ đạo mới có hiệu lực:** người dùng đã yêu cầu tiếp tục Phase 03 và giữ phần Phase 02 chưa xong thành nợ kỹ thuật. EDU-0054 đã triển khai riêng P03-T01 và đang `in_review`. Chỉ đạo này không accept Phase 02, không approve các policy mở và không tự cho phép P03-T02..T09 trước review P03-T01. Các mục gate lịch sử bên dưới vẫn dùng để theo dõi nợ, nhưng câu “không tạo module Phase 03” không còn áp dụng hồi tố cho EDU-0054.

---

## Bắt đầu prompt

Bạn là Agent tiếp theo làm việc trên EduOps 360 tại **`D:\eduops360`**. Hãy đọc toàn bộ phần bắt buộc bên dưới trước khi sửa file hoặc chạy migration.

Mục tiêu của lượt tiếp theo là:

1. review độc lập P03-T01 trong EDU-0054 nếu actor khác Codex; task review không đồng thời sửa finding mới;
2. tiếp tục theo dõi/đóng từng khoản nợ Phase 02 nếu actor đủ độc lập;
3. không bắt đầu P03-T02..T09 cho đến khi P03-T01 có review riêng và phạm vi task kế tiếp được ghi rõ.

Yêu cầu “bắt đầu Phase tiếp theo” không tự động thay thế prerequisite, independent review hoặc chữ ký của người có thẩm quyền.

### 0. Sự thật hiện tại — phải kiểm tra lại, không được mặc định

- `docs/phases/PHASE-03.md` ghi prerequisite: **PHASE-02 accepted**.
- Người dùng đã tạo ngoại lệ kickoff có điều kiện cho riêng P03-T01; EDU-0054 là implementation evidence, không phải Phase 02 acceptance.
- Phase 01 và Phase 02 hiện là `IN_REVIEW / NOT ACCEPTED`; Phase 00 cũng chưa có acceptance chính thức.
- EDU-0046 và EDU-0048 là remediation của Codex, đang chờ actor khác re-review.
- R42-F02 là P2 chưa có quyết định Human Security Owner; brief vẫn `NOT APPROVED`.
- UI49-F01 vẫn cần actor khác Codex sửa và một reviewer khác fixer kiểm tra lại.
- OD-001/003/007/008/011, MFA custody/enrollment/recovery, audit archive/retention và human acceptance còn mở.
- EDU-0051 đổi theme mặc định sang sáng, thay dropdown bằng icon sáng/tối 44 px và thêm tint cam nhẹ. Không được làm mất thay đổi này khi sửa UI49-F01.
- Baseline gần nhất: backend host `78 passed, 20 skipped`; PostgreSQL cô lập `98 passed`; Alembic head `0008`; frontend `24 passed`; UI Playwright `9 passed, 1 real-auth conditional skip`; required-real-auth gần nhất ở EDU-0050 là `9 passed`.
- Git đã được khởi tạo và push trong EDU-0055 tại `https://github.com/phongbao-uopeopleuni/eduops360`; `main` được bảo vệ sau EDU-0056. Phải đo `git status`, remote, checks và PR/merge thật; không bịa Git success.
- Local UI/API/DB có thể đang chạy ở `5173/58080/55440` cho người dùng xem. Phải tự đo lại; không dừng hoặc ghi test vào DB dev đó nếu chưa được yêu cầu.

Nếu trạng thái thực tế khác, ưu tiên bằng chứng mới và cập nhật tài liệu; không sửa lịch sử cũ.

### 1. Đọc bắt buộc theo đúng thứ tự

1. `AGENTS.md`.
2. Toàn bộ `docs/phases/PHASE-00.md`.
3. `ai-agent-sp/PROJECT_CONTEXT.md` và `ai-agent-sp/OPERATING_RULES.md`.
4. Task journal được giao và `docs/progress/HANDOFF.md`.
5. `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md` và `docs/quality/RELEASE_GATE.md`.
6. `docs/phases/PHASE-01.md`, `PHASE-02.md`, rồi toàn bộ `PHASE-03.md`.
7. `docs/requirements/SRS_MASTER.md`, `docs/quality/TRACEABILITY_MATRIX.md`, `docs/architecture/DOMAIN_DATA_MODEL.md`.
8. Journal/evidence EDU-0042, EDU-0046..0052 và source/test liên quan trực tiếp.
9. `ai-agent-sp/skills/REGISTRY.md`; chỉ đọc skill cần cho task. Với kickoff Phase 03, bắt đầu bằng `lap-ke-hoach/spec-to-tasks`; chỉ dùng `thuc-thi/database-workflow`, `thuc-thi/backend-feature`, `kiem-thu/test-strategy` hoặc `ra-soat/migration-review` khi lát cắt thực sự cần chúng.

Markdown là claim, không phải bằng chứng chạy. Đối chiếu source, test, process, DB và journal trước khi kết luận.

### 2. Ranh giới tuyệt đối

- Chỉ làm trong `D:\eduops360`.
- Không đọc, in, sửa hoặc sao chép `backend/.env`, `infra/.env` hay `.env*`; mọi lệnh recursive phải loại trừ chúng.
- Không cài package, không truy cập package index, không đổi lockfile.
- Không dùng dữ liệu học sinh thật, credential thật hoặc deploy public.
- Không tự quyết OD, không biến suggested default thành requirement, không điền chữ ký/approval thay con người.
- Không review và sửa cùng một finding trong cùng task; không tự approve output của chính mình.
- Dùng `apply_patch` cho edit thủ công. Journal append-only; `TASK_BOARD.md` chỉ được tạo bằng script.
- DB test phải là PostgreSQL cô lập với Compose project riêng; không ghi test vào `eduops360-dev`.
- Chỉ xóa container/volume/file credential do task hiện tại tạo. Giữ local dev cho người dùng nếu nó có trước task.

### 3. Bước 0 — preflight

1. Xác nhận ID task tiếp theo còn trống, dự kiến từ **EDU-0055**; kiểm tra file/process mới để tránh đè actor khác.
2. Chạy `git status -sb` và `git reflog`; ghi exit code thực tế, không khởi tạo Git.
3. Đo listener/process, Docker Desktop và Compose project; phân biệt dev stack có sẵn với stack test của task.
4. Tạo baseline/manifest dưới `.local/<task>/`; loại `.env*`, `.venv`, `node_modules`, `.local`, cache, `dist`, `test-results`.
5. Chạy gate nền phù hợp trước khi sửa. Nếu số liệu lệch, điều tra và ghi lại trước.
6. Xác định actor hiện tại đã implement/review task nào; dùng ma trận độc lập để biết việc nào được phép làm.

### 4. Gate bắt buộc trước Phase 03

Chỉ coi Phase 03 được phép bắt đầu khi **tất cả** mục sau có bằng chứng mới, cụ thể và không phải self-approval:

- Phase 01 được reviewer độc lập và human authority chấp nhận.
- EDU-0046 và EDU-0048 có independent re-review hợp lệ; không còn P0/P1 chưa xử lý.
- UI49-F01 đã được fixer đủ độc lập sửa và reviewer khác fixer xác nhận.
- R42-F02 có quyết định Human Security Owner, implementation/test tương ứng nếu quyết định yêu cầu đổi code.
- OD-001/007/008/011, MFA custody và audit archive/retention đã được authority tương ứng xử lý theo Phase 02 exit gate.
- Phase 02 có acceptance record thật: người phê duyệt, thời điểm ISO-8601, quyết định và evidence/signature.
- Gói nghiệm thu/HANDOFF phản ánh trạng thái mới; không dựa vào approval ledger còn trống.

Agent không được tự tạo bằng chứng acceptance để mở gate cho chính mình.

### 5. Nếu gate CHƯA đạt

**Ngoại lệ hiện hành:** EDU-0054 P03-T01 đã được người dùng cho phép và triển khai. Không xóa hoặc phủ nhận module đó chỉ vì Phase 02 còn nợ; thay vào đó review EDU-0054 độc lập. Hạn chế dưới đây tiếp tục áp dụng cho việc mở rộng ngoài P03-T01.

**Không tạo module Phase 03, migration, API, UI hoặc seed mới.** Chỉ làm một trong các closeout task dưới đây nếu actor đủ độc lập; mỗi nhóm là task riêng:

1. Re-review EDU-0046/0048 nếu không phải fixer. Task review không sửa source; nếu phát hiện finding mới, ghi `NEEDS_CHANGES` và dừng phần sửa.
2. Sửa UI49-F01 nếu không phải người phát hiện/reviewer finding. Làm tối thiểu bằng fail-first hit-area test và CSS cần thiết; giữ nguyên theme/icon/tint EDU-0051. Fixer không tự re-review.
3. Cập nhật acceptance package/HANDOFF bằng sự thật mới, nhưng không ký thay Product/Security/DB authority.
4. Nếu chỉ còn quyết định/chữ ký con người, lập blocker ngắn gồm: quyết định cần ai, tài liệu nào, tác động và lựa chọn hiện có. Không viết code dự phòng cho mọi phương án.

Kết thúc lượt với trạng thái `Phase 03 NOT STARTED — prerequisite not met` nếu gate vẫn mở.

### 6. Nếu gate ĐÃ đạt — chỉ kickoff P03-T01

Tạo task riêng và chỉ thực hiện **P03-T01: định nghĩa constraint và state transition cho school, academic year, academic term**. Không gộp P03-T02..T09.

Trước implementation, ghi expected behavior và failure cases trong journal:

- `start_date < end_date`; term phải nằm hoàn toàn trong academic year.
- Không cho khoảng năm/term không hợp lệ hoặc trạng thái chuyển ngược trái policy.
- Mỗi school chỉ có tối đa một active year tại một thời điểm.
- Archived year là read-only; lịch sử không bị overwrite.
- Scope lấy từ authorized request context, không lấy từ đồng hồ hoặc lựa chọn frontend.
- `DATE` dùng cho ngày; timezone school có cấu hình, không hardcode ngày khai giảng/kết thúc.
- Sai school/year scope phải fail closed.
- Concurrency/revision conflict phải được nêu rõ; không silently last-write-wins.

Lát cắt nhỏ nhất được phép:

1. Chốt tên trạng thái và transition table từ requirement đã duyệt.
2. Cập nhật đúng một nguồn kiến trúc hiện có nếu cần; không tạo baseline/phase spec cạnh tranh.
3. Nếu thêm pure domain validation, viết fail-first unit tests trước và giữ module trong `backend/app/modules/academic_years/`.
4. **Không tạo migration ở P03-T01**; migration/index thuộc P03-T03 và cần schema/reviewer riêng.
5. Không thêm Student/Class/Teacher/Subject CRUD, year selector UI, 2k seed hay E2E trong task này; chúng thuộc P03-T02/P03-T04..T09.
6. Bàn giao P03-T01 ở `in_review`; reviewer phải khác implementer trước task tiếp theo.

Nếu OD-002/005/006/008 còn ảnh hưởng trực tiếp đến thiết kế, dừng đúng phần đó. Chỉ dùng invariant đã xác nhận; không tự chọn lịch năm học, campus hierarchy, student fields hoặc semantics scope.

### 7. Chống over-engineering

- Giữ FastAPI modular monolith và pattern hiện có; không thêm microservice, CQRS, event sourcing, plugin engine, rules DSL hoặc generic repository framework.
- Một trường trong MVP; giữ `school_id` boundary nhưng không làm multi-tenant SaaS, billing hay tenant admin.
- Không làm import/export ở Phase 03; CSV staging/rollback thuộc Phase 04.
- Không làm calendar/timetable/solver, gradebook, analytics, ML hoặc legal sync.
- Không thêm cache, queue, background worker hay benchmark nếu acceptance của lát cắt không cần.
- Không thêm field hồ sơ “phòng khi cần”. Chỉ dùng field đã được requirement/OD phê duyệt.
- Ưu tiên constraint DB/domain rõ ràng và test nhỏ hơn abstraction tổng quát.
- Không refactor file không liên quan chỉ để “dọn đẹp”.

### 8. Verification tối thiểu

Luôn chạy từ root và ghi exit code thật:

```powershell
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python -m unittest discover -s tests -p test_*.py
python scripts/sync_task_board.py
```

Nếu chạm backend: Ruff, host pytest và OpenAPI drift check. Nếu chạm contract/frontend: generated type check, frontend typecheck/lint/format/unit/build. Nếu chạm DB: PostgreSQL cô lập, Alembic current/check/upgrade/downgrade phù hợp và migration review. Không chạy full matrix chỉ để trang trí; chạy theo rủi ro và giải thích phần không chạy.

### 9. Bàn giao bắt buộc

- Journal có actor/role, phạm vi, changed files, fail-first/pass-after, lệnh/exit code, issue và Git fields thật.
- Evidence được sanitize; không lưu DSN, password, token hoặc dữ liệu thật.
- Ghi mọi side effect: `dist`, `test-results`, cache, mtime, process, container, volume, file tạm.
- Regenerate `TASK_BOARD.md`; cập nhật `HANDOFF.md` và prompt kế tiếp nếu trạng thái thay đổi.
- Đo lại HTTP/listener/container/Git ngay trước báo cáo.
- Không dùng từ `accepted`, `done`, `ready` nếu chỉ có test xanh nhưng thiếu reviewer/authority.

Báo cáo cuối phải nói rõ một trong hai kết quả:

1. `Phase 03 NOT STARTED — prerequisite not met`, kèm blocker/owner/evidence; hoặc
2. `P03-T01 implemented and IN_REVIEW`, kèm exact files/tests và xác nhận P03-T02..T09 chưa bắt đầu.

## Kết thúc prompt
