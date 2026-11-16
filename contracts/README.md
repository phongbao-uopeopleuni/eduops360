# Hợp đồng API

FastAPI/Pydantic là nguồn sinh schema. `openapi.json` và types frontend được lưu cùng code để kiểm tra drift trước review.

Từ thư mục gốc, xuất schema rồi sinh types.

```powershell
backend/.venv/Scripts/python scripts/export_openapi.py
npm run api:generate --prefix frontend
```

Kiểm tra tính đồng bộ.

```powershell
backend/.venv/Scripts/python scripts/export_openapi.py --check
npm run api:check --prefix frontend
```

Phase 01 gồm GET `/api/v1/health/live` và `/api/v1/health/ready`, với readiness 200/503. Hợp đồng lỗi chứa mã, thông báo và request ID. Các API nghiệp vụ được bổ sung theo phase sở hữu và kiểm thử phạm vi dữ liệu tương ứng.

Schema hiện tại cũng có `/api/v1/auth/*`, `/api/v1/admin/roles` và
`/api/v1/admin/users/*` cho IAM/Admin local. Danh sách method/path chính xác nằm
trong `openapi.json`; `docs/architecture/API_CONTRACT_PLAN.md` là đề xuất cho các
phase, không phải danh sách endpoint đã triển khai. Chưa có API học sinh, import,
calendar, solver, gradebook, legal, analytics hoặc ML.
