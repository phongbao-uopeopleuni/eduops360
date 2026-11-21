> **Phase 00 canonical:** `docs/phases/PHASE-00.md` (v2.2, IN_REVIEW). Do not maintain a second product baseline or open decisions file.


# EduOps 360 — Hệ thống quản trị học vụ local

React/TypeScript/Vite, FastAPI và PostgreSQL đã được triển khai local qua các task EDU-0007..0010. Trạng thái review và bằng chứng hiện tại nằm trong `docs/progress/HANDOFF.md`. Phase 00 giữ sổ quyết định chuẩn tại `docs/phases/PHASE-00.md`.

Khởi chạy tại thư mục gốc với Docker Engine hoạt động và `infra/.env` có password local ngẫu nhiên theo `infra/.env.example`.

```powershell
docker compose --env-file infra/.env -f infra/compose.dev.yml up --build -d --wait
docker compose --env-file infra/.env -f infra/compose.dev.yml exec -T backend python -m alembic upgrade head
python scripts/smoke_local.py
```

Mở `http://127.0.0.1:5173`. Dừng bằng `docker compose --env-file infra/.env -f infra/compose.dev.yml down`. Volume local được giữ lại. Hướng dẫn chạy riêng từng phần và kiểm thử nằm tại `frontend/README.md`, `backend/README.md`, `infra/README.md` và `contracts/README.md`.

## Read in this order
1. `docs/phases/PHASE-00.md` (**single authoritative Phase 00 file; decisions, open items, steps, exit gates**)
2. `docs/requirements/SRS_MASTER.md` (detailed cross-phase functional requirements)
3. `docs/roles/README.md` (authority)
4. `ai-agent-sp/skills/REGISTRY.md` (7 skill groups)
5. `docs/quality/TEST_STRATEGY.md` and `docs/progress/HANDOFF.md` (verification/handoff)

## Validate locally (Python 3.11+ stdlib)
```bash
python scripts/validate_blueprint.py
python scripts/check_structure.py
python scripts/check_text_encoding.py
python -m unittest discover -s tests -p 'test_*.py'
python scripts/sync_task_board.py
```

Sinh fixture kỹ thuật tại `.local/` với năm học được chỉ định cho lần thử nghiệm.

```powershell
python scripts/generate_synthetic_students.py .local/synthetic/students.csv --count 2000 --seed 360 --academic-year 2026-2027
```

Generator từ chối ghi đè file đã có. `python scripts/benchmark_startup.py` đo startup local và tự dừng các process do phép đo tạo.

## Import dữ liệu trường/ngành học mẫu

File [backend/school_academic_2000_import.sql](backend/school_academic_2000_import.sql) chứa
1 năm học, 72 lớp, 2.000 học sinh và 2.000 ghi danh từ SQLite-style SQL. Script sau ánh xạ
đúng các thực thể đang có trong PostgreSQL EduOps và chạy idempotent:

```powershell
$env:EDUOPS_DATABASE_URL = "postgresql+psycopg://eduops_runtime:<mật-khẩu>@127.0.0.1:<cổng>/eduops360"
python scripts/import_school_academic_sql.py --sql-file backend/school_academic_2000_import.sql
```

Script cập nhật school, year, class, student, enrollment, subject, teacher,
grade-subject, teaching assignment, assessment và attendance theo mã. Các bảng dữ liệu
này được migration `0016_full_academic_seed` quản lý. Chỉ dùng dữ liệu tổng hợp trong
môi trường local/isolated.

Tạo tài khoản quản trị local với migrator DSN và mật khẩu truyền qua biến môi trường:

```powershell
$env:EDUOPS_TEST_MIGRATOR_DSN = "postgresql://eduops_migrator:<mật-khẩu>@127.0.0.1:<cổng>/eduops360"
$env:EDUOPS_LOCAL_ADMIN_PASSWORD = "<mật-khẩu-local-mạnh>"
python scripts/seed_local_school_admin.py
```
