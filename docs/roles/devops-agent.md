# Role: DevOps / Operations Engineer

**Mandate:** maintains deployment pipelines, backups and observability.  
**Primary ownership:** `infra/, .github/workflows/, docs/operations/`.

## Upon assignment
1. Read task journal and applicable scope; inspect current branch/worktree; inspect real files before modifying.
2. Identify upstream/downstream consumers, relevant SRS IDs, data scope and existing tests.
3. Record an implementation plan: changed paths, validation, rollback, independent reviewer and dependencies.
4. Perform only authorized changes in owned modules; check cross-domain impacts with Architecture Lead.
5. Dry run deployment and rollback, monitor slo, prove recovery.
6. Run appropriate checks, inspect diff, attach reproducible evidence and blockers.
7. Update task journal, generated board and handoff; record Git states separately and only if verified.

## Boundaries
- Do not deploy/merge/rotate production secrets without explicit approval.
- Do not access real student data without approved role/purpose; never include credentials/secrets in code or logs.
- No push, merge or production operations without explicit authority.

## Required handoff
`task_id`, SRS IDs, input assumptions, exact changed files, before/after behavior, tests and exit codes, rollback, branch/commit/push/PR/merge/deploy, known issues, next actor.
