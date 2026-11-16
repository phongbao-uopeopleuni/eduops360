# GitHub Pages — UI preview

## Purpose and limits

The Pages site is a public, static preview of the EduOps 360 frontend. It is
not an online application environment: no FastAPI service, PostgreSQL database,
authentication provider, session store or real school data is connected.
The user-management and system routes display an explicit unavailable state;
they do not submit credentials or administrative mutations. Never enter real
credentials or student information on the public preview.

Target URL after a verified deployment:
`https://phongbao-uopeopleuni.github.io/eduops360/`

## Repository configuration

1. Open **Settings → Pages**.
2. Set **Build and deployment → Source** to **GitHub Actions**.
3. Keep `main` as the deployment source. Do not change the repository default
   branch or disable branch protection to enable Pages.

## Vite and router behavior

- When `VITE_GITHUB_PAGES=true`, Vite uses `base: '/eduops360/'` and the
  application uses `HashRouter`.
- Local development and Railway omit that variable: Vite uses `base: '/'`
  and the application retains `BrowserRouter`.
- Fonts are self-hosted through the existing `@fontsource` packages. No CDN
  font dependency is introduced.
- Pages navigation uses hash URLs such as `/#/system`; reloads do not require
  server-side SPA rewrite support.

## Workflow and trust boundary

`.github/workflows/github-pages.yml` runs on pull requests to `main`,
pushes to `main`, and manual dispatch. Pull requests run checks and a static
preview browser smoke test but never upload or deploy a Pages artifact.
Only a push or manual dispatch whose ref is exactly `refs/heads/main` can
upload and deploy. The workflow uploads only `frontend/dist`.

The build uses the Node version supported by `frontend/package.json` and
`frontend/package-lock.json`, runs `npm ci`, API contract/format/lint/type
checks and unit tests, builds with the Pages flag, checks repository-prefixed
assets and self-hosted fonts, scans text assets for common secret markers, and
tests the static preview on loopback with Playwright.

Permissions are read-only for the build job. The deploy job alone receives
`pages: write` and `id-token: write`, and uses the `github-pages`
environment. No Railway, Docker, PostgreSQL or backend workflow is required.

## Manual verification

After the workflow deploy job succeeds:

1. Open the environment URL recorded by the deployment.
2. Confirm the overview page, then navigate to System, Users and an unknown
   route. Check that URLs use `#/` and reload each route.
3. Confirm the backend-not-connected notice is visible and no login form or
   service-health claim appears.
4. Check light/dark mode, mobile layout, self-hosted fonts and browser console.
5. Confirm JavaScript, CSS and font assets load under `/eduops360/assets/`.

Do not report the target URL as live until the workflow deployment is successful
and the published URL and browser behavior have been checked. A successful build
alone is not a deployment. This preview is not Phase 00 acceptance or a
production release.
