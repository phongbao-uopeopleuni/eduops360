# Frontend EduOps 360

React + TypeScript + Vite, giao diện tiếng Việt với Source Sans 3 tự phục vụ từ package font có license đi kèm. Node 24.12.0 là phiên bản đã dùng kiểm thử local.

Chạy tại `frontend/`.

```powershell
npm ci
npm run dev
```

Mở `http://127.0.0.1:5173`. Vite chuyển `/api` đến `http://127.0.0.1:8000`. Biến `API_PROXY_TARGET` có thể đổi địa chỉ backend cho dev server. Dừng bằng Ctrl+C.

Trang tổng quan, trạng thái hệ thống và 404 thuộc Phase 01. Các trạng thái loading, mất mạng, PostgreSQL chưa sẵn sàng và thử lại được hiển thị từ kết quả API. Lựa chọn giao diện theo hệ thống/sáng/tối được lưu local khi trình duyệt cho phép.

```powershell
npm run api:generate
npm run api:check
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build
```

Types tại `src/shared/api/generated/schema.d.ts` được sinh từ `contracts/openapi.json`. Client sử dụng `openapi-fetch`; cập nhật schema tại backend trước khi sinh lại.

Audit EDU-0011 khóa override `minimatch@>=7 <11.0.1` sang 11.0.8 để xử lý GHSA-g3hv-75wg-m249 trong dependencies của ESLint/typescript-eslint. Các lệnh lint/typecheck/test/build và cài đặt từ lockfile được kiểm tra sau thay đổi này. Xem [advisory của minimatch](https://github.com/advisories/GHSA-g3hv-75wg-m249).

E2E dùng Chromium đầy đủ và lưu ảnh sáng/tối/mobile, JSON kết quả và trace khi lỗi vào `test-results/`. Chạy từ `frontend/` trong PowerShell.

Chuẩn bị PostgreSQL bằng Compose và `backend/.env` theo hướng dẫn backend trước khi chạy E2E tự quản lý server. Bài kiểm thử đường đi thành công yêu cầu kết nối database thật trong môi trường local giả lập.

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = 'D:\eduops360\.local\browsers'
npx playwright install --no-shell chromium
npm run test:e2e
```

Playwright tự chạy và dừng server khi cần. Để dùng stack Compose đã chạy, đặt `$env:PLAYWRIGHT_EXTERNAL_SERVER = '1'`. `npm run build` tạo lại `dist/`. `npm run preview` phục vụ bundle để xem giao diện; chạy kiểm tra API qua dev server hoặc Compose có proxy.
