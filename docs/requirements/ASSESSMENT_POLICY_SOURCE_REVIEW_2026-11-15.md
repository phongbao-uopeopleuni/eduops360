# Phase 07 — rà soát nguồn chính sách đánh giá (2026-11-15)

**Trạng thái:** `RESEARCHED / NOT APPROVED / DO NOT ACTIVATE`

Tài liệu này hoàn thành phạm vi P07-T01: nhận diện nguồn chính thức và ranh giới
áp dụng ở mức văn bản. Nó không diễn giải công thức điểm, rounding, xếp loại hay
tạo policy có thể chạy. Domain SME phải đọc bản ký, kiểm tra sửa đổi/chuyển tiếp
và ký duyệt trước P07-T02/P07-T03.

## Nguồn chính thức đã kiểm tra

| Văn bản | Phạm vi metadata chính thức | Ban hành | Hiệu lực ghi trên nguồn | URL chính thức | Trạng thái dùng trong EduOps |
| --- | --- | --- | --- | --- | --- |
| `27/2020/TT-BGDĐT` | Đánh giá học sinh tiểu học | 2020-09-04 | 2020-10-20 | https://vanban.chinhphu.vn/?docid=201006&pageid=27160 | Baseline candidate cho lớp 1–5; chưa được kích hoạt thành rule |
| `22/2021/TT-BGDĐT` | Đánh giá học sinh THCS và THPT | 2021-07-20 | 2021-09-05 | https://vanban.chinhphu.vn/default.aspx?docid=203926&pageid=27160 | Baseline candidate cho lớp 6–12; chưa được kích hoạt thành rule |
| `89/2026/TT-BGDĐT` | Sửa đổi cả `27/2020` và `22/2021` | 2026-10-16 | **2026-12-01** | https://vanban.chinhphu.vn/?docid=220070&orggroupid=4&pageid=27160 | Đã ban hành nhưng chưa có hiệu lực tại ngày rà soát; block activation cho đến khi có reviewed diff |

Các trang metadata trên Cổng Thông tin điện tử Chính phủ liên kết bản PDF đã ký.
Metadata được truy xuất ngày 2026-11-15. Không suy ra rằng không còn văn bản
liên quan chỉ vì ba trang này được tìm thấy.

## Ma trận áp dụng tạm thời

| Khoảng thời gian nghiệp vụ | Cấp/lớp | Baseline candidate | Quyết định hệ thống |
| --- | --- | --- | --- |
| Đến hết 2026-11-30 | Tiểu học, lớp 1–5 | `27/2020/TT-BGDĐT` | Chỉ tham chiếu; không tạo calculation rule |
| Đến hết 2026-11-30 | THCS/THPT, lớp 6–12 | `22/2021/TT-BGDĐT` | Chỉ tham chiếu; không tạo calculation rule |
| Từ 2026-12-01 | Lớp 1–12 | Baseline tương ứng + `89/2026/TT-BGDĐT` | `BLOCKED_PENDING_DOMAIN_REVIEW`; không tự chuyển policy theo ngày đồng hồ |

Mốc trên chỉ phản ánh ngày hiệu lực từ metadata nguồn chính thức. Việc áp dụng
cho năm học, loại trường, môn học, học sinh khuyết tật/chương trình đặc thù và
hồ sơ đang chuyển tiếp vẫn chưa được phê duyệt.

## Bất định phải được Domain SME xử lý

1. Đọc toàn văn ba bản ký, lập diff từng điều/khoản và kiểm tra đính chính,
   văn bản hợp nhất, bãi bỏ hoặc hướng dẫn thi hành mới hơn.
2. Xác nhận phạm vi theo loại trường, chương trình, lớp, môn và năm học; không
   mặc định mọi cơ sở/lớp đặc thù dùng cùng một rule.
3. Xác nhận assessment type, thang đo/nhận xét, completeness, rounding, xếp loại
   và trường hợp miễn/khuyết dữ liệu bằng test vector có nguồn.
4. Xác nhận transition đối với kết quả đã ghi trước 2026-12-01 và quy tắc replay
   lịch sử; tuyệt đối không tính lại lịch sử bằng policy mới.
5. Kiểm tra hướng dẫn địa phương/trường chỉ sau khi authority xác định chúng có
   thẩm quyền và không xung đột văn bản cấp trên.

## Gate kích hoạt

- Domain SME: `PENDING` — tên/chữ ký/thời điểm chưa có.
- Product/School authority: `PENDING`.
- Reviewed policy snapshot/version: `NOT_CREATED`.
- Calculation/API/grade mutation: `PROHIBITED_BY_THIS_TASK`.

Nếu không xác định chắc policy áp dụng, hệ thống phải trả trạng thái unsupported
hoặc yêu cầu review, không suy đoán và không tạo “GPA chung” cho tiểu học.
