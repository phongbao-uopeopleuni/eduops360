# Module ownership map

| Domain | Frontend feature | Backend module | Notes |
|---|---|---|---|
| Authentication/RBAC | `features/auth/` | `modules/auth/` | Server-side authorization |
| Academic years | `features/academic-years/` | `modules/academic_years/` | Date/time governance |
| Students/classes | `features/students/`, `features/classes/` | `modules/students/`, `modules/classes/` | Scoped records |
| Examination | `features/examinations/` | `modules/examinations/` | Deterministic policy rules |
| Timetable | `features/timetables/` | `modules/timetables/` | Solver workers, conflict checks |
| Holidays/calendar | `features/school-calendar/` | `modules/school_calendar/` | Canonical source for closed slots |
| Legal archive | `features/legal-documents/` | `modules/legal_documents/` | Official sources, history |
| Analytics/ML | `features/analytics/` | `modules/analytics/` | Human-reviewed predictions |
| Auditing | `features/audit-logs/` | `modules/audit_logs/` | Immutable event record |

Only create a directory when implementing that slice. Avoid empty/duplicated modules.
Cross-module API schema changes must update `contracts/` and regenerate clients.
