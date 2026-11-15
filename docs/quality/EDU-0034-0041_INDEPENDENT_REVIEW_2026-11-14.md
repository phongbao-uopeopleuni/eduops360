# Review kỹ thuật độc lập EDU-0034..EDU-0041 — 2026-11-14

**Task:** `EDU-0042` · **Múi giờ:** Asia/Ho_Chi_Minh (+07:00) · **Phạm vi:** `D:\eduops360`
**Reviewer:** Claude (AI agent), không triển khai EDU-0035..0041. Không phải Human Security Owner (OD-001).
**Kết luận kỹ thuật:** **NEEDS_CHANGES cho Phase 02.** Một finding P1 và một finding P2 tái hiện được trên PostgreSQL cô lập. Gate kỹ thuật Phase 01 tái lập được.
**Trạng thái phase:** Phase 01 và Phase 02 **NOT ACCEPTED**. Kết luận `READY_FOR_HUMAN_ACCEPTANCE` trong `PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md` **không còn đúng với Phase 02** cho tới khi R42-F01 được sửa và R42-F02 được quyết định/sửa. OD-001/003/007/008/011 vẫn **OPEN**.

Lượt này chỉ review. Không sửa source, test, migration, contract hay gói nghiệm thu của Codex. Reviewer không sửa finding của chính vòng review này.

**Xung đột lợi ích cần biết:**

- EDU-0034 là bản review của Codex đối với EDU-0032, mà Claude là implementer. Với EDU-0034, reviewer chỉ đánh giá phương pháp và evidence, không tự xác nhận lại phần mình làm.
- R42-F01 là lỗ hổng nằm trong chính thiết kế F01 mà Claude triển khai ở EDU-0032. Claude vì vậy không được sửa nó.

## 1. Tóm tắt

Số liệu trong gói nghiệm thu tái lập được: host 77/18, PostgreSQL 95, frontend 22, Playwright 8 (có real-auth), root 24, encoding 370, head `0008`. Phần lớn bản sửa P3 của Codex đúng và tối thiểu. Tuy vậy, probe trực tiếp cho thấy:

1. **P1 — R42-F01:** quy tắc "actor phải bao trùm quyền của tài khoản đích" (A0102-F01) chỉ được kiểm **lúc phát hành** token, không kiểm lại **lúc dùng** token.
   - Actor chỉ có `user:password_reset` phát hành reset cho tài khoản thường. Tài khoản đó sau đó được nâng lên admin, và actor dùng token cũ để chiếm tài khoản admin.
   - Tương tự, actor chỉ có `user:create` giữ raw invitation token. Tài khoản pending sau đó được cấp quyền, và actor kích hoạt nó bằng mật khẩu do mình chọn.
2. **P2 — R42-F02:** limiter theo IP (giá trị TẠM 50/60 s) chặn **mọi** đăng nhập từ cùng địa chỉ peer, kể cả mật khẩu đúng của tài khoản khác. 50 request sai với email ngẫu nhiên là đủ chặn mọi người dùng sau cùng NAT hoặc reverse proxy trong khoảng 56 s, và lặp lại được.
3. **P3:** limiter bão hòa thì ngừng theo dõi định danh mới (R42-F03). E2E real-auth không tái lập được từ file tracked và sẽ bị skip trong CI (R42-F04). Evidence EDU-0040 chưa đủ chi tiết (R42-F05).

## 2. Preflight và baseline

| Hạng mục | Kết quả |
|---|---|
| Thời điểm | 2026-11-14T15:47:13+07:00 |
| `git status -sb`, `git reflog -n 5` | exit 128, `not a git repository` |
| Listener cổng dự án / process EduOps 360 | không có. Chỉ có shell của chính reviewer |
| Docker Desktop | **đang dừng**. Được khởi động lúc 15:55 cho DB cô lập, dừng lại và xác nhận lúc 16:10 |
| Manifest SHA-256 | 401 file lúc 15:50 (`.local/edu-0042/manifest-before.json`). File mới nhất được sửa lúc 15:34:07 (EDU-0041). Không có actor nào khác đang sửa |
| Task ID | `EDU-0042` còn trống |

## 3. Gate chạy lại

Lệnh, cwd, thời điểm và exit code nằm trong `docs/progress/evidence/EDU-0042/verification.json`.

| Lớp | Kết quả |
|---|---|
| Blueprint / structure / encoding / students CSV | exit 0. Encoding: 370 file, 0 lỗi. CSV: 3 dòng, 0 lỗi |
| `python -m unittest discover` (mặc định và `-s tests`) | exit 0, 24 test OK |
| `ruff check backend tests/foundation`, `ruff format --check ...` | exit 0, 56 file đã format |
| `pytest backend/tests` (host) | exit 0, **77 passed, 18 skipped** |
| `export_openapi.py --check` | exit 0 |
| Frontend typecheck / lint / format / api:check / test / build | exit 0, **22 passed** |
| PostgreSQL 18 cô lập `eduops360-edu0042` (cổng 55495) | alembic `upgrade head` → `check` → `downgrade -1` (0007) → `upgrade head` → `check`, tất cả exit 0. Cột `mfa_last_used_step` là `bigint` nullable, khớp model |
| `pytest backend/tests` với DSN cô lập | exit 0, **95 passed**. Sau suite, mapping seed của 7 role hệ thống vẫn là 0 (F19 đúng) |
| Playwright (server ngoài, API 58099, Vite 5173) | exit 0, **8 passed**. Real-auth chạy thật, không skip. Log API có `POST /auth/login 200`, `POST /auth/logout 204`. DB ghi phiên `revoked` |

## 4. Findings mới

Mức độ dùng thang của EDU-0031: P1 nghĩa là kiểm soát bảo mật bị vượt qua; P2 nghĩa là lỗi đáng kể; P3 nghĩa là rủi ro thấp hoặc quy trình.

| ID | Mức | Tóm tắt | Task liên quan | Ai sửa |
|---|---|---|---|---|
| R42-F01 | P1 | Quy tắc bao trùm F01 bị vượt qua do chỉ kiểm lúc phát hành token (reset và invitation) | EDU-0032 (thiết kế F01), EDU-0038 (reissue thừa hưởng) | actor khác Claude; Security Owner xác nhận quy tắc |
| R42-F02 | P2 | Limiter theo IP cho phép người chưa đăng nhập chặn đăng nhập của mọi tài khoản sau cùng peer | EDU-0036 | actor khác Claude, sau quyết định của Security Owner |
| R42-F03 | P3 | Limiter bão hòa thì không theo dõi định danh mới; mỗi key mới tốn quét O(n) dưới lock trên event loop | EDU-0036 | actor khác |
| R42-F04 | P3 | E2E real-auth phụ thuộc helper nằm trong `.local` bị ignore, tự skip khi thiếu biến môi trường (CI sẽ skip), cần cookie không Secure | EDU-0038/0040 | actor khác |
| R42-F05 | P3 | EDU-0040 không có `verification.json` và raw output. "14 file được format" không liệt kê tên, trong đó có 3 migration đã áp dụng | EDU-0040/0041 | actor khác (chỉ tài liệu) |

### R42-F01 — P1 — Bao trùm đặc quyền chỉ kiểm lúc phát hành token

**Vị trí:**

- `admin_router.py`: `issue_password_reset`, `create_user_invitation` và `reissue_user_invitation` gọi `_require_actor_covers_target` lúc phát hành.
- `router.py`: `_consume_account_token`, `accept_password_reset` và `accept_invitation` không kiểm lại người phát hành (`token.created_by`) so với quyền hiện tại của tài khoản đích.
- `grant_role` không vô hiệu token còn hạn của tài khoản đích, và cho phép cấp role cho tài khoản `pending`.

**Tái hiện** (`probe_review.json`, `RA_*` và `RB_*`, chạy 15:58:47 trên DB cô lập):

| Bước | Biến thể reset (RA) | Biến thể invitation (RB) |
|---|---|---|
| Actor | chỉ có `user:password_reset` | chỉ có `user:create` |
| 1 | Phát hành reset cho tài khoản thường → **201** | Tạo lời mời → **201**, giữ raw token |
| 2 | Một admin nâng tài khoản đó lên role đủ quyền `user:*` | Admin có thẩm quyền cấp role scoped (`user:grant_role` tại S,Y) cho tài khoản pending → **201** |
| 3 | Phát hành reset mới → **403** (quy tắc F01 hoạt động). Lần bị từ chối này **không** vô hiệu token cũ | Actor tự cấp role đó → **403** |
| 4 | Dùng token cũ → **204** | Actor accept lời mời bằng mật khẩu tự chọn → **204** |
| 5 | Đăng nhập bằng mật khẩu mới → **200** | Đăng nhập → **200** |
| 6 | Đọc user khác → **200**, trong khi chính actor nhận **403** | Cấp role tại (S,Y) → **201** |

**Tác động:** leo thang đặc quyền đúng như A0102-F01 (P1), chỉ cần một cửa sổ thời gian:

- Reset có hạn 1–24 giờ.
- Lời mời có hạn tới 168 giờ.

Luồng "mời → cấp role → người dùng accept" là luồng onboarding thông thường. Admin UI hiện form "Cấp vai trò có scope" ngay trên tài khoản vừa mời. Gói nghiệm thu ghi F01 là "Đã sửa, đã re-review" và quy tắc bao trùm là "chặn reset/suspend/reissue vượt đặc quyền"; khẳng định này chưa đúng với thời điểm dùng token. Rủi ro raw token (F03) đã được công bố, nhưng hệ quả leo thang khi kết hợp với cấp quyền sau khi phát hành thì chưa được ghi.

**Hướng sửa tối thiểu** (cho actor khác):

1. Khi dùng token, kiểm lại `can_delegate_role` của **người phát hành hiện tại** đối với mọi grant còn hiệu lực của tài khoản đích. Nếu không còn bao trùm → `ACCOUNT_TOKEN_INVALID` (fail-closed).
2. Hoặc bổ sung thêm: `grant_role` vô hiệu mọi account token chưa dùng của tài khoản đích trong cùng transaction.

Việc có cho cấp role cho tài khoản `pending` hay không là câu hỏi OD-008 / Security Owner.

**Regression đề xuất:** hai kịch bản RA/RB ở trên, chạy live trên PostgreSQL. Kỳ vọng: bước 4 nhận 400 và tài khoản đích không đổi.

### R42-F02 — P2 — Limiter theo IP chặn đăng nhập của mọi tài khoản sau cùng peer

**Vị trí:**

- `router.py` (login): kiểm `ip_limiter.check(ip_rate_key)` trước khi verify, và ghi failure cho mọi lần sai.
- `session.py:client_ip`: chỉ dùng direct peer, chưa cấu hình trusted proxy.
- `config.py`: `login_ip_rate_limit_attempts = 50` (TẠM).

**Tái hiện** (`RC_*`):

- Cùng một peer gửi 50 lần đăng nhập sai với email ngẫu nhiên không tồn tại → 50 × 401.
- Tài khoản khác đăng nhập **đúng mật khẩu** → **429** `LOGIN_RATE_LIMITED`, `Retry-After: 56`.
- Tài khoản nạn nhân vẫn `active`, `failed_login_count = 0`.

**Tác động:** người chưa đăng nhập có thể chặn đăng nhập mới của toàn bộ người dùng chung địa chỉ peer, chỉ với khoảng 50 request mỗi phút:

- Mạng trường học sau một NAT.
- Mọi người dùng, khi triển khai sau reverse proxy mà chưa cấu hình trusted proxy (limiter khi đó trở thành limiter toàn cục).

Phiên đang có vẫn dùng được (TẠM F05). Bảng TẠM của gói nghiệm thu chỉ ghi mục đích "giảm password spray", không nêu rủi ro này.

**Hướng xử lý:** cần quyết định của Security Owner về ngưỡng, trusted proxy và ngữ nghĩa chặn. Ví dụ:

- Chỉ chặn tiếp các lần sai với email khác nhau, không chặn mật khẩu đúng của tài khoản đã biết.
- Kết hợp CAPTCHA hoặc backoff.
- Hoặc tạm tắt khi chưa có trusted proxy.

Không tự chọn giá trị mặc định.

**Regression đề xuất:** kịch bản RC. Kỳ vọng do Security Owner chốt, nhưng tối thiểu tài khoản khác với mật khẩu đúng không bị 429 chỉ vì lỗi của người khác.

### R42-F03 — P3 — Limiter bão hòa

`rate_limit.py:record_failure`. Khi cả 10.000 slot đều là key đang bị chặn:

- Key mới **không được ghi** (0/200 trong probe `RE_*`), tức giới hạn bị tắt với định danh mới.
- Mỗi key mới tốn khoảng **3,9 ms** quét toàn bảng dưới `threading.Lock`, được gọi đồng bộ trên event loop.

Muốn đạt trạng thái này cần khoảng 100.000 lần sai từ nhiều IP, vì limiter theo IP kìm lại. Lockout tài khoản trong DB vẫn là kiểm soát bền vững. Đề xuất: giới hạn số phần tử được quét, hoặc ghi rõ hành vi khi bão hòa vào gói nghiệm thu.

### R42-F04 — P3 — E2E real-auth chưa phải gate bền vững

- `frontend/tests/e2e/real-auth.spec.ts` tự `skip` khi thiếu `PLAYWRIGHT_REAL_AUTH_EMAIL/PASSWORD`.
- Helper seed fixture chỉ có ở `.local/EDU-0034/seed_real_e2e.py`, thư mục bị ignore.
- `foundation-check.yml` không seed và không đặt các biến này, nên hosted CI sẽ **skip** test.
- Chạy local qua HTTP cần `EDUOPS_SESSION_COOKIE_SECURE=false`; điều này chỉ được ghi trong `PHASE_01_LOCAL_GATE`.

Reviewer đã tái hiện test với fixture tổng hợp tự seed, và nó đi qua backend/PostgreSQL thật. Như vậy khẳng định "real-backend E2E" đúng với các lượt chạy local, nhưng chưa tái lập được từ file tracked. Đề xuất: đưa helper seed vào `scripts/` hoặc test fixture, tài liệu hóa, và cân nhắc để CI fail thay vì skip khi chưa có fixture.

### R42-F05 — P3 — Evidence EDU-0040

- `docs/progress/evidence/EDU-0040/` chỉ có `playwright-results.json` và `startup.json`.
- Exit code được tóm tắt trong `EDU-0041/verification.md`, nhưng không có timestamp từng lệnh hay raw output của gate host/PostgreSQL.
- `changed_files` ghi "14 mechanically formatted backend Python files" mà không liệt kê tên. Danh sách đầy đủ gồm 3 migration đã áp dụng: `0002_auth_users.py`, `0003_audit_logs.py`, `0007_account_tokens.py`.

Reviewer đã kiểm: diff sau khi chuẩn hóa format của 3 migration là rỗng, nghĩa là chỉ đổi định dạng, không đổi ngữ nghĩa. Roundtrip và `alembic check` đều sạch. Đề xuất: bổ sung danh sách file và quy ước không format lại migration đã áp dụng nếu không có review migration.

## 5. Trả lời các câu hỏi kiểm tra bắt buộc

| Câu hỏi | Kết quả |
|---|---|
| Còn bypass quy tắc target-privilege? | **Có: R42-F01** (thời điểm dùng token). Lúc phát hành thì reset, status, reissue và cancel đều kiểm đúng, kể cả grant chưa bắt đầu (EDU-0034) |
| Self-target reset/suspend/reissue/cancel | Tự đình chỉ: 409. Tự reissue/cancel: 409 vì actor không `pending`. Tự reset: được phép, vô hại vì actor đã có quyền với chính mình |
| Account token single-use khi đồng thời | Đúng: `populate_existing` cộng khóa dòng user; regression EDU-0032 pass trong suite 95. Reissue đồng thời với accept bị tuần tự hóa nhờ khóa dòng user |
| Reissue vô hiệu mọi token cũ trong cùng transaction | Đúng: `UPDATE used_at` trước khi chèn token mới, dưới khóa dòng user; test xác nhận token cũ nhận 400 |
| Cancel mở đường `pending → active`? | Không: trạng thái vẫn `pending`; endpoint status vẫn trả 409 cho `pending` |
| Rate limiter: eviction và spraying | Spraying từ một IP bị chặn. Spraying phân tán vẫn không bị chặn (đã công bố). Key bị chặn được giữ, nhưng **R42-F02** và **R42-F03** |
| Idle timeout race / cập nhật activity | Mỗi request đã xác thực ghi `last_activity_at` và commit. Frontend không polling, nên không có keep-alive giả. Ghi đồng thời không gây hại |
| TOTP replay đồng thời / cửa sổ ±1 | Đúng: 5/5 lần race có đúng một 200 và một 401 (`probe_totp_race.json`). Bước phải tăng nghiêm ngặt. Bước chỉ được tiêu thụ khi thành công trọn vẹn |
| Migration 0008 | Upgrade, downgrade và upgrade nhất quán. Downgrade chỉ xóa cột mới |
| Workflow CI | Đủ 3 mật khẩu role. `alembic check` chạy qua service `migrate` (role migrator), không qua runtime. `PLAYWRIGHT_EXTERNAL_SERVER` được đặt ở cấp job |
| Integration test chạy nhầm DB lâu dài / làm bẩn mapping | Không làm bẩn mapping (đã kiểm sau suite). Chưa có marker DB disposable; chỉ dựa vào việc có DSN (rủi ro còn lại đã công bố) |
| Real-auth E2E đi qua backend/PostgreSQL thật | Đúng với lượt chạy local, nhưng không tái lập từ repo và bị skip trong CI (**R42-F04**) |
| Audit actor/target/issued_by/scope | Reissue và cancel ghi actor, resource, after_state. Accept ghi `issued_by`. Grant ghi đủ scope và hiệu lực. Không có token trong audit |
| Secret/token lọt vào log/audit/response | Không thấy trong evidence tracked. Raw token chỉ trả trong response phát hành (đã công bố, chờ Security Owner) |
| Claim của gói EDU-0041 khớp source/evidence? | Số liệu khớp. **Không khớp:** "không còn P0/P1/P2" và "F01 đã sửa" (R42-F01, R42-F02). Mô tả F21 đúng |

## 6. F21 (chỉ review, không triển khai)

Đã kiểm trên DB cô lập: `eduops_migrator` là superuser (`rolsuper = true`, do `POSTGRES_USER` của Compose), `0003.downgrade()` xóa `audit_outbox` và `audit_logs` vô điều kiện, và chưa có anchor HMAC ngoài DB.

Gói nghiệm thu mô tả đúng hiện trạng. Các phương án đều ghi `NOT APPROVED` và phụ thuộc OD-011/DBA/Security. Reviewer đồng ý không triển khai kiến trúc audit mới khi chưa có quyết định.

## 7. Đánh giá từng task

| Task | Kết luận review | Ghi chú |
|---|---|---|
| EDU-0034 (Codex review EDU-0032) | PASS_WITH_NOTES | Phương pháp và evidence đầy đủ. Bỏ sót R42-F01, giống implementer EDU-0032. Reviewer có xung đột lợi ích với nội dung được review |
| EDU-0035 | PASS | F13/F14/F15/F16/F18 (tách runtime)/F19 đúng. Hash lock vẫn blocked hợp lệ |
| EDU-0036 | NEEDS_CHANGES | CORS và idle timeout đúng. Limiter theo IP: R42-F02; bão hòa: R42-F03 |
| EDU-0037 | PASS | Chống replay đúng, kể cả khi đồng thời. Migration 0008 nhất quán |
| EDU-0038 | PASS_WITH_NOTES | Reissue/cancel đúng khi xét riêng, nhưng thừa hưởng R42-F01 (biến thể invitation). E2E: R42-F04 |
| EDU-0039 | PASS | Correction append-only, không bịa lịch sử |
| EDU-0040 | PASS_WITH_NOTES | Gate tái lập được. Evidence: R42-F05 |
| EDU-0041 | NEEDS_CHANGES | Kết luận `READY` và "không còn P1/P2" phải đổi cho Phase 02. Decision brief, sổ phê duyệt trống và ma trận độc lập đều đúng |

## 8. Giới hạn

- AI reviewer không thay Human Security Owner (OD-001). Không có Git hay hosted CI.
- Race TOTP và token được điều phối bằng `TestClient` trong thread, với một app cho mỗi worker. Chưa chạy nhiều tiến trình Uvicorn thật.
- Probe đầu tiên dùng chung một app cho hai worker và bị treo do chính probe (hai lifespan ghi đè `app.state.database`). Kết quả TOTP chỉ lấy từ probe đã sửa.
- Không đo trên Linux. Toàn bộ chạy trên Windows 11, Python 3.13.5, Node 24.12.0, `postgres:18` có sẵn local.

## 9. Tác dụng phụ và teardown

- **Tạo mới:** báo cáo này, `docs/progress/tasks/EDU-0042.md`, `docs/progress/evidence/EDU-0042/`. Thêm một mục vào `HANDOFF.md`. Sinh lại `TASK_BOARD.md`.
- **Source sản phẩm, test, migration, contract, gói EDU-0041:** không sửa. Manifest trước/sau được đối chiếu trong evidence.
- **Ghi đè thư mục ignored:** `frontend/dist` (build), `frontend/test-results` (Playwright), `.local/playwright-tmp`, cache Python/Node.
- **`.local/edu-0042/`** (ignored): manifest, diff đã chuẩn hóa, probe, log, snapshot Docker. File mật khẩu tổng hợp và fixture E2E đã bị xóa.
- **Docker:**
  - Khởi động Docker Desktop. Project `eduops360-edu0042` chỉ có service `db`, cổng 55495, mật khẩu tổng hợp ngẫu nhiên. `down -v` lúc 16:08:19.
  - Danh sách container, volume, network và image khớp baseline.
  - Lần `docker desktop stop` đầu tiên không giữ được: Desktop chạy lại, có thể do lệnh `docker version` gọi ngay sau đó. Lần dừng thứ hai được xác nhận lúc 16:10:39 (không lấy được status, không còn process).
- **Server tạm:** API 58099 và Vite 5173. Tiến trình node mồ côi của Vite (PID xác minh bằng command line) đã được dừng. Không còn listener.
- **Sai sót của reviewer, được ghi minh bạch:**
  1. Khi tạo diff chuẩn hóa, script sao cả thư mục `infra/` nên vô tình sao `infra/.env` vào `.local/edu-0042/normdiff/`. Nội dung **không được in**; bản sao và diff chứa nó đã bị xóa ngay, và diff được tạo lại có loại trừ `.env`.
  2. Lệnh quét secret trên cây thư mục quên loại trừ `.env`, nên đã đọc và **in ra transcript một dòng của `backend/.env`** (DSN local của role `eduops` thuộc Phase 01, kèm mật khẩu). Giá trị không được ghi vào file evidence nào. **Khuyến nghị người dùng xoay mật khẩu đó** (volume `eduops360-local_postgres-data`), hoặc xóa volume nếu xác nhận là disposable.
- Không dùng dữ liệu thật, không deploy public, không cài package, không truy cập package index, không có thao tác Git.
