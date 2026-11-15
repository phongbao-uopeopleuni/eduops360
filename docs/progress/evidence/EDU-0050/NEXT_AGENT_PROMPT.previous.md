# Prompt bàn giao cho AGENT tiếp theo — EduOps 360 (cập nhật 2026-11-14 21:50 +07:00)

Sao chép toàn bộ nội dung từ mục **Bắt đầu prompt** đến **Kết thúc prompt** cho agent tiếp theo.

Tạo bởi EDU-0045. Prompt này thay prompt EDU-0043 (prompt đó chưa được thực thi). Bản cũ được giữ nguyên tại `docs/progress/evidence/EDU-0045/NEXT_AGENT_PROMPT.previous.md`. Prompt là chỉ dẫn thực thi, không phải đặc tả hay sổ phê duyệt.

---

## Bắt đầu prompt

Bạn là **agent tiếp theo** làm việc trên dự án **EduOps 360** tại `D:\eduops360`. Bạn có thể là Codex hoặc một agent khác.

**Quan trọng nếu bạn là Claude:** Claude đã làm EDU-0032, 0042, 0043, 0044 và 0045. Vì vậy Claude **không được** làm Việc A, B, C (sửa finding mà chính Claude tìm ra) hay Việc D (review giao diện mà chính Claude làm). Nếu bạn là Claude, chỉ làm Việc E, hoặc re-review bản sửa A–C do actor khác làm. Báo người dùng phần còn lại cần một agent khác.

### 0. Tóm tắt trong một phút

- **Ứng dụng:** web quản lý học vụ cho một trường, lớp 1–12. Backend FastAPI + PostgreSQL, frontend React + Vite + TypeScript. Chỉ chạy local, chỉ dùng dữ liệu tổng hợp. Thư mục **không phải Git repository**.
- **Đã có:**
  - Nền tảng Phase 01.
  - IAM Phase 02: đăng nhập, phiên, CSRF, phân quyền theo scope, audit, quản trị người dùng.
  - Giao diện mới theo đặc tả "Minimalist SaaS" (EDU-0044).
  - Chưa có module học sinh, thời khóa biểu hay khảo thí.
- **Trạng thái:** Phase 00/01/02 đều **NOT ACCEPTED**.
  - Phase 01 đạt gate kỹ thuật.
  - Phase 02 **NEEDS_CHANGES** theo review EDU-0042: một P1 (R42-F01), một P2 (R42-F02) và ba P3 (R42-F03..F05).
  - Giao diện EDU-0044 đang chờ review độc lập.
- **Việc tiếp theo, theo thứ tự ưu tiên:**
  - **A.** Sửa R42-F01 (P1).
  - **B.** Soạn decision brief cho R42-F02 (P2).
  - **C.** Sửa R42-F03..F05 (P3).
  - **D.** Review độc lập giao diện EDU-0044.
  - **E.** Cập nhật gói nghiệm thu, HANDOFF và prompt cho người kế tiếp.
- Không nghiệm thu phase. Không quyết định OD. Không bắt đầu Phase 03.

### 1. Định nghĩa "xong"

1. R42-F01 đã sửa, có regression live trên PostgreSQL cho hai biến thể (reset và invitation); toàn bộ suite xanh.
2. R42-F02 có decision brief ghi `NOT APPROVED`. Chỉ có code khi người dùng chọn phương án rõ ràng trong phiên.
3. R42-F03..F05 đã xử lý tối thiểu. Phần nào cần quyết định thì ghi blocker kèm phương án.
4. EDU-0044 có báo cáo review độc lập, kết luận `PASS`, `PASS_WITH_NOTES` hoặc `NEEDS_CHANGES`. Reviewer không tự sửa finding của mình.
5. Mọi gate xanh (host, PostgreSQL cô lập, frontend, E2E kể cả real-auth, governance). Evidence có lệnh và exit code.
6. Gói nghiệm thu và HANDOFF nói đúng sự thật:
   - Phase 02 **chỉ** được ghi `READY_FOR_HUMAN_ACCEPTANCE` khi R42-F01 đã sửa **và** đã được re-review bởi một actor khác người sửa.
   - Nếu R42-F02 chưa có quyết định, phải ghi nó là P2 còn mở chờ Security Owner. Không ghi "không còn P1/P2".
7. Mọi task mới ở trạng thái `in_review`, có ghi rõ ai được phép review.

### 2. Ranh giới, thẩm quyền và quyền được cấp

- Chỉ làm trong `D:\eduops360`. Đọc `AGENTS.md` trước mọi hành động.
- Không tự accept, tự approve, merge hay deploy. Không dùng dữ liệu học sinh thật hay production credential.
- Chỉ DEC-001..008 là quyết định đã xác nhận. OD-001..013, giá trị `TẠM` và mọi đề xuất đều chưa được duyệt.
- **Ma trận độc lập** (người review khác người sửa):

| Việc | Ai được làm | Ai được review |
|---|---|---|
| A, B, C (R42) | Agent khác Claude (Claude tìm ra finding và thiết kế F01 ở EDU-0032) | Actor khác người sửa; Claude được re-review |
| D (review EDU-0044) | Agent khác Claude (Claude implement EDU-0044) | — (đây là việc review) |
| E (gói/HANDOFF/prompt) | Bất kỳ ai | Con người có thẩm quyền |

- **Docker:** được dùng Compose project cô lập theo task (ví dụ `eduops360-<task>`), chỉ service `db`, mật khẩu tổng hợp ngẫu nhiên, cổng localhost 55xxx còn trống.
  - Chỉ `down -v` project do bạn tạo. Không đụng `eduops360-local_*`, `eduops360-audit-0011_*` hay `eduops360-dev` (môi trường dev của người dùng, xem mục 6).
  - Lúc bàn giao EDU-0045, Docker Desktop **đang chạy** do người dùng bật. Ghi trạng thái ban đầu và trả về đúng trạng thái đó. Xác nhận bằng `docker desktop status`; không gọi `docker version` ngay sau khi stop vì có thể làm Desktop chạy lại.
- **Git:** không `git init`, commit, push, tạo remote hay PR.
- **Mạng và dependency:** không cài thêm package, không đổi lockfile, không truy cập package index. Font đã được cài ở EDU-0044 theo phê duyệt của người dùng.
- **File `.env` thật** (`backend/.env`, `infra/.env`): không đọc, in, sửa hay sao chép.
  - Mọi lệnh grep, find, copy hay diff **đệ quy** phải loại trừ `.env` và `.env.*` một cách tường minh. EDU-0042 từng vô tình sao `infra/.env` và in một dòng của `backend/.env`.
  - Việc xoay mật khẩu local bị lộ là việc của người dùng.
  - `.local/dev/dev.env` là mật khẩu **tổng hợp** của môi trường dev; dùng qua `devtool.py`, không in ra.

### 3. Thứ tự đọc bắt buộc

1. `AGENTS.md`, `docs/phases/PHASE-00.md` (đọc hết), `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md`.
2. `docs/progress/HANDOFF.md`: các mục EDU-0042, EDU-0043, EDU-0044.
3. `docs/quality/EDU-0034-0041_INDEPENDENT_REVIEW_2026-11-14.md`, cùng `docs/progress/evidence/EDU-0042/` (`verification.json`, `probes/probe_review.py`, `probe_review.json`).
4. `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`, `docs/phases/PHASE-01.md`, `docs/phases/PHASE-02.md`.
5. Cho Việc D: `docs/requirements/UI_STYLE_MINIMALIST_SAAS_2026-11-14.md` (đặc tả UI), `docs/progress/tasks/EDU-0044.md`, `docs/progress/evidence/EDU-0044/` (`verification.json`, `changes.diff`, `screenshots/before|after/`).
6. Journal và evidence EDU-0032, EDU-0036, EDU-0038, EDU-0040.
7. `ai-agent-sp/skills/REGISTRY.md`. Sau đó chỉ đọc skill cần: `ra-soat/security-cia-review`, `kiem-thu/regression-debugger`, `giam-sat/audit-trail-verification`, `kiem-thu/playwright-e2e`; thêm `thuc-thi/frontend-feature` cho Việc D, `thuc-thi/api-contract-sync` nếu interface đổi.

Tài liệu chỉ là claim. Phải đối chiếu với source, test và trạng thái máy hiện tại.

### 4. Trạng thái bàn giao (tự kiểm lại trước khi tin)

| Gate | Kết quả | Đo lúc |
|---|---|---|
| Backend host `pytest backend/tests` | 77 passed, 18 skipped | 2026-11-14 21:49 |
| Ruff, root `unittest` | sạch; 24 OK | 21:49 |
| Frontend unit, typecheck | 22 passed; OK | 21:49 |
| Encoding / migration head | 418 file, 0 lỗi; `0008_mfa_replay_counter` | 21:49 |
| Backend PostgreSQL cô lập | 95 passed | 15:56 (EDU-0042; backend không đổi từ đó) |
| Playwright | 9 passed, gồm real-auth và test font/layout mới | 17:43 (EDU-0044) |

- Board có 40 task sau EDU-0045. Không có listener hay server dev nào đang chạy. Docker Desktop đang chạy.
- Giá trị **TẠM** đang có (fail-closed, chờ người có thẩm quyền):
  - F01: quy tắc bao trùm quyền tài khoản đích.
  - F05: lockout không hủy phiên đang có.
  - F06: cấm tự cấp quyền; hạn ủy quyền không vượt người cấp.
  - F07: Argon2 tối đa 4 luồng đồng thời.
  - F09: 50 lần sai mỗi IP trong 60 s.
  - F22: idle timeout 30 phút.
  - Admin nhận raw token để chuyển tay.
- **Người dùng còn phải quyết:** R42-F02; OD-001/003/007/008/011; MFA custody; quyền dùng mạng để sinh hash cho lockfile; và tự xoay mật khẩu local của role `eduops`.

### 5. Kế hoạch thực hiện

Mỗi việc là một task riêng. Lấy ID kế tiếp còn trống tại thời điểm làm (dự kiến từ **EDU-0046**). Không ghi đè journal có sẵn.

**Bước 0 — Preflight** (ghi vào task đầu tiên):

1. Chạy `git status -sb`; kỳ vọng exit 128.
2. Kiểm tra listener và process; ghi trạng thái Docker Desktop.
3. Chụp snapshot Docker nếu Docker đang chạy.
4. Lập manifest SHA-256 cho source, **loại trừ `.env*`**, `.venv`, `node_modules`, `.local`, cache, `dist`, `test-results`.
5. Sao baseline vào `.local/<task>/baseline/`.
6. Chạy lại gate host.

Nếu số liệu lệch so với mục 4, hoặc có file đang bị actor khác sửa: **dừng lại và điều tra.**

**Việc A — R42-F01 (P1): kiểm lại quy tắc bao trùm lúc dùng token.**

*Nguyên nhân:* `_require_actor_covers_target` (`backend/app/modules/auth/admin_router.py`) chỉ chạy lúc phát hành token (`issue_password_reset`, `create_user_invitation`, `reissue_user_invitation`). Lúc dùng token (`backend/app/modules/auth/router.py`: `_consume_account_token`, `accept_invitation`, `accept_password_reset`) thì không kiểm lại. Vì vậy token phát hành khi tài khoản đích chưa có quyền vẫn dùng được sau khi tài khoản đó được nâng quyền.

*Sửa tối thiểu*, trong cùng transaction, **sau** lần đọc lại có khóa (giữ thứ tự khóa F04 và `populate_existing=True`) và **trước** mọi thay đổi:

1. Nạp quyền hiệu lực **hiện tại** của người phát hành (`token.created_by`).
2. Yêu cầu người phát hành vẫn có quyền phát hành tương ứng ở scope toàn cục: `user:password_reset` cho reset, `user:create` cho invitation.
3. Yêu cầu người phát hành vẫn bao trùm mọi grant chưa hết hạn của tài khoản đích, kể cả grant chưa bắt đầu. Tái dùng logic hiện có, không nhân bản và không refactor rộng.
4. Không đạt → `400 ACCOUNT_TOKEN_INVALID`, ghi failure vào limiter, không đổi mật khẩu hay trạng thái.

Ghi trong journal: token bị từ chối có bị vô hiệu luôn không (lưu ý request lỗi sẽ rollback); và có từ chối token do người nay đã bị đình chỉ phát hành không (TẠM, chờ Security Owner). Không đổi việc cho cấp role cho tài khoản `pending`; đó là câu hỏi OD-008.

*Regression* (fail trước, pass sau, live trong `backend/tests/integration/`):

- **RA:** actor chỉ có `user:password_reset` phát hành reset; tài khoản đích sau đó được nâng quyền; dùng token → 400, mật khẩu và trạng thái không đổi.
- **RB:** actor chỉ có `user:create` giữ token lời mời; tài khoản pending sau đó được cấp role; accept → 400, tài khoản vẫn `pending`.
- **Trường hợp dương:** người phát hành vẫn bao trùm → dùng token thành công; tài khoản đích không đổi quyền → vẫn thành công.
- Test F04 đồng thời và audit `issued_by` vẫn xanh.

Kịch bản tham khảo: `probe_reset_toctou` và `probe_invitation_toctou` trong `docs/progress/evidence/EDU-0042/probes/probe_review.py`. Dùng role tổng hợp riêng; không sửa mapping toàn cục.

**Việc B — R42-F02 (P2): decision brief, không tự đổi chính sách.**

*Hiện trạng:* limiter theo IP (`login_ip_rate_limit_attempts = 50`, TẠM) chặn mọi đăng nhập từ cùng peer. 50 lần sai với email ngẫu nhiên khiến tài khoản khác nhận 429 dù nhập đúng mật khẩu. `client_ip` chỉ dùng direct peer.

*Brief* ghi `NOT APPROVED`, kèm trade-off của từng phương án:

- (A) Tắt cửa sổ theo IP mặc định cho tới khi có trusted proxy. Đổi lại, spraying quay về như F09; chỉ còn lockout theo tài khoản.
- (B) Giữ cửa sổ theo IP nhưng đổi ngưỡng hoặc ngữ nghĩa.
- (C) Trusted proxy kèm ngưỡng cao hơn. Không giải quyết trường hợp NAT.
- (D) Trì hoãn tăng dần thay vì chặn cứng.

*Ràng buộc:* phản hồi 429 hay 200 không được phụ thuộc mật khẩu đúng hay sai (oracle A0102-F02). Chỉ viết code khi người dùng chọn phương án; khi đó viết regression theo kịch bản RC. Nếu chưa có quyết định, giữ nguyên code và ghi blocker.

**Việc C — R42-F03..F05 (P3).**

- **F03:** giới hạn số phần tử được quét trong `rate_limit.py:record_failure` khi bảng đầy. Giữ nguyên key đang bị chặn. Ghi rõ hành vi khi bão hòa. Regression: số phần tử kiểm cho mỗi key mới không vượt giới hạn.
- **F04:** đưa helper seed fixture real-auth vào file tracked, ví dụ `scripts/seed_real_auth_e2e.py`. Helper chỉ dùng dữ liệu tổng hợp, bắt buộc `EDUOPS_TEST_MIGRATOR_DSN`, không in credential.
  - Tài liệu hóa `EDUOPS_SESSION_COOKIE_SECURE=false`, chỉ dùng cho HTTP cô lập.
  - Thêm opt-in `PLAYWRIGHT_REQUIRE_REAL_AUTH=1`: khi bật mà thiếu fixture thì test fail thay vì skip.
  - Có thể tham khảo `.local/dev/devtool.py` (lệnh `seed`).
- **F05:** thêm correction append-only, timestamp thật, vào `docs/progress/tasks/EDU-0040.md`.
  - Liệt kê 14 file đã format: `app/modules/audit_logs/models.py`, `service.py`; `app/modules/auth/admin_router.py`, `models.py`, `rate_limit.py`, `router.py`; `migrations/versions/0002_auth_users.py`, `0003_audit_logs.py`, `0007_account_tokens.py`; `tests/auth/test_permissions.py`, `test_schema_alignment.py`, `test_services.py`; `tests/integration/test_auth_api.py`, `test_auth_remediation.py`.
  - Ghi rằng EDU-0042 đã xác minh 3 migration chỉ đổi định dạng. Không bịa lịch sử.
  - Thêm quy ước ngắn: không format lại migration đã áp dụng nếu chưa qua review migration.

**Việc D — Review độc lập giao diện EDU-0044** (không sửa source trong task này).

- So sánh với `docs/requirements/UI_STYLE_MINIMALIST_SAAS_2026-11-14.md`: 14 mục checklist, token màu và typography, khoảng cách, radius, shadow, component, responsive, motion.
- Xác nhận hoặc phản bác ba điểm lệch có chủ đích:
  - **Be Vietnam Pro thay Poppins.** Poppins thiếu U+1EA0–1EF1.
  - **Bảng màu tối tự suy ra.** Đặc tả chỉ có giao diện sáng.
  - **Bỏ scroll-reveal.**
- Accessibility:
  - Bàn phím: skip link, focus ring, thứ tự tab.
  - Trình đọc màn hình: heading đúng cấp, `aria`, phần minh họa có `aria-hidden`.
  - Tương phản ở cả hai theme.
  - Vùng chạm ≥ 44 px.
  - `prefers-reduced-motion`.
- **Trung thực nội dung:** trang Tổng quan không được ngụ ý module chưa có là đã có (ô lộ trình ghi "chưa triển khai", badge đồng hồ).
- **Hành vi không đổi:** so `changes.diff` với baseline; label và luồng đăng nhập/mời không đổi.
- Có thể chụp lại ảnh bằng `node .local/edu-0044/shoot.mjs <thư mục ra>` (cần server dev chạy, xem mục 6).
- Kết quả ghi vào `docs/quality/EDU-0044_UI_REVIEW_<YYYY-MM-DD>.md`. Mỗi finding có mức độ, cách tái hiện và ảnh hoặc bằng chứng. Finding phải do actor khác người review sửa.

**Việc E — Cập nhật gói nghiệm thu và bàn giao.**

- Thêm R42-F01..F05 và kết quả review EDU-0044 vào `PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md` (hoặc bản mới có ngày): sổ finding, bảng giá trị TẠM, decision brief R42-F02.
- Kết luận Phase 02 tuân thủ mục 1.6. Sổ phê duyệt để trống.
- Cập nhật HANDOFF; viết prompt cho người kế tiếp, sao lưu prompt cũ trước khi ghi đè.

### 6. Môi trường và lệnh (Windows, đã kiểm chứng)

**Môi trường dev của người dùng** (dùng để xem và chụp UI; **không** dùng để chạy test ghi dữ liệu):

- Bật: `powershell -ExecutionPolicy Bypass -File D:\eduops360\.local\dev\start-dev.ps1`. Lệnh này khởi động DB `eduops360-dev` (cổng 55440), migrate, seed admin tổng hợp, rồi mở hai cửa sổ: API 127.0.0.1:58080 và UI 127.0.0.1:5173.
- Tắt: `powershell -ExecutionPolicy Bypass -File D:\eduops360\.local\dev\stop-dev.ps1`. Thêm `-StopDocker` để tắt Docker Desktop; `-Reset` để xóa dữ liệu dev.
- Tài khoản admin tổng hợp nằm trong `.local/dev/admin-login.txt`. Không in mật khẩu vào log hay báo cáo.

**Gate host:**

```powershell
cd D:\eduops360
python scripts/validate_blueprint.py; python scripts/check_structure.py; python scripts/check_text_encoding.py
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python -m unittest discover
backend\.venv\Scripts\python.exe -m ruff check backend tests/foundation
backend\.venv\Scripts\python.exe -m ruff format --check backend tests/foundation
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
backend\.venv\Scripts\python.exe scripts/export_openapi.py --check
```

**Frontend** (trong `frontend/`): `npm run typecheck`, `lint`, `format:check`, `api:check`, `test`, `build`.

**PostgreSQL cô lập cho test:**

1. Env file trong `.local/<task>/` gồm `POSTGRES_MIGRATOR_PASSWORD`, `POSTGRES_RUNTIME_PASSWORD`, `POSTGRES_AUDIT_WORKER_PASSWORD` (ngẫu nhiên, không in ra) và `DATABASE_PORT`.
2. `docker compose -p eduops360-<task> --env-file .local\<task>\<file>.env -f infra\compose.dev.yml up -d db --wait`.
3. Chờ cổng TCP sẵn sàng.
4. Đặt `EDUOPS_DATABASE_URL` là DSN migrator tường minh, rồi chạy `alembic upgrade head`, `current`, `check`.
5. Chạy test với `EDUOPS_TEST_MIGRATOR_DSN`, `EDUOPS_TEST_RUNTIME_DSN`, `EDUOPS_TEST_AUDIT_WORKER_DSN`.
6. Teardown: `down -v` đúng project, rồi xóa env file.

**E2E:**

- Không dùng cổng 8000 (nằm trong dải Windows loại trừ).
- API trên cổng 58xxx còn trống, với `EDUOPS_DATABASE_URL` là DSN runtime và `EDUOPS_SESSION_COOKIE_SECURE=false`.
- Vite: `API_PROXY_TARGET=http://127.0.0.1:<port> npm run dev -- --host 127.0.0.1 --port 5173 --strictPort`.
- Chạy: `PLAYWRIGHT_EXTERNAL_SERVER=1 PLAYWRIGHT_CHANNEL=chrome PLAYWRIGHT_REAL_AUTH_EMAIL=... PLAYWRIGHT_REAL_AUTH_PASSWORD=... npx playwright test`.
- Sau khi dừng npm, tiến trình node của Vite có thể còn giữ 5173. Kiểm PID và command line rồi mới dừng.

**Khi interface đổi:** chạy `scripts/export_openapi.py` (không có `--check`) và `npm run api:generate`, rồi kiểm lại `--check` và `api:check`.

**Probe hoặc test đồng thời:** mỗi worker dùng một FastAPI app riêng. Dùng chung app cho nhiều `TestClient` trong nhiều thread sẽ gây treo (đã gặp ở EDU-0042).

**Quy ước sửa file:** dùng `apply_patch`. Giữ nguyên kiểu xuống dòng CRLF/LF của từng file. Không có Git, nên evidence mỗi task phải có `changes.diff` so với baseline.

### 7. Quy tắc evidence và kiểm chứng

- **Fail trước:** chạy test mới trên code chưa sửa và lưu output fail. Nếu test chỉ fail vì API chưa tồn tại, ghi rõ.
- Mỗi task có `docs/progress/evidence/<task>/verification.json`, ghi lệnh, cwd, `started_at` (+07:00), `exit_code` và kết quả. Không ghi timestamp cho thời điểm chưa diễn ra; giá trị nào không đo thì ghi "không đo".
- **Kiểm chứng lại ngay trước khi bàn giao:** sau lần sửa file cuối cùng, chạy lại mọi lệnh trạng thái sắp khẳng định (test, manifest, Docker, listener). Khi khẳng định về một dòng hay khối code, đọc hết dòng hoặc khối đó.
- Chỉ dùng dữ liệu tổng hợp và role tổng hợp riêng. Không ghi secret vào log hay evidence. Quét evidence trước khi publish, **có loại trừ `.env`**.
- Kê khai đủ tác dụng phụ, kể cả `frontend/dist`, `frontend/test-results`, `.local/`.

### 8. Điểm dừng bắt buộc

- Cần quyết định OD hoặc Security Owner (R42-F02, trạng thái người phát hành, cấp role cho `pending`): dừng phần đó, ghi blocker kèm phương án.
- Baseline lệch, hoặc có actor khác đang sửa file: dừng và báo người dùng.
- Cần mạng, cài package, khởi tạo Git hoặc chạm `.env` thật: hỏi người dùng trước.
- Gate vẫn fail sau khi sửa: giữ evidence fail, không đánh dấu xong.
- Bạn là Claude và việc được giao là A, B, C hoặc D: dừng và báo người dùng cần agent khác.

### 9. Bàn giao cuối lượt

- Với mỗi task:
  - Frontmatter đầy đủ.
  - Activity log append-only, có timezone.
  - Evidence riêng.
  - Status `in_review`.
  - commit, push, PR, merge đều `not_done`.
- Cập nhật HANDOFF và gói nghiệm thu theo Việc E. Chạy `python scripts/sync_task_board.py`; không sửa tay board.
- Không sửa `docs/phases/PHASE-00.md`. Không chuyển OD thành DEC. Không điền sổ phê duyệt.
- Báo cáo cho người dùng, mở đầu bằng kết quả, gồm:
  - Phần đã sửa hoặc review, kèm test fail trước và pass sau.
  - Phần fail hoặc `not_run`.
  - Quyết định đang chờ (đặc biệt R42-F02).
  - Đường dẫn file quan trọng.
  - Mọi tác dụng phụ.
  - Ai cần review tiếp.

## Kết thúc prompt
