# Gói nghiệm thu Phase 01 và Phase 02 — 2026-11-14

**Kết luận kỹ thuật hiện tại:** `PHASE_01_GATE_REPRODUCED; PHASE_02 NEEDS_REVIEW + P2 DECISION; UI NEEDS_CHANGES`  
**Trạng thái phase:** `IN_REVIEW / NOT ACCEPTED`  
**Task đóng gói hiện tại:** EDU-0050 (thay kết luận cũ của EDU-0041 sau review EDU-0042 và remediation EDU-0046..0049)  
**Giới hạn:** tài liệu này không phải chữ ký Product Owner, Human Security Owner, DBA, Git maintainer hay reviewer độc lập.

> **Ghi chú sau đóng gói — EDU-0054, 2026-11-15:** người dùng đã chỉ đạo kickoff có điều kiện P03-T01 trong khi giữ toàn bộ phần còn lại của Phase 02 là nợ kỹ thuật. Ngoại lệ này không thay đổi kết luận `IN_REVIEW / NOT ACCEPTED`, không điền approval ledger và không phê duyệt R42/OD/MFA/archive policy.

## 1. Ý nghĩa kết luận

Phase 01 vẫn tái lập được gate kỹ thuật, nhưng chưa có hosted CI/human acceptance và UI review EDU-0049 có một P2 cần actor khác sửa. Phase 02 không còn P1 chưa có bản sửa: R42-F01 đã được Codex sửa ở EDU-0046, nhưng chưa được actor khác re-review nên chưa đóng. R42-F03..F05 đã được sửa ở EDU-0048 và cũng chờ re-review. R42-F02 vẫn là P2 mở, decision brief `NOT APPROVED`, chưa được phép đổi code. Vì vậy không được dùng lại kết luận "không còn P1/P2" hoặc `READY_FOR_HUMAN_ACCEPTANCE` cho Phase 02.

Final local gates của EDU-0050: backend host `78 passed, 20 skipped`; PostgreSQL cô lập `98 passed`; frontend `22 passed`; Playwright `9 passed` gồm real-auth bắt buộc; root `24`; final encoding `446/0`; Alembic head `0008`, không drift. Gate xanh không thay thế independent review, Security Owner hay chữ ký acceptance.

## 2. Bảng gate

### Phase 01

| Gate | Trạng thái | Bằng chứng / điều kiện còn lại |
|---|---|---|
| Frontend/backend khởi động độc lập | Đạt kỹ thuật | EDU-0040; backend 1.2 s, frontend 0.573 s, không còn listener |
| OpenAPI và TypeScript client đồng bộ | Đạt kỹ thuật | `scripts/export_openapi.py --check`; `npm run api:check` |
| Theme, UTF-8, calendar/UTC, fixture tổng hợp | Đạt kỹ thuật | EDU-0007..0011; EDU-0040 validators/E2E |
| Regression, unit, integration, browser và build | Đạt kỹ thuật | EDU-0050: host `78 passed, 20 skipped`; PostgreSQL `98 passed`; frontend `22 passed`; Playwright `9 passed` |
| UI design/accessibility | Needs changes | EDU-0049: UI49-F01 P2, brand 36 px và text-link 25,6 px thấp hơn hit-area 44 px; actor khác reviewer phải sửa |
| Journal/evidence/task board | Đạt kỹ thuật | EDU-0039..0041; validator và board sync cuối lượt |
| Git/hosted CI | Đạt kỹ thuật sau gói ban đầu | EDU-0055/0056: public GitHub repo, protected `main`, foundation/governance/blueprint checks xanh trên `d8012da`; human merge authority/acceptance vẫn mở |
| Reviewer độc lập và người nghiệm thu | Chờ con người | OD-001; Codex không được tự review/approve phần mình triển khai |

### Phase 02

| Gate | Trạng thái | Bằng chứng / điều kiện còn lại |
|---|---|---|
| Default deny, scope/IDOR/escalation/stale grant | Chờ independent re-review | R42-F01 được sửa ở EDU-0046; live RA/RB và positive path xanh; Codex không được tự đóng finding |
| Session, CSRF, lockout, token một lần, idle timeout | Đạt kỹ thuật | EDU-0025/0032/0036/0038 |
| Admin invitation/status/role lifecycle và audit | Đạt kỹ thuật | EDU-0027/0032/0038; OpenAPI/client đồng bộ |
| Audit transaction và quyền DB | Đạt kỹ thuật | EDU-0024/0027/0034; runtime/worker bị chặn sửa/xóa/truncate |
| TOTP replay | Đạt kỹ thuật | EDU-0037, migration `0008`, roundtrip và live replay test |
| Login availability/rate-limit policy | P2 decision blocked | R42-F02; brief `docs/security/R42-F02_LOGIN_RATE_LIMIT_DECISION_BRIEF.md` là `NOT APPROVED`; code giữ nguyên |
| Limiter saturation/real-auth/evidence correction | Chờ independent re-review | R42-F03..F05 được xử lý ở EDU-0048; 9 E2E và helper tracked, nhưng Codex không tự review |
| MFA secret custody/enrollment/recovery | Blocked | cần phê duyệt custody, encryption, notification và authorities; plaintext secret không được mở rộng sử dụng |
| Role/scope/two-person matrix chính thức | Blocked | OD-007/008; mappings toàn cục vẫn không được kích hoạt |
| Archive/retention/audit anchor/downgrade authority | Blocked | OD-011/DBA/Security; F21 chưa được phép thay đổi kiến trúc/migration |
| Phase 01 prerequisite | Chờ con người | Phase 01 đạt kỹ thuật nhưng chưa được human accept |
| Human Security Owner approval | Chờ con người | OD-001 |

## 3. Sổ finding A0102-F01..F22

| Finding | Trạng thái | Xử lý / bằng chứng | Phần còn mở |
|---|---|---|---|
| F01 target privilege | Bản sửa R42 chờ re-review | EDU-0042 tìm TOCTOU lúc redeem; EDU-0046 recheck issuer permission + target coverage, PostgreSQL 98 xanh | Claude/actor khác Codex re-review; quy tắc vẫn TẠM chờ OD-008 |
| F02 User-Agent dài rollback audit/lockout | Đã sửa, đã re-review | EDU-0032/0034; UA dài vẫn lock và audit | không |
| F03 pending → active/password ban đầu | Đã sửa, đã re-review | EDU-0032/0034; pending phải đi qua invitation | kênh giao token chờ Security Owner |
| F04 token race | Đã sửa, đã re-review | EDU-0032/0034; row lock + refresh, concurrency test | không |
| F05 lockout hủy phiên có sẵn | Đã sửa kỹ thuật | EDU-0032/0034; phiên hợp lệ còn dùng được | chính sách là TẠM |
| F06 tự cấp/vượt hạn/audit thiếu scope | Đã sửa kỹ thuật | EDU-0032/0034; deny self, cap validity, đủ audit | chờ OD-007/008 |
| F07 Argon2 chặn event loop | Đã sửa kỹ thuật | EDU-0032/0034; bounded thread offload, liveness probe | concurrency 4 là TẠM |
| F08 test gap | Bản sửa R42 chờ re-review | tracked seeder + `PLAYWRIGHT_REQUIRE_REAL_AUTH=1` ở EDU-0048; full 9 E2E qua backend/DB thật | Admin UI breadth test vẫn mock có chủ đích |
| F09 limiter IP/LRU | Một phần sửa, P2 còn mở | EDU-0048 giới hạn scan saturation; EDU-0047 brief shared-peer DoS | R42-F02 chờ Security Owner; 50 lỗi/IP/60 s là TẠM; limiter theo process |
| F10 không có mời lại/hủy lời mời | Đã sửa kỹ thuật | EDU-0038 reissue/cancel, invalidation, audit, target bound | kênh giao token chờ duyệt |
| F11 CORS wildcard + credentials | Đã sửa | EDU-0036 validator/test từ chối `*` | không |
| F12 TOTP replay + plaintext secret | Một phần đạt, một phần blocked | replay đóng bởi EDU-0037/migration 0008 | mã hóa/custody/enrollment/recovery chờ phê duyệt |
| F13 cấu hình local cũ | Đã sửa trong file được phép | EDU-0035: example/docs/runtime role; Alembic/Playwright cần DSN rõ | `.env` thật không đọc/sửa theo guardrail |
| F14 Compose healthcheck race | Đã sửa | EDU-0035 dùng TCP loopback | không |
| F15 cổng/reuse E2E | Đã sửa | EDU-0035; port qua env, reuse explicit opt-in | không |
| F16 generator thoát workspace | Đã sửa | EDU-0035; output chỉ dưới `.local` | không |
| F17 evidence thiếu lệnh/exit | Đã correction minh bạch | EDU-0039 append-only, trỏ evidence mới | evidence cũ giữ nguyên lịch sử |
| F18 image runtime/lock hash | Runtime split đã sửa; hash blocked | EDU-0035 `requirements.runtime.lock` | sinh hash cần quyền truy cập package index/network |
| F19 test làm bẩn mapping toàn cục | Đã sửa | EDU-0035 dùng role tổng hợp; mapping seed 9→9 | DSN cô lập vẫn là yêu cầu vận hành |
| F20 Admin UI nuốt lỗi | Đã sửa | EDU-0038 hiển thị lỗi và controls pending; unit test | không |
| F21 toàn vẹn audit | Blocked có phương án | xem §4 OD-011 và §5 archive | cần quyết định DBA/Security/Legal; không tự sửa role/migration |
| F22 không có idle timeout | Đã sửa kỹ thuật | EDU-0036, `last_activity_at`, live expiry test | 30 phút là TẠM |

EDU-0042 đã thay thế khẳng định cũ của EDU-0034: tìm R42-F01 P1 và R42-F02 P2. R42-F01 hiện có bản sửa nhưng chưa re-review; R42-F02 vẫn mở. EDU-0049 thêm UI49-F01 P2. Không finding nào trong ba mục này được tự động đóng bởi package author.

## 4. Decision briefs — tất cả đều `NOT APPROVED`

### R42-F02 — limiter đăng nhập theo shared peer

- **Hiện trạng:** 50 lỗi từ cùng direct peer khiến credential đúng của tài khoản khác cũng nhận 429; ảnh hưởng NAT trường học và reverse proxy chưa có trusted-proxy policy.
- **Phương án:** (A) tắt hard-block IP tạm thời; (B) giữ nhưng chốt ngưỡng/ngữ nghĩa; (C) trusted proxy + ngưỡng mới; (D) progressive delay thay hard block.
- **Bất biến:** không được cho phản hồi/chặn phụ thuộc mật khẩu đúng hay sai, tránh oracle A0102-F02.
- **Trạng thái:** `NOT APPROVED`; brief đầy đủ tại `docs/security/R42-F02_LOGIN_RATE_LIMIT_DECISION_BRIEF.md`; không code nào được đổi ở EDU-0047.

### OD-001 — Người có thẩm quyền

- **Câu hỏi:** ai là Product Owner, Human Security Owner, reviewer độc lập, DBA reviewer và Git maintainer?
- **Phương án:** (A) chỉ định các cá nhân nội bộ, phân tách implementer/reviewer; (B) reviewer bảo mật/DB bên ngoài; (C) tạm dừng acceptance.
- **Đề xuất `NOT APPROVED`:** A, bổ sung B cho security nếu nội bộ không đủ độc lập; không một người vừa sửa vừa duyệt cùng task.
- **Tác động sau duyệt:** cập nhật role assignment, review matrix, approval log; tạo task review riêng, không sửa code chung với review.

### OD-003 — Git và hosted CI

- **Câu hỏi:** repository nào, ai quản trị, bảo vệ nhánh/required checks ra sao?
- **Phương án:** private repo mới; repo hiện hữu được chỉ định; tiếp tục local-only.
- **Đề xuất `NOT APPROVED`:** private repo `eduops360`, protected main, PR bắt buộc, required backend/frontend/governance checks và ít nhất một reviewer độc lập.
- **Tác động sau duyệt:** task riêng để import lịch sử được chấp thuận, chạy hosted CI, ghi commit/push/PR/merge tách biệt. Không `git init` trong lượt này.

### OD-007 — Hai người phê duyệt

- **Câu hỏi:** action nào cần two-person approval, submitter có bao giờ được approve không, timeout/escalation thế nào?
- **Phương án:** danh sách hẹp; mọi thay đổi nhạy cảm; policy theo loại tài nguyên có cấu hình.
- **Đề xuất `NOT APPROVED`:** cấu hình data-driven; grade lock/approve, timetable publish, assessment-policy activation, break-glass và thay đổi quyền cao phải có approver khác submitter; không ngoại lệ self-approval.
- **Tác động sau duyệt:** migration/config + state-machine/API/audit/negative tests ở task mới.

### OD-008 — RBAC/scope chính thức

- **Câu hỏi:** chiều scope bắt buộc theo role, semantics `NULL`, global grants và target-privilege rule?
- **Phương án:** `NULL = all`; `NULL = missing/deny`; explicit global flag/role.
- **Đề xuất `NOT APPROVED`:** school + academic year luôn rõ; grade/class/subject bắt buộc theo role; global chỉ bằng grant/role được phê duyệt rõ, không suy từ `NULL`; giữ target-privilege containment và cấm self-grant.
- **Tác động sau duyệt:** seed/migration validation, API checks và matrix tests; mappings global vẫn để trống trước duyệt.

### OD-011 — Audit, retention, backup và production authority

- **Câu hỏi:** legal basis/retention, RPO/RTO, archive owner, incident responder, ai được chạy migration/downgrade phá hủy?
- **Phương án:** DB-only; archive bất biến ngoài DB; SIEM/WORM managed service.
- **Đề xuất `NOT APPROVED`:** bootstrap owner riêng; migrator production không phải superuser; chuỗi hash/HMAC có anchor ngoài application DB; downgrade phá audit cần DBA + Security phê duyệt, export/checkpoint trước; không auto-delete khi chưa có legal retention.
- **Tác động sau duyệt:** threat model/ADR, migration bootstrap riêng, archive worker/delivery, restore drill và tamper verification.

### MFA custody

- **Câu hỏi:** ai giữ khóa, mã hóa secret thế nào, enrollment/recovery/rotation/notification ra sao?
- **Phương án:** application key; envelope encryption bằng KMS/HSM; TOTP chưa kích hoạt.
- **Đề xuất `NOT APPROVED`:** envelope encryption với key ngoài DB, dual control cho recovery, notification độc lập, recovery code một lần, revoke sessions và immutable audit. Giữ enrollment/recovery disabled cho đến khi duyệt.
- **Tác động sau duyệt:** task security riêng có migration, key rotation, negative tests và human runbook drill.

### Archive/retention operation

- **Câu hỏi:** đích archive, delivery guarantee, retention/legal hold, verify/restore và monitoring?
- **Phương án:** object storage WORM; SIEM; archive service nội bộ.
- **Đề xuất `NOT APPROVED`:** append-only/WORM ngoài DB, outbox retry có idempotency, daily integrity anchor, legal hold, restore verification định kỳ; thời hạn chỉ được nhập sau legal approval.
- **Tác động sau duyệt:** task vận hành riêng; không nối external destination trong Phase 02 hiện tại.

## 5. Giá trị TẠM cần phê duyệt

| Giá trị hiện tại | Mục đích | Owner cần quyết định | Nếu thay đổi |
|---|---|---|---|
| Actor phải bao trùm mọi quyền hiệu lực của target | chặn reset/suspend/reissue vượt đặc quyền | OD-008 / Security Owner | cập nhật guard + negative matrix |
| Pending chỉ active qua invitation | không cho Admin chọn mật khẩu ban đầu | Security Owner | cập nhật lifecycle/API/UI |
| Lockout không hủy session đã hợp lệ | giảm DoS từ login sai | Security Owner | cập nhật session policy/tests |
| Cấm self-grant; delegated validity không vượt grant bao trùm | ngăn leo thang/chuyển quyền vĩnh viễn | OD-007/008 | cập nhật grant workflow |
| Argon2 concurrency = 4 | bảo vệ event loop/CPU | OD-004/Security/Operations | benchmark và cấu hình lại |
| 50 login failures/IP/60 s | giảm password spray nhưng tạo shared-peer DoS R42-F02 | Security Owner/Operations | chọn A/B/C/D trong brief, regression RC + oracle test trước khi đổi code |
| Token redemption recheck issuer grant nhưng chưa xét riêng issuer suspended/locked; denied token không bị consume | chặn token cũ vượt authority mà không tạo irreversible mutation khi fail | Security Owner/OD-008 | chốt status semantics và retry/consume policy, cập nhật regression |
| Idle timeout = 30 phút | giới hạn session bỏ quên | Security Owner/Product | chỉnh config/UX/tests |
| Invitation/reset raw token trả cho Admin | chưa có notification channel | Security Owner | thay bằng delivery service; không log token |

## 6. Ma trận độc lập của mọi task `in_review`

`Reviewer hợp lệ` dưới đây là điều kiện tối thiểu; task security/high-impact vẫn cần Human Security Owner/Product Owner theo release gate.

| Task | Implementer/actor | Reviewer hợp lệ | Hiện trạng |
|---|---|---|---|
| EDU-0002 | Architecture preparation | người/agent không tham gia chuẩn bị + human domain owner | thiếu human approval |
| EDU-0003 | Architecture preparation | reviewer độc lập về data/UTF-8 + human owner | thiếu human approval |
| EDU-0004 | Architecture preparation | reviewer governance độc lập | thiếu human approval |
| EDU-0005 | Architecture preparation/BA | Product Owner và reviewer độc lập | thiếu human approval |
| EDU-0006 | Architecture/Governance | reviewer tài liệu độc lập + Product Owner | thiếu human approval |
| EDU-0007 | Codex | Claude hoặc human backend reviewer, không Codex | thiếu human approval |
| EDU-0008 | Codex | Claude hoặc human frontend/a11y reviewer | thiếu human approval |
| EDU-0009 | Codex | Claude hoặc human DevOps/data reviewer | thiếu human approval |
| EDU-0010 | Codex | Claude hoặc human QA/CI reviewer | thiếu hosted CI/human approval |
| EDU-0011 | Codex | Claude hoặc human reviewer | thiếu human approval |
| EDU-0012 | Codex | Claude + Human Security Owner | thiếu OD-007/008/human |
| EDU-0013 | Codex | Claude + Human Security Owner/DB reviewer | thiếu human approval |
| EDU-0014 | Codex | Claude + Human Security Owner/DBA | thiếu OD-011/human |
| EDU-0015 | Hermes | Codex/Claude không tham gia sửa + Human Security Owner | chưa có human approval |
| EDU-0021 | Codex | Claude hoặc human documentation reviewer | chưa duyệt |
| EDU-0022 | Codex | Claude hoặc human handoff reviewer | đã được thay thế; chưa đóng bởi human |
| EDU-0023 | Hermes + Codex | Claude hoặc human DB/security reviewer | thiếu human approval |
| EDU-0024 | Codex | Claude + DBA/Human Security Owner | thiếu OD-011/human |
| EDU-0025 | Codex | Claude + Human Security Owner | thiếu human approval |
| EDU-0026 | Codex | Claude + Human Security Owner | thiếu OD-007/008/human |
| EDU-0027 | Codex | Claude + Product/Security reviewer | thiếu human approval |
| EDU-0028 | Codex | Claude hoặc human QA/Security reviewer | thiếu human approval |
| EDU-0029 | Codex | Human Security Owner/incident authority | draft, chưa approved |
| EDU-0030 | Codex | Claude + Human Security Owner | audit EDU-0031 đã review kỹ thuật; human còn thiếu |
| EDU-0031 | Claude reviewer | human security reviewer/authority; không Claude tự duyệt | findings đã xử lý; review task chưa human-close |
| EDU-0032 | Claude implementer | Codex được review kỹ thuật; Human Security Owner duyệt cuối | EDU-0034 `PASS_WITH_NOTES`; human còn thiếu |
| EDU-0033 | Claude | Codex/human handoff reviewer | prompt đã được thực thi và thay thế; chưa human-close |
| EDU-0034 | Codex reviewer | Claude hoặc human reviewer; không Codex tự duyệt | thiếu reviewer của review task |
| EDU-0035 | Codex | Claude + DevOps/DB reviewer | thiếu hash network authorization/human |
| EDU-0036 | Codex | Claude + Human Security Owner | giá trị TẠM chưa duyệt |
| EDU-0037 | Codex | Claude + Human Security Owner/DBA | custody vẫn blocked |
| EDU-0038 | Codex | Claude + Product/Security reviewer | token channel chưa duyệt |
| EDU-0039 | Codex | Claude hoặc human evidence reviewer | chưa duyệt |
| EDU-0040 | Codex | Claude + human Phase 01 authority | kỹ thuật đạt; human/Git còn thiếu |
| EDU-0041 | Codex | Claude và các human authority tương ứng | gói này chờ review/approval |
| EDU-0042 | Claude reviewer | Human Security Owner hoặc reviewer độc lập không Claude | `NEEDS_CHANGES`; findings đang được xử lý |
| EDU-0044 | Claude implementer | Codex đã review ở EDU-0049 | `NEEDS_CHANGES` do UI49-F01 |
| EDU-0045 | Claude handoff author | Codex/human documentation reviewer | prompt đã được EDU-0046..0050 thực thi và thay thế |
| EDU-0046 | Codex remediation | Claude hoặc actor khác Codex + Human Security Owner | R42-F01 implementation xanh, chờ re-review |
| EDU-0047 | Codex brief author | Human Security Owner | R42-F02 `NOT APPROVED`, P2 mở |
| EDU-0048 | Codex remediation | Claude hoặc actor khác Codex | R42-F03..F05 implementation xanh, chờ re-review |
| EDU-0049 | Codex UI reviewer | Claude có thể sửa finding; reviewer sau sửa phải khác fixer | UI49-F01 P2 mở |
| EDU-0050 | Codex package author | Claude/human documentation and acceptance authorities | package/handoff kỹ thuật, không phải acceptance |

## 7. Mẫu sổ phê duyệt — để trống

Không điền thay người có thẩm quyền.

| Phạm vi | Reviewer/authority | ISO-8601 time + offset | Quyết định | Evidence/signature | Điều kiện/follow-up |
|---|---|---|---|---|---|
| Phase 01 technical review |  |  |  |  |  |
| Phase 01 acceptance |  |  |  |  |  |
| Phase 02 security review |  |  |  |  |  |
| Phase 02 acceptance |  |  |  |  |  |
| OD-001 |  |  |  |  |  |
| OD-003 |  |  |  |  |  |
| OD-007 |  |  |  |  |  |
| OD-008 |  |  |  |  |  |
| OD-011 |  |  |  |  |  |
| MFA custody |  |  |  |  |  |
| Archive/retention |  |  |  |  |  |

## 8. Việc reviewer phải làm tiếp

1. Đọc Phase 00, release gate, báo cáo EDU-0031, review EDU-0034 và gói này.
2. Claude hoặc actor khác Codex re-review EDU-0046 và EDU-0048 bằng PostgreSQL/E2E cô lập; không sửa trong cùng task review nếu tìm finding mới.
3. Actor khác Codex sửa UI49-F01; reviewer sau sửa phải khác fixer. Ghi task/evidence riêng.
4. Các authority quyết định OD/MFA/archive trong sổ riêng, sau đó tạo task triển khai quyết định.
5. Chỉ đổi phase sang `accepted` khi các hàng approval tương ứng có người, thời điểm, quyết định và evidence thật.

Không bắt đầu Phase 03. Phase 02 vẫn có P2 policy chưa quyết và các remediation chưa được independent re-review; Phase 01/02 đều chưa được human accept.
