# Phase 08 — Official legal source registry v1

**Status:** `REVIEW_REQUIRED / AUTOMATION_DISABLED`

Registry này hoàn thành phạm vi P08-T01. Nó cho phép con người tham chiếu các
nguồn chính thức nhưng **không** cấp quyền crawl/sync. Khi chưa có API contract,
usage approval và rate limit chính thức, mọi connector có `automated_rate = 0`.

## Allowlist và capability

| Source ID | Host / phạm vi | Authority/capability đã quan sát | Usage/rate decision v1 | Trạng thái |
| --- | --- | --- | --- | --- |
| `GOV_VANBAN` | `https://vanban.chinhphu.vn/` | Metadata văn bản, ngày ban hành/hiệu lực, cơ quan, link bản ký | Trang yêu cầu ghi rõ nguồn Cục Thông tin và Truyền thông Chính phủ hoặc `chinhphu.vn` khi phát hành lại. Chưa xác minh API/rate/automation terms: `automated_rate=0`, `concurrency=0` | `MANUAL_ALLOWED` |
| `GOV_SIGNED_FILES` | `https://datafiles.chinhphu.vn/` | PDF ký được liên kết từ trang metadata đã allowlist | Chỉ mở attachment từ một record `GOV_VANBAN`; không directory crawl; giữ source URL/checksum/retrieved-at. Chưa có rate approval: `automated_rate=0` | `MANUAL_ATTACHMENT_ONLY` |
| `MOET_PORTAL` | `https://moet.gov.vn/` và subdomain thuộc Bộ | Văn bản/tin/hướng dẫn và attachment do Bộ GDĐT công bố; dùng để corroborate, không tự thay thế record pháp quy | Chưa xác minh public API, license hoặc rate limit cho connector: `automated_rate=0`, `concurrency=0` | `MANUAL_CORROBORATION_ONLY` |
| `NATIONAL_VBPL` | `https://vbpl.vn/` | Cơ sở dữ liệu quốc gia về pháp luật, có trang toàn văn/thuộc tính/lịch sử và file gốc | Automated retrieval trong preflight trả `403`; không bypass. Chưa có approved integration/API credentials/rate: `automated_rate=0`, `concurrency=0` | `MANUAL_ONLY / CONNECTOR_BLOCKED` |

Không host mirror, blog, mạng xã hội, kết quả AI hoặc website thương mại nào nằm
trong allowlist v1. Search result chỉ là discovery hint; claim phải trỏ tới record
allowlist và giữ thời điểm truy xuất.

## Connector capability contract

| Capability | v1 |
| --- | --- |
| Human open/search | Cho phép trên allowlist theo điều khoản site |
| Automated listing/search | Tắt |
| Automated metadata fetch | Tắt |
| Automated attachment fetch | Tắt |
| API integration | Chưa xác định endpoint/contract; tắt |
| Authentication/credentials | Không được cấp trong task này |
| Retry/backoff | Không áp dụng khi connector tắt |
| Policy activation from source | Cấm tuyệt đối; luôn cần reviewed snapshot + human approval |

## Điều kiện để bật một connector sau này

1. Source owner hoặc authority xác nhận API/integration method, usage terms,
   attribution, allowed purpose, retention và rate/concurrency cụ thể.
2. Security review xác nhận TLS, redirect/attachment host, MIME/size limits,
   malware quarantine, SSRF controls và secret custody nếu có credential.
3. Connector dùng conditional request/cursor nếu nguồn hỗ trợ; retry có jitter,
   circuit breaker và không bypass `403`, robots hoặc throttling.
4. Mỗi retrieval lưu source ID, canonical URL, retrieved-at UTC, content checksum,
   media type và observed status; không overwrite version cũ.
5. Domain reviewer xác nhận quan hệ amend/repeal/effective interval trước khi một
   document được dùng làm policy input. Source sync không tự đổi grade/calendar.

## Unresolved authority items

- Ai đại diện liên hệ source owner và phê duyệt usage/rate: `OPEN`.
- Public API chính thức cho từng source: `NOT_FOUND / NOT_CONFIRMED`.
- License/retention cho bản PDF và extracted text: `OPEN`.
- Production egress IP, user agent và contact channel: `OPEN`.
- Revalidation cadence và incident owner: `OPEN`.

Cho đến khi các mục trên được duyệt, registry v1 chỉ phục vụ research thủ công.
