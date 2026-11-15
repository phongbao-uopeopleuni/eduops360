# EDUOPS 360 — Đặc tả yêu cầu kỹ thuật tổng thể (SRS v2.1)

> **Tình trạng:** DESIGN / SPECIFICATION ONLY, chưa được nghiệm thu cho dữ liệu học sinh thật. Phiên bản tài liệu: 2.1 (2026-11-12). Toàn bộ lịch, ngày và chỉ số minh họa không phải quy định pháp lý mặc định.

## 1. Mục tiêu
EduOps 360 là Web Application/PWA dành cho cán bộ đào tạo, khảo thí, giáo viên và quản trị viên của **một trường trong MVP** tại Việt Nam; giữ ranh giới dữ liệu để mở rộng nhiều trường về sau. Thiết kế hỗ trợ **lớp 1–12** và quy mô mục tiêu **2.000–10.000 học sinh / 20–100 người dùng** (mức đồng thời chưa được xác nhận). Hệ thống tích hợp Student Information, Academic Years, Schedule Optimizer, Examination, Legal Documents, Analytics, ML, IAM, Audit và Monitoring.

## 2. Phạm vi và không nằm trong phạm vi
- **Phase 00 master duy nhất:** `docs/phases/PHASE-00.md` (8 quyết định đã chốt và 13 vấn đề còn mở, phân biệt rõ).
- **Thứ tự MVP:** Phases 01–02 là nền tảng, 03–04 Học sinh/CSV, 05–06 Thời khóa biểu, 07 Khảo thí. Văn bản tự động, Analytics và ML (08–10) nằm trong roadmap mở rộng, không phải điều kiện hoàn tất MVP. Bảo mật/release gate Phase 11 được áp dụng trước mọi phát hành thực tế.
- Trong phạm vi: CRUD có phân quyền; import/export CSV/XLSX; giao diện tiếng Việt Light/Dark; cấu hình từng tiết/ngày nghỉ; tìm lịch có kiểm chứng xung đột; điểm theo policy version; tra cứu văn bản có nguồn; thống kê; ML hỗ trợ quyết định; nhật ký chống sửa/xóa trái phép.
- Ngoài phạm vi v1: điểm danh bằng nhận diện khuôn mặt; tự động quyết định năng lực/xếp loại; công bố dữ liệu học sinh công khai; tự ý thay đổi quy chế khi AI tìm thấy văn bản; huấn luyện ML với dữ liệu giả lập rồi sử dụng dự báo như thực tế; cung cấp dịch vụ pháp lý kết luận không qua kiểm duyệt.

## 3. Nhóm người dùng
- Admin: quản lý tài khoản và nghiệp vụ toàn phạm vi được cấp; không có quyền sửa trực tiếp kho audit bất biến.
- User: thao tác theo permission + scope; mặc định deny.
- Service account: cho worker đồng bộ/tính toán, không sử dụng quyền Admin người thật.
- Approval authority: người có thẩm quyền chuyên môn thực sự xác nhận chính sách điểm, lịch, vận hành và thay đổi dữ liệu nhạy cảm.

## 4. Yêu cầu chức năng có mã định danh
| Requirement ID | Acceptance-oriented requirement | Phase |
| --- | --- | --- |
| GOV-01 | Canonical baseline and open decision register with owner approval | 00 |
| SCALE-01 | Synthetic fixtures for 2k and 10k students plus planned 20/100-user benchmarks | 01/11 |
| APPROVAL-01 | Two-stage approval workflow for critical actions; server-side no-self-approval policy by default | 02/05/07 |
| ENV-01 | Local Docker first, separately configured synthetic staging | 01/11 |
| AUTH-01 | Admin/User login, sessions, MFA Admin, reset, lockout | 02 |
| AUTH-02 | RBAC + data scope + deny by default API/resource | 02 |
| YEAR-01 | Multiple academic years, term states, archived read-only | 03 |
| YEAR-02 | Date/Time/timezone control, UTC audit, no zero-time defaults | 03 |
| SIS-01 | Student master profile, enrollment history, class assignments | 03 |
| IMPORT-01 | Versioned CSV UTF-8 (BOM for Excel), preview, errors and staging | 04 |
| IMPORT-02 | Idempotent and conflict-aware imports, batch audit and rollback | 04 |
| CAL-01 | Add/edit/reorder time slots by day and session | 05 |
| CAL-02 | Single/range/partial/recurring holidays + makeup day + legal link | 05 |
| SCH-01 | No teacher/class/student-group/room/holiday overlaps | 06 |
| SCH-02 | CP-SAT draft generation, infeasible/timeout diagnostic, local repair | 06 |
| SCH-03 | Timetable versioning, approve, publish, change log | 06 |
| EXAM-01 | Policy-versioned grade/assessment rules Grades 1–12 | 07 |
| EXAM-02 | Grade approval, freeze/unfreeze, validated corrections and audit | 07 |
| LEGAL-01 | Official-source sync, archive originals and effective periods | 08 |
| LEGAL-02 | Full-text & semantic search with provenance and human confirmation | 08 |
| ANA-01 | Scatter/histogram/KDE/box/swarm/heatmap, filters and download | 09 |
| ML-01 | Versioned learning model with temporal splits and model cards | 10 |
| ML-02 | Human-in-the-loop early warning; never automatic official classification | 10 |
| SEC-01 | 3-class logging (business/security/error), trace IDs, immutable evidence | 02/11 |
| OPS-01 | Backups, restore drills, observability, deployment approval and rollback | 11 |
| UI-01 | White-first scientific minimalism, Vietnamese typography, Light/Dark | 01 |

## 5. Phi chức năng / Acceptance gates
- **NFR-SCOPE:** School-scoped launch; `school_id` boundary preserved for expansion; Grades 1–12 supported without hardcoding the actual institution’s current grade distribution.
- **NFR-SEC:** Backend authorizes each sensitive operation on (principal, action, resource, scope, workflow state); MFA for admin; HTTPS; no secrets in frontend or logs; audit immutable independent of business Admin.
- **NFR-DATA:** UTF-8 strict + NFC as appropriate, source identifiers preserved, student codes as strings, referential integrity, transactional bulk imports, no silent rewrite of historic grades.
- **NFR-TIME:** `DATE` for day, `TIME` for period, `TIMESTAMPTZ` for audit, default zone `Asia/Ho_Chi_Minh`; date-only strings never accidentally converted to timestamp; time slot start < end.
- **NFR-AVAIL:** Worker failure must not stop routine API reads/writes; critical writes fail closed when transactional audit cannot be secured; monitored backup restore.
- **NFR-PERF targets pending benchmarks:** search p95 <500ms, load single-class gradebook p95 <1s, conflict check p95 <200ms, dashboard p95 <2s for agreed load/hardware; CP-SAT solver asynchronous, timeboxed, status reflects solver outcome.
- **NFR-QUALITY:** Unit + integration + contract + E2E + security + encoding + recovery tests as relevant; reproducible fixtures and evidence; code review and human approvals for high impact.
- **NFR-ACCESSIBILITY:** WCAG 2.2 AA target; non-color indicators; keyboard navigation and contrast testing for both themes.

## 6. Governance
- Eight business decisions confirmed on 2026-11-12; change only with Product Owner approval and an ADR (`docs/phases/PHASE-00.md`). Phase 00 remains `in_review` pending named reviewers and formal acceptance.
- Repository canonical SOP: `ai-agent-sp/`. See `AGENTS.md`, `CLAUDE.md`, `ai-agent-sp/skills/REGISTRY.md`.
- One task → one owner → one branch/worktree → evidence → review → merge (only authorized human-approved operations).
- Policies/văn bản pháp lý are draft until domain owner validates effective date and applicability; school/city-specific settings are configurable.
- Real personal data not permitted in demo/test environment. Define lawful basis and retention before production use.

## 7. Traceability
See `docs/quality/TRACEABILITY_MATRIX.md` for requirement-to-phase-to-test-to-evidence mapping. Each phase has a detailed specification in `docs/phases/`.
