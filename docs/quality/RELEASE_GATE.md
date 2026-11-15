# Release Gate and Definition of Done

Before a phase may be marked `accepted`:
1. SRS requirement IDs mapped to commits/PR/tests and reviewed by domain owner.
2. Frontend/backend/API contract aligned and generated client types updated.
3. No unresolved P0/P1; other known issues documented with impact and owner.
4. RBAC and scope tests for new endpoints; CIA review as applicable.
5. utf8/locale/date/regression checks when strings/time are affected.
6. Real commands/test results recorded with exit code, environment, commit; no invented pass.
7. Audit events include actor/time/change where required.
8. DBA review of migrations and rollback; backup/restore when schema/data operations affect production.
9. Owner reviews proposed PR, CI has green evidence. `commit`, `push`, `PR`, `merge`, `deploy` recorded as distinct statuses.
10. Human Product Owner or designated school authority signs off high-impact domain changes and releases.

The original starter contains specification materials. Current implementation and acceptance evidence is tracked in task journals and `docs/progress/HANDOFF.md`. Source checks form part of the phase verification.
