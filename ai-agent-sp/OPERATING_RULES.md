# Operating Rules — Canonical v2.1

## Minimum read set
1. Read project context, confirmed `docs/phases/PHASE-00.md`, open decisions, assigned `EDU-XXXX` journal, current Git status and branch.
2. Read only the relevant phase, role card, skill(s) and standards for this task; do not load all repo documentation by default.
3. Record file ownership, SRS IDs, conflicts, approval requirements and test plan before editing.

## One source of truth
- Business SRS: `docs/requirements/SRS_MASTER.md`; phases: `docs/phases/`; technical architecture: `docs/architecture/`.
- Skills: `ai-agent-sp/skills/`; role cards: `docs/roles/`; progress: per-task `docs/progress/tasks/EDU-XXXX.md`.
- `AGENTS.md` and `CLAUDE.md` are thin adapters and may not redefine architecture, security controls or tasks.
- Do not convert proposed default values in OPEN_DECISIONS into confirmed requirements. One task one branch/worktree and a clear file owner. Cross-boundary changes (frontend+backend/contracts/db migrations) require coordination and review.

## Risk handling
- Deny by default for all sensitive API requests; real students prohibited in demo; avoid secrets and personal details in Git/logs.
- Changes to grades, rights, student imports, legal rules and time/calendar require audit, policy scope tests and independent review.
- Preserve strict UTF-8 NFC policy and never mutate original legal document bytes.
- No unapproved force-push, merge, migration, credential update, production deployment or real-student export.

## Finish
1. Run exact relevant tests, report pass/fail/untested with commands and error output snippets.
2. Inspect diffs and identify all changed files, interface impacts and rollback.
3. Update task frontmatter and activity row with timezone-aware time and factual Git states (commit/push/PR/merge/deploy separately).
4. Regenerate board. Update handoff with blocking issues and next actor.
5. Do not mark a phase accepted without evidence and appropriate human approval.
