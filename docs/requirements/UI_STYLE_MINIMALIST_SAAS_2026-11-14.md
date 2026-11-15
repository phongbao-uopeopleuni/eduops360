# Đặc tả kỹ thuật UI — Minimalist SaaS (Soft UI, Product-led)

Nov 14, 2026 · @Phong Bao

## Tổng quan & nguyên tắc

Phong cách này là **Minimalist SaaS** kết hợp **Soft UI** và **minh họa bằng sản phẩm (product-led)**. Đặc trưng: nền trắng, tiêu đề đen cỡ lớn, một màu nhấn xanh indigo, và giao diện app thật làm hình minh họa chính. Trang tham chiếu: [Elton DataUtils](https://datautilshub.eltondata.com/), quan sát ngày 14/11/2026.

**Quy ước:** giá trị ghi *(đo)* được đo trực tiếp trên trang tham chiếu. Các giá trị còn lại là đề xuất để giữ đúng phong cách.

### Sáu nguyên tắc cốt lõi

1. **Chữ dẫn dắt (type-led).** Headline cỡ lớn là điểm nhấn thị giác số 1. Hero không dùng ảnh nền.
2. **Một màu nhấn.** Màu primary chỉ dành cho hành động (CTA, link) và dữ liệu (biểu đồ). Mọi thứ khác là trắng, xám, đen.
3. **Khoảng trắng là cấu trúc.** Tách nội dung bằng khoảng cách và nền section xen kẽ, không dùng đường kẻ.
4. **Mềm mại.** Bo góc lớn, bóng đổ rất nhạt. Gradient chỉ xuất hiện ở glow nền và icon.
5. **Show, don't tell.** Minh họa bằng ảnh chụp app hoặc mảnh UI (card, chart, progress bar), không dùng ảnh stock.
6. **Một hành động chính.** Chỉ một CTA chính (ví dụ "Đặt lịch demo"), lặp lại ở navbar và cuối trang.

**Nên dùng cho:** landing page B2B SaaS, công cụ AI, sản phẩm dashboard/data, trang giới thiệu app. **Không hợp với:** thương hiệu cần cảm xúc mạnh hoặc hình ảnh đời thường làm chủ đạo (thời trang, F&B, lifestyle).

## Màu sắc

Bảng màu gồm một primary xanh indigo `#394CFF` trên nền trắng–xám trung tính. Màu phụ chỉ dùng cho dữ liệu.

| Token | Giá trị | Dùng cho | Nguồn |
| --- | --- | --- | --- |
| `--color-primary` | `#394CFF` | CTA, link, chart chính, icon | Đo |
| `--color-primary-hover` | `#2B3BE6` | Hover/active của CTA | Đề xuất |
| `--color-primary-soft` | `#EEF0FF` | Nền badge, tag, vùng fill chart nhạt | Đề xuất |
| `--color-glow` | `rgba(124, 108, 255, 0.18)` | Quầng sáng lavender sau mockup hero | Ước lượng từ ảnh chụp |
| `--color-bg` | `#FFFFFF` | Nền trang, section chính | Đo |
| `--color-bg-alt` | `#F4F4F5` | Section xen kẽ | Ước lượng từ ảnh chụp |
| `--color-surface` | `#FFFFFF` | Card, mockup, form | Đề xuất |
| `--color-text` | `#0A0A0A` | Heading, số liệu lớn | Ước lượng từ ảnh chụp |
| `--color-text-muted` | `#5F6673` | Đoạn mô tả, bullet, caption | Đề xuất |
| `--color-border` | `#E5E7EB` | Viền card, đáy navbar | Đề xuất |
| `--color-data-2` | `#2CC59A` | Series phụ thứ 2 trong chart, progress | Ước lượng từ ảnh chụp |
| `--color-data-3` | `#F5B83D` | Series phụ thứ 3 trong chart | Ước lượng từ ảnh chụp |

### Quy tắc dùng màu

- Primary chiếm diện tích nhỏ. Mỗi màn hình chỉ nên có 1 nút primary nổi bật.
- Màu phụ (`data-2`, `data-3`) chỉ dùng trong chart và progress, không dùng cho nút hay chữ.
- Không dùng gradient trên nút hoặc chữ. Gradient chỉ dùng cho glow nền và icon soft 3D.
- Độ tương phản đã tính theo WCAG: chữ trắng trên `#394CFF` = 5.75:1; `#5F6673` trên `#FFFFFF` = 5.78:1 và trên `#F4F4F5` = 5.26:1. Cả ba đều đạt AA cho chữ thường.
- Tránh xám nhạt kiểu `#9CA3AF` cho chữ nội dung: chỉ đạt 2.54:1 trên nền trắng.

## Typography

Hai font: **Poppins** (sans hình học) cho tiêu đề và **Inter** cho nội dung. H1 cỡ 60px, đậm 700 *(đo)*.

Font stack đo được:

- Heading: `Poppins, "Avenir Next", Futura, "Century Gothic", ui-rounded, system-ui, sans-serif`
- Body: `Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`

| Vai trò | Font | Desktop | Mobile | Weight | Line-height | Letter-spacing |
| --- | --- | --- | --- | --- | --- | --- |
| H1 / Display | Poppins | 60px *(đo)* | 36px | 700 *(đo)* | 1.1 | -0.02em |
| H2 section | Poppins | 44px | 30px | 700 | 1.15 | -0.015em |
| H3 card / feature | Poppins | 24px | 20px | 600 | 1.3 | -0.01em |
| Số liệu lớn (stat) | Poppins | 32px | 28px | 700 | 1.0 | -0.02em |
| Lead (mô tả dưới H1/H2) | Inter | 18px | 16px | 400 | 1.7 | 0 |
| Body / bullet | Inter | 16px | 16px | 400 | 1.6 | 0 |
| Button | Inter | 16px | 15px | 600 | 1.0 | 0 |
| Caption / label chart | Inter | 13px | 12px | 500 | 1.4 | 0 |
| Code | `ui-monospace, "JetBrains Mono"` | 13px | 12px | 400 | 1.6 | 0 |

Các cỡ ngoài H1 là đề xuất, ước theo tỉ lệ trên ảnh chụp ở khung rộng \~1020px.

### Quy tắc

- Hero và phần giới thiệu section: căn giữa. Khối zig-zag: căn trái.
- Heading tối đa 2–3 dòng, dùng `text-wrap: balance` để các dòng dài đều nhau.
- Đoạn lead rộng tối đa \~640px (60–70 ký tự mỗi dòng), màu `--color-text-muted`.
- Tiếng Việt: line-height heading không dưới 1.1, nếu thấp hơn dấu chồng (Ể, Ặ, Ỹ) sẽ bị cắt hoặc đè dòng trên.
- Tải Poppins và Inter kèm subset `vietnamese`. Nếu Poppins không tải được, trình duyệt rơi về Futura/Century Gothic, vốn hiển thị dấu tiếng Việt kém đồng đều.
- Chỉ dùng 3 weight: 400, 600, 700.

## Layout, grid & spacing

Bố cục dùng container 1200px, lưới 12 cột và thang khoảng cách gốc 4px. Mỗi section có khoảng đệm dọc lớn (\~120px) để trang "thở".

| Thành phần | Desktop | Mobile |
| --- | --- | --- |
| Container `max-width` | 1200px | 100% |
| Padding ngang container | 24px | 16px |
| Lưới | 12 cột, gutter 24px | 4 cột, gutter 16px |
| Navbar (sticky) | cao \~80px *(ước lượng từ ảnh chụp)* | cao 64px |
| Padding dọc section | 120px | 72px |
| Heading → lead | 24px | 16px |
| Lead → visual / grid | 64px | 40px |
| Gap cột zig-zag | 64px | xếp dọc, gap 32px |
| Gap card trong grid | 24px | 16px |
| Padding trong card | 32px | 24px |

### Thang khoảng cách

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 120` (px). Chỉ dùng giá trị trong thang, không dùng số lẻ như 13px hay 37px.

### Nhịp trang

- Nền section xen kẽ `--color-bg` và `--color-bg-alt` để phân đoạn, không dùng đường kẻ ngang.
- Feature 3 cột: mỗi cột span 4. Zig-zag: span 6/6 hoặc 5/7, đảo bên sau mỗi section.
- Mockup sản phẩm ở hero rộng bằng container (full 12 cột), các visual khác tối đa 7 cột.

## Bo góc, bóng đổ & hiệu ứng

Mọi khối đều bo góc lớn, bóng đổ rất nhẹ và tỏa rộng. Nút dùng dạng viên thuốc `border-radius: 999px` *(đo)*.

### Radius

| Token | Giá trị | Dùng cho |
| --- | --- | --- |
| `--radius-pill` | 999px *(đo)* | Button, badge, bộ chọn ngôn ngữ |
| `--radius-xl` | 24px | Khung mockup hero, khối visual zig-zag |
| `--radius-lg` | 16px | Card con (Knowledge Base, chart card) |
| `--radius-md` | 12px | Input, tile icon |
| `--radius-sm` | 8px | Tag, chip code |

Quy tắc lồng nhau: radius trong = radius ngoài − padding. Ví dụ khung 24px, padding 8px thì card bên trong bo 16px.

### Elevation

| Token | Giá trị | Dùng cho |
| --- | --- | --- |
| `--shadow-sm` | `0 1px 2px rgba(16,24,40,.04), 0 1px 3px rgba(16,24,40,.06)` | Navbar khi cuộn, card nhỏ |
| `--shadow-md` | `0 8px 24px rgba(16,24,40,.06)` | Card tiêu chuẩn, card hover |
| `--shadow-lg` | `0 24px 64px rgba(57,76,255,.10)` | Mockup hero, visual chính (bóng ánh xanh) |

Tất cả giá trị radius và shadow ngoài `999px` là đề xuất, ước từ ảnh chụp.

### Hiệu ứng nền

- **Glow blob:** hình tròn lớn màu lavender phía sau mockup, `filter: blur(60px)` hoặc `radial-gradient(circle, rgba(124,108,255,.18), transparent 60%)`.
- **Nền khung hero:** chuyển từ trắng sang lavender nhạt, ví dụ `linear-gradient(135deg, #FFFFFF 40%, #EDEBFF 100%)`.
- Mỗi khối chỉ dùng **hoặc** viền 1px `--color-border` **hoặc** shadow, không dùng cả viền đậm lẫn bóng nặng.
- Không dùng glassmorphism (blur nền trong suốt) cho nội dung chính. Ngoại lệ: navbar sticky có thể dùng `backdrop-filter: blur(12px)` với nền trắng 85%.

## Components

Bộ component gồm 11 khối. Tất cả dùng chung token ở các phần trên, không tự đặt màu hoặc radius riêng.

| Component | Cấu trúc | Thông số chính | Trạng thái |
| --- | --- | --- | --- |
| Navbar | Logo bên trái; bộ chọn ngôn ngữ + CTA bên phải | Sticky top, cao 80px, nền trắng | Khi cuộn: thêm `--shadow-sm` hoặc viền dưới 1px |
| Button primary | Nhãn ngắn, động từ ("Đặt lịch demo") | Nền `#394CFF`, chữ trắng 16/600, cao 48px, padding 0 24px, pill | Hover `#2B3BE6` + nâng 1px; focus ring 3px; disabled opacity 0.5 |
| Button secondary | Nhãn + mũi tên (tuỳ chọn) | Nền trắng, viền 1px `--color-border`, chữ `--color-text`, pill | Hover nền `--color-bg-alt` |
| Bộ chọn ngôn ngữ | Icon quả địa cầu + nhãn + chevron | Ghost, không viền, chữ 15px | Mở dropdown card `--radius-lg` + `--shadow-md` |
| Feature tile | Ô minh họa + caption căn giữa bên dưới | Ô tỉ lệ \~6:5, nền gradient rất nhạt `#F7F8FF → #FFFFFF`, icon soft 3D ở giữa; caption 16px muted | Không có hover (thuần minh họa) |
| Mockup frame | Khung chứa ảnh chụp app, có thể có nút play video ở giữa | `--radius-xl`, `--shadow-lg`, nền gradient trắng→lavender, padding 32–48px | Nút play: tròn 64px, trắng, `--shadow-md` |
| Skeleton placeholder | Thanh xám thay chữ trong mockup | Nền `#EEF0F3`, cao 8–12px, radius 4–6px | Tĩnh, không shimmer |
| Stat card | Tiêu đề + menu "…"; số lớn + nhãn; thanh tiến độ nhiều màu | Tiêu đề 16/600; số 32/700; nhãn 13px muted; thanh cao 6px, pill | Thanh dùng primary → `data-2` → `data-3` |
| Chart card | Tiêu đề căn giữa; chart; dòng kết luận "30% …" | Line/bar màu primary, vùng fill `--color-primary-soft`; số kết luận 32/700 | Tooltip: nền trắng, `--radius-sm`, `--shadow-sm`, số màu primary |
| Code window | Thanh tiêu đề với 3 chấm kiểu macOS; thân chứa code | Chấm 12px `#FF5F57` `#FEBC2E` `#28C840`; nền trắng; mono 13px; keyword/string màu primary | Không tương tác |
| Form đặt lịch demo | Modal: tiêu đề, các field, nút gửi; màn hình xác nhận "Đã nhận yêu cầu" | Input cao 48px, `--radius-md`, viền 1px; label 14/500 trên field | Focus: viền primary + ring; lỗi: viền đỏ + thông báo dưới field |

**Bullet list nội dung** (dùng trong zig-zag): chấm xám 6px, chữ 17–18px muted, line-height 1.6, cách nhau 16px. Mỗi bullet tối đa 2 dòng.

## Section patterns

Trang được ghép từ 5 pattern lặp lại: hero, feature 3 cột, showcase, zig-zag và CTA cuối trang. Thứ tự dưới đây theo đúng trang tham chiếu.

&#91;embedded content: giải phẫu trang · 7 khối từ navbar đến CTA\]

Đọc từ trên xuống: nền đổi màu khi đổi nhóm nội dung, và nút primary chỉ xuất hiện ở navbar, hero và cuối trang.

| # | Section | Pattern | Bố cục | Nền |
| --- | --- | --- | --- | --- |
| 1 | Hero | Hero | H1 căn giữa 2–3 dòng → lead → mockup frame full container, glow lavender phía sau | `bg` |
| 2 | Giá trị cốt lõi | Feature 3 cột | H2 căn giữa → 3 feature tile, mỗi tile 1 icon soft 3D + caption | `bg` |
| 3 | Không gian AI | Showcase | Mockup app lớn → H2 + lead căn giữa bên dưới | `bg-alt` |
| 4 | Trực quan hóa / chẩn đoán | Zig-zag | Chữ trái (H2 + bullet), hình phải (ảnh + card UI nổi phủ lên) | `bg` |
| 5 | Cá nhân hóa | Zig-zag (đảo bên) | Hình trái (stat card), chữ phải | `bg-alt` |
| 6 | Tạo biểu đồ | Zig-zag biến thể | H2 + bullet căn trái → hàng 3 chart card | `bg` |
| 7 | Bộ metrics chuẩn | Zig-zag | Chữ trái, hình phải (bảng định nghĩa metric trong card) | `bg` |
| 8 | SQL từ ngôn ngữ tự nhiên | Showcase | H2 + lead căn giữa → code window | `bg-alt` |
| 9 | Tối ưu chi phí, tài liệu | Feature / zig-zag | Theo nội dung | xen kẽ |
| 10 | CTA cuối trang | CTA | H2 căn giữa "Sẵn sàng…" → button primary | `bg-alt` hoặc `primary-soft` |

### Quy tắc ghép

- Mỗi section chỉ có 1 H2 và 1 ý chính.
- Hai section liền nhau không dùng cùng pattern **và** cùng màu nền.
- Zig-zag đảo bên chữ/hình sau mỗi lần lặp.
- CTA chính xuất hiện tối thiểu 2 lần: navbar (luôn thấy) và section cuối.

## Iconography & minh họa

Minh họa có 3 loại: icon soft 3D cho ý tưởng trừu tượng, ảnh chụp app cho tính năng thật, và mảnh UI cho từng lợi ích cụ thể.

### Icon soft 3D (feature tile)

- Gồm 2–3 lớp chồng nhau: một card trắng làm nền, hình dữ liệu (cột, đường, vòng tròn) và một badge tròn nổi ở góc (sparkle, đồng hồ, danh sách).
- Màu: gradient primary → lavender (`#394CFF` → `#A9B1FF`); phần còn lại trắng và xám rất nhạt.
- Ánh sáng từ trên bên trái, bóng mềm tím nhạt bên dưới. Không viền đen, không outline.
- Phong cách thống nhất giữa các icon: cùng góc nhìn, cùng bảng màu, cùng mức chi tiết.
- Xuất ảnh PNG/WebP nền trong suốt ở 2x (ví dụ ô hiển thị 240px thì ảnh 480px), hoặc SVG nếu vẽ vector.

### Ảnh chụp sản phẩm

- Chụp app thật ở chế độ sáng, dữ liệu mẫu trông thực tế (tên công ty giả định, số liệu hợp lý).
- Có thể thay phần không quan trọng bằng skeleton xám để mắt tập trung vào vùng chính (ví dụ khung chat AI).
- Đặt trong mockup frame. Không dùng khung laptop/điện thoại giả lập.

### Mảnh UI (UI fragment)

- Cắt một card đơn lẻ từ app (stat card, chart, bảng metric) và phóng to để minh họa đúng 1 lợi ích.
- Có thể phủ card nổi lên ảnh người thật (ví dụ card phân tích có progress 75% đặt trên ảnh). Ảnh phải có tông ấm, độ bão hòa thấp để không cạnh tranh với card.

### Icon giao diện (UI icon)

Dùng bộ icon outline nét 1.5–2px, 20–24px (ví dụ Lucide hoặc Heroicons), màu theo chữ. Không trộn icon fill và outline trong cùng màn hình.

## Motion & tương tác

Chuyển động ngắn (150–600ms) và tiết chế, chỉ để phản hồi thao tác và dẫn mắt khi cuộn. Phần này là đề xuất; trang tham chiếu chưa được đo hiệu ứng.

| Tương tác | Hiệu ứng | Thời lượng | Easing |
| --- | --- | --- | --- |
| Hover button | Đổi nền sang `primary-hover`, nâng `translateY(-1px)` | 150ms | `ease-out` |
| Hover card có link | `--shadow-sm` → `--shadow-md`, nâng 2px | 200ms | `ease-out` |
| Focus (bàn phím) | Ring 3px `rgba(57,76,255,.35)`, offset 2px | Ngay lập tức | — |
| Navbar khi cuộn qua 8px | Hiện `--shadow-sm` hoặc viền dưới | 200ms | `ease` |
| Section vào khung nhìn | Fade-in + trượt lên 16px, chạy 1 lần | 500ms | `cubic-bezier(.22,1,.36,1)` |
| Card trong grid | Như trên, lệch nhau 80ms mỗi card | 500ms | như trên |
| Chart trong card | Vẽ đường / mọc cột khi vào khung nhìn | 600ms | `ease-out` |
| Mở modal form | Nền mờ dần; modal phóng từ 96% lên 100% | 200ms | `ease-out` |

### Quy tắc

- Chỉ animate `transform` và `opacity` để không gây giật layout.
- Không dùng parallax, không tự chạy carousel, không animation lặp vô hạn.
- Video demo trong hero chỉ phát khi người dùng bấm nút play.
- Tôn trọng `prefers-reduced-motion`: tắt trượt/phóng, chỉ giữ fade.

## Responsive

Thiết kế mobile-first với 4 breakpoint. Mọi bố cục nhiều cột xếp thành 1 cột dưới 768px.

| Breakpoint | Khoảng rộng | Thay đổi chính |
| --- | --- | --- |
| `sm` | < 640px | 1 cột; H1 36px; padding ngang 16px; navbar chỉ còn logo + CTA thu gọn, ngôn ngữ vào menu |
| `md` | 640–767px | 1 cột; feature tile có thể 2 cột; H1 44px |
| `lg` | 768–1023px | Zig-zag 2 cột 6/6; feature 3 cột; H1 52px |
| `xl` | ≥ 1024px | Layout đầy đủ; container 1200px; H1 60px |

### Cách co giãn từng pattern

- **Cỡ chữ:** dùng `clamp()` thay vì nhảy bậc, ví dụ H1 `clamp(2.25rem, 1.2rem + 3.6vw, 3.75rem)`.
- **Zig-zag:** trên mobile luôn hiển thị chữ trước, hình sau, bất kể thứ tự trên desktop.
- **Hàng 3 chart card:** chuyển thành dải cuộn ngang có `scroll-snap`, hoặc xếp dọc.
- **Mockup hero:** giữ tỉ lệ, cho phép tràn nhẹ ra mép phải; dùng ảnh riêng cho mobile nếu chữ trong ảnh nhỏ hơn 10px.
- **Code window:** cuộn ngang bên trong khung, không để cả trang bị cuộn ngang.
- **Chạm:** vùng bấm tối thiểu 44 × 44px.

## Accessibility

Mục tiêu: đạt WCAG 2.1 AA. Rủi ro lớn nhất của phong cách này là chữ xám nhạt và chữ nằm trong ảnh.

- **Tương phản:** chữ thường ≥ 4.5:1, chữ lớn (≥ 24px, hoặc ≥ 18.66px đậm) ≥ 3:1. Dùng các cặp màu đã kiểm ở phần Màu sắc.
- **Chữ trong ảnh chụp app:** chỉ để trang trí. Thông tin quan trọng phải có bản chữ thật bên ngoài ảnh.
- **Alt text:** ảnh chụp app mô tả điều nó chứng minh (ví dụ "Khung chat AI đang lập kế hoạch phân tích MRR"); icon soft 3D thuần trang trí dùng `alt=""`.
- **Bàn phím:** mọi nút, link, dropdown, modal đều dùng được bằng Tab/Enter/Esc. Modal giữ focus bên trong và trả focus về nút đã mở nó.
- **Focus hiển thị rõ:** không dùng `outline: none` nếu không thay bằng ring tương đương.
- **Chart:** không phân biệt series chỉ bằng màu; thêm nhãn hoặc chú thích trực tiếp.
- **Ngôn ngữ:** đặt `<html lang="vi">` (hoặc `en` khi đổi ngôn ngữ) để trình đọc màn hình phát âm đúng.
- **Heading:** mỗi trang 1 H1; mỗi section 1 H2; không nhảy cấp.
- **Chuyển động:** tôn trọng `prefers-reduced-motion` (xem phần Motion).

## Code mẫu

Bộ CSS dưới đây gom toàn bộ token và các component cơ bản. Code đã được render thử bằng Chromium ở khung 1280px và 390px: H1 ra đúng 60px và 36px, zig-zag đảo bên trên desktop và về "chữ trước, hình sau" trên mobile.

### tokens.css

```css
/* Google Fonts css2 tự chia subset (gồm vietnamese) theo unicode-range */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@600;700&display=swap');

:root {
  /* Color */
  --color-primary: #394CFF;
  --color-primary-hover: #2B3BE6;
  --color-primary-soft: #EEF0FF;
  --color-glow: rgba(124, 108, 255, 0.18);
  --color-bg: #FFFFFF;
  --color-bg-alt: #F4F4F5;
  --color-surface: #FFFFFF;
  --color-text: #0A0A0A;
  --color-text-muted: #5F6673;
  --color-border: #E5E7EB;
  --color-data-2: #2CC59A;
  --color-data-3: #F5B83D;

  /* Typography */
  --font-display: Poppins, "Avenir Next", Futura, system-ui, sans-serif;
  --font-body: Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --fs-h1: clamp(2.25rem, 1.2rem + 3.6vw, 3.75rem);   /* 36 → 60px */
  --fs-h2: clamp(1.875rem, 1rem + 2.6vw, 2.75rem);    /* 30 → 44px */
  --fs-h3: clamp(1.25rem, 1rem + 0.8vw, 1.5rem);      /* 20 → 24px */
  --fs-lead: clamp(1rem, 0.9rem + 0.4vw, 1.125rem);   /* 16 → 18px */

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-pill: 999px;

  /* Elevation */
  --shadow-sm: 0 1px 2px rgba(16, 24, 40, .04), 0 1px 3px rgba(16, 24, 40, .06);
  --shadow-md: 0 8px 24px rgba(16, 24, 40, .06);
  --shadow-lg: 0 24px 64px rgba(57, 76, 255, .10);

  /* Layout */
  --container: 1200px;
  --gutter: 24px;
  --section-y: 120px;
}

@media (max-width: 767px) {
  :root { --gutter: 16px; --section-y: 72px; }
}

/* Base */
body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font: 400 16px/1.6 var(--font-body);
}
h1, h2, h3 { margin: 0; font-family: var(--font-display); text-wrap: balance; }
h1 { font-size: var(--fs-h1); font-weight: 700; line-height: 1.1; letter-spacing: -0.02em; }
h2 { font-size: var(--fs-h2); font-weight: 700; line-height: 1.15; letter-spacing: -0.015em; }
h3 { font-size: var(--fs-h3); font-weight: 600; line-height: 1.3; letter-spacing: -0.01em; }
.lead {
  max-width: 640px;
  margin: 24px auto 0;
  font-size: var(--fs-lead);
  line-height: 1.7;
  color: var(--color-text-muted);
}
.lead--left { margin-inline: 0; }

/* Layout */
.container { max-width: var(--container); margin-inline: auto; padding-inline: var(--gutter); }
.section { padding-block: var(--section-y); }
.section--alt { background: var(--color-bg-alt); }
.section__intro { text-align: center; }
.hero__cta { margin-top: 32px; }

/* Button */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  height: 48px; padding: 0 24px;
  border: 1px solid transparent; border-radius: var(--radius-pill);
  font: 600 16px/1 var(--font-body); text-decoration: none; cursor: pointer;
  transition: background-color .15s ease-out, transform .15s ease-out;
}
.btn--primary { background: var(--color-primary); color: #fff; }
.btn--primary:hover { background: var(--color-primary-hover); transform: translateY(-1px); }
.btn--secondary { background: var(--color-surface); color: var(--color-text); border-color: var(--color-border); }
.btn--secondary:hover { background: var(--color-bg-alt); }
.btn:focus-visible { outline: 3px solid rgba(57, 76, 255, .35); outline-offset: 2px; }

/* Card */
.card {
  padding: 32px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

/* Mockup frame + glow */
.mockup {
  position: relative; isolation: isolate; overflow: hidden;
  margin-top: 64px; padding: 48px;
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, #FFFFFF 40%, #EDEBFF 100%);
  box-shadow: var(--shadow-lg);
}
.mockup::before {
  content: ""; position: absolute; z-index: -1;
  top: -10%; right: 10%; width: 480px; height: 480px; border-radius: 50%;
  background: radial-gradient(circle, var(--color-glow), transparent 60%);
}
.mockup img { display: block; width: 100%; border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }
@media (max-width: 767px) { .mockup { margin-top: 40px; padding: 16px; } }

/* Zig-zag: markup luôn là chữ trước, hình sau */
.zigzag { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center; }
.zigzag--reverse > :first-child { order: 2; }
@media (max-width: 767px) {
  .zigzag { grid-template-columns: 1fr; gap: 32px; }
  .zigzag--reverse > :first-child { order: 0; }
}

/* Scroll reveal (chỉ ẩn khi JS đã chạy) */
.js .reveal {
  opacity: 0; transform: translateY(16px);
  transition: opacity .5s cubic-bezier(.22, 1, .36, 1), transform .5s cubic-bezier(.22, 1, .36, 1);
}
.js .reveal.is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) {
  .js .reveal { transform: none; transition: opacity .3s; }
  .btn { transition: none; }
}
```

### reveal.js

Thêm class `js` vào `<html>` rồi hiện từng khối khi cuộn tới. Nếu JS lỗi, nội dung vẫn hiển thị bình thường.

```javascript
document.documentElement.classList.add('js');
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
  });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach((el, i) => {
  el.style.transitionDelay = `${(i % 3) * 80}ms`;
  io.observe(el);
});
```

### Ví dụ markup: hero + zig-zag

```html
<section class="section">
  <div class="container section__intro">
    <h1>Phân tích dữ liệu bằng hội thoại tự nhiên</h1>
    <p class="lead">Mô tả ngắn 1–2 câu về giá trị chính của sản phẩm, viết cho người không chuyên kỹ thuật.</p>
    <div class="hero__cta"><a class="btn btn--primary" href="#demo">Đặt lịch demo</a></div>
    <div class="mockup reveal">
      <img src="app-screenshot.png" alt="Khung chat AI đang lập kế hoạch phân tích doanh thu">
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="container zigzag zigzag--reverse">
    <div class="reveal">
      <h2>Cá nhân hóa theo từng doanh nghiệp</h2>
      <p class="lead lead--left">Nội dung mô tả tính năng.</p>
    </div>
    <div class="card reveal">Stat card / UI fragment</div>
  </div>
</section>
```

## Checklist triển khai & nghiệm thu

Một trang đạt chuẩn phong cách khi qua hết 14 mục dưới đây.

### Thiết kế

- [ ] Chỉ có 1 màu primary; màu phụ chỉ xuất hiện trong chart và progress
- [ ] Mỗi màn hình có tối đa 1 nút primary nổi bật
- [ ] Mọi màu, radius, shadow, khoảng cách đều lấy từ token, không có giá trị lẻ
- [ ] Nền section xen kẽ trắng / xám nhạt, không dùng đường kẻ ngang
- [ ] Icon soft 3D cùng góc nhìn, cùng bảng màu, cùng mức chi tiết
- [ ] Minh họa dùng ảnh chụp app hoặc mảnh UI, không dùng ảnh stock

### Kỹ thuật

- [ ] Poppins và Inter tải đúng, dấu tiếng Việt không bị cắt ở heading
- [ ] Không có cuộn ngang ở 360px, 390px, 768px, 1280px
- [ ] Ảnh xuất 2x, định dạng WebP/AVIF, ảnh dưới màn hình đầu dùng `loading="lazy"`
- [ ] Animation chỉ dùng `transform` / `opacity`; có xử lý `prefers-reduced-motion`

### Accessibility

- [ ] Mọi cặp chữ/nền đạt ≥ 4.5:1 (chữ lớn ≥ 3:1)
- [ ] Dùng được toàn bộ trang chỉ bằng bàn phím, focus ring luôn thấy rõ
- [ ] Ảnh có alt đúng (ảnh nội dung có mô tả, ảnh trang trí `alt=""`)
- [ ] Cấu trúc heading đúng: 1 H1, mỗi section 1 H2, `lang` đúng ngôn ngữ
