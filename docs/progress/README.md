# Work tracking — 4 distinct artifacts

Current implementation/acceptance snapshot: [PROJECT_STATUS](PROJECT_STATUS.md).
Latest remediation: [EDU-0068](tasks/EDU-0068.md); residual audit:
[EDU-0067 report](../quality/RESIDUAL_BUG_AUDIT_2026-11-16.md).

1. `tasks/EDU-xxxx.md`: **source of truth per task**. Owner, branch, status, file list, before/after behavior, tests, issues, commit/push/merge evidence, activity timeline. Append/update in task branch.
2. `TASK_BOARD.md`: **generated summary table**, refreshed with `python scripts/sync_task_board.py` after merging tasks (or in a branch for review). Avoid concurrent manual edits to the board.
3. `HANDOFF.md`: short **current state for the next agent**. Link to active tasks and blockers.
4. `REVIEW_PACKAGE_2026-11-12.md`: read-only navigation package for the current human review. It links to canonical specifications, tasks and evidence; it does not own task status or acceptance.

`CHANGELOG.md` in repo root describes release-level user-visible changes; it is not a substitute for task history. Git/PR history is authoritative for commit, push and merge. Product audit logs belong in a secured database, **not** in this developer task register.

Statuses: `planned`, `in_progress`, `blocked`, `in_review`, `done`.
Git fields: `not_done`, `done` plus evidence hashes/URLs. Never write `done` without verifying.

Historical package integrity evidence is stored at `evidence/EDU-0021/`:
`docs-tree.sha256` describes that package, not today's changing docs tree.
EDU-0068 inventories 44 gitignored historical logs with original hashes and
numeric test summaries in `evidence/EDU-0068/historical-log-manifest.json`.
Raw originals remain local/ignored because they may contain credentials; this
manifest is a sanitized evidence index, not a full raw-log backup or independent
verification of the historical results. New logs must be sanitized before Git.
