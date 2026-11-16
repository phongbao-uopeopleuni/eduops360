# Backend EduOps 360

FastAPI modular monolith, Python 3.13. Health, IAM/session/RBAC, audit và Admin API
đã có local. Academic-year/calendar/timetable/analytics mới có các domain slice,
chưa có API nghiệp vụ tương ứng. Xem [tiến độ](../docs/progress/PROJECT_STATUS.md).

Chạy từ `backend/` trong PowerShell sau khi có PostgreSQL local và `.env` cấu hình theo `.env.example`.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.lock
.venv/Scripts/python -m pip install --no-deps -e .
.venv/Scripts/python -m app
```

Entry point `python -m app` chọn SelectorEventLoop trên Windows để psycopg async hoạt động. `--host` mặc định `127.0.0.1`, `--port` mặc định `8000`. Dừng bằng Ctrl+C.

- Liveness tại `http://127.0.0.1:8000/api/v1/health/live` trả 200 khi API hoạt động.
- Readiness tại `/api/v1/health/ready` trả 200 khi PostgreSQL kết nối được, 503 khi cấu hình hoặc kết nối chưa sẵn sàng.
- Swagger tại `/api/docs`, OpenAPI tại `/api/openapi.json`.

Alembic baseline `0001_foundation` tạo bảng quản lý revision. Schema học vụ thuộc Phase 03. Chạy với database local giả lập đã được cấu hình.

Migration chain hiện kết thúc ở `0008_mfa_replay_counter`; baseline `0001` không
phải head hiện tại. Dùng role migrator riêng cho các lệnh Alembic bên dưới.

```powershell
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m alembic current
.venv/Scripts/python -m alembic check
.venv/Scripts/python -m pytest tests -q
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format --check .
```

`requirements.lock` khóa dependencies phát triển và công cụ kiểm thử; `requirements.runtime.lock` là tập con dùng trong image runtime. `pyproject.toml` khai báo dependencies trực tiếp. Hai lock hiện khóa phiên bản nhưng chưa có hash; bổ sung hash cần một lượt tạo lock có truy cập package index được phê duyệt. Khi thay dependencies, cài trong môi trường sạch, xuất lại cả hai lock và kiểm tra Windows/Linux.

Ứng dụng host có thể nạp secrets từ biến `EDUOPS_` hoặc `.env` local bị ignore. Riêng Alembic chỉ nhận `EDUOPS_DATABASE_URL` được truyền rõ trong process hiện tại và phải dùng role `eduops_migrator`; nó không đọc fallback từ `backend/.env`. Không dùng URL migrator để chạy API.
