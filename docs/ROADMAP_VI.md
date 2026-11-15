# EduOps 360 — Hướng dẫn triển khai kỹ thuật bằng tiếng Việt (v2.1)

> Đây là tài liệu diễn giải dành cho Product Owner/cán bộ khảo thí/đào tạo. Các file `docs/phases/PHASE-XX.md` mới là nguồn nhiệm vụ kỹ thuật chi tiết cho từng Agent. Nếu phát hiện khác biệt, tạo task sửa nguồn chuẩn và cập nhật tài liệu diễn giải; không tự áp dụng hai phương án song song.

**Quyết định Product Owner:** 2026-11-12 — 1 trường trong MVP, thiết kế hỗ trợ lớp 1–12, 2.000–10.000 học sinh / 20–100 người dùng, trình tự Học sinh + CSV → Thời khóa biểu → Khảo thí. Xem `docs/phases/PHASE-00.md` và `docs/phases/PHASE-00.md`.

## Cách tổ chức công việc

**Chuỗi bắt buộc:** Yêu cầu nghiệp vụ → BA xác nhận điều kiện → Architecture thiết kế giải pháp → Tạo task `EDU-XXXX` → Chọn Role và Skills → Agent triển khai trên branch/worktree riêng → QA kiểm thử → Security/Domain review → Người có quyền duyệt → Commit/Push/PR/Merge (mỗi trạng thái có bằng chứng riêng) → Bàn giao.

Mỗi task phải có ngày giờ (timezone-aware nếu ghi sự kiện thực), người thực hiện, mã yêu cầu SRS, mục tiêu, đầu vào, bước thay đổi, tên file trước/sau, câu lệnh kiểm thử và kết quả thật, lỗi, branch, commit SHA, push remote, PR, merge SHA, kế hoạch rollback và người nhận bàn giao. Nếu chưa thực hiện một thao tác Git, ghi `not_done`.

## Phase 00 — Chuẩn hóa yêu cầu và quy trình Agent
**Mục tiêu:** Trước khi viết code, mọi người cùng hiểu một mô hình nghiệp vụ và một cấu trúc repository.

1. Kiểm tra cấu trúc `frontend/`, `backend/`, bộ `ai-agent-sp/` và starter v1.2; bảo toàn quy chuẩn UTF-8 sẵn có.
2. Lập danh mục yêu cầu với mã như `AUTH-01`, `SCH-01`, `EXAM-01`; phân loại bắt buộc/ưu tiên và trường hợp ngoại lệ.
3. Gắn mỗi yêu cầu với module sở hữu, nhóm người dùng, tác động dữ liệu và test cần có.
4. Định nghĩa Role (người thực hiện, người review, người duyệt) và quy trình phân quyền cho Agent khi làm việc.
5. Đăng ký skills trong một Registry; agent không tự suy diễn rằng thư mục tùy ý được tải tự động.
6. Chạy kiểm tra cấu trúc, encoding, metadata của skill và kiểm thử âm tính.
7. Ghi task bàn giao; chỉ chốt Phase sau khi người phụ trách xác nhận không còn quy định chồng chéo.

**Điều kiện qua Phase:** một SRS, một danh mục skill, một quy tắc Git, bảng task có nguồn gốc và không có policy bản sao riêng cho từng AI.

## Phase 01 — Dựng khung Web và Backend
**Mục tiêu:** Có ứng dụng chạy local đủ để kiểm tra API, cấu trúc file và giao diện.

1. Frontend Agent khởi tạo React + Vite + TypeScript; quy định `src/app`, `src/features`, `src/shared`.
2. Backend Agent dựng FastAPI theo module; không để toàn bộ nghiệp vụ trong `main.py`.
3. Database Agent cấu hình PostgreSQL local và công cụ migration Alembic; tuyệt đối dùng dữ liệu giả.
4. Architecture Lead tạo hợp đồng API OpenAPI; frontend lấy client/types từ contract đã sinh.
5. UI Agent dựng bố cục White-first Scientific Minimalism, chữ tương phản, Light/Dark, kiểm tra dấu tiếng Việt.
6. QA tạo smoke test, API health, lỗi form, kiểm tra code/type, kiểm tra UTF-8 và thời gian.

**Điều kiện qua Phase:** có thể mở UI, gọi health API, kiểm tra type và chạy test bằng lệnh tái lập; Frontend/Backend khởi động độc lập.

## Phase 02 — Login, phân quyền và Audit
**Mục tiêu:** Đảm bảo User chỉ sử dụng phần được cấp quyền; thao tác quan trọng được truy vết.

1. Thiết kế bảng user/role/permission/resource scope; Admin nghiệp vụ không được xóa log bất biến.
2. Thực hiện đăng nhập, đăng xuất, reset, MFA cho Admin, giới hạn đăng nhập thất bại và thu hồi session.
3. Backend kiểm tra quyền theo tài khoản + thao tác + trường/lớp/năm học + trạng thái nghiệp vụ.
4. Frontend hiển thị chức năng được cấp quyền nhưng không dùng ẩn nút thay thế kiểm tra backend.
5. Việc cấp/thu hồi quyền ghi audit với người thực hiện, thời điểm, lý do và giá trị trước/sau.
6. QA thử API truy cập lớp không được phân công, nâng quyền, sửa điểm bị khóa và session hết hạn.
7. Security Agent review CIA, không cho qua Phase nếu lỗi IDOR hoặc audit chưa nhất quán.

## Phase 03 — Năm học và dữ liệu học vụ lõi
**Mục tiêu:** Quản lý nhiều năm học nhưng không ghi đè học sinh và lịch sử điểm.

1. Dựng bảng trường, năm học, học kỳ, danh mục khối/lớp/giáo viên/môn.
2. Phân tách một học sinh (`students`) và lịch sử thuộc lớp theo năm (`enrollments`).
3. API luôn nhận/ngầm kiểm tra `academic_year_id` trong phạm vi quyền.
4. Màn hình có Year Switcher, banner chế độ read-only với năm cũ, hai tab độc lập.
5. Kiểm thử đổi năm liên tục, năm học bị chồng khoảng ngày, giáo viên chuyển lớp, dữ liệu trùng.

## Phase 04 — Import / Export hàng loạt
**Mục tiêu:** Import CSV an toàn và có thể kiểm tra từng dòng.

1. Xây template phiên bản với các cột ASCII `snake_case`; cột họ tên và tên lớp hỗ trợ UTF-8.
2. Nhận UTF-8/UTF-8 BOM, xử lý `errors=strict`, giới hạn file, kiểm tra header và giữ mã HS dạng chuỗi.
3. Tạo bảng staging, xem trước dòng lỗi/trùng/thông tin khác với database; chưa ghi thẳng bảng chính.
4. User được cấp `students.import` xác nhận tạo mới/cập nhật; backend đối chiếu quyền lần nữa.
5. Import bằng transaction hoặc chunk có checkpoint/idempotency; ghi batch audit và báo cáo lỗi.
6. Test 2.000 hồ sơ giả, mã có `0` đầu, NFC/NFD, dấu phẩy trong tên, ngày sai, BOM, phát lại batch.

## Phase 05 — Time Slots và ngày nghỉ
**Mục tiêu:** Mỗi ngày có thể cấu hình số tiết và giờ khác nhau; ngày nghỉ ngăn xếp lịch.

1. Tạo template thời gian theo năm/cấp/ngày/thứ; hỗ trợ sáng/chiều, Add Slot, nghỉ giữa tiết.
2. Kiểm tra `start_time < end_time`, không mặc định giờ thiếu thành `00:00`; cho phép nửa đêm khi hợp lệ.
3. Tạo ngày nghỉ một ngày, khoảng ngày, một buổi hoặc lặp lại; quy định phạm vi toàn trường/khối/lớp.
4. Khi thêm ngày nghỉ sau lúc công bố lịch, preview các tiết ảnh hưởng và yêu cầu phê duyệt sửa.
5. Hỗ trợ ngày học bù và ngày học ngoại lệ; bảo tồn lịch đã công bố.
6. QA test trùng khoảng giờ, ngày biên cuối, múi giờ và phạm vi năm học.

## Phase 06 — Auto Scheduling / CP-SAT
**Mục tiêu:** Tự xếp không trùng giáo viên, lớp, nhóm và phòng; giải thích khi không có nghiệm.

1. Đóng băng snapshot đầu vào: số tiết từng môn, giáo viên, phòng, slot, ngày nghỉ, lịch cố định.
2. Pre-check sức chứa/tổng số tiết/tính khả dụng để phát hiện đầu vào bất khả thi.
3. Thiết lập hard constraints; thiết lập soft scores cho tiết trống và cân bằng lịch.
4. Chạy CP-SAT ở worker riêng; API trả job ID, trạng thái FEASIBLE/OPTIMAL/INFEASIBLE/UNKNOWN.
5. Validator độc lập kiểm tra giờ giao nhau thực tế và số tiết; chỉ lịch hợp lệ mới lưu bản nháp.
6. UI cho kéo thả, đổi tiết, đổi phòng và re-optimize cục bộ với ít thay đổi nhất.
7. QA benchmark 5/20/50/80 lớp giả lập; công bố phải có duyệt và log.

## Phase 07 — Khảo thí, đánh giá lớp 1–12
**Mục tiêu:** Phân biệt đánh giá tiểu học, THCS và THPT theo văn bản áp dụng đúng năm.

1. Chuyên gia nghiệp vụ xác nhận căn cứ pháp lý, phạm vi và ngày hiệu lực trước khi code công thức.
2. Thiết kế đánh giá định tính, định lượng, môn lựa chọn, số lần đánh giá và rounding theo policy version.
3. Viết pure functions kiểm thử từng trường hợp mẫu đã được chuyên môn xác nhận.
4. Thiết kế sổ điểm, nhập điểm, duyệt, khóa sổ, mở khóa theo quyền và lý do.
5. Khi sửa điểm, ghi old/new/actor/policy version trong giao dịch nhất quán; xử lý đồng thời bằng revision.
6. QA kiểm thử thiếu điểm, sai thang, thay năm học, áp dụng nhầm policy, người khác lớp cố sửa.

## Phase 08 — Quản lý văn bản giáo dục
**Mục tiêu:** Tự theo dõi nguồn chính thức, giữ lịch sử và tra cứu theo thời điểm.

1. Lập danh sách nguồn chính thức có thể kết nối hợp lệ; xác minh API và điều kiện thu thập riêng mỗi cổng.
2. Định kỳ thu thập metadata và tệp, lưu file gốc/hash; phiên bản cũ không bị xóa.
3. Trích xuất văn bản theo điều/khoản, xử lý lỗi PDF và nhận diện nội dung chưa chắc chắn.
4. Người kiểm duyệt xác minh quan hệ sửa đổi/thay thế và hiệu lực; AI chỉ gợi ý có dẫn nguồn.
5. Lập chỉ mục tìm kiếm theo số hiệu, chủ đề, cấp, năm học và thời điểm hiệu lực.
6. Các thay đổi chính sách chỉ được đề nghị rà soát, không tự làm biến đổi kết quả khảo thí.

## Phase 09 — Statistical Analytics
**Mục tiêu:** Chart Builder trực quan, tự tạo biểu đồ đúng và an toàn.

1. Chuẩn hóa nguồn tổng hợp điểm theo năm/lớp/khối/môn, quyền truy cập và dữ liệu thiếu.
2. Làm Scatter, Histogram/KDE, Box/Swarm, Heatmap, Line, ECDF; đặt chú giải và mô tả đúng mục tiêu.
3. Cho người dùng chọn biến X/Y, nhóm, bộ lọc, xem số mẫu và loại thống kê.
4. Đối chiếu thống kê bằng Python để bảo đảm bin/quartile không sai lệch.
5. Xuất CSV/XLSX/PNG/SVG, kiểm tra UTF-8 và ẩn danh khi phù hợp.
6. Kiểm thử performance và chống lọt tên học sinh qua tooltip/export.

## Phase 10 — ML hỗ trợ học tập
**Mục tiêu:** Dự báo có kiểm chứng, không tự kết luận năng lực.

1. Chọn biến mục tiêu rõ ràng, ví dụ nguy cơ không đạt ngưỡng môn Toán học kỳ tiếp theo.
2. Tạo features theo `as_of_date`; không lấy dữ liệu tương lai gây leakage.
3. Dùng train/validation/test tách theo thời gian và học sinh; baseline trước mô hình phức tạp.
4. Đánh giá MAE/RMSE, precision/recall/calibration và drift theo nhóm.
5. Viết Model Card; kết quả chỉ hỗ trợ giáo viên xem xét, có quyền tắt model.
6. Không huấn luyện dữ liệu thật nếu chưa có quy trình quyền riêng tư và phê duyệt.

## Phase 11 — Triển khai, giám sát, bảo mật
**Mục tiêu:** Chuyển dự án từ tính năng sang hệ thống có thể vận hành an toàn.

1. Tách local/staging/production, quản lý secrets, HTTPS và tài khoản dịch vụ quyền tối thiểu.
2. CI kiểm tra type/lint/unit/integration/E2E/contract/migration/encoding/security tương ứng file thay đổi.
3. Thiết lập logging, metrics, tracing, cảnh báo ngừng API, lỗi worker, dung lượng và lịch backup.
4. Kiểm thử phân quyền sâu, SQL injection, dữ liệu xuất hàng loạt, lịch năm cũ, CP-SAT DoS.
5. Benchmark theo chỉ số p95 đã định; thử backup/restore và báo cáo RTO/RPO.
6. UAT với cán bộ đào tạo/khảo thí/giáo viên, hoàn tất lỗi P0/P1, ký duyệt.
7. Deploy và rollback chỉ theo phê duyệt thực tế; ghi Git SHA, thời gian và người thực hiện.

## Tình huống điển hình: Agent xử lý bug sai ngày nghỉ

- **BA/Triage:** nhận sự kiện `CAL-02`, mô tả lịch ngày 18/11 bị xếp dù đã khai báo nghỉ 16–18/11.
- **QA:** tạo reproduction bằng năm học, time slot, lớp giả lập; test xác nhận ngày cuối khoảng được tính inclusive.
- **Backend Agent:** kiểm tra `calendar_exceptions` và service filter, so sánh `date <= end_date`.
- **Solver Agent:** kiểm tra snapshot holiday đã truyền vào CP-SAT; validator cuối cần phát hiện lỗi ngay cả khi solver sai.
- **Security Reviewer:** kiểm tra người sửa ngày nghỉ có đúng quyền, audit có đủ actor/time/reason.
- **QA:** chạy lại test cũ, E2E và kiểm tra không phát sinh lỗi giờ `00:00` hoặc lệch múi giờ.
- **Handoff:** nêu nguyên nhân, file sửa, before/after, lệnh test, commit/push/merge chưa hay đã, vấn đề còn lại.

## Không được tuyên bố hoàn thành khi chưa có bằng chứng

`docs/progress/tasks/EDU-XXXX.md` là nhật ký từng task. `TASK_BOARD.md` là báo cáo sinh tự động. Tài liệu v2.0 mới là **blueprint**, chưa thể hiện sản phẩm Web chạy được, chưa có kiểm thử bảo mật ứng dụng thực, chưa có commit/push/merge.
