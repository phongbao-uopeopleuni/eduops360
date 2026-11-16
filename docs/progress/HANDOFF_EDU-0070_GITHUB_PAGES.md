# EDU-0070 — GitHub Pages Deployment Handoff

**Audience:** Desktop Codex working in `D:\\eduops360`  
**Recorded:** 2026-11-16 (Asia/Ho_Chi_Minh)  
**Task:** EDU-0070 — Publish a backend-free EduOps 360 UI preview on GitHub Pages  
**Status:** Public UI preview deployed successfully; PR integration into `main` remains unmerged.

## 1. Executive result

The EduOps 360 frontend is published at:

`https://phongbao-uopeopleuni.github.io/eduops360/`

The user opened the URL in their browser and confirmed that the page loads.

Deployment evidence:

- GitHub Actions workflow run: [#31 — run 43863545271](https://github.com/phongbao-uopeopleuni/eduops360/actions/runs/43863545271)
- Attempt: **2**
- Deployed application commit: `851f9983886d2e21d0e56f6c1545a292d95dc54c`
- Run conclusion: **success**
- Build job: **success**
- Deploy job: **success**
- Deploy log explicitly reported `Reported success!` and resolved the environment URL to the Pages URL above.
- The user subsequently confirmed that the public page opens.

The Playwright tests ran against the built static preview served on loopback in GitHub Actions. They did not run against the public URL. The user's browser confirmation is the available public-site smoke-test evidence.

## 2. Why deployment used a feature branch

The repository is maintained by one person. The protected `main` branch requires an independent approving review, including approval from someone other than the last pusher. There is no second collaborator available.

The deployment was therefore enabled from the explicitly trusted task branch rather than bypassing repository governance:

- Deployment branch: `codex/edu-0070-github-pages`
- Integration branch: `main`
- PR #14 remains open and unmerged: [feat(deploy): publish backend-free UI preview on GitHub Pages](https://github.com/phongbao-uopeopleuni/eduops360/pull/14)
- PR #14 head at deployment: `851f9983886d2e21d0e56f6c1545a292d95dc54c`
- PR #14 base: `main`
- `main` SHA at verification: `c622467377980c2ff7a3bc0b80714d11f5d17007`
- PR #13 (the earlier duplicate HashRouter-only PR) is **closed, not merged**.

No self-approval, fabricated approval, admin bypass, force-push, default-branch change, branch-protection weakening, or merge of the unrelated stacked PR chain was used. The Pages site is live independently of PR #14 being merged.

## 3. GitHub repository settings

The repository owner configured:

1. **Settings → Pages → Build and deployment → Source:** `GitHub Actions`.
2. **Settings → Environments → github-pages → Deployment branches and tags:**
   - Mode: `Selected branches and tags`
   - Allowed branch: `codex/edu-0070-github-pages`
   - Allowed branch: `main`

The owner shared a screenshot showing **2 branches and 0 tags allowed** and the saved-environment confirmation.

The screenshot also showed:
- `Required reviewers`: unchecked.
- `Wait timer`: unchecked.
- `Allow administrators to bypass configured protection rules`: checked.
- No environment secrets or variables configured.

Do not broaden the branch allowlist to `No restriction`. The environment allowlist is separate from `main` branch protection.

## 4. Implementation details

### Vite base path

File: `frontend/vite.config.ts`

- With `VITE_GITHUB_PAGES=true`: `base: '/eduops360/'`.
- Without the flag: `base: '/'`.

This preserves root-path asset loading for local development and Railway.

### Router selection

File: `frontend/src/main.tsx`

- Pages build: `HashRouter`.
- Local/Railway build: `BrowserRouter`.

Pages route URLs use hashes (for example, `/#/system`), so reloading a nested route does not depend on a server-side SPA rewrite.

### Safe static-preview behavior

Files:
- `frontend/src/app/App.tsx`
- `frontend/src/app/styles.css`

When `VITE_GITHUB_PAGES=true`:
- A visible Vietnamese notice states that this is a public UI preview, the backend is not connected, and users must not enter login information or real data.
- The System page shows an unavailable state instead of reporting backend/service health.
- The Users page shows an unavailable state instead of rendering the API-backed user-management feature.
- The preview does not expose a login form or submit administrative mutations.

The preview is static UI only. It is not an authenticated application and is not evidence that backend, database, or business workflows are operational.

### Pages-specific browser tests

File: `frontend/tests/e2e/github-pages.spec.ts`

Two Playwright tests cover:
- Overview page and backend-not-connected notice.
- Hash navigation to System and Users.
- Reload of nested hash routes.
- Unknown route and return-to-overview link.
- No `/api/` requests during the tested preview navigation.
- No input fields on the Users preview route.
- Mobile viewport width (390 px) without horizontal overflow.
- Self-hosted Be Vietnam Pro and Inter font loading.
- Repository-prefixed static assets under `/eduops360/assets/`.
- No failed asset requests in the static-preview test.

The Pages-specific tests do not replace a separate manual check of light/dark theme behavior at the public URL.

## 5. GitHub Actions workflow

File: `.github/workflows/github-pages.yml`

### Triggers

- `pull_request` targeting `main`: validation only; no Pages artifact upload or deployment.
- `push` to `main` or `codex/edu-0070-github-pages`: build and deploy.
- `workflow_dispatch`: manual run; deployment job is still guarded so only the two allowed refs can deploy.

### Build checks

- Node `24.12.0`.
- `npm ci --prefix frontend --no-fund --no-audit`.
- From `frontend/`:
  - `npm run api:check`
  - `npm run format:check`
  - `npm run lint`
  - `npm run typecheck`
  - `npm test`
- Production build with `VITE_GITHUB_PAGES=true`.
- Verify `/eduops360/assets/` prefix and self-hosted `.woff2` fonts.
- Scan built text assets for common secret markers (database URLs, `DATABASE_URL`, private-key markers, GitHub token patterns).
- Serve the built output on `127.0.0.1:4173` and run the two Pages Playwright tests.
- Upload **only** `frontend/dist` as the Pages artifact.

### Permissions and concurrency

- Workflow/build: `contents: read`.
- Deploy job only: `pages: write`, `id-token: write`, `contents: read`.
- Uses `actions/configure-pages@v5`, `actions/upload-pages-artifact@v4`, and `actions/deploy-pages@v4`.
- Concurrency group includes event name and ref, preventing a PR validation run from cancelling a deployment run.

No Railway, Docker, PostgreSQL, backend build, or database migration is part of this workflow.

## 6. Verified CI/deployment results

For run #31, attempt 2, on commit `851f998`:

| Check | Result |
|---|---|
| `npm ci` | PASS |
| API contract check | PASS |
| Format check | PASS |
| Lint | PASS |
| Typecheck | PASS |
| Frontend unit tests | PASS |
| Pages production build | PASS |
| Asset prefix / self-hosted font verification | PASS |
| Secret-marker scan | PASS |
| Chromium setup | PASS |
| Pages Playwright smoke tests | PASS |
| Pages artifact upload | PASS |
| Deploy to GitHub Pages | PASS |

The deploy log recorded:
- Artifact `github-pages` found.
- Deployment created for commit `851f9983886d2e21d0e56f6c1545a292d95dc54c`.
- Pages deployment status: `Reported success!`.
- Environment URL: `https://phongbao-uopeopleuni.github.io/eduops360/`.

Earlier on the same task, the first trusted-branch attempt failed before the deploy step because the `github-pages` environment allowed only `main`. The owner then added the task branch to the selected-branch allowlist. Rerunning the failed deploy job succeeded. This is resolved; do not treat the first failed attempt as the current state.

## 7. Files changed in PR #14

The PR currently reports these 10 changed files:

- `.github/workflows/github-pages.yml`
- `docs/operations/GITHUB_PAGES.md`
- `docs/progress/HANDOFF.md`
- `docs/progress/TASK_BOARD.md`
- `docs/progress/tasks/EDU-0070.md`
- `frontend/src/app/App.tsx`
- `frontend/src/app/styles.css`
- `frontend/src/main.tsx`
- `frontend/tests/e2e/github-pages.spec.ts`
- `frontend/vite.config.ts`

The present handoff file is an additional report for Desktop Codex.

## 8. Important documentation reconciliation still required

The existing EDU-0070 task journal and generated task board contain stale values from before the successful deployment. In particular, the task journal frontmatter still records an earlier commit (`4b3e547`), `deploy: not_done`, and an earlier main-only deployment description. The EDU-0070 row in `docs/progress/TASK_BOARD.md` mirrors stale metadata.

The bottom EDU-0070 section of `docs/progress/HANDOFF.md` also still says deployment is not complete and describes the first failed deploy attempt without recording the later successful retry.

**Desktop Codex must reconcile these records using verified evidence:**
1. Update `docs/progress/tasks/EDU-0070.md` with the actual deployment outcome, run #31 / attempt 2, deployed SHA, branch, push and PR status. Keep task status `in_review` unless the repository's review policy has actually been satisfied. Keep merge as `not_done`; deployment success is not a merge or acceptance.
2. Add an append-only activity-log entry for the successful deployment and the user's public-page confirmation.
3. Update `docs/progress/HANDOFF.md` to say the static Pages preview is deployed and user-confirmed, while PR #14 remains open/unmerged and the backend is not connected. Preserve all unrelated phase/security acceptance history.
4. Regenerate `docs/progress/TASK_BOARD.md` by running `python scripts/sync_task_board.py`. Do not hand-edit the generated board.
5. Check whether `docs/progress/PROJECT_STATUS.md` exists in the local working tree. It was absent from the main-based task branch and was reported as present only in the unrelated PR #12 chain. Do not import or merge the unrelated stacked PR chain just to obtain that file, and do not invent a replacement.

## 9. Desktop Codex local-worktree instructions

This handoff session changed the GitHub remote through the GitHub integration; it did **not** inspect or modify the user's local `D:\\eduops360` working tree. Desktop Codex must first inspect local state and preserve any user changes.

Run read-only checks first:

```powershell
Set-Location D:\\eduops360
git status --short --branch
git remote -v
git branch -vv
git fetch origin
git log --oneline --decorate --graph -20 --all
git rev-parse origin/main
git rev-parse origin/codex/edu-0070-github-pages
```

Expected remote facts at the time this report was written:
- `origin/main`: `c622467377980c2ff7a3bc0b80714d11f5d17007`.
- `origin/codex/edu-0070-github-pages`: `851f9983886d2e21d0e56f6c1545a292d95dc54c`.

The report itself is committed after the deployment commit, so the task branch head may have advanced. Fetch and inspect the actual current remote SHA rather than assuming the value above remains HEAD.

Do not run `reset --hard`, `clean -fd`, force-push, or overwrite the local working tree. If the local branch differs, compare and reconcile deliberately before syncing.

After local/remote reconciliation:
- Update the task journal and HANDOFF as described above.
- Run `python scripts/sync_task_board.py`.
- Run relevant local frontend checks without starting backend/DB unless separately needed.
- Inspect the diff and ensure no secrets or real student data are introduced.
- Commit/push only the intended documentation corrections after confirming the current branch and working tree.
- A push to `codex/edu-0070-github-pages` triggers the Pages workflow and may redeploy the static frontend.
- Do not merge PR #14 unless the independent approval rule is legitimately satisfied. Do not self-approve or bypass protection.

## 10. Boundaries and non-goals

- The public site is a **UI preview**, not a production application.
- No backend or PostgreSQL is connected.
- No credentials, student data, environment secrets, or backend configuration are included in the Pages artifact.
- Railway and local behavior are intended to remain unchanged: no Pages flag means root base and BrowserRouter.
- No backend, Docker, PostgreSQL, Railway, schema, migration, or API contract change was part of EDU-0070.
- No project phase has been accepted by this deployment.
- PR #14 is not merged; `main` has not been advanced by this task.

## 11. Useful links

- [Published UI preview](https://phongbao-uopeopleuni.github.io/eduops360/)
- [Workflow run #31](https://github.com/phongbao-uopeopleuni/eduops360/actions/runs/43863545271)
- [PR #14](https://github.com/phongbao-uopeopleuni/eduops360/pull/14)
- [GitHub Pages operator guide](../operations/GITHUB_PAGES.md)
- [EDU-0070 task journal](./tasks/EDU-0070.md)
