# Audit bug nguy hiểm — 2026-11-17

**Task:** EDU-0071  
**Reviewed commit:** `62d6beba633992858b31abcfea841ff28f7e4323`  
**Branch:** `codex/edu-0070-github-pages` (khớp
`origin/codex/edu-0070-github-pages` trước audit)  
**Kết luận:** `NEEDS_CHANGES` — không có P0 được xác nhận; có 2 P1 mới, 4 P2
đang mở và các release blocker đã biết. Không phase nào được chấp nhận bởi audit
này.

## 1. Phạm vi và cách phân loại

Audit chỉ đọc mã đang checkout: IAM/session/CSRF/RBAC, audit, pure-domain Phase
03, frontend/API client, GitHub Pages, Docker/CI và dependency lock. Không kiểm
tra hay nhập dữ liệu học sinh thật; không sửa product code, migration, workflow,
cloud setting hoặc branch protection.

- **P0:** đang tạo nguy cơ mất dữ liệu/chiếm quyền diện rộng tức thời.
- **P1:** có thể giữ/nhân quyền trái phép hoặc phá toàn vẹn kiểm soát quan trọng
  với tiền điều kiện thực tế.
- **P2:** gây từ chối dịch vụ hoặc mở đường bỏ qua release/supply-chain gate.
- Cảnh báo policy/hardening không được nâng thành bug xác nhận nếu thiếu quyết
  định hoặc đường khai thác hiện tại.

## 2. Tóm tắt finding

| ID | Mức | Trạng thái | Kết quả |
|---|---:|---|---|
| A71-F01 | P1 | Mới, xác nhận bằng code/schema | Grant được ủy quyền vẫn hoạt động sau khi grant nguồn bị thu hồi sớm, trái invariant “không sống lâu hơn delegator”. |
| A71-F02 | P1 | Mới, xác nhận bằng code/schema | Hai request đồng thời có thể tạo hai active grant giống nhau; thu hồi một row không loại bỏ quyền từ row còn lại. |
| A71-F03 | P2 | Mới, probe an toàn xác nhận | Login nhận password 1 MiB và không có app/edge body cap được khai báo, tạo bề mặt DoS trước xác thực. |
| R42-F02 / A71-F04 | P2 | Đã biết, tái xác nhận | 50 lỗi từ một direct peer chặn login đúng của tài khoản khác cùng IP/NAT. Chính sách vẫn `NOT APPROVED`. |
| A71-F05 | P2 | Mới, remote config xác nhận | Nhánh được phép deploy Pages đang không được bảo vệ, tạo đường phát hành public ngoài gate của `main`. |
| A71-F06 | P2 | Mới, config xác nhận | 13 GitHub Action references đều dùng mutable major tag; action deploy có `pages: write` và OIDC. |

Không phát hiện bug P0 hoặc P1 khai thác được trong frontend hiện tại. Public
Pages bundle được kiểm tra là preview tĩnh, không chứa login/admin API route trong
đường tương tác đã test.

## 3. Finding chi tiết

### A71-F01 — P1 — Delegated grant sống sau khi quyền nguồn bị thu hồi

**Bằng chứng**

- `backend/app/modules/auth/admin_router.py:163-193` tuyên bố delegated grant
  không được sống lâu hơn delegator nhưng chỉ chụp `valid_until` tại lúc cấp.
- `backend/app/modules/auth/admin_router.py:529-581` lưu `granted_by` nhưng không
  lưu grant nguồn nào đã cho phép delegation.
- `backend/app/modules/auth/guards.py:58-85` nạp grant của principal chỉ theo
  trạng thái/thời hạn của chính grant đó; không tái xác minh authority chain.
- `backend/app/modules/auth/admin_router.py:620-645` chỉ thu hồi row được chỉ định,
  không vô hiệu dependent grant.
- Probe metadata: `UserRole` có `granted_by` nhưng không có
  `authorizing_grant_id` hay ràng buộc tương đương.

**Tiền điều kiện:** A hợp lệ cấp vai trò cho B; sau đó grant đã cho A quyền cấp bị
thu hồi hoặc rút hạn sớm.  
**Tác động:** B tiếp tục giữ quyền nhạy cảm, làm giảm hiệu lực containment và
stale-grant revocation.  
**Test còn thiếu:** cấp A → B, thu hồi grant nguồn của A, sau đó yêu cầu B thực
hiện thao tác phải bị 403 ngay.  
**Sửa nhỏ nhất:** chốt invariant delegation với Security Owner; lưu provenance
đủ để tái xác minh/revoke descendant hoặc thực hiện cascade có kiểm soát. Không
mở rộng thành role-graph chung khi chưa cần.

### A71-F02 — P1 — Race tạo duplicate active role grant

**Bằng chứng**

- `backend/app/modules/auth/admin_router.py:553-584` dùng mô hình
  `SELECT duplicate → INSERT`; hai transaction `READ COMMITTED` có thể cùng
  không thấy row và cùng insert.
- `backend/app/modules/auth/models.py:229-235` và migration
  `0002_auth_users.py:124-180` không có unique constraint/index cho active grant.
- Probe SQLAlchemy metadata trả `user_role_unique_constraints=0`.
- `backend/app/modules/auth/admin_router.py:620-645` thu hồi theo một
  `user_role_id`; duplicate còn lại vẫn cấp quyền.
- Thiết kế cũ tại `docs/security/RBAC_DESIGN.md:128` cũng dự kiến uniqueness,
  nhưng database hiện tại không thực thi.

**Tiền điều kiện:** retry đồng thời, double-click hoặc hai Admin cấp cùng
user/role/scope.  
**Tác động:** giao diện/audit có thể báo đã thu hồi một grant trong khi principal
vẫn còn quyền từ duplicate; đây là lỗi toàn vẹn authorization.  
**Test còn thiếu:** hai POST đồng thời, kỳ vọng đúng một `201`, request còn lại
`409`; sau revoke phải không còn permission.  
**Sửa nhỏ nhất:** migration thêm uniqueness active-grant ở DB với xử lý `NULL`
scope an toàn, bắt `IntegrityError` và trả `409`; bắt buộc migration review.

### A71-F03 — P2 — Login password/body không giới hạn

**Bằng chứng**

- `backend/app/modules/auth/schemas.py:96-102` dùng `password: SecretStr` không
  `max_length`, trong khi các schema tạo/reset password giới hạn 128.
- `backend/app/modules/auth/router.py:152-178` nhận body đã parse rồi chuyển
  password sang Argon2; limiter Argon2 chỉ giới hạn số worker, không giới hạn
  kích thước body đã nhận.
- `backend/app/main.py:20-100` không có request-size guard; chưa có edge contract
  nào trong branch này.
- Probe không gọi DB/hash xác nhận `LoginRequest` chấp nhận password 1 MiB.

**Tiền điều kiện:** endpoint login được công khai.  
**Tác động:** nhiều body lớn có thể tiêu thụ memory/bandwidth và làm nghẽn trước
xác thực.  
**Test còn thiếu:** password vượt ngưỡng phải 422 và body vượt giới hạn phải bị
edge/app từ chối trước hashing.  
**Sửa nhỏ nhất:** thêm `max_length=128` cho login password và một giới hạn body ở
edge/app; không thay đổi thuật toán auth.

### R42-F02 / A71-F04 — P2 — Shared-peer login DoS vẫn mở

`backend/app/modules/auth/router.py:160-171,203-205` kiểm và ghi một limiter theo
IP độc lập với email. `backend/app/modules/auth/session.py:39-41` tạo cùng key cho
mọi account sau cùng direct peer. Probe in-memory xác nhận identity key khác nhau
nhưng account thứ hai cùng IP vẫn bị block sau khi IP window đầy.

Finding này đã được ghi tại `docs/security/R42-F02_LOGIN_RATE_LIMIT_DECISION_BRIEF.md`.
Không chọn phương án A/B/C/D trong audit này; Security Owner vẫn phải chốt NAT,
trusted proxy, ngưỡng và invariant chống password oracle.

### A71-F05 — P2 — Nhánh deploy Pages không có protection

**Bằng chứng ngày 2026-11-17**

- `.github/workflows/github-pages.yml:6-10,89-112` cho push từ
  `codex/edu-0070-github-pages` build/upload/deploy với `pages: write` và
  `id-token: write`.
- GitHub Branch Protection API trả `404 Branch not protected` cho nhánh này.
- Environment `github-pages` dùng custom branch policy cho nhánh task và `main`,
  nhưng chỉ có branch-policy rule, không có required reviewer rule.

**Tiền điều kiện:** credential/collaborator có quyền push repo bị chiếm dụng hoặc
lạm dụng.  
**Tác động:** JavaScript/phishing tùy ý có thể được phát tại URL Pages tin cậy mà
không qua review/check bắt buộc của `main`.  
**Sửa nhỏ nhất:** sau merge hợp lệ, bỏ nhánh task khỏi trigger và environment
allowlist, chỉ deploy `main`; nếu buộc giữ preview branch thì bảo vệ chính nhánh
đó bằng required checks/review.

### A71-F06 — P2 — Action deploy không pin immutable SHA

Cả 13 `uses:` trong ba workflow đều dùng major tag (`@v4`, `@v5`), gồm
`actions/deploy-pages@v4` chạy với quyền Pages/OIDC. Khi upstream tag hoặc action
bị compromise, runner có thể thực thi code ngoài revision đã review.

**Sửa nhỏ nhất:** pin full commit SHA cho action, giữ comment version dễ đọc và
dùng Dependabot/Renovate để mở PR cập nhật có review. Không có third-party action
ngoài nhóm official GitHub trong branch hiện tại.

## 4. Release blocker/risk đã biết — không ghi trùng thành bug mới

- `users.mfa_secret` vẫn là plaintext
  (`backend/app/modules/auth/models.py:51-53`). Enrollment/recovery chưa được mở;
  encrypted custody và key ownership vẫn là blocker P1 trước production.
- Audit outbox chưa có archive/retention/anchor bên ngoài DB; OD-011 vẫn mở.
- Việc issuer `SUSPENDED`/`LOCKED` có vô hiệu invitation/reset token hay không
  vẫn là policy chưa duyệt; không tự quyết trong audit.
- Python lock chưa có hash, build backend resolve build dependency theo range và
  image dùng mutable tag. Đây là supply-chain debt đã biết, không phải finding
  mới của EDU-0071.
- Frontend P3: one-time token còn trong React state/DOM tới cancel/logout/unmount;
  Pages thiếu CSP, `X-Content-Type-Options`, `Referrer-Policy` và anti-framing.
- Pages safety hiện phụ thuộc `VITE_GITHUB_PAGES=true`. Workflow và Playwright
  đang đặt đúng flag; nên thêm fail-closed theo host/bundle assertion trước khi
  có pipeline deploy khác.
- Dependabot alerts đang disabled và GitHub code scanning chưa có analysis;
  secret-scanning API hiện trả 0 alert mở. Đây là detection gap, không chứng minh
  source không có lỗ hổng.

## 5. Bằng chứng kiểm tra

| Kiểm tra | Kết quả |
|---|---|
| Root unittest | `24 passed` |
| Backend host pytest | `93 passed, 20 skipped`; toàn bộ PostgreSQL integration skip vì không có DSN cô lập |
| Backend Ruff theo CI | `ruff check backend` và `ruff format --check backend`: pass, 55 file formatted |
| OpenAPI | `scripts/export_openapi.py --check`: pass |
| Frontend | API contract, lint, typecheck và 24 unit test pass; lint có 1 warning Fast Refresh |
| Frontend format local | exit `1` trên 6 file do worktree CRLF trong khi Git index là LF; hosted run #33 trên cùng HEAD đã pass. Không format/write trong audit |
| NPM audit | production và full lock: 0 vulnerability |
| Python OSV query | 41 locked package/version, 0 advisory match tại thời điểm query |
| Secret markers | tracked/current-history scan không tìm private-key/GitHub-token marker; GitHub secret scanning có 0 alert mở |
| GitHub controls | `main` protected, strict 3 checks + 1 approval; default workflow permission `read`; không có `pull_request_target` |
| Public Pages | HTML/asset HTTP 200; HSTS có, CSP/nosniff/referrer/frame policy vắng |
| Custom safe probes | password 1 MiB accepted; same-IP limiter chặn account khác; UserRole có 0 unique constraint và không có authorizing-grant reference |

Docker Desktop daemon không chạy, nên audit không tự khởi động Docker và không
thể tái chạy PostgreSQL concurrency suite. Vì vậy A71-F01/F02 dựa trên code/schema
proof; regression live vẫn bắt buộc trong task sửa.

## 6. Thứ tự xử lý tối thiểu

1. EDU-0072: sửa A71-F01 và A71-F02 cùng migration/regression PostgreSQL cô lập;
   một reviewer khác fixer kiểm tra lại.
2. EDU-0073: giới hạn login body/password và đóng R42-F02 sau quyết định Security
   Owner; giữ phản hồi không tạo password oracle.
3. Đóng đường deploy feature branch sau merge hợp lệ hoặc bảo vệ nhánh; pin SHA
   cho action trong một PR CI nhỏ.
4. Giữ MFA plaintext, audit archive và issuer-status semantics ở trạng thái
   blocked cho tới khi đúng authority phê duyệt.

Không cần tái kiến trúc toàn bộ RBAC, đổi framework hay thêm dịch vụ mới để xử lý
các finding trên.

## 7. Tác dụng phụ audit

- Không product code, schema, workflow hoặc cloud setting nào được sửa.
- Một scan ban đầu của reviewer backend vô tình đọc ignored `backend/.env` và
  `infra/.env`, làm giá trị kết nối DB local xuất hiện trong output nội bộ. Scan
  được dừng ngay; không lặp giá trị, không kết nối DB, không sửa hoặc gửi dữ liệu.
  Nếu credential local đó được tái sử dụng ngoài local, phải rotate.
- Các kiểm tra đã refresh file ignored sau thời điểm audit bắt đầu: một
  `backend/.pytest_cache` node list, hai Python bytecode dưới
  `backend/app/**/__pycache__`, ba Ruff cache entry và mười Vitest cache/result
  entry dưới `frontend/node_modules`. Không cache nào bị xóa hoặc đưa vào Git.
- `npm audit` có thể sử dụng cache cấp máy ở ngoài project; audit không đọc tiếp
  vị trí đó vì nằm ngoài ranh giới `D:\eduops360`.
- Không server/container nào được khởi động. Kiểm tra cuối không thấy kết nối ở
  các port dev thông dụng 3000/4173/5173/8000/5432/6379; service Docker vẫn
  `Stopped` và không bị thay đổi.

