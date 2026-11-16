> **Phase 00 canonical:** `docs/phases/PHASE-00.md` (v2.2, IN_REVIEW). Do not maintain a second product baseline or open decisions file.


# EduOps 360 — Triển khai local đang review

React/TypeScript/Vite, FastAPI và PostgreSQL đã được triển khai local qua các task EDU-0007..0010. Trạng thái review và bằng chứng hiện tại nằm trong `docs/progress/HANDOFF.md`. Phase 00 giữ sổ quyết định chuẩn tại `docs/phases/PHASE-00.md`.

Tiến độ hiện tại: [PROJECT_STATUS](docs/progress/PROJECT_STATUS.md). IAM/Admin local
đã có; Phase 03–10 mới có các lát cắt đầu tiên, Phase 11 mới triển khai một phần.
Chưa có phase nào nghiệm thu chính thức hoặc production deployment được xác minh.
Các ghi chú starter ở cuối là lịch sử, không mô tả code/Git hiện tại.

Khởi chạy tại thư mục gốc với Docker Engine hoạt động và `infra/.env` có password local ngẫu nhiên theo `infra/.env.example`.

```powershell
docker compose --env-file infra/.env -f infra/compose.dev.yml up --build -d --wait
python scripts/smoke_local.py
```

Mở `http://127.0.0.1:5173`. Dừng bằng `docker compose --env-file infra/.env -f infra/compose.dev.yml down`. Volume local được giữ lại. Hướng dẫn chạy riêng từng phần và kiểm thử nằm tại `frontend/README.md`, `backend/README.md`, `infra/README.md` và `contracts/README.md`.

Service `migrate` tự chạy trước backend bằng role migrator. API dùng role runtime
và không được chạy Alembic. Lệnh kiểm tra migration thủ công nằm trong
[infra README](infra/README.md).

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

Generator từ chối ghi đè file đã có. Năm học trong lệnh là ví dụ dữ liệu giả lập. `python scripts/benchmark_startup.py` đo startup local và tự dừng các process do phép đo tạo.

---

## Prior starter notes — historical v1.2 package
# EduOps 360 — Unified AI Agent Starter v1.2

**Repository governance and CSV-import starter only** — not a runnable school management application and not connected to a production Git repository.

## Layout

- `frontend/` — React + TypeScript (scaffold only)
- `backend/` — Python + FastAPI (scaffold only)
- `ai-agent-sp/` — **single source of truth** for all coding agents
- `AGENTS.md`, `CLAUDE.md` — only tool-discovery entry points
- `docs/progress/` — task logs, handoff, incidents, generated board
- `docs/requirements/STUDENT_IMPORT.md` — CSV requirements and staged import workflow
- `samples/templates/students_import_template.csv` — synthetic CSV sample
- `scripts/validate_students_csv.py` — local **preflight** CSV structure check (not a database importer)
- `contracts/`, `infra/`, `tests/` — integration/operations scaffolding

## Verify this starter

```bash
python scripts/check_structure.py
python scripts/validate_students_csv.py samples/templates/students_import_template.csv
python scripts/sync_task_board.py
```

See `ai-agent-sp/README.md` and `docs/requirements/STUDENT_IMPORT.md` before implementing any data import.

## Git status

Files are prepared in this starter ZIP only. No claim of a Git commit, push, PR, merge or deployed system is made.


## Unicode/UTF-8 assurance (v1.2)

Canonical specification: `ai-agent-sp/standards/UNICODE_UTF8.md`.

```bash
python scripts/check_text_encoding.py
python -m unittest discover -s tests/encoding -p 'test_*.py'
```

The CSV sample intentionally includes the UTF-8 BOM for Windows Excel compatibility. Strict UTF-8 is required in source code and agent documentation. This is a governance prototype, not a production upload service.

**Hướng dẫn giải thích chi tiết bằng tiếng Việt:** `docs/ROADMAP_VI.md`.
