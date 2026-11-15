# Prompt bàn giao cho Codex — sửa finding review EDU-0042 (R42-F01..F05)

Sao chép toàn bộ nội dung từ mục **Bắt đầu prompt** đến **Kết thúc prompt** cho Codex.

Tạo bởi EDU-0043 (2026-11-14). Prompt reviewer trước đó (EDU-0041) được giữ nguyên tại `docs/progress/evidence/EDU-0043/NEXT_AGENT_PROMPT.previous.md`. Prompt là chỉ dẫn thực thi, không phải đặc tả hay sổ phê duyệt.

---

## Bắt đầu prompt

Bạn là **Codex**, đóng vai **remediation implementer** cho các finding mà Claude tìm ra khi review độc lập EDU-0034..0041 (task EDU-0042). Dự án: **EduOps 360**, tại `D:\eduops360`.

**Mục tiêu:**

- Sửa tối thiểu **R42-F01 (P1)** và các finding P3 **R42-F03..F05**. Mỗi bản sửa có regression test chạy fail trước, pass sau.
- Với **R42-F02 (P2)**: chuẩn bị bản đề xuất quyết định (decision brief) cho Security Owner. Chỉ triển khai khi người dùng chọn phương án rõ ràng trong phiên.
- Cập nhật gói nghiệm thu cho đúng sự thật.

Không nghiệm thu phase. Không quyết định OD. Không bắt đầu Phase 03.

### 1. Định nghĩa "xong"

1. R42-F01 đã sửa, có regression live trên PostgreSQL cho cả hai biến thể (reset và invitation), toàn bộ suite xanh.
2. R42-F03, F04, F05 đã xử lý tối thiểu. Cái nào cần quyết định thì ghi blocker kèm phương án.
3. R42-F02: decision brief ghi `NOT APPROVED`. Chỉ có code nếu người dùng đã chọn phương án trong phiên.
4. Mọi gate xanh (host, PostgreSQL cô lập, frontend, E2E kể cả real-auth, governance). Evidence có lệnh và exit code.
5. Gói nghiệm thu, sổ finding và HANDOFF được cập nhật:
   - Phase 02 **chỉ** được ghi `READY_FOR_HUMAN_ACCEPTANCE` khi R42-F01 đã sửa **và** đã được re-review bởi một actor khác Codex.
   - Nếu R42-F02 chưa có quyết định, phải liệt kê nó là P2 còn mở chờ Security Owner. Không được ghi "không còn P1/P2".
6. Mọi task mới ở trạng thái `in_review`. Người review lại phải là actor khác Codex.

### 2. Ranh giới, thẩm quyền và quyền được cấp

- Chỉ làm trong `D:\eduops360`. Đọc `AGENTS.md` trước mọi hành động.
- Không tự accept, tự approve, merge hay deploy. Không dùng dữ liệu học sinh thật hay production credential.
- Chỉ DEC-001..008 là quyết định đã xác nhận. OD-001..013, giá trị `TẠM` và mọi đề xuất đều chưa được duyệt.
- **Tính độc lập:**
  - Claude là reviewer của EDU-0042, còn bạn thì không, nên bạn được sửa các finding R42.
  - Bạn implement EDU-0036, 0038 và 0040 (nguồn của R42-F02..F05). Sửa code của chính mình thì được, nhưng **không được tự review** bản sửa.
  - R42-F01 nằm trong thiết kế F01 của EDU-0032 (Claude implement). Bạn sửa được, vì Claude không sửa finding của vòng review mình.
- **Docker (người dùng cấp trong prompt này):**
  - Chỉ dùng một Compose project cô lập theo task (ví dụ `eduops360-edu0044`), chỉ service `db`, mật khẩu tổng hợp ngẫu nhiên, cổng localhost 55xxx còn trống.
  - Chỉ `down -v` project do bạn tạo. Không đụng `eduops360-local_postgres-data`, `eduops360-audit-0011_*` hay image có sẵn.
  - Nếu Docker Desktop đang dừng lúc bắt đầu, cuối lượt phải dừng lại. Xác nhận bằng `docker desktop status`; không gọi `docker version` ngay sau khi stop vì có thể làm Desktop chạy lại (đã gặp ở EDU-0042).
- **Git:** không `git init`, commit, push, tạo remote hay PR. Thư mục không phải repository.
- **Mạng và dependency:** không cài package, không đổi lockfile, không truy cập package index.
- **File `.env` thật** (`backend/.env`, `infra/.env`): không đọc, không in, không sửa, không sao chép.
  - Mọi lệnh grep, find, copy hay diff **đệ quy** phải loại trừ `.env` và `.env.*` một cách tường minh (ví dụ `--exclude='.env' --exclude='.env.*'`, hoặc lọc trong Python walk).
  - EDU-0042 đã vô tình sao `infra/.env` và in một dòng của `backend/.env` vì quên loại trừ. Đừng lặp lại.
  - Việc xoay mật khẩu local bị lộ là việc của người dùng, không phải của bạn.

### 3. Thứ tự đọc bắt buộc

1. `AGENTS.md`, `docs/phases/PHASE-00.md` (đọc hết), `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md`.
2. `docs/progress/HANDOFF.md` (mục EDU-0042) và `docs/quality/EDU-0034-0041_INDEPENDENT_REVIEW_2026-11-14.md`.
3. `docs/progress/tasks/EDU-0042.md` và `docs/progress/evidence/EDU-0042/`: `verification.json`, cùng `probes/probe_review.py` và `probe_review.json`, là kịch bản tái hiện R42-F01..F03.
4. `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`, `docs/phases/PHASE-02.md`.
5. Journal và evidence EDU-0032, EDU-0036, EDU-0038, EDU-0040.
6. `ai-agent-sp/skills/REGISTRY.md`. Sau đó chỉ đọc skill cần: `ra-soat/security-cia-review`, `kiem-thu/regression-debugger`, `giam-sat/audit-trail-verification`, `kiem-thu/playwright-e2e`; thêm `thuc-thi/api-contract-sync` nếu interface đổi.

Tài liệu chỉ là claim. Phải đối chiếu với source, test và trạng thái máy hiện tại.

### 4. Trạng thái bàn giao (tự kiểm lại trước khi tin)

- Phase 01/02 **NOT ACCEPTED**. Theo EDU-0042: Phase 01 đạt gate kỹ thuật; Phase 02 **NEEDS_CHANGES**.
- Số liệu lúc 2026-11-14 16:18 +07:00:
  - Backend host: 77 passed, 18 skipped.
  - PostgreSQL 18 cô lập: 95 passed.
  - Frontend: 22 unit test. Playwright: 8 passed, gồm real-auth.
  - Root: 24 test. Alembic head `0008_mfa_replay_counter`.
  - Encoding: 0 lỗi. Số file tăng theo tài liệu mới, nên đừng coi số file là cố định.
- Board có 38 task sau EDU-0043. Docker Desktop đang dừng. Không có listener hay process của dự án.

### 5. Kế hoạch thực hiện

Mỗi bước là một task riêng. Lấy ID kế tiếp còn trống (dự kiến bắt đầu từ **EDU-0044**). Không ghi đè journal có sẵn.

**Bước 0 — Preflight** (ghi vào task đầu tiên):

1. Chạy `git status -sb` và `git reflog`; kỳ vọng exit 128.
2. Kiểm tra listener và process.
3. Kiểm tra trạng thái Docker Desktop; nếu đang chạy thì chụp snapshot Docker.
4. Lập manifest SHA-256 cho source, **loại trừ `.env*`**.
5. Sao baseline vào `.local/<task>/baseline/`.
6. Chạy lại gate host.

Nếu số liệu lệch hoặc có actor khác đang sửa file, dừng lại và điều tra trước khi thay đổi gì.

**Bước 1 — R42-F01 (P1): kiểm lại quy tắc bao trùm lúc dùng token.**

*Nguyên nhân:* `_require_actor_covers_target` (`backend/app/modules/auth/admin_router.py`) chỉ chạy lúc phát hành (`issue_password_reset`, `create_user_invitation`, `reissue_user_invitation`). Lúc dùng token (`backend/app/modules/auth/router.py`: `_consume_account_token`, `accept_invitation`, `accept_password_reset`) thì không kiểm lại. Vì vậy token phát hành khi tài khoản đích chưa có quyền vẫn dùng được sau khi tài khoản đó được nâng quyền.

*Sửa tối thiểu:* trong cùng transaction, **sau** lần đọc lại có khóa (giữ nguyên thứ tự khóa của F04 và `populate_existing=True`), và **trước** mọi thay đổi:

1. Nạp quyền hiệu lực **hiện tại** của người phát hành (`token.created_by`).
2. Yêu cầu người phát hành vẫn còn quyền phát hành tương ứng ở scope toàn cục: `user:password_reset` cho reset, `user:create` cho invitation.
3. Yêu cầu người phát hành vẫn bao trùm mọi grant chưa hết hạn của tài khoản đích, kể cả grant chưa bắt đầu. Dùng cùng quy tắc với lúc phát hành; tái dùng logic hiện có, không nhân bản và không refactor rộng.
4. Không đạt → `400 ACCOUNT_TOKEN_INVALID`, ghi failure vào limiter, không đổi mật khẩu hay trạng thái tài khoản.

Ghi rõ trong journal hai lựa chọn của bạn:

- Token bị từ chối có bị vô hiệu luôn hay không. Nếu có, lưu ý request lỗi sẽ rollback transaction.
- Có từ chối token do người nay đã bị đình chỉ phát hành hay không. Đây là giá trị TẠM fail-closed, chờ Security Owner.

*Không làm:* không đổi việc cho phép cấp role cho tài khoản `pending`. Đó là câu hỏi OD-008, chỉ ghi vào decision brief.

*Regression (fail trước trên code hiện tại, pass sau), chạy live trên PostgreSQL trong `backend/tests/integration/`:*

- Biến thể RA: actor chỉ có `user:password_reset` phát hành reset. Tài khoản đích sau đó được nâng quyền. Dùng token → 400. Mật khẩu và trạng thái không đổi.
- Biến thể RB: actor chỉ có `user:create` giữ token lời mời. Tài khoản pending sau đó được cấp role. Accept → 400. Tài khoản vẫn `pending`.
- Trường hợp dương:
  - Người phát hành vẫn bao trùm sau khi tài khoản đích được nâng quyền (ví dụ actor có đủ quyền `user:*`) → dùng token vẫn thành công.
  - Tài khoản đích không đổi quyền → vẫn thành công.
- Các test F04 đồng thời và audit `issued_by` hiện có phải vẫn xanh.

Kịch bản tham khảo: `docs/progress/evidence/EDU-0042/probes/probe_review.py` (`probe_reset_toctou`, `probe_invitation_toctou`). Khi viết test, dùng role tổng hợp riêng; không sửa mapping toàn cục.

**Bước 2 — R42-F02 (P2): decision brief, không tự đổi chính sách.**

*Hiện trạng:* limiter theo IP (`login_ip_rate_limit_attempts = 50`, TẠM) chặn mọi đăng nhập từ cùng peer. Probe RC cho thấy: 50 lần sai với email ngẫu nhiên khiến tài khoản khác nhận 429 dù nhập đúng mật khẩu. `client_ip` chỉ dùng direct peer.

*Decision brief*, ghi `NOT APPROVED`, nêu trade-off đo được của từng phương án:

- (A) Tắt cửa sổ theo IP mặc định cho tới khi có thiết kế trusted proxy. Đổi lại, spraying qua nhiều tài khoản quay về như F09, chỉ còn lockout bền vững theo tài khoản.
- (B) Giữ cửa sổ theo IP, nhưng tách ngưỡng hoặc ngữ nghĩa.
- (C) Cấu hình trusted proxy kèm ngưỡng cao hơn. Cách này không giải quyết trường hợp NAT.
- (D) Trì hoãn tăng dần thay vì chặn cứng.

*Ràng buộc với mọi phương án:* không được để phản hồi 429 hay 200 phụ thuộc vào việc mật khẩu đúng hay sai, vì đó chính là oracle của A0102-F02.

*Triển khai:* chỉ khi người dùng chọn phương án rõ ràng trong phiên. Khi đó viết regression theo kịch bản RC. Nếu không có quyết định, giữ nguyên code và ghi blocker.

**Bước 3 — R42-F03 (P3): giới hạn quét khi limiter bão hòa.**

- `backend/app/modules/auth/rate_limit.py:record_failure`: giới hạn số phần tử được quét khi tìm key để đẩy ra.
- Vẫn giữ nguyên key đang bị chặn.
- Ghi rõ hành vi khi mọi slot đều bị chặn (định danh mới không được theo dõi; lockout bền vững vẫn là lớp bảo vệ chính).
- Regression: số phần tử được kiểm cho mỗi key mới không vượt quá giới hạn; key bị chặn không bị đẩy ra.

**Bước 4 — R42-F04 (P3): E2E real-auth tái lập được từ file tracked.**

- Đưa helper seed fixture vào file tracked, ví dụ `scripts/seed_real_auth_e2e.py`. Helper:
  - Chỉ dùng dữ liệu tổng hợp.
  - Bắt buộc có `EDUOPS_TEST_MIGRATOR_DSN` tường minh.
  - Không in credential.
  - Nếu cần lưu credential cho phiên chạy, chỉ ghi vào `.local/`.
- Tài liệu hóa quy trình local, gồm `EDUOPS_SESSION_COOKIE_SECURE=false`, **chỉ** dùng cho HTTP cô lập.
- Thêm cơ chế opt-in, ví dụ `PLAYWRIGHT_REQUIRE_REAL_AUTH=1`: khi bật mà thiếu fixture thì test fail thay vì skip.
- Nếu sửa `.github/workflows/foundation-check.yml`, giữ nhất quán với ba DB role và cập nhật regression tĩnh. Không tuyên bố hosted CI đã chạy (OD-003).

**Bước 5 — R42-F05 (P3): bổ sung evidence EDU-0040 (append-only).**

- Thêm mục correction có timestamp thật vào `docs/progress/tasks/EDU-0040.md`. Liệt kê 14 file backend đã được format:
  - `app/modules/audit_logs/models.py`, `app/modules/audit_logs/service.py`
  - `app/modules/auth/admin_router.py`, `models.py`, `rate_limit.py`, `router.py`
  - `migrations/versions/0002_auth_users.py`, `0003_audit_logs.py`, `0007_account_tokens.py`
  - `tests/auth/test_permissions.py`, `test_schema_alignment.py`, `test_services.py`
  - `tests/integration/test_auth_api.py`, `test_auth_remediation.py`
- Ghi rằng EDU-0042 đã xác minh 3 migration chỉ đổi định dạng. Trỏ tới evidence chạy lại của EDU-0042.
- **Không** bịa lệnh, timestamp hay output cũ.
- Thêm một quy ước ngắn (ví dụ trong `backend/README.md`): không format lại migration đã áp dụng nếu không qua review migration.

**Bước 6 — Cập nhật gói nghiệm thu.**

- Thêm R42-F01..F05 vào sổ finding, ghi đúng trạng thái: đã sửa (task, test), TẠM, hoặc blocked (người quyết định).
- Thêm R42-F02 vào bảng giá trị TẠM / decision brief.
- Kết luận Phase 02 tuân thủ mục 1.5.
- Giữ sổ phê duyệt để trống.
- Cập nhật HANDOFF và viết prompt cho reviewer tiếp theo (một actor khác Codex).

### 6. Môi trường và lệnh (Windows, đã kiểm chứng)

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

**PostgreSQL cô lập:**

1. Env file trong `.local/<task>/` gồm `POSTGRES_MIGRATOR_PASSWORD`, `POSTGRES_RUNTIME_PASSWORD`, `POSTGRES_AUDIT_WORKER_PASSWORD` (ngẫu nhiên, không in ra) và `DATABASE_PORT`.
2. `docker compose -p eduops360-<task> --env-file .local\<task>\<file>.env -f infra\compose.dev.yml up -d db --wait`.
3. Chờ cổng TCP sẵn sàng.
4. Đặt `EDUOPS_DATABASE_URL` là DSN migrator tường minh, rồi chạy `alembic upgrade head`, `current`, `check`.
5. Chạy test với `EDUOPS_TEST_MIGRATOR_DSN`, `EDUOPS_TEST_RUNTIME_DSN`, `EDUOPS_TEST_AUDIT_WORKER_DSN`.
6. Teardown: `down -v` đúng project, rồi xóa env file.

**Khi interface đổi:** chạy `scripts/export_openapi.py` (không có `--check`) và `npm run api:generate`, rồi kiểm lại `--check` và `api:check`.

**E2E:**

- Không dùng cổng 8000 (nằm trong dải Windows loại trừ). Chạy API trên cổng 58xxx còn trống, với `EDUOPS_DATABASE_URL` là DSN runtime của DB cô lập và `EDUOPS_SESSION_COOKIE_SECURE=false`.
- Vite: `API_PROXY_TARGET=http://127.0.0.1:<port> npm run dev -- --host 127.0.0.1 --port 5173 --strictPort`.
- Chạy: `PLAYWRIGHT_EXTERNAL_SERVER=1 PLAYWRIGHT_CHANNEL=chrome PLAYWRIGHT_REAL_AUTH_EMAIL=... PLAYWRIGHT_REAL_AUTH_PASSWORD=... npx playwright test`.
- Sau khi dừng npm, tiến trình node của Vite có thể còn giữ 5173. Kiểm PID và command line rồi mới dừng.

**Probe hoặc test đồng thời:** mỗi worker dùng một FastAPI app riêng. Dùng chung một app cho nhiều `TestClient` trong nhiều thread sẽ làm hai lifespan ghi đè `app.state.database` và gây treo (đã gặp ở EDU-0042).

**Quy ước sửa file:** dùng `apply_patch`. Giữ nguyên kiểu xuống dòng CRLF/LF của từng file. Không có Git, nên evidence mỗi task phải có `changes.diff` so với baseline.

### 7. Quy tắc evidence và kiểm chứng

- **Fail trước:** chạy test mới trên code chưa sửa và lưu output fail. Nếu test chỉ fail vì API chưa tồn tại, ghi rõ.
- Mỗi task có `docs/progress/evidence/<task>/verification.json`, ghi lệnh, cwd, `started_at` (+07:00), `exit_code` và kết quả. Không ghi timestamp cho thời điểm chưa diễn ra; giá trị nào không đo thì ghi "không đo".
- **Kiểm chứng lại ngay trước khi bàn giao:** sau lần sửa file cuối cùng, chạy lại mọi lệnh trạng thái sắp khẳng định (test, manifest, Docker, listener). Khi khẳng định về một dòng hay khối code, đọc hết dòng hoặc khối đó.
- Chỉ dùng dữ liệu tổng hợp và role tổng hợp riêng. Không ghi secret vào log hay evidence. Quét evidence trước khi publish, **có loại trừ `.env`**.
- Kê khai đủ tác dụng phụ, kể cả `frontend/dist`, `frontend/test-results`, `.local/`.

### 8. Điểm dừng bắt buộc

- Cần quyết định OD hoặc Security Owner (R42-F02, trạng thái người phát hành, cấp role cho `pending`): dừng phần đó, ghi blocker kèm phương án.
- Baseline lệch hoặc có actor khác đang sửa file: dừng và báo người dùng.
- Cần mạng, cài package, khởi tạo Git hoặc chạm `.env` thật: hỏi người dùng trước.
- Gate vẫn fail sau khi sửa: giữ evidence fail, không đánh dấu xong.

### 9. Bàn giao cuối lượt

- Với mỗi task:
  - Frontmatter đầy đủ.
  - Activity log append-only, có timezone.
  - Evidence riêng.
  - Status `in_review`.
  - commit, push, PR, merge đều `not_done`.
- Cập nhật HANDOFF và gói nghiệm thu theo Bước 6. Chạy `python scripts/sync_task_board.py`; không sửa tay board.
- Không sửa `docs/phases/PHASE-00.md`. Không chuyển OD thành DEC. Không điền sổ phê duyệt.
- Báo cáo cho người dùng, mở đầu bằng kết quả, gồm:
  - Phần đã sửa, kèm test fail trước và pass sau.
  - Phần fail hoặc `not_run`.
  - Quyết định đang chờ (đặc biệt R42-F02).
  - Đường dẫn file quan trọng.
  - Mọi tác dụng phụ.
  - Người cần re-review (actor khác Codex).

## Kết thúc prompt
