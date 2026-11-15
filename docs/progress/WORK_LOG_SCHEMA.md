# Task Activity Ledger — append-only human-readable entries

Each `docs/progress/tasks/EDU-XXXX.md` owns its full history; `TASK_BOARD.md` is generated, not edited manually. This minimizes conflicts between agents. One new activity row **per meaningful action**:

| recorded_at ISO 8601 + offset | task_id | actor/role | phase | action | changed_paths | before → after | tests/evidence | branch | commit SHA | push remote/SHA | PR URL | merge SHA | blockers/bugs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Required state vocabulary: `not_done`, `not_verified`, `verified:<identifier>` for Git actions; a PR opened ≠ PR merged ≠ deployed. CI run success is not a local test result unless actual CI evidence available.

### Task transitions
`planned → in_progress → in_review → done` (or `blocked`), where `done` requires defined DoD; **phase accepted** additionally needs role/authority gate.

### Bug evidence
See `docs/quality/TEST_STRATEGY.md`: actual / expected, steps, isolated fixture, request_id, timestamps with offset, before/after, failing test and regressions.
