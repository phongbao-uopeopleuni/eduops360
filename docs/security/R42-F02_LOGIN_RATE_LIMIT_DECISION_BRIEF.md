# R42-F02 — Decision brief cho giới hạn đăng nhập theo IP

**Trạng thái:** `NOT APPROVED`  
**Ngày ghi nhận:** 2026-11-14  
**Người quyết định cần có:** Human Security Owner theo OD-001, với thông tin về topology triển khai  
**Code hiện tại:** giữ nguyên cho đến khi có quyết định rõ ràng

## Vấn đề cần quyết định

Limiter tạm thời theo direct peer chặn cứng sau 50 lần đăng nhập sai trong 60 giây. Một người chưa xác thực có thể dùng email ngẫu nhiên để làm mọi đăng nhập mới từ cùng peer nhận `429 LOGIN_RATE_LIMITED`, kể cả khi tài khoản khác nhập đúng mật khẩu. Rủi ro áp dụng cho mạng trường học dùng NAT; nếu ứng dụng đứng sau reverse proxy chưa được cấu hình tin cậy, limiter có thể trở thành limiter chung cho toàn bộ người dùng.

Probe độc lập EDU-0042 đã tái hiện: 50 phản hồi 401 cho email không tồn tại, sau đó tài khoản khác với mật khẩu đúng nhận 429; tài khoản đó vẫn `active` và `failed_login_count = 0`.

## Bất biến bắt buộc

1. Không tạo oracle A0102-F02: với cùng trạng thái limiter, HTTP status/body và nhánh chặn không được phụ thuộc vào việc mật khẩu vừa gửi đúng hay sai. Phương án "verify rồi chỉ cho mật khẩu đúng đi qua" không chấp nhận được nếu làm lộ tính đúng của credential qua 200/401/429 hoặc khác biệt thời gian rõ ràng.
2. Chỉ tin `Forwarded`/`X-Forwarded-For` từ danh sách proxy được cấu hình tường minh. Request trực tiếp hoặc proxy không tin cậy phải dùng direct peer.
3. Lockout theo tài khoản hiện tại vẫn là kiểm soát bền vững. Chính sách IP chỉ là lớp giảm password spraying, không được thay thế lockout hay audit.
4. Mọi giá trị ngưỡng, thời gian và backoff phải được phê duyệt; không biến giá trị `TẠM` thành mặc định sản phẩm bằng suy luận của agent.
5. Regression RC phải chứng minh vừa chống oracle, vừa thể hiện đúng quyết định về người dùng hợp lệ chung NAT.

## Các phương án

| Phương án | Cách làm | Lợi ích | Rủi ro/đổi lại | Điều kiện kiểm thử |
|---|---|---|---|---|
| A — Tạm tắt hard-block theo IP | Không kiểm/ghi cửa sổ IP; giữ per-identity limiter và lockout tài khoản | Loại bỏ DoS chéo tài khoản trong NAT/proxy; đơn giản nhất cho local/single-school | Password spraying qua nhiều email từ một nguồn quay lại mức đã công bố ở F09; phụ thuộc lockout theo tài khoản, audit và giám sát | Sau 50 lỗi cùng peer, tài khoản khác đúng mật khẩu không bị 429; per-identity và lockout vẫn đạt |
| B — Giữ hard-block nhưng đổi ngưỡng/ngữ nghĩa | Tăng ngưỡng/cửa sổ hoặc thay cách tính failure | Giữ một phần giảm spraying; ít thay đổi kiến trúc | Tăng ngưỡng chỉ tăng chi phí tấn công, không loại bỏ DoS; mọi hard-block trước verify vẫn chặn cả người hợp lệ; cho credential đúng đi qua sau verify vi phạm bất biến oracle | Test ngưỡng biên, NAT RC, unknown/known email, mật khẩu đúng/sai có phản hồi không phân biệt ngoài kết quả auth bình thường |
| C — Trusted proxy + ngưỡng cao hơn | Lấy địa chỉ client từ header chỉ khi direct peer nằm trong allowlist proxy; áp ngưỡng được duyệt | Tránh biến reverse proxy thành một peer toàn cục; attribution/audit chính xác hơn | Không giải quyết nhiều người dùng thật sau cùng NAT; cấu hình sai header có thể cho spoof/bypass; cần topology staging/production | Proxy tin cậy/không tin cậy, chuỗi header, spoof trực tiếp, IPv4/IPv6, NAT RC và fallback direct peer |
| D — Progressive delay thay hard-block | Áp độ trễ tăng dần theo peer trước verify, giống nhau cho mọi credential trong cùng trạng thái | Giảm tốc spraying mà không tạo hard deny kéo dài; có thể kết hợp per-identity lockout | Vẫn làm chậm người dùng chung NAT; giữ request/timer có thể gây resource DoS; cần giới hạn delay, concurrency và observability | Độ trễ giống nhau cho đúng/sai; giới hạn trên; hủy client; concurrency/load; NAT RC không nhận hard 429 nếu đó là quyết định |

CAPTCHA hoặc rate limiting ở edge có thể bổ sung sau, nhưng không phải một trong các khả năng hiện có và không được coi là đã phê duyệt.

## Khuyến nghị để người có thẩm quyền cân nhắc

- **Tạm thời/local:** A có bề mặt hành vi nhỏ nhất nếu ưu tiên tránh tự khóa cả mạng trường học trước khi biết topology.
- **Khi có reverse proxy được quản trị:** C chỉ giải quyết attribution; vẫn cần chọn A, B hoặc D cho người dùng chung NAT.
- **Hướng dài hạn:** D có thể cân bằng availability và chống spraying hơn hard-block, nhưng chỉ sau benchmark tải và chốt giới hạn cụ thể.

Đây là phân tích, không phải quyết định. Không phương án nào được triển khai từ brief này.

## Câu hỏi phê duyệt

Security Owner cần ghi rõ:

1. Chọn A, B, C, D hay tổ hợp nào; ngày hiệu lực và người phê duyệt.
2. Topology: direct local, reverse proxy nào, CIDR proxy tin cậy và có NAT trường học hay không.
3. Ngưỡng/cửa sổ hoặc dãy delay tối đa; hành vi khi limiter bão hòa.
4. 429 có còn được dùng hay không; nếu có, đối tượng và thời điểm áp dụng sao cho không tạo oracle.
5. Yêu cầu metrics/alert/retention cho các đợt spraying.

Cho đến khi năm mục trên được điền, R42-F02 vẫn là P2 mở và Phase 02 không được ghi "không còn P1/P2".
