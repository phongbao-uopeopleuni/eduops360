# Prompt bàn giao cho Claude — re-review remediation và sửa UI49-F01

Tạo bởi EDU-0050. Prompt này thay prompt EDU-0045 đã được Codex thực thi; bản cũ được sao lưu nguyên vẹn tại `docs/progress/evidence/EDU-0050/NEXT_AGENT_PROMPT.previous.md`.

---

## Bắt đầu prompt

Bạn là **Claude**, agent tiếp theo làm việc trên EduOps 360 tại **`D:\eduops360`**. Hãy đọc kỹ trước khi hành động. Mục tiêu lượt này không phải phát triển Phase 03 mà là:

1. re-review độc lập các remediation R42 do Codex vừa làm;
2. sửa finding UI49-F01 do Codex phát hiện, trong task tách biệt;
3. cập nhật tài liệu/evidence trung thực, không tự nghiệm thu phase.

### 0. Trạng thái hiện tại

- Phase 01: local technical gate tái lập được, nhưng **NOT ACCEPTED**; chưa có Git/hosted CI/human approval. UI EDU-0044 đang `NEEDS_CHANGES` vì UI49-F01.
- Phase 02: **NOT ACCEPTED**.
  - R42-F01 P1: Codex đã implement bản sửa ở EDU-0046, **chờ Claude/actor khác Codex re-review**.
  - R42-F02 P2: vẫn mở; decision brief `NOT APPROVED`, chờ Human Security Owner. Không được tự đổi code.
  - R42-F03..F05 P3: Codex đã implement ở EDU-0048, **chờ re-review**.
- UI49-F01 P2: brand link cao 36 px và content text-link cao 25,6 px, thấp hơn vùng chạm 44 px. Codex chỉ review, không sửa; Claude được phép sửa finding này.
- Không bắt đầu Phase 03.

Final local gates do EDU-0050 đo sau mọi source change:

| Gate | Kết quả |
|---|---|
| Backend host | 78 passed, 20 skipped |
| Backend PostgreSQL cô lập | 98 passed |
| Alembic | head `0008_mfa_replay_counter`, no drift |
| Ruff | clean; 57 files formatted |
| Frontend | 22 unit; typecheck/lint/format/api/build pass |
| Playwright | 9 passed, real-auth bắt buộc, session revoked |
| Governance/root | blueprint + structure pass; final encoding 446/0; root 24 |

### 1. Ranh giới tuyệt đối

- Chỉ làm trong `D:\eduops360`. Không chuyển dự án.
- Không `git init`, commit, push, remote, PR hay bịa trạng thái Git. Thư mục không phải Git repository.
- Không đọc/in/sửa/sao chép `backend/.env` hoặc `infra/.env`. Mọi lệnh recursive search/copy/diff phải loại `.env` và `.env.*` tường minh.
- Không cài package, không truy cập package index/network, không đổi dependency/lockfile.
- Chỉ dữ liệu tổng hợp và DB cô lập. Không deploy public, không dữ liệu học sinh thật.
- Không điền approval ledger, không đổi OD thành DEC, không tự làm Product/Security/DB authority.
- Nếu dùng Docker: project riêng `eduops360-<task>`, chỉ xóa project/volume bạn tạo; không đụng `eduops360-local_*`, `eduops360-audit-0011_*`, `eduops360-dev`. Trạng thái Docker Desktop tại bàn giao phải tự đo lại; đừng tin lịch sử.
- Dùng `apply_patch` cho edit thủ công. Journal append-only; correction không được viết lại lịch sử.

### 2. Đọc bắt buộc theo thứ tự

1. `AGENTS.md`, toàn bộ `docs/phases/PHASE-00.md`, `ai-agent-sp/PROJECT_CONTEXT.md`, `ai-agent-sp/OPERATING_RULES.md`.
2. `docs/progress/HANDOFF.md` phần EDU-0046..0050 và `docs/quality/PHASE_01_02_ACCEPTANCE_PACKAGE_2026-11-14.md`.
3. Review gốc: `docs/quality/EDU-0034-0041_INDEPENDENT_REVIEW_2026-11-14.md`, journal/evidence EDU-0042.
4. Remediation: journal/evidence EDU-0046, EDU-0047, EDU-0048; đọc source/test liên quan.
5. UI: `docs/requirements/UI_STYLE_MINIMALIST_SAAS_2026-11-14.md`, EDU-0044 evidence/screenshots/diff, `docs/quality/EDU-0044_UI_REVIEW_2026-11-14.md`, EDU-0049 evidence.
6. `docs/security/R42-F02_LOGIN_RATE_LIMIT_DECISION_BRIEF.md`, `docs/security/THREAT_MODEL.md`, `docs/quality/RELEASE_GATE.md`.
7. `ai-agent-sp/skills/REGISTRY.md`, rồi chỉ đọc skill cần cho security review, regression, Playwright và frontend.

Tài liệu là claim; phải đối chiếu source và chạy lại bằng chứng.

### 3. Ma trận độc lập

| Việc | Claude được làm? | Ai review tiếp? |
|---|---|---|
| Re-review EDU-0046 R42-F01 | Có; Claude không phải fixer | Nếu PASS, Human Security Owner vẫn duyệt policy; nếu có finding, Claude không tự sửa finding mới |
| Re-review EDU-0048 R42-F03..F05 | Có; Codex là fixer | Nếu có finding, Claude không tự sửa trong task review |
| Quyết R42-F02 | Không | Human Security Owner/Operations |
| Sửa UI49-F01 | Có; Codex là reviewer/finding author | Codex hoặc actor khác Claude re-review bản sửa |
| Nghiệm thu phase | Không | Named human authorities |

Mỗi nhóm review/fix phải là task riêng, ID kế tiếp còn trống (dự kiến từ EDU-0051). Không gộp review security với sửa UI.

### 4. Bước 0 — preflight

1. Xác nhận EDU-0051 còn trống; kiểm file mới nhất và process/listener để phát hiện actor đồng thời.
2. `git status -sb` và `git reflog` phải báo không phải repository; chỉ ghi bằng chứng, không khởi tạo Git.
3. Đo `docker desktop status`, listener 5173/5178/58xxx/55xxx và process có command line thuộc workspace.
4. Tạo manifest/baseline dưới `.local/<task>/`, loại `.env*`, `.venv`, `node_modules`, `.local`, caches, `dist`, `test-results`.
5. Chạy host gate. Nếu số liệu lệch, điều tra trước khi review/fix.

### 5. Task A — re-review EDU-0046, chỉ review

Không sửa source trong task review. Dựng PostgreSQL 18 cô lập, migrate tới 0008, chạy full suite và probe các điểm sau:

- Reset token: issuer chỉ có `user:password_reset`, target được nâng quyền sau issue → redeem 400, password/status không đổi.
- Invitation: issuer chỉ có `user:create`, pending target được grant role sau issue → accept 400, target vẫn pending.
- Thu hồi grant của issuer sau issue → redeem 400.
- Positive path: issuer còn global issue permission và bao trùm target → reset/invitation thành công.
- Target grant future-start cũng phải được tính; expired/revoked grant không tạo false denial.
- Giữ lock ordering, `populate_existing`, single-use concurrent F04 và `issued_by` audit.
- Denial phải generic `ACCOUNT_TOKEN_INVALID`, limiter failure, không commit password/status/session/token-used/audit mutation.
- Đánh giá rõ hai semantics chưa được duyệt, không tự quyết: issuer `suspended/locked`; token bị deny không bị consume và có thể dùng lại trước expiry nếu authority phục hồi.

Kết quả task review: `PASS`, `PASS_WITH_NOTES` hoặc `NEEDS_CHANGES`, report + verification JSON. Nếu phát hiện bug mới, ghi finding và dừng phần sửa; Claude không tự sửa finding của chính review.

### 6. Task B — re-review EDU-0048, chỉ review

- R42-F03: chứng minh mỗi insertion khi full không kiểm quá `eviction_scan_limit` (default 64); blocked identity không bị evict; khi prefix không có slot, new key không được track đúng như tài liệu. Kiểm CPU/lock complexity ở mức source/test, không over-engineer benchmark.
- R42-F04:
  - `scripts/seed_real_auth_e2e.py` bắt buộc `EDUOPS_TEST_MIGRATOR_DSN`, chỉ seed synthetic, không in DSN/password, từ chối output ngoài `.local/`.
  - `PLAYWRIGHT_REQUIRE_REAL_AUTH=1` + thiếu email/password phải fail rõ, không skip và không cần browser/server.
  - Chạy helper trên DB cô lập; chạy full Playwright qua backend thật với Chrome, cookie non-Secure chỉ trên HTTP local disposable; xác nhận login/logout và session `revoked`.
  - Xóa fixture credential/test artifact khi teardown. Không in error-context vì nó có thể chứa password form.
- R42-F05: xác nhận correction EDU-0040 là append-only, đủ đúng 14 file; ba migration 0002/0003/0007 chỉ formatting; quy ước không format migration applied đã ghi.

Ghi report task riêng. Không sửa trong task review nếu có finding mới.

### 7. Task C — sửa UI49-F01, được phép sửa

Làm tối thiểu, không redesign:

1. Viết fail-first Playwright regression đo tất cả interactive target đang hiển thị trên Overview ở 390 px và desktop. Ít nhất `.brand` và `.text-link` phải fail vì cao 36/25,6 px; kỳ vọng mỗi target rộng và cao tối thiểu 44 px hoặc có hit-area tương đương đo được.
2. Chỉ sửa CSS cần thiết, dự kiến `min-height: 44px` + alignment/padding cho `.brand` và `.text-link`. Không đổi label, route, handler, theme, token hay layout ngoài nhu cầu hit-area.
3. Chạy test mới, full frontend static/unit/build, full Playwright ở 360/390/768/1280 và light/dark. Chụp ảnh nếu nhịp navbar/content đổi thấy rõ.
4. Journal/evidence task ở `in_review`. Claude không tự review bản sửa; bàn giao cho Codex/actor khác Claude.

### 8. R42-F02 — điểm dừng quyết định

Không sửa limiter policy. Brief hiện có bốn phương án A/B/C/D và invariant không tạo password oracle. Nếu người dùng chưa chọn phương án và ngưỡng/topology cụ thể, giữ P2 `OPEN / NOT APPROVED` và Phase 02 không được ghi "không còn P1/P2".

### 9. Lệnh gate chuẩn

Host, từ root:

```powershell
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python -m unittest discover -s tests -p test_*.py
backend\.venv\Scripts\python.exe -m ruff check backend tests/foundation scripts/seed_real_auth_e2e.py
backend\.venv\Scripts\python.exe -m ruff format --check backend tests/foundation scripts/seed_real_auth_e2e.py
backend\.venv\Scripts\python.exe -m pytest backend/tests -q -p no:cacheprovider
backend\.venv\Scripts\python.exe scripts/export_openapi.py --check
```

Frontend: `npm run typecheck`, `lint`, `format:check`, `api:check`, `test`, `build`.

DB cô lập: tạo env synthetic dưới `.local/<task>/`, `docker compose -p eduops360-<task> --env-file <synthetic> -f infra/compose.dev.yml up -d db --wait`; chạy Alembic bằng migrator DSN, test bằng đủ migrator/runtime/audit-worker DSN; cuối task `down -v` đúng project và xóa credential file.

Real-auth: chạy tracked seeder, nạp JSON từ `.local` vào process env mà không echo, đặt `PLAYWRIGHT_REQUIRE_REAL_AUTH=1`, `PLAYWRIGHT_CHANNEL=chrome`, backend HTTP disposable có `EDUOPS_SESSION_COOKIE_SECURE=false`. Không dùng port 8000.

### 10. Điều kiện bàn giao

- Mỗi task có frontmatter, activity log append-only, verification JSON/raw output, status `in_review`, commit/push/PR/merge `not_done`.
- Báo đủ fail-first/pass-after, test not-run/fail, side effects (dist/test-results/cache/mtime/process/Docker).
- Teardown server/container/volume/credential synthetic; chứng minh ngay trước khi phát biểu.
- Cập nhật acceptance package/HANDOFF/TASK_BOARD theo sự thật. Không sửa PHASE-00, không điền approval ledger.
- Phase 02 chỉ có thể bỏ trạng thái `NEEDS_REVIEW` cho R42-F01/F03..F05 sau review task độc lập PASS; vẫn không `READY` nếu R42-F02 chưa được authority quyết định.
- Phase 01/02 vẫn `NOT ACCEPTED` cho đến khi human authorities ký. Không bắt đầu Phase 03.

## Kết thúc prompt
