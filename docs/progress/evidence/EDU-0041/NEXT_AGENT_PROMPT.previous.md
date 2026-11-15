# Prompt bàn giao cho AGENT tiếp theo (Codex) — chốt Phase 01/02

Sao chép toàn bộ nội dung từ mục **Bắt đầu prompt** đến **Kết thúc prompt** cho Codex.

Tạo bởi EDU-0033 (2026-11-14). Bản trước (prompt EDU-0023 của EDU-0022) được giữ nguyên tại `docs/progress/evidence/EDU-0033/NEXT_AGENT_PROMPT.previous.md`. Prompt là chỉ dẫn thực thi, không phải đặc tả hay sổ phê duyệt.

---

## Bắt đầu prompt

Bạn là **Codex**, làm việc trên dự án **EduOps 360** tại `D:\eduops360`.

**Mục tiêu lượt này:** đưa Phase 01 và Phase 02 tới trạng thái **sẵn sàng để con người nghiệm thu**. Cụ thể: hoàn tất mọi việc kỹ thuật còn lại, có bằng chứng tái lập được, và đóng gói mọi quyết định mà chỉ con người có thẩm quyền mới được đưa ra.

"Dứt điểm" trong lượt này **không** có nghĩa là tự đánh dấu phase `accepted`. Nếu báo cáo cuối có câu "Phase 01/02 đã được nghiệm thu" mà không có chữ ký của người có thẩm quyền, lượt làm việc bị coi là sai.

### 1. Định nghĩa "xong" của lượt này

**Phải đạt (kỹ thuật):**

1. EDU-0032 (remediation F01–F08 do Claude thực hiện) được bạn re-review kỹ thuật độc lập, có kết luận và bằng chứng.
2. Các finding P3 A0102-F09..F22 trong `docs/quality/PHASE_01_02_INDEPENDENT_AUDIT_2026-11-14.md` được xử lý hết phần **không cần quyết định của con người**, mỗi bản sửa có regression test chạy fail trước, pass sau.
3. Có ít nhất một E2E chạy với backend và PostgreSQL thật cho luồng login → CSRF → logout (không route-mock).
4. Toàn bộ gate đều xanh trên host, PostgreSQL cô lập và frontend/E2E, kèm evidence có lệnh và exit code.

**Phải đạt (quản trị):**

5. Có gói nghiệm thu Phase 01/02 và bản đề xuất quyết định (decision brief) cho từng OD còn mở.
6. Mọi task `in_review` đều có ghi chú ai được phép review độc lập.

**Không thể xong trong lượt này (chỉ con người):**

- OD-001: chỉ định Product Owner, Human Security Owner, reviewer độc lập, Git maintainer.
- OD-003: repository và hosted CI.
- OD-007, OD-008, OD-011.
- Phê duyệt MFA secret custody và quyết định archive/retention audit.
- Nghiệm thu Phase 00/01/02.

Với các mục này, ghi là blocker kèm phương án đề xuất. Không tự chọn thay.

### 2. Ranh giới, thẩm quyền và quyền được cấp

- Chỉ làm việc trong `D:\eduops360`.
- Không tự accept, tự approve, merge hay deploy. Không dùng dữ liệu học sinh thật, production credential hay public deployment.
- Chỉ DEC-001..008 trong `docs/phases/PHASE-00.md` là quyết định đã xác nhận. OD-001..013 vẫn mở. Giá trị `TẠM`, suggested default hay comment trong code đều không phải quyết định.
- **Tính độc lập:**
  - Bạn là implementer của EDU-0007..0014 và EDU-0021..0030, nên **không được** review hay nghiệm thu chính các task đó.
  - Bạn độc lập với EDU-0032 (Claude implement), nên được phép re-review kỹ thuật task này.
  - Người dùng yêu cầu **người review khác người sửa**. Finding mà bạn tìm ra khi re-review EDU-0032 phải do một actor khác sửa, ở một vòng riêng.
  - Ngược lại, bạn được sửa các finding P3 của EDU-0031 (Claude audit) vì bạn không phải người review vòng đó.
- **Docker (người dùng cấp trong prompt này):**
  - Được dùng **một Compose project cô lập theo task** (ví dụ `eduops360-edu0034`), chỉ service `db`, mật khẩu tổng hợp ngẫu nhiên và cổng localhost còn trống trong dải 55xxx.
  - Chỉ chạy `down -v` cho project do chính bạn tạo. Không đụng volume hay project khác, gồm `eduops360-local_postgres-data`, `eduops360-audit-0011_*` và image có sẵn.
  - Nếu Docker Desktop chưa chạy, bạn được khởi động. Cuối lượt, trả Docker Desktop về đúng trạng thái ban đầu.
- **Git:** `D:\eduops360` không phải Git repository. Không `git init`, commit, push, tạo remote hay PR, trừ khi người dùng cho phép rõ trong phiên. Hosted CI phụ thuộc OD-003.
- **Mạng và dependency:** không thêm package hay đổi lockfile nếu không bắt buộc. Việc cần mạng (ví dụ sinh hash cho lock ở F18) chỉ làm khi người dùng cho phép. Nếu không được phép, ghi blocker.
- **File `.env` thật** (`backend/.env`, `infra/.env`): không đọc, không in và không sửa nếu chưa được phép. `backend/.env` cũ trỏ tới role superuser của Phase 01 (A0102-F13), vì vậy mọi lệnh chạm DB phải đặt `EDUOPS_DATABASE_URL` rõ ràng.

### 3. Thứ tự đọc bắt buộc

Đọc theo đúng thứ tự trước khi thay đổi gì:

1. `AGENTS.md`, rồi `docs/phases/PHASE-00.md` (đọc hết), `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md`.
2. `docs/progress/HANDOFF.md`, `docs/phases/PHASE-01.md`, `docs/phases/PHASE-02.md`.
3. `docs/quality/PHASE_01_02_INDEPENDENT_AUDIT_2026-11-14.md`. Đây là danh sách finding mới nhất và có thẩm quyền nhất.
4. `docs/quality/PHASE_01_AUDIT_2026-11-12.md` và `docs/quality/PHASE_02_TECHNICAL_AUDIT_2026-11-13.md`, làm bối cảnh lịch sử.
5. `docs/progress/tasks/EDU-0031.md`, `docs/progress/tasks/EDU-0032.md`, `docs/progress/evidence/EDU-0032/verification.json` và `changes.diff`. Không có Git, nên `changes.diff` là bản ghi thay đổi duy nhất.
6. `ai-agent-sp/skills/REGISTRY.md`. Sau đó chỉ đọc các skill cần cho từng bước: `ra-soat/security-cia-review`, `ra-soat/migration-review`, `giam-sat/audit-trail-verification`, `kiem-thu/regression-debugger`, `kiem-thu/playwright-e2e`, `thuc-thi/api-contract-sync`, `lap-ke-hoach/handoff-planning`.

Tài liệu chỉ là claim. Phải đối chiếu với source, lệnh kiểm tra và trạng thái máy hiện tại.

### 4. Trạng thái bàn giao (tự kiểm lại trước khi tin)

- Phase 00, 01, 02: **NOT ACCEPTED**. Mọi task trên `TASK_BOARD.md` đang `in_review`, trừ EDU-0001 (`planned`).
- EDU-0031 (Claude, audit độc lập, 2026-11-14) kết luận **NEEDS_CHANGES**: 2 P1, 6 P2 và 14 P3 (F09–F22).
- EDU-0032 (Claude, remediation) đã sửa F01–F08 và đang `in_review`. Số liệu lúc 2026-11-14 12:07 +07:00:
  - Backend host: 74 passed, 14 skipped.
  - PostgreSQL 18 cô lập: 88 passed.
  - ruff sạch. `alembic` head là `0007_account_tokens`, `check` sạch.
  - OpenAPI không đổi.
  - Frontend: typecheck/lint/format/api:check/build đều đạt, 20 unit test, 7 E2E Chrome (server ngoài).
- Giá trị **TẠM** EDU-0032 đưa vào, đều fail-closed và chờ người có thẩm quyền:
  - F01: actor phải bao trùm mọi quyền của tài khoản đích (OD-008).
  - F03: tài khoản `pending` không đổi được trạng thái qua endpoint status.
  - F05: khóa do đăng nhập sai không chấm dứt phiên đang có (Security Owner).
  - F06: cấm tự cấp quyền; hạn ủy quyền không vượt hạn grant bao trùm của người cấp (OD-007/008).
  - F07: `PASSWORD_HASH_CONCURRENCY = 4` (OD-004).
- Hệ quả cần biết: tài khoản `pending` hiện không đình chỉ được, nên **không còn đường API nào để hủy lời mời**. F10 vì thế trở nên cấp thiết hơn.
- Docker lúc kết thúc EDU-0032: daemon đang chạy, không có container nào của dự án. Volume cũ của dự án khác vẫn còn và phải giữ nguyên.

### 5. Kế hoạch thực hiện

Mỗi bước là một task EDU riêng. Lấy số ID kế tiếp còn trống tại thời điểm làm (dự kiến bắt đầu từ EDU-0034). Không bao giờ ghi đè journal có sẵn.

**Bước 0 — Preflight** (ghi vào task đầu tiên):

1. Chạy `git status -sb`; kỳ vọng exit 128.
2. Kiểm tra listener trên các cổng dự án (5173, 4173, 8000, 55xxx, 58xxx) và tiến trình liên quan.
3. Chụp snapshot Docker: container, volume, network, image.
4. Lập manifest SHA-256 cho source. Loại trừ `node_modules`, `.venv`, `.local`, cache, `dist`, `test-results`.
5. Sao baseline source vào `.local/<task>/baseline/`.
6. Chạy lại các gate host: pytest, ruff, frontend checks.

Nếu số liệu lệch so với mục 4, hoặc có file đang bị agent khác sửa: **dừng lại và điều tra trước khi thay đổi bất cứ gì.**

**Bước 1 — Task A: re-review độc lập EDU-0032.** Trong task này **không sửa source sản phẩm**.

- Trên PostgreSQL cô lập: chạy lại toàn bộ suite và các regression của EDU-0032.
- Chạy lại probe EDU-0031 (P1–P7 trong `docs/progress/evidence/EDU-0031/probes/`):
  - Sao probe vào `.local/<task>/` trước khi chạy, để không ghi đè evidence cũ.
  - Chỉnh kỳ vọng: các thao tác trước đây thành công giờ phải bị từ chối.
- Soát `changes.diff` để tìm đường vòng (bypass). Tối thiểu kiểm:
  - **F01:** mọi đường làm thay đổi credential hay trạng thái tài khoản đều có quy tắc bao trùm, gồm cả grant chưa bắt đầu, mã quyền lạ và trường hợp tự nhắm vào chính mình.
  - **F03:** mọi chuyển trạng thái, kể cả từ `locked`.
  - **F04:** đường lời mời cũng an toàn khi chạy đồng thời.
  - **F05:** tương tác với đình chỉ/thu hồi phiên, và việc `/auth/me` trả `locked`.
  - **F06:** trường hợp có nhiều grant bao trùm, chuỗi ủy quyền A→B→A, và thu hồi.
  - **F07:** limiter theo từng event loop, khả năng starvation và việc hủy request.
  - **F02:** mọi nơi ghi `user_agent`.
  - Audit `issued_by` có ghi đúng người phát hành.
- Kết quả ghi vào `docs/quality/EDU-0032_REMEDIATION_REVIEW_<YYYY-MM-DD>.md`, với kết luận `PASS`, `PASS_WITH_NOTES` hoặc `NEEDS_CHANGES`. Mỗi finding có mức độ, cách tái hiện và bằng chứng.
- Nếu có P1/P2: **không tự sửa**. Ghi blocker cho một actor khác. Bạn vẫn tiếp tục Bước 2 với những phần không chạm vào code lỗi.

**Bước 2 — Các task B..F: xử lý P3 của EDU-0031.**

Với mỗi finding: viết regression test fail trước, sửa tối thiểu, ghi giá trị TẠM, và sinh lại OpenAPI/TS nếu interface đổi. Thứ tự gợi ý: E → B → C → D → F.

| Nhóm | Finding | Việc bạn làm | Giới hạn |
|---|---|---|---|
| E (hạ tầng/test) | F19 | Test integration cũ dùng role tổng hợp riêng thay vì sửa mapping `system_admin`. Thêm kiểm tra DB disposable trước khi test ghi dữ liệu | Làm sớm vì ảnh hưởng độ tin cậy của test |
| E | F14, F15, F16 | Healthcheck dùng `pg_isready -h 127.0.0.1`. Cổng Playwright cấu hình qua biến môi trường, `reuseExistingServer` chỉ bật khi được yêu cầu rõ. Generator chỉ ghi dưới workspace/`.local` | — |
| E | F13, F18 | Cập nhật `.env.example`/README để runtime không dùng superuser. Image runtime chỉ cài dependency runtime | Không sửa `.env` thật. Hash cho lock cần mạng, nên chỉ làm khi được phép |
| B (auth/session) | F09, F11, F22 | Key đang bị chặn không bị đẩy khỏi LRU; thêm giới hạn theo IP với ngưỡng TẠM. Validator từ chối `*` trong `cors_origins`. Idle timeout dựa trên `last_activity_at` với giá trị TẠM cấu hình được | Ghi rõ limiter chỉ có hiệu lực trong từng tiến trình |
| C (MFA) | F12 | Chống replay TOTP bằng cách lưu bước đã dùng: migration mới, có upgrade, downgrade và test roundtrip | **Không** mã hóa `mfa_secret`; việc này chờ phê duyệt custody |
| D (vòng đời tài khoản) | F10, F20, phần còn lại của F08 | Endpoint phát hành lại lời mời (vô hiệu token cũ, ghi audit, áp dụng quy tắc bao trùm F01) và nếu cần thì hủy lời mời. UI hiện lỗi tải role thay vì nuốt lỗi. E2E backend + DB thật cho login/CSRF/logout | Không bao giờ cho Admin chọn mật khẩu ban đầu |
| F (evidence) | F17 | Thêm mục correction (append-only, timestamp thật) vào EDU-0024..0030, ghi rõ evidence cũ thiếu lệnh và exit code, rồi trỏ tới lượt chạy lại hiện tại | **Không** bịa lệnh hay kết quả cũ |
| — | F21 | Chỉ soạn phương án cho OD-011/DBA: migrator không phải superuser, HMAC anchor, chặn downgrade xóa audit | Không đổi role hay migration audit khi chưa có quyết định |

**Bước 3 — Task G: chốt Phase 01.**

- Kiểm lại từng gate ở mục E của `PHASE-01.md` bằng evidence mới: frontend và backend khởi chạy độc lập; OpenAPI và client khớp; snapshot Light/Dark và fixture UTF-8; test edge case.
- Chạy cục bộ các bước trong `.github/workflows/foundation-check.yml` và `governance-check.yml`, làm evidence local. **Không** gọi đó là hosted CI.
- Đối chiếu vấn đề còn mở trong EDU-0007..0011.
- Chỉ cập nhật bảng evidence local trong `PHASE-01.md`. Không đánh dấu gate cần con người.

**Bước 4 — Task H: gói nghiệm thu** tại `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_<YYYY-MM-DD>.md`. Gói gồm:

- Bảng gate của Phase 01 và Phase 02. Mỗi gate có trạng thái `Đạt kỹ thuật`, `Chờ con người` hoặc `Blocked`, kèm link evidence.
- Sổ finding F01–F22 cùng finding từ re-review EDU-0032. Mỗi mục ghi: đã sửa (task, test), TẠM, hay blocked (người chịu trách nhiệm).
- Decision brief cho OD-001, OD-003, OD-007, OD-008, OD-011, MFA custody, archive/retention và từng giá trị TẠM. Mỗi mục có câu hỏi, các phương án, đề xuất (ghi rõ `NOT APPROVED`), tác động lên code/config, và task triển khai sau khi được duyệt.
- Ma trận độc lập: mỗi task `in_review` → implementer → ai được phép review. Đánh dấu task còn thiếu reviewer.
- Mẫu sổ phê duyệt với các trường để trống: reviewer, thời điểm ISO-8601 kèm offset, quyết định, evidence. **Không tự điền.**
- Kết luận cuối: `READY_FOR_HUMAN_ACCEPTANCE` hoặc `NOT_READY`, kèm lý do.

### 6. Môi trường và lệnh (Windows)

Đã kiểm chứng trên máy này. Python 3.13.5 trong `backend/.venv`, Node 24.12.0, image `postgres:18` có sẵn local.

**Backend:**

```powershell
cd D:\eduops360\backend
.venv\Scripts\python -B -m pytest tests -q -p no:cacheprovider
.venv\Scripts\python -B -m ruff check --no-cache app migrations tests
.venv\Scripts\python -B ..\scripts\export_openapi.py --check
```

**PostgreSQL cô lập:**

1. Tạo env file trong `.local/<task>/` với `POSTGRES_MIGRATOR_PASSWORD`, `POSTGRES_RUNTIME_PASSWORD`, `POSTGRES_AUDIT_WORKER_PASSWORD` (ngẫu nhiên, không in ra) và `DATABASE_PORT`.
2. Chạy:

   ```powershell
   docker compose -p eduops360-<task> --env-file .local\<task>\<file>.env -f infra\compose.dev.yml up -d db --wait
   ```

3. Chờ cổng TCP sẵn sàng rồi mới chạy Alembic, vì healthcheck chỉ kiểm Unix socket (F14).
4. Migrate bằng role migrator: đặt `EDUOPS_DATABASE_URL=postgresql+psycopg://eduops_migrator:...@127.0.0.1:<port>/eduops360`, rồi chạy `alembic upgrade head`, `alembic current` và `alembic check`.
5. Chạy test với `EDUOPS_TEST_MIGRATOR_DSN`, `EDUOPS_TEST_RUNTIME_DSN`, `EDUOPS_TEST_AUDIT_WORKER_DSN` (dạng `postgresql://...`).
6. Teardown bằng `down -v` cho đúng project, rồi xóa env file.

**Khi interface đổi:** chạy `export_openapi.py` (không có `--check`) để ghi `contracts/openapi.json`, rồi `npm run api:generate`. Sau đó chạy lại `--check` và `npm run api:check`.

**Frontend:** `npm run typecheck`, `lint`, `format:check`, `api:check`, `test`, `build`.

**E2E:**

- Cổng 8000 nằm trong dải bị Windows loại trừ (7957–8956), nên không dùng.
- Chạy API trên một cổng 58xxx còn trống, với `EDUOPS_DATABASE_URL` trỏ tới role runtime của DB cô lập.
- Chạy Vite: `API_PROXY_TARGET=http://127.0.0.1:<port> npm run dev`.
- Chạy test: `PLAYWRIGHT_EXTERNAL_SERVER=1 PLAYWRIGHT_CHANNEL=chrome npx playwright test`.
- Sau khi dừng npm, tiến trình node của Vite có thể vẫn giữ cổng 5173. Kiểm PID và command line trước khi dừng nó.

**Governance:**

```powershell
cd D:\eduops360
python -B scripts\validate_blueprint.py
python -B scripts\check_structure.py
python -B scripts\check_text_encoding.py
python -B scripts\validate_students_csv.py samples\templates\students_import_template.csv
python -B -m unittest discover -s tests -p "test_*.py"
python -B scripts\sync_task_board.py
```

**Quy ước sửa file:**

- Dùng `apply_patch` cho mọi chỉnh sửa thủ công.
- Nhiều file đang dùng CRLF, số khác dùng LF. Giữ nguyên kiểu xuống dòng của từng file.
- Không có Git, nên evidence của mỗi task phải có `changes.diff` (diff so với baseline đã sao).

### 7. Quy tắc evidence và kiểm chứng

- **Fail trước:** chạy test mới trên code chưa sửa và lưu output fail. Nếu test chỉ fail vì API chưa tồn tại, ghi rõ điều đó.
- Mỗi task có `docs/progress/evidence/<task>/verification.json` với các trường: lệnh, cwd, `started_at` (+07:00), `exit_code`, kết quả. Không bịa timestamp; giá trị nào không đo thì ghi "không đo".
- **Kiểm chứng lại ngay trước khi bàn giao.** Sau lần sửa file cuối cùng, chạy lại mọi lệnh trạng thái mà bạn sắp khẳng định (số test, danh sách file, trạng thái Docker, listener). Hành động của chính bạn làm trạng thái đổi.
- Khi khẳng định về một dòng hay một khối code (ví dụ "chỗ này an toàn"), đọc **hết** dòng hoặc khối đó.
- Chỉ dùng dữ liệu tổng hợp. Không ghi secret vào log. Test integration dùng role tổng hợp riêng.
- Kê khai đủ tác dụng phụ, kể cả thư mục bị ignore: `frontend/dist`, `frontend/test-results`, `.local/`.

### 8. Điểm dừng bắt buộc

- Thay đổi cần quyết định OD hoặc Security Owner: dừng phần đó, ghi blocker kèm phương án.
- Baseline lệch mà không giải thích được, hoặc có file đang bị agent khác sửa: dừng và báo người dùng.
- Re-review EDU-0032 ra P1/P2: không tự sửa, bàn giao cho actor khác.
- Cần mạng, cài package, khởi tạo Git hoặc sửa `.env` thật: hỏi người dùng trước.
- Gate vẫn fail sau khi sửa: giữ evidence fail và không đánh dấu task là xong.

### 9. Bàn giao cuối lượt

- Với mỗi task:
  - Frontmatter đầy đủ.
  - Activity log append-only, có timezone.
  - Evidence riêng.
  - Status tối đa `in_review`.
  - commit, push, PR, merge đều `not_done`.
- `docs/progress/HANDOFF.md`: cập nhật ngắn trạng thái, blocker, ba hành động tiếp theo và người nhận.
  - Các task mới của bạn: reviewer độc lập không phải Codex.
  - Các quyết định: con người có thẩm quyền.
- Chạy `scripts/sync_task_board.py`. Không sửa tay board.
- Không sửa `docs/phases/PHASE-00.md`. Không chuyển OD thành DEC.
- Báo cáo cho người dùng, mở đầu bằng kết quả, gồm:
  - Phần đã đạt.
  - Phần fail hoặc `not_run`.
  - Blocker cần con người quyết.
  - Đường dẫn file quan trọng.
  - Mọi tác dụng phụ.

Không mô tả phần việc dở dang là đã xong.

## Kết thúc prompt
