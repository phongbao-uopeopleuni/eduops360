# ADR-0002 — Incremental MVP delivery order

**Date:** 2026-11-12  
**Status:** Accepted as product requirement  
**Decision owner:** Product Owner

## Decision
1. Foundations Phase 01 and minimum secure RBAC/audit Phase 02.
2. **MVP-A:** Student master + academic year + CSV import (Phases 03–04).
3. **MVP-B:** School Calendar / Timeslots + Timetable solving (Phases 05–06).
4. **MVP-C:** Assessment/Examination 1–12 (Phase 07).
5. Legal document automation, Statistical Analytics and ML are subsequent increments (Phases 08–10).
6. Security, monitoring, disaster recovery and release gate checks (Phase 11) must be applied before any outside-staging or production use; they are cross-cutting controls, not deferred protection.

## Consequences
One feature slice reaches a testable state before the next. No promise that deferred features are in MVP.
