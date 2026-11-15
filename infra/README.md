# Môi trường Docker local

Compose project `eduops360-local` gồm PostgreSQL, backend và frontend. Các cổng publish bind vào `127.0.0.1`. Chạy lệnh từ thư mục gốc `D:\eduops360` với Docker Engine đang hoạt động.

Tạo `infra/.env` từ mẫu khi file chưa có. Dùng ba mật khẩu URL-safe ngẫu nhiên và khác nhau cho migrator, API runtime và audit worker. File `.env` cũ chỉ có `POSTGRES_PASSWORD` phải được cập nhật trước khi chạy cấu hình mới; không ghi các giá trị này vào Git hoặc log.

```powershell
docker compose --env-file infra/.env -f infra/compose.dev.yml config --quiet
docker compose --env-file infra/.env -f infra/compose.dev.yml up --build -d --wait
python scripts/smoke_local.py
```

Service `migrate` chạy Alembic bằng `eduops_migrator` và phải hoàn tất trước khi API khởi động. API chỉ kết nối bằng `eduops_runtime`; audit delivery dùng `eduops_audit_worker` khi worker được triển khai. Runtime không được chạy Alembic, tạo schema, sửa/xóa/truncate `audit_logs` hay giao quyền cho chính nó.

```powershell
docker compose --env-file infra/.env -f infra/compose.dev.yml run --rm migrate python -m alembic current
docker compose --env-file infra/.env -f infra/compose.dev.yml run --rm migrate python -m alembic check
```

Frontend tại `http://127.0.0.1:5173`, API tại `http://127.0.0.1:8000/api/docs`, PostgreSQL local tại `127.0.0.1:55432`. Có thể đổi port qua `infra/.env`. Readiness kiểm tra kết nối DB thật; Compose chờ DB/API khỏe trước khi khởi chạy dịch vụ phụ thuộc.

```powershell
docker compose --env-file infra/.env -f infra/compose.dev.yml ps
docker compose --env-file infra/.env -f infra/compose.dev.yml logs --tail 50
docker compose --env-file infra/.env -f infra/compose.dev.yml down
```

`down` dừng/xóa container và network của project. Volume `eduops360-local_postgres-data` được giữ lại. Chỉ dùng `down -v` cho project/volume tổng hợp đã xác nhận là disposable. PostgreSQL 18 lưu dữ liệu tại `/var/lib/postgresql` trong named volume. Các login role được tạo khi volume khởi tạo lần đầu; đổi mật khẩu trong `.env` không tự đổi mật khẩu của volume cũ. Staging được thiết kế ở giai đoạn sau với cấu hình và dữ liệu giả lập riêng.

Để phát triển backend/frontend trực tiếp trên host, chạy riêng DB bằng `up -d db --wait`, đặt `backend/.env` theo mẫu rồi xem README từng phần.
