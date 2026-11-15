# AI Agent Collaboration — roles and concurrent work

## One canonical source
`ai-agent-sp/` owns skill and operating instructions; `docs/roles/` owns roles; `docs/phases/` owns phased plan. Root AGENTS.md and CLAUDE.md only route to the source. Never sync copied text between vendor-specific skill directories.

## Concurrent changes
- A single task has one primary implementer. Separate branches/worktrees for parallel tasks.
- Concurrency-safe examples: frontend UI for CSV import and backend solver benchmarks **only if API contract is frozen**, or writing tests unrelated to DB migrations.
- Reserved shared files (needs change coordination): `contracts/`, backend migrations, root package/config/CI, `ai-agent-sp/`, global theme tokens, auth session policy.
- Cross-module change rule: owner proposes contract first; architecture lead reviews; both consumer/producer update and test in one PR or coordinated sequenced PRs.

## Role/approval gates
- No AI-only sign-off on legal effect, official grade policy, release to real students, or incident destruction/restore.
- Independent QA/security reviewer should not be same unreviewed actor for critical task.

## Skill activation
Read only selected skill SKILL.md; skills may stack: plan → implement → test → review → monitor/release. Do not assume skills auto-loaded from arbitrary `ai-agent-sp/` directory.
