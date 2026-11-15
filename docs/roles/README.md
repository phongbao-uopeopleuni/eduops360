# Roles, review authority and approval chain

Roles describe responsibilities, not distinct AI models or accounts. One Claude/Codex agent may be assigned one role per task. An **independent review role** should verify high-risk changes. Technical agents propose and verify; designated humans approve business policy, real-data access, production deployment, and irreversible operations.

RACI: **A** accountable (decision), **R** responsible (implementation), **C** consulted, **I** informed. A never equals an autonomous Agent for official grades or legal policies.

| Work type | Accountable | Responsible | Consulted |
|---|---|---|---|
| Domain/requirements | Human Product Owner | Business Analyst | Education SME |
| UI/UX | Tech Lead | Frontend Agent | Domain SME, QA |
| Backend/API | Tech Lead | Backend Agent | Security, DB |
| Data migration | Human Tech Lead / Data Owner | Database Agent | QA, Security |
| Scheduling | Domain SME | Solver Agent | QA, Backend |
| Grading policy | School Examination Authority | Examination Agent | Legal Researcher, QA |
| Legal relation/effective policy | Education Legal Authority | Legal Data Agent | Examination SME |
| ML deployment | Human Data Owner | ML Agent | QA, Security, Domain SME |
| Security | Human Security Owner | Security Agent | Tech Lead |
| Production release | Human Operations Owner | DevOps Agent | QA, Security, Product Owner |

All task journals must record the concrete assigned reviewer and approver, not just role names.
