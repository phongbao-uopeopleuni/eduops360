# Audit độc lập Phase 01 và Phase 02 — 2026-11-14

**Task:** `EDU-0031` · **Múi giờ:** Asia/Ho_Chi_Minh (+07:00) · **Phạm vi:** `D:\eduops360`
**Vai trò:** Claude (AI agent) đóng vai Independent Technical / Security Reviewer. Không tham gia triển khai EDU-0007..0030.
**Kết luận kỹ thuật:** **NEEDS_CHANGES** — có 2 finding P1 và 6 finding P2 tái hiện được trên API thật.
**Trạng thái phase:** Phase 01 và Phase 02 **NOT ACCEPTED**. OD-001/007/008/011 vẫn **OPEN**. Tài liệu này không thay Human Security Owner hay Product Owner (PHASE-02 §E, PHASE-00 §4).

Lượt này chỉ audit. Không sửa source sản phẩm, không bật role matrix, MFA recovery, break-glass hay audit retention. Không dùng dữ liệu học sinh thật và không deploy public. Không có thao tác Git vì `D:\eduops360` không phải Git repository.

## 1. Tóm tắt

Các bộ test hiện có đều pass khi chạy lại, và nhiều kiểm soát nền đúng như mô tả: default deny, grant nạp lại từ DB ở mỗi request, cookie/CSRF, token chỉ lưu hash, quyền DB tách ba role, rollback migration, readiness khi DB sập. Tuy vậy, probe trên PostgreSQL cô lập cho thấy:

1. **P1:** actor chỉ có `user:password_reset` có thể chiếm tài khoản admin cấp cao hơn. Actor chỉ có `user:suspend` có thể đình chỉ admin cấp cao hơn. Khẳng định "Admin API denies ... role escalation" chỉ đúng cho endpoint grant role (A0102-F01).
2. **P1:** chỉ cần gửi `User-Agent` dài hơn 500 ký tự, lần đăng nhập sai sẽ không tăng bộ đếm lockout và không ghi audit. Trạng thái rate limiter còn tạo ra oracle 429/500 để đoán mật khẩu (A0102-F02).
3. **P2:** Admin có thể chuyển tài khoản `pending` sang `active`, sau đó phát hành reset token, tự đặt mật khẩu và đăng nhập thay người dùng. Khẳng định "no Admin-selected initial password" vì vậy không đúng trên thực tế (A0102-F03).
4. **P2:** reset token có thể bị dùng hai lần khi hai request chạy đồng thời (A0102-F04). Kẻ tấn công chưa đăng nhập có thể đá phiên đang hoạt động bằng lockout (A0102-F05). Grant được ủy quyền tồn tại lâu hơn hiệu lực của người ủy quyền (A0102-F06). Argon2 chạy đồng bộ, chặn event loop (A0102-F07). E2E của Admin chỉ chạy trên mock (A0102-F08).

Không finding nào yêu cầu thay đổi kiến trúc. Mỗi finding có hướng sửa tối thiểu và regression test đề xuất cho lượt remediation riêng.

## 2. Preflight và baseline

| Hạng mục | Kết quả lúc audit |
|---|---|
| Working directory | `D:\eduops360` (10:41:40 +07:00) |
| `git status -sb`, `git reflog -n 10` | exit 128, `fatal: not a git repository` |
| Listener cổng dự án (5173/4173/8000/55432/55xxx) | không có |
| Tiến trình liên quan | Không có Uvicorn/Vite/PostgreSQL của dự án. Có tiến trình OpenAI Codex và chrome-devtools MCP không thuộc dự án, nên không đụng tới |
| Docker | Daemon không chạy. Có sẵn container/volume/image của dự án khác và volume cũ `eduops360-local_postgres-data`, `eduops360-audit-0011_postgres-data` |
| Manifest source | 326 file đã băm SHA-256 (loại trừ `node_modules`, `.venv`, `.local`, cache, `dist`, `test-results`). Đối chiếu ở mục 9 |
| Thư mục ignored có thể bị ghi đè | `frontend/dist` (12 file), `frontend/test-results` (5 file), `.local/playwright-tmp` |
| Task ID mới | `EDU-0031`. Không có tham chiếu EDU-0031+ trong `docs/progress` |

Inventory đã đối chiếu:

- **Backend:** `app/main.py`, `core/`, `db/`, `modules/health`, `modules/auth` (router, admin_router, session, guards, permissions, services, rate_limit, models, schemas), `modules/audit_logs`.
- **Migration:** `0001_foundation` → `0007_account_tokens`.
- **Endpoint (14):** health live/ready; auth login/logout/me/invitations-accept/password-reset-accept; admin roles, invitations, read user, password-reset, status, grant, revoke.
- **Test:** 11 file backend (79 test), 4 file Vitest (19 test), 2 file Playwright (7 test), 17 unittest gốc.
- **Tài liệu:** toàn bộ danh sách bắt buộc trong yêu cầu audit, kèm `THREAT_MODEL.md`, `MFA_RECOVERY_AND_BREAK_GLASS.md` và `SECURITY_GUARDRAILS.md`.

## 3. Verification chạy lại

Lệnh, exit code và môi trường chi tiết nằm trong `docs/progress/evidence/EDU-0031/verification.json`.

| Lớp | Lệnh (rút gọn) | Kết quả lúc audit |
|---|---|---|
| Backend host | `.venv\Scripts\python.exe -B -m pytest tests -q -p no:cacheprovider` | exit 0 — **72 passed, 7 skipped** (10:50) |
| Backend lint | `python -B -m ruff check --no-cache app migrations tests` | exit 0 — All checks passed |
| PostgreSQL 18 cô lập | cùng lệnh pytest, có `EDUOPS_TEST_*_DSN` | exit 0 — **79 passed**, trong đó 7/7 integration (10:55) |
| Migration | `alembic upgrade head` / `current` / `check` | `0007_account_tokens (head)`, "No new upgrade operations detected" |
| Roundtrip | `downgrade 0003` → `downgrade base` → `upgrade head` → `check` | đều exit 0, check sạch |
| Runtime chạy Alembic | `alembic current` bằng `eduops_runtime` | exit 1, `permission denied for table alembic_version` |
| Governance | `validate_blueprint`, `check_structure`, `check_text_encoding` (293 file), `unittest` (17) | exit 0 |
| OpenAPI | `scripts/export_openapi.py --check` | "OpenAPI contract matches FastAPI" |
| Frontend | `typecheck`, `lint`, `format:check`, `api:check`, `test` | exit 0 — **19 passed** |
| E2E | `playwright test`, Chrome cài sẵn | Cấu hình mặc định lỗi bind cổng 8000 (xem F15). Với server ngoài (`PLAYWRIGHT_EXTERNAL_SERVER=1`, API 58093): **7 passed** |
| Build | `npm run build` | exit 0 |

Các con số trong handoff (72 passed/7 skipped, 7 integration, 19 unit, 7 E2E, head `0007`, không phải Git repo) **khớp** với lần chạy lại. Các khẳng định định tính được đối chiếu ở mục 5.

## 4. Findings

Mức độ: **P1** — kiểm soát bảo mật bị vượt qua, phải sửa trước khi nghiệm thu Phase 02. **P2** — lỗi bảo mật hoặc tính đúng đắn đáng kể, hoặc test gap che giấu P1. **P3** — rủi ro thấp, cấu hình, hoặc quy trình.

| ID | Mức | Tóm tắt | Probe |
|---|---|---|---|
| A0102-F01 | P1 | Phát hành reset và đổi trạng thái không bị giới hạn theo đặc quyền của tài khoản đích → chiếm tài khoản cấp cao hơn | P2 |
| A0102-F02 | P1 | `User-Agent` > 500 ký tự rollback bộ đếm lockout và audit đăng nhập sai, kèm oracle 429/500 | P4 |
| A0102-F03 | P2 | `pending → active` vượt qua lời mời; Admin tự đặt mật khẩu; audit gán hành động cho người dùng đích | P1 |
| A0102-F04 | P2 | Hai request đồng thời cùng tiêu thụ được một reset token (identity map cũ) | P3 + offline |
| A0102-F05 | P2 | Người chưa đăng nhập khóa tài khoản và chấm dứt phiên đang hoạt động của nạn nhân | P5 |
| A0102-F06 | P2 | Grant được ủy quyền không bị giới hạn bởi hiệu lực của người ủy quyền; tự cấp cho mình được phép; audit grant thiếu scope/validity | P7 |
| A0102-F07 | P2 | Argon2id chạy đồng bộ trong handler async, chặn event loop; endpoint chưa xác thực khuếch đại DoS | P6 + offline B |
| A0102-F08 | P2 | Test gap che các finding trên: E2E Admin hoàn toàn mock; test lockout nhắm vào hàm không được dùng | log E2E |
| A0102-F09 | P3 | Rate limiter: khóa theo IP+email cho phép password spraying; đẩy key LRU; giới hạn trong từng tiến trình | offline C |
| A0102-F10 | P3 | Không có đường mời lại; tài khoản `pending` có token hết hạn bị kẹt | P10 |
| A0102-F11 | P3 | `cors_origins=["*"]` được chấp nhận cùng credentials → phản chiếu mọi Origin | offline A |
| A0102-F12 | P3 | TOTP không chống replay; `mfa_secret` là cột văn bản thường | đọc code |
| A0102-F13 | P3 | `backend/.env` và `infra/.env` cũ (role superuser Phase 01); E2E/Alembic đọc `backend/.env` | đọc config |
| A0102-F14 | P3 | Healthcheck Compose kiểm Unix socket → có thể báo healthy khi server init tạm đang chạy | log DB |
| A0102-F15 | P3 | Playwright hard-code cổng 8000 (bị Windows loại trừ) và `reuseExistingServer` | E2E |
| A0102-F16 | P3 | Generator dữ liệu giả không giới hạn đường dẫn trong workspace | đọc code |
| A0102-F17 | P3 | Evidence EDU-0024..0030 không ghi lệnh/exit code; HANDOFF nói ngược lại | đọc evidence |
| A0102-F18 | P3 | Image runtime cài dependency dev; lock không có hash | Dockerfile |
| A0102-F19 | P3 | Integration test sửa mapping toàn cục của `system_admin` mà không dọn | đọc test |
| A0102-F20 | P3 | Admin UI: lỗi tải role bị nuốt; form trạng thái mặc định `active` cho tài khoản vừa mời | đọc code |
| A0102-F21 | P3 (tồn đọng) | Toàn vẹn audit chỉ dựa trên GRANT; migrator là superuser; chưa có anchor HMAC; downgrade xóa audit | P11, roundtrip |
| A0102-F22 | P3 (tồn đọng) | Không có idle timeout cho phiên | đọc code |

Probe nằm ở `docs/progress/evidence/EDU-0031/probes/`, output tương ứng ở cùng thư mục evidence.

### A0102-F01 — P1 — Reset/đổi trạng thái không bị giới hạn theo đặc quyền đích

- **Vị trí:** `backend/app/modules/auth/admin_router.py:220-271` (`issue_password_reset`) và `:274-321` (`change_user_status`). Chỉ có `enforce_permission(..., scope=Scope())`. Không so sánh quyền của actor với quyền của người dùng đích. `grant_role` thì có `can_delegate_role` (`:347`).
- **Tái hiện** (`probe_live.json` → `P2_...`):
  - Actor có duy nhất `user:password_reset` toàn cục. Actor này không được đọc user (403).
  - Actor vẫn phát hành reset cho admin có đủ `user:*` → **201**, tự accept → **204**, đăng nhập bằng mật khẩu mới → **200**. Sau đó gọi `GET /admin/users/{id}` với tư cách admin → **200**.
  - Actor chỉ có `user:suspend` đình chỉ admin cấp cao hơn → **200**.
- **Tác động:** leo thang đặc quyền hoàn toàn từ một quyền hẹp. MFA lẽ ra giảm rủi ro, nhưng enrollment chưa được phép bật. Audit accept ghi `actor_id` là **người dùng đích** (`router.py:276, 334`), nên người thực sự nắm token không hiện ra trong bản ghi.
- **Kỳ vọng:** khớp với THREAT_MODEL ("delegation subset check") và PHASE-02 §E ("denies ... role escalation").
- **Hướng sửa tối thiểu:** trước khi reset, suspend hoặc activate, yêu cầu quyền của actor bao trùm toàn bộ quyền hiệu lực của tài khoản đích. Có thể tái dùng `can_delegate_role` với cặp quyền hiệu lực của tài khoản đích. Ghi `token.created_by` vào audit khi accept. Quy tắc cụ thể phụ thuộc OD-008, cần Security Owner xác nhận.
- **Regression:** live API — actor chỉ có reset nhắm vào admin có quyền rộng hơn → 403. Actor chỉ có suspend nhắm vào admin cấp cao hơn → 403.

### A0102-F02 — P1 — User-Agent dài vô hiệu hóa lockout và audit đăng nhập sai

- **Vị trí:**
  - Header được ghi nguyên văn tại `router.py:196, 215, 229, 280, 338, 372`.
  - Cột `audit_logs.user_agent VARCHAR(500)` (`audit_logs/models.py:48`, `0003_audit_logs.py:34`) và `sessions.user_agent VARCHAR(500)` (`auth/models.py:267`, `0002_auth_users.py:198`).
  - Nhánh đăng nhập sai (`router.py:181-199`) tăng `failed_login_count`, ghi audit rồi commit trong cùng transaction. Audit lỗi kéo theo rollback bộ đếm.
- **Tái hiện** (`P4_...`):
  - 8 lần sai với UA dài 612 ký tự → toàn bộ **500** (`StringDataRightTruncation`). Tài khoản vẫn `active`, `failed_login_count=0`, **0** dòng audit `session:login_failed`.
  - Đối chứng với UA bình thường: 5 lần sai → `locked`, 5 dòng audit.
  - **Oracle:** limiter (giới hạn 3) ghi nhận lỗi trong bộ nhớ *trước* khi ghi audit, còn mật khẩu đúng thì không. Sau 2 lần sai đã biết, đoán **sai** → request kế tiếp nhận **429**. Đoán **đúng** → request kế tiếp nhận **500**.
- **Tác động:** kẻ tấn công chưa đăng nhập đoán mật khẩu với tốc độ của limiter trong bộ nhớ (10/60 s mỗi cặp IP+email theo mặc định), không bị lockout và không để lại audit. Mỗi IP thêm vào lại có cửa sổ riêng. Người dùng thật có UA dài cũng bị 500 ở mọi thao tác ghi audit.
- **Hướng sửa tối thiểu:** cắt hoặc chuẩn hóa `user_agent` về giới hạn cột (hoặc đổi sang `Text`) tại một helper dùng chung trước khi gán vào `Session` và audit. Có thể cân nhắc ghi nhận failure vào limiter theo cùng cách cho cả nhánh lỗi hệ thống. Không nới fail-closed của audit.
- **Regression:** live API — UA 600+ ký tự, 5 lần sai → tài khoản `locked`, 5 dòng audit, không có 500.

### A0102-F03 — P2 — `pending → active` vượt qua lời mời; Admin tự đặt mật khẩu ban đầu

- **Vị trí:**
  - `admin_router.py:282-298` cho phép chuyển sang `active` từ mọi trạng thái, kể cả `pending`.
  - `accept_invitation` yêu cầu `pending` (`router.py:251`).
  - `issue_password_reset` chỉ chặn `pending` (`admin_router.py:230`).
  - Form UI mặc định `active` (`UserManagementPage.tsx:264`).
- **Tái hiện** (`P1_...`): mời → `pending`. PATCH status `active` → **200**. Người được mời accept → **400** (lời mời vô hiệu). Admin phát hành reset → **201** và tự accept với mật khẩu do Admin chọn → **204**. Đăng nhập thay người dùng → **200**.
- **Tác động:** trái với khẳng định ở EDU-0030 và PHASE_02_TECHNICAL_AUDIT ("no Admin-selected initial password"). Audit gán `password_reset_accept` cho tài khoản đích (xem F01). Việc Admin luôn nhận raw invitation token là thiết kế kênh chuyển tay, cần Security Owner chấp nhận rủi ro một cách tường minh.
- **Hướng sửa tối thiểu:** `activate` chỉ áp dụng cho `suspended` (và có thể `locked`). Tài khoản `pending` phải đi qua lời mời (kèm F10). UI không mặc định `active` cho tài khoản `pending`.
- **Regression:** PATCH `active` trên tài khoản `pending` → 409. Lời mời vẫn dùng được sau lần thử đó.

### A0102-F04 — P2 — Reset token dùng được hai lần khi đồng thời

- **Vị trí:** `router.py:69-101`. Lần đọc đầu không khóa đưa `AccountToken` vào identity map. Lần đọc lại `with_for_update()` không làm mới attribute (không có `populate_existing`), nên kiểm tra `used_at` dùng giá trị cũ.
- **Tái hiện:**
  - `probe_identity_map.txt` (SQLAlchemy 2.1.8): DB đã có `used_at`, nhưng lần đọc lại có khóa vẫn thấy `None`. Với `populate_existing` thì thấy giá trị mới.
  - `P3_...` trên PostgreSQL với hàm thật `_consume_account_token`: request B bị chặn khi A chưa commit, rồi được **accepted** sau khi A commit (`orm_used_at_seen_by_b: None`). Dùng lại tuần tự sau commit → `ACCOUNT_TOKEN_INVALID`.
- **Tác động:** bất biến "single-use" chỉ đúng khi các request chạy tuần tự. Hai bên cùng giữ token (ví dụ token bị lộ) có thể cùng đặt mật khẩu. Bên commit sau thắng. Đường lời mời được bảo vệ phụ nhờ kiểm tra `status == pending`, còn đường reset thì không.
- **Hướng sửa tối thiểu:** thêm `.execution_options(populate_existing=True)` cho lần đọc có khóa, hoặc tiêu thụ nguyên tử bằng `UPDATE ... WHERE id=:id AND used_at IS NULL AND expires_at > now() RETURNING` rồi kiểm tra rowcount.
- **Regression:** test hai session như probe P3 → request thứ hai nhận `ACCOUNT_TOKEN_INVALID`.

### A0102-F05 — P2 — Lockout từ người chưa đăng nhập chấm dứt phiên đang hoạt động

- **Vị trí:** `session.py:84-85` từ chối mọi phiên khi `user.status != active`. Login (`router.py:184-187`) đặt `locked` sau 5 lần sai, bất kể ai gửi.
- **Tái hiện** (`P5_...`): nạn nhân đăng nhập, `/me` → 200. Người lạ gửi 5 lần sai → nạn nhân `/me` → **401 `ACCOUNT_UNAVAILABLE`**. Lặp lại mỗi 30 phút sẽ giữ Admin bị đẩy ra liên tục.
- **Hướng sửa tối thiểu:** khóa do sai mật khẩu chỉ nên chặn *đăng nhập mới*, không vô hiệu phiên hợp lệ đã có. Phiên chỉ bị từ chối khi tài khoản `suspended` hoặc `pending`. Chính sách lockout cụ thể (thời gian, ngưỡng, khóa theo IP) cần Security Owner chốt.
- **Regression:** phiên còn hiệu lực sau 5 lần sai từ client khác. Đăng nhập mới vẫn bị chặn.

### A0102-F06 — P2 — Ủy quyền vượt hiệu lực của người ủy quyền; tự cấp cho mình; audit grant thiếu thông tin

- **Vị trí:** `admin_router.py:324-413`. Không chặn `user_id == actor`. `valid_until` do người gọi chọn, không giới hạn theo grant của actor (`:354-360`). `after_state` chỉ có `user_id/role_id/school_id/academic_year_id` (`:404-409`).
- **Tái hiện** (`P7_...`): người ủy quyền có grant scope (S,Y) hết hạn sau 10 phút.
  - Cấp cùng role cho người khác **không thời hạn** → 201. Tự cấp cho mình scope (S,Y,khối 1) không thời hạn → 201.
  - Sau khi grant gốc hết hạn, cấp ở (S,Y) → 403 (đúng), nhưng cấp ở (S,Y,khối 1) → **201**.
  - Audit của lần tự cấp thiếu `grade_id` và `valid_until`.
- **Hướng sửa tối thiểu:** `valid_until` của grant mới ≤ hạn sớm nhất của grant bao trùm của actor. Chặn tự cấp (hoặc buộc qua quy trình hai bước theo OD-007). Ghi đủ `grade_id/class_id/subject_id/valid_from/valid_until` vào `after_state`.
- **Regression:** tự cấp → 403. Grant vượt hạn của actor → 422/403. Audit có đủ các khóa scope và validity.

### A0102-F07 — P2 — Argon2id chặn event loop

- **Vị trí:** `services.py:19-25,46-62`, được gọi trực tiếp trong `async def login`, `accept_*` và `create_user_invitation`. `LoginRateLimiter` khóa theo IP+email (`session.py:34-36`), nên mỗi email mới không bị chặn.
- **Tái hiện:** mỗi lần verify mất khoảng 45 ms (`probe_offline.txt` B). `probe_loop.json` với 10 login sai đồng thời (email khác nhau): latency `/health/live` tối đa **197 ms**, burst 627 ms, chỉ lấy được 10 mẫu ping thay vì khoảng 100. Ước tính khoảng 22 request login/giây là đủ chiếm toàn bộ event loop, đến từ một client chưa đăng nhập.
- **Hướng sửa tối thiểu:** chạy hash/verify trong threadpool (`anyio.to_thread`/`run_in_threadpool`) với semaphore giới hạn đồng thời, và thêm giới hạn theo IP riêng (xem F09).
- **Regression:** latency `/health/live` dưới ngưỡng khi có N login đồng thời.

### A0102-F08 — P2 — Test gap che các finding trên

- `tests/e2e/user-management.spec.ts` route-mock toàn bộ `/auth/*` và `/admin/*`, và tự cấy cookie CSRF. Log backend trong lượt E2E: **0** request `auth/admin` tới server. Vì vậy "browser confirms CSRF header" (TRACEABILITY, EDU-0027/0030) chỉ chứng minh client gửi header, không chứng minh cookie do server cấp hay việc server kiểm tra.
- Test lockout (`tests/auth/test_services.py`) nhắm vào `check_account_locked` (`services.py:79`), một hàm **không được gọi** ở đâu trong `app/`. Router có logic lockout riêng (`router.py:160-187`), và logic này không có integration test cho khóa hay hết hạn khóa.
- `HIGH_RISK_ACTIONS`/`is_high_risk_action` (`audit_logs/service.py:156,191`) không được dùng. Finding F14 của review 2026-11-12 vẫn còn.
- Chưa có test cho đồng thời, chuyển trạng thái `pending`, giới hạn đặc quyền khi reset, độ dài header, hay phiên sau lockout.
- **Đề xuất:** thêm các regression ở F01–F06 vào `tests/integration/`. Thêm một E2E tối thiểu chạy với backend và DB thật cho login/CSRF/logout. Nối hoặc xóa `check_account_locked`, và cưỡng chế hoặc xóa `HIGH_RISK_ACTIONS`.

### A0102-F09 — P3 — Rate limiter

`session.py:34-36` và `rate_limit.py:15-71`. (a) Khóa SHA-256(IP + email), không có giới hạn theo IP, nên password spraying qua nhiều tài khoản (mỗi tài khoản dưới 5 lần) không bị giới hạn. (b) Đẩy key LRU: 10.000 key giả làm key nạn nhân đang bị chặn trở về `None` (`probe_offline.txt` C). (c) Giới hạn trong từng tiến trình; nhiều worker sẽ nhân giới hạn lên. Lockout DB vẫn là kiểm soát bền vững, nên mức là P3, nhưng liên quan đến F02/F07.

### A0102-F10 — P3 — Không có đường mời lại

`P10`: tài khoản `pending` có token hết hạn. Mời lại cùng email → **409** `EMAIL_EXISTS`. Reset → **409** `INVITATION_REQUIRED`. Lối thoát duy nhất qua API là đường F03. Cần endpoint phát hành lại lời mời có audit, đồng thời vô hiệu token cũ.

### A0102-F11 — P3 — CORS wildcard cùng credentials

`config.py:16` không kiểm tra giá trị. Với `cors_origins=["*"]`, Starlette trả `Access-Control-Allow-Origin: https://attacker.example` và `Allow-Credentials: true` khi có header Cookie (`probe_offline.txt` A). Đây là lỗi chỉ xuất hiện khi cấu hình sai, nhưng hiện chưa có gì chặn. Đề xuất validator từ chối `*`.

### A0102-F12 — P3 — TOTP replay và lưu secret

`session.py:39-57` chấp nhận lại cùng một mã trong cửa sổ ±1 bước vì không lưu bước đã dùng. `auth/models.py:55` lưu `mfa_secret` dạng văn bản. Hiện chỉ cấp phát được qua ghi DB trực tiếp. Không có endpoint enrollment, điều này đúng với trạng thái chưa phê duyệt. Cả hai điểm thuộc thiết kế custody đang chờ duyệt. `MFA_RECOVERY_AND_BREAK_GLASS.md` ghi đúng trạng thái `DRAFT / NOT APPROVED`.

### A0102-F13 — P3 — Cấu hình local cũ

- `backend/.env` trỏ tới `eduops@127.0.0.1:55432`, tức role khởi tạo superuser của Phase 01 (giá trị đã che).
- `infra/.env` chỉ có `POSTGRES_PASSWORD`, trong khi Compose hiện tại yêu cầu ba mật khẩu, nên `up` sẽ fail-closed.
- Playwright `webServer` (`playwright.config.ts:40-43`, `cwd: backend`) và `migrations/env.py` đọc `backend/.env`. Nếu volume Phase 01 còn chạy, E2E hoặc Alembic sẽ kết nối bằng superuser mà không báo gì.
- Đề xuất cập nhật mẫu và không dùng role superuser cho runtime host.

### A0102-F14 — P3 — Healthcheck Compose có race khi init lần đầu

`infra/compose.dev.yml:20` dùng `pg_isready` qua Unix socket. Log lượt này cho thấy server init tạm chỉ nghe socket trong khoảng 03:55:00.77→01.50 UTC. Lần check đầu (03:55:03.8) không trúng cửa sổ đó, nhưng trên máy chậm, `migrate` có thể bắt đầu khi server thật chưa nghe TCP. Đề xuất `pg_isready -h 127.0.0.1`.

### A0102-F15 — P3 — Tính di động của E2E

`playwright.config.ts:40-49` hard-code cổng 8000. Cổng này nằm trong dải 7957–8056 bị Windows loại trừ sau khi Docker chạy, và vẫn bị loại trừ sau khi dừng Docker. Lỗi bind đã tái hiện; EDU-0030 cũng ghi nhận lỗi này. `reuseExistingServer: !CI` có thể bám vào một server lạ trên 8000/5173. Đề xuất cho phép cấu hình cổng qua biến môi trường.

### A0102-F16 — P3 — Generator không giới hạn đường dẫn

`scripts/generate_synthetic_students.py:25-27` nhận đường dẫn bất kỳ (tuyệt đối hoặc chứa `..`) và tạo thư mục cha. Phần chống ghi đè (`open("x")`), tính tất định, BOM, NFC và số 0 đứng đầu đều đúng, và test pass. Unit test gốc ghi CSV 2k/10k vào TEMP hệ thống, ngoài workspace (tự dọn). Đề xuất chỉ cho phép ghi dưới `.local/` hoặc workspace.

### A0102-F17 — P3 — Evidence không tái lập được

`docs/progress/evidence/EDU-0024..0030/verification.json` chỉ có tóm tắt, không có lệnh, exit code hay output. `HANDOFF.md` ghi "Exact commands and side effects are in ... verification.json", điều này không đúng. Yêu cầu tương ứng là PHASE-00 P00-T09/G07. Evidence của EDU-0031 ghi đủ các trường này.

### A0102-F18 — P3 — Image runtime và lockfile

`backend/Dockerfile:6` cài toàn bộ `requirements.lock`, gồm cả pytest, ruff và httpx2, vào image runtime. Lock không có `--hash`. `httpx2/httpcore2` có metadata trỏ tới `github.com/pydantic/httpx2` và được Starlette TestClient import, nên không bị coi là typosquat. Chưa kiểm tra lại upstream trong lượt này.

### A0102-F19 — P3 — Integration test làm bẩn mapping toàn cục

`tests/integration/test_auth_api.py:158-180, 295-306` chèn quyền vào role `system_admin` và không dọn. Test chỉ dựa vào DSN để chạy, không có gì bảo đảm DB là disposable. Nếu chạy nhầm vào DB lâu dài, mapping toàn cục mà OD-008 đang cố ý để trống sẽ bị kích hoạt. Đề xuất dùng role tổng hợp riêng như các probe, hoặc kiểm tra marker DB disposable.

### A0102-F20 — P3 — Admin UI

`UserManagementPage.tsx:55` nuốt lỗi tải role (danh sách rỗng, không báo lỗi hay thiếu quyền). Form trạng thái mặc định `active` ngay cho tài khoản vừa mời (`:264`), dẫn thẳng tới F03. Token chỉ nằm trong React state, không vào `localStorage`, render qua JSX escape. Không thấy `dangerouslySetInnerHTML`.

### A0102-F21 — P3 (tồn đọng, OD-011) — Toàn vẹn audit

Runtime và audit worker không sửa được audit (test live pass). Tuy nhiên, `eduops_migrator` là superuser do `POSTGRES_USER` tạo (`migrator_is_superuser: true`). Chưa có chữ ký/HMAC neo ngoài tài khoản ứng dụng như THREAT_MODEL mô tả. `0003.downgrade()` xóa bảng audit vô điều kiện. Ngoài ra, `ALTER DEFAULT PRIVILEGES ... FROM PUBLIC` của `0004` không tạo entry nào (`pg_default_acl` rỗng), nghĩa là bảng tương lai fail-closed nhờ mặc định của PostgreSQL chứ không nhờ lệnh này. Đã xác nhận runtime không có quyền trên bảng mới.

### A0102-F22 — P3 (tồn đọng) — Không có idle timeout

Phiên có hạn tuyệt đối 24 giờ. `last_activity_at` được cập nhật nhưng không được dùng để hết hạn (`session.py:87-89`). Điểm này đã được review 2026-11-12 nêu và vẫn còn.

## 5. Đối chiếu khẳng định trong handoff và audit cũ

| Khẳng định | Kết quả kiểm chứng |
|---|---|
| 72 passed / 7 skipped; 7 integration; 19 unit; 7 E2E; head `0007`; không phải Git repo | **Đúng** lúc 10:50–11:04 |
| Default deny; grant nạp lại từ DB; stale grant bị từ chối | **Đúng** (code + test live) |
| "Admin API denies ... role escalation" | **Một phần** — đúng với grant; sai với reset/suspend (F01) |
| "No Admin-selected initial password" | **Sai trên thực tế** (F03) |
| Token "single-use" | **Chỉ đúng tuần tự** (F04) |
| "Browser confirms CSRF header" | **Chỉ trên mock** (F08) |
| Runtime và worker không sửa/xóa/truncate audit | **Đúng** (test live) |
| Audit lỗi → rollback ghi nghiệp vụ | **Đúng**, nhưng chính cơ chế này bị khai thác ở F02 |
| Lockout hết hạn (F08 của review 2026-11-12) | **Đã sửa** trong router (`router.py:164-171`) |
| Thiếu `submitter_id` → từ chối (F07 cũ) | **Đã sửa** (`permissions.py:96-100`), chưa có endpoint nào dùng |
| MFA recovery/break-glass ở trạng thái DRAFT/NOT APPROVED | **Đúng**. Không có endpoint enrollment hay recovery |
| Evidence ghi đủ lệnh | **Sai** (F17) |

## 6. Mục đã kiểm và không phát hiện lỗi

- **Phase 01:**
  - App factory đăng ký đủ 4 router dưới `/api/v1`. Error envelope an toàn, có request ID, `no-store` và `Allow` khi 405.
  - Settings dùng `SecretStr`, `hide_input_in_errors`. URL bắt buộc `postgresql+psycopg` có host và DB. Engine dùng `hide_parameters`.
  - Readiness: DB sập → 503 sau khoảng 3 s, body chỉ có `status/database/checked_at`, liveness vẫn 200, tự phục hồi (`probe_readiness.json`).
  - OpenAPI và TypeScript khớp hai chiều.
  - Uvicorn 0.54 dùng `create_event_loop` làm loop factory (Selector trên Windows).
  - Ngày lịch và UTC chặt chẽ ở cả backend và frontend. Timestamp sai định dạng được xử lý an toàn.
  - Theme bền vững, chịu được khi storage bị chặn. Skip link, bàn phím, mobile và contrast ≥ 4.5 (E2E).
- **Phase 02:**
  - Cookie `HttpOnly; Secure; SameSite=strict`. CSRF double-submit gắn với hash trong phiên.
  - Session, CSRF, invitation và reset token đều chỉ lưu SHA-256 và có entropy 256 bit.
  - Đăng nhập sai cho cùng một response 401 cho mọi lý do, có dummy hash cho email không tồn tại.
  - Đình chỉ thu hồi phiên (`P9`). Reset thu hồi phiên.
  - Race email trùng (khác hoa thường) → 1×201, 3×409, chỉ 1 user (`probe_invite_race.json`).
  - Path UUID được validate.
  - Quyền DB: runtime có SELECT/INSERT/UPDATE trên `account_tokens`, không DELETE/TRUNCATE, worker không SELECT. Không có quyền trên bảng mới.
  - Downgrade dưới `0004` trả quyền CONNECT/USAGE mặc định cho PUBLIC nhưng không mở quyền bảng nào.
  - Frontend không quyết định authorization: các control chỉ hỗ trợ UX, backend vẫn trả 403.

## 7. Giới hạn của audit

- AI reviewer không thay Human Security Owner (OD-001).
- Không có Git hay hosted CI.
- Không kiểm tra lại advisory npm/PyPI trực tuyến.
- Probe race F04 điều phối bằng hàm thật với hai session, chưa chạy qua hai HTTP request thật.
- Chưa đo trên Linux container. Toàn bộ chạy trên Windows 11, Python 3.13.5, Node 24.12.0, PostgreSQL 18 (image `postgres:18` có sẵn local).

## 8. Câu hỏi cần người có thẩm quyền quyết định

1. **OD-008:** quy tắc "actor phải bao trùm quyền của tài khoản đích" cho reset, suspend và activate (F01). Có được tự cấp quyền cho mình không, và hạn tối đa của grant được ủy quyền là bao lâu (F06)?
2. **Security Owner:** chính sách lockout có nên chấm dứt phiên đang có (F05)? Ngưỡng và thời gian khóa, giới hạn theo IP (F09)?
3. **Security Owner:** có chấp nhận rủi ro "Admin nhận raw invitation/reset token để chuyển tay" khi chưa có kênh thông báo đã duyệt không (F03)?
4. **OD-011:** ai được chạy downgrade xóa audit? Có cần anchor HMAC ngoài DB không (F21)?

## 9. Tác dụng phụ và teardown

- **Tạo mới:** tài liệu này, `docs/progress/tasks/EDU-0031.md`, `docs/progress/evidence/EDU-0031/` (evidence và bản sao probe). Bổ sung một mục trỏ tới audit này trong `docs/progress/HANDOFF.md`. `TASK_BOARD.md` được sinh lại bằng script.
- **Source sản phẩm:** không sửa. Manifest SHA-256 được đối chiếu sau cùng (xem evidence).
- **`.local/audit-phase-01-02/`** (ignored): probe, log, manifest, ảnh chụp trạng thái Docker và file env tổng hợp. File env bị xóa khi kết thúc.
- **Ghi đè thư mục ignored:** `frontend/dist` (build), `frontend/test-results` (E2E), `.local/playwright-tmp`.
- **Docker:**
  - Đã khởi động Docker Desktop. Compose project `eduops360-audit-p0102` chỉ chạy service `db` với image có sẵn và mật khẩu ngẫu nhiên tổng hợp, cổng 55491.
  - `down -v` đã xóa container, network và volume. Không build image nào.
  - Danh sách container/volume/network/image khớp baseline. Docker Desktop đã được dừng lại.
- **Server tạm:** API ở cổng 58093 và Vite ở 5173 cho E2E, đã dừng. Không còn listener nào.
- **Ngoài workspace:** `/tmp/out.txt` của Git Bash được tạo rồi xóa ngay. Unit test gốc tạo và tự dọn thư mục trong TEMP hệ thống. Cache npm/pip có thể đã được đọc.
- Không dùng dữ liệu thật, không deploy public, không có thao tác Git.
