# Git Workflow & Multi-Agent Coordination

## Normal workflow
1. Assign task ID and named scope. Use branches `feat/EDU-xxxx-topic`, `fix/EDU-xxxx-topic`, etc.
2. Inspect `git status`, `git branch --show-current`, `git log -5 --oneline`.
3. For parallel work, use different `git worktree` directories/branches.
4. Modify only owned files. Do not commit generated artifacts or unrelated diffs accidentally.
5. Run checks; update the task journal with exact commands and results.
6. If authorized: stage selected paths; `git commit` with task ID, verify SHA.
7. If authorized: `git push -u origin <branch>`, verify remote ref.
8. Open PR and review CI/diff; if authorized merge via protected main; verify merge commit or PR state.
9. Record commit/push/merge separately. Update `HANDOFF.md`.

## Sample commands (only if authorized; do not run blindly)
```
git status --short
git branch --show-current
git worktree add ../eduops360-codex -b feat/EDU-0002-timetable
git worktree add ../eduops360-claude -b feat/EDU-0003-audit
git diff --check
git log -5 --oneline
```

Use branch protection with PR review and required checks where available. Worktrees share Git object history but have separate working directories; shared files can still conflict during merge. Agent instructions are guidance, not a filesystem permission boundary.
