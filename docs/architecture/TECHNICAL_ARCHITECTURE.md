# Kiến trúc kỹ thuật EduOps 360 — v2.0

## 1. Principles
- Monorepo, `frontend/` and `backend/` split at repo root. **Feature-based frontend**; **modular-monolith backend** with domain-owned repositories and services.
- Contract-first API: FastAPI/Pydantic OpenAPI generated → TypeScript client; never manual duplicated transport models.
- DB PostgreSQL. File originals in private object storage; only metadata, hashes, references and indexes in DB.
- Async tasks via queue and dedicated workers: timetable CP-SAT, legal sync, export and ML. No solver running inside HTTP request.
- Default deny RBAC on backend; BFF not mandatory. For deployment, use HTTPS gateway and cookie session policy.

## 2. Structural map
```
eduops360/
  frontend/                       # TypeScript React Vite, PWA optional
    src/app/ src/features/ src/shared/ tests/
  backend/
    app/core/ app/common/ app/db/ app/modules/ app/jobs/
    migrations/ tests/
  contracts/                      # generated OpenAPI / version docs
  ai-agent-sp/                    # single knowledge base + skills + roles
  docs/phases/ docs/requirements/ docs/security/ docs/quality/
  docs/progress/tasks/ docs/operations/
  infra/ scripts/ samples/ tests/
  AGENTS.md CLAUDE.md README.md
```

## 3. Domain ownership
- `auth`: identities, sessions, roles, rights, scopes.
- `academic_years`: school years, terms, active-year transitions, date policies.
- `students`: immutable student identity, enrollment, class associations.
- `school_calendar`: holidays, slots and exceptional teaching days.
- `timetables`: schedule domain and CP-SAT input/constraint/solution validation, versioning.
- `examinations`: assessment entries, policy snapshots, approval, score-change audit.
- `legal_documents`: sources, originals, versions, effective relations, review.
- `analytics`: SQL aggregations and statistical export, scoped access.
- `machine_learning`: feature snapshots, temporal splits, trained models and monitoring.
- `audit_logs`: immutable evidence pipeline; business Admin never deletes audit artifacts.

## 4. Dependency direction
Frontend pages → feature hooks/API client → documented API → FastAPI routers → service → domain policies/repositories → DB. Cross-domain access via service interface or versioned event, never direct import of another module's ORM repository. Workers use domain services and restricted service identities.

## 5. Integrity & concurrency
- Writes involving grade or permissions: DB transaction + audit/outbox in same transaction, immutable export of log to segregated store.
- Updates use optimistic revision fields or DB concurrency constraints; stale updates return conflict (409).
- Timetable prevents interval overlap, not merely period number. School-year transitions preserve old versions and historical policy snapshots.

## 6. Encoding
Source/doc/script: UTF-8 without BOM. API JSON UTF-8. CSV imported with strict UTF-8/UTF-8 BOM; Excel CSV export BOM; NFC for normalized text; never coerce student code to numbers. See `ai-agent-sp/standards/UNICODE_UTF8.md`.

## 7. Visual design
Current local UI: Minimalist SaaS indigo tokens, light/dark, self-hosted Be Vietnam
Pro display and Inter body fonts. Style evidence: EDU-0044/0049 and
`docs/requirements/UI_STYLE_MINIMALIST_SAAS_2026-11-14.md`. Never embed an
unlicensed font file. Architecture sections above include planned components;
implemented scope is tracked in `docs/progress/PROJECT_STATUS.md`.

## 8. Deployment stages
Local fake-data Docker Compose → staging with synthetic identities and isolated secrets → production only after school/data-owner approval and recovery test. No production action by an AI agent unless explicitly authorized.
