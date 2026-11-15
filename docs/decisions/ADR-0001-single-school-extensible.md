# ADR-0001 — One-school MVP with extensible school boundary

**Date:** 2026-11-12  
**Status:** Accepted as product requirement; technical mapping under review  
**Decision owner:** Product Owner

## Context
The initial product operates for one institution, supports Grades 1–12 and may expand to multiple schools later. Avoid premature multi-tenant SaaS complexity while preventing difficult future schema rewrites.

## Decision
Use a single-school application initially. Include `school_id` and scoped access where logically appropriate (`students`, `academic_years`, `classes`, `teachers`, user memberships and role grants); keep student codes unique *within a school*. Do not implement tenant billing, cross-school federation or multi-tenant UI in MVP. Validate cross-school isolation in synthetic tests even if only one school is active.

## Consequences
+ Easier initial UX and deployment, stronger path to partitioned data in future.
- Additional schema keys and access checks now.

## Verification
FK and unique constraints, `school_id` data leak tests, no frontend direct database access.
