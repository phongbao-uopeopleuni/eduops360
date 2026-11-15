# EduOps 360 — API Contract Planning v2.0

The following endpoints are **design proposals**, not deployed routes. Version prefix: `/api/v1`. Auth is cookie session + CSRF protection for browser clients; all resource routes verify role, school, year, assignment scope and workflow state.

| Phase | Method & route | Request concepts | Response/status & auth |
|---|---|---|---|
| 01 | GET `/health/ready` | None | 200/503, internal readiness checks |
| 02 | POST `/auth/login` | user credentials / MFA | 200 session cookie / 401 / 429; rate limits |
| 02 | GET `/auth/me` | Cookie | scoped principal, 200/401 |
| 02 | POST `/admin/users/{id}/grants` | permission+scope+expiry | 200/403/409, admin, audit |
| 03 | GET `/academic-years` | school scope | array and paging, 200/403 |
| 03 | POST `/academic-years/{id}/activate` | revision + reason | 200/403/409, only authorized admin |
| 03 | GET `/students` | year, class, pagination, search | 200/403, no cross-year/tenant leak |
| 04 | POST `/student-imports/preflight` | CSV upload, template version | batch_id + row diagnostics; 400/413/422 |
| 04 | POST `/student-imports/{id}/confirm` | mode, idempotency_key | summary, 202/400/403/409; audited |
| 04 | GET `/student-imports/{id}/errors` | batch id | safe CSV/XLSX, scoped auth |
| 05 | POST `/calendar/holidays` | date_from,to, scope, session, reason | preview or draft 201/422/403 |
| 05 | POST `/calendar/holidays/{id}/approve` | revision | affected lessons count + 200/409 |
| 05 | PUT `/time-slot-templates/{id}` | day+slot ranges, revision | collision diagnostics 200/409/422 |
| 06 | POST `/timetables/jobs` | snapshot version, objective, constraints | 202 job id, scoped permissions |
| 06 | GET `/timetables/jobs/{id}` | job id | status optimal/feasible/infeasible/unknown |
| 06 | POST `/timetables/{id}/publish` | revision, approval evidence | 200/409/403, audited |
| 07 | PUT `/grades/{id}` | score, revision, reason | 200/403/409/422, policy scoped and audited |
| 07 | POST `/grades/{id}/approve` | review note / revision | 200/403/409, logged |
| 08 | GET `/legal-documents` | search, as_of, state, issuer | 200 search results w provenance |
| 08 | POST `/legal-documents/{id}/review` | legal relationship decision | 200/403/409, reviewer audited |
| 09 | POST `/analytics/query` | subject, school_year, graph spec | typed aggregate and count /403/422 |
| 10 | GET `/ml/predictions` | approved model, as_of, scope | verified human-support output or denied |
| 11 | GET `/admin/audit-events` | time range, actor, action | scoped, redacted, append-only view |

## Error envelope
```json
{"error":{"code":"RESOURCE_CONFLICT","message":"Dữ liệu đã thay đổi; tải lại để đối chiếu.","request_id":"synthetic-req-01","details":[]}}
```
Use stable machine codes and human-readable localized messages. Do not leak PII or stack traces in API response. Error contracts must be versioned and tested.

## Contract synchronization process
1. Modify authoritative Pydantic schemas/router; update backend contract tests.
2. Generate OpenAPI JSON and TypeScript client using pinned tool version.
3. CI asserts generated artifacts match source and no unapproved breaking changes exist.
4. Frontend validates representative API fixtures and error states.
5. Release migration and API changes with compatibility window when multiple clients exist.
