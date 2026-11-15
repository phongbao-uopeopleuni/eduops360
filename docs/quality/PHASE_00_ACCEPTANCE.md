# Phase 00 — Acceptance Evidence Checklist v2.2

> Current status: DOCUMENTED / REVIEW REQUIRED. A checked output is documentary evidence only, not human acceptance or implemented features.

| Gate | Requirement | Evidence | Current result |
|---|---|---|---|
| P00-G01 | All eight product decisions recorded without reinterpretation | `docs/phases/PHASE-00.md` | Documented; review pending |
| P00-G02 | MVP scope, non-goals and phase dependencies explicit | Product baseline, ADR-0002, `PHASE-00.md` | Documented; review pending |
| P00-G03 | Open decisions prioritized, phase gate and owner identified | `docs/phases/PHASE-00.md` | Documented; unresolved |
| P00-G04 | Roles and independent review authority named | `docs/roles/ROLE_ASSIGNMENT_MATRIX.md`, OD-001 | **Blocked until human assignments** |
| P00-G05 | Single canonical agent SOP, no contradictory vendor rules | `ai-agent-sp/`, root adapters | Verify via reviewer |
| P00-G06 | Requirement ID ↔ phase ↔ test/evidence mapping updated | `SRS_MASTER.md`, `TRACEABILITY_MATRIX.md` | Documented; tests not implemented |
| P00-G07 | UTF-8/CSV/governance validation passes in captured environment | Local commands + EDU-0005 activity record | v2.1 historic run: 11 tests / 132 files; v2.2 local run: 13 tests / 131 files; independent CI/review pending |
| P00-G08 | Branch/PR rules and remote Git repository known | OD-003, GIT_WORKFLOW | **Blocked until repository/maintainer** |
| P00-G09 | No unverified commit/push/merge or app claims | `EDU-0005.md`, `EDU-0006.md`, TASK_BOARD | Not performed |
| P00-G10 | Product Owner + independent reviewer approve Phase 00 | Signed approval entry in task | **Not approved** |

## Acceptance proof template
- Reviewer: ________; date/time with offset: ________
- Reviewed commit SHA: ________; CI run ID: ________
- Critical unknowns accepted/deferred with owner: ________
- Decision: `ACCEPTED` / `REJECTED` / `CONDITIONAL`; evidence URL/path: ________

## Allowed transition
The specification package can be distributed for review now. Start Phase 01 only after approval of Phase 00 governance, with any deferred questions recorded and no real student data.
