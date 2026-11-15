# Development Phases

Each document is a **planned implementation specification**, not a report of completed code. Each phase contains explicit dependency, task steps, technical artifacts, tests and exit gate. Change scope only via a tracked task + ADR.

| Phase | Scope | Implementation owner(s) | Reviewer |
| --- | --- | --- | --- |
| PHASE-00 | Governance, requirements & agent harness | Architecture Lead / BA | Governance Reviewer |
| PHASE-01 | App foundations, shared design & API contracts | Tech Lead / Frontend Agent / Backend Agent | QA Agent |
| PHASE-02 | IAM, security baseline, audit & roles | Security Agent / Backend Agent | Human Security Owner |
| PHASE-03 | Academic year, master data & school hierarchy | Backend Domain Agent / Database Agent | Domain SME / QA |
| PHASE-04 | Student bulk import/export & Unicode | Data Engineer / Backend Agent | QA Agent / Security Agent |
| PHASE-05 | Calendar, time slots, holidays & temporal integrity | Backend Agent / UX Agent | Domain SME / QA |
| PHASE-06 | Automatic scheduling with CP-SAT and local repair | Solver Agent / Backend Agent | Domain SME / Performance QA |
| PHASE-07 | Grade 1–12 examination rules & integrity | Examination Domain Agent / Backend Agent | Domain SME / Security QA |
| PHASE-08 | Legal documents sync, provenance & temporal search | Legal Data Agent / Backend Agent | Education Domain SME / Security QA |
| PHASE-09 | Statistical Analytics Studio | Data Analytics Agent / Frontend Agent | QA / Examination SME |
| PHASE-10 | Educational ML lab and careful predictive use | ML Agent / Domain SME | Independent ML QA / Security |
| PHASE-11 | Operations, security hardening, performance & release | DevOps Agent / Security Agent / QA Lead | Human Product Owner + Operations Owner |

**Hướng dẫn giải thích chi tiết bằng tiếng Việt:** `../ROADMAP_VI.md`.
