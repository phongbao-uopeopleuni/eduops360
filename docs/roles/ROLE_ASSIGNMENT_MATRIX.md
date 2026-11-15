# Suggested assignment and task allocation (not people or AI brand bound)

| Phase | Implementer roles | Independent verification | Human approval |
|---|---|---|---|
| 00 | Architecture Lead, BA | QA / Architecture reviewer | Product Owner |
| 01 | Frontend + Backend | QA + Architecture Lead | Tech Lead |
| 02 | Security + Backend | QA + Security reviewer | Security Owner |
| 03 | Database + Backend | QA + Data owner | Academic admin |
| 04 | Import/Data + Backend | QA + Security | Academic admin |
| 05 | Calendar/UX + Backend | QA + Domain SME | Training officer |
| 06 | Solver + Backend | QA + Domain SME | Training officer |
| 07 | Examination + Backend | Independent test + Legal | Examination authority |
| 08 | Legal Data + Backend | Legal/domain independent reviewer | Authorized policy reviewer |
| 09 | Analytics + Frontend | Statistical QA + Privacy | Data owner |
| 10 | ML + Domain SME | ML evaluation + Security | Human Data Owner |
| 11 | DevOps + Security | QA + Product Owner | Human Operations Owner |

One model instance can fill several roles across tasks, but critical author and reviewer roles must be independently verified. Brand names Claude/Codex do not confer additional system permissions.

## Phase 00 approvals and RACI detail (v2.1)

| Decision/artefact | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
|---|---|---|---|---|
| Confirm eight business decisions | BA | Human Product Owner | Architecture Lead | QA, dev agents |
| Single school scope and academic data boundaries | Architecture Lead/DBA | Architecture Lead | Academic SME, Security | BA, Frontend |
| Student import and duplicate policy | Data/Backend Agent | Academic Data Owner | QA, School registrar | Product Owner |
| Two-step sensitive workflow | Backend/Security Agent | Human Security/Examination Authority | Product Owner, QA | User roles |
| Phase 00 governance review | Independent Governance Reviewer | Human Product Owner | BA, Architecture Lead | All agents |
| Git main merge after required checks | Assigned maintainer | Repository owner | Code reviewer, QA | Product Owner |

**Open:** the individuals holding human approval/merge roles have not yet been designated. No AI brand (Claude, Codex, etc.) has independent authorization to self-merge or to approve school regulations.
