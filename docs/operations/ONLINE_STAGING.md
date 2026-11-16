# Railway online preview — synthetic staging

Task EDU-0069. This is a deployment package, not proof of a live deployment.
User prefers Railway + Docker and has no VPS/domain yet. No Railway account,
project, database or paid resource has been created by this task.

## Recommended layout

- GitHub stores the source. Railway builds `infra/Dockerfile.railway` from repo
  root; one non-root Python container serves the compiled React frontend and
  FastAPI on the same domain. No Vite dev server or separate Vercel is needed.
- A separate Railway PostgreSQL service holds synthetic staging data only.
- A separate one-shot migrator service has DB-owner credentials. The web service
  has only `eduops_runtime` credentials; never copy PostgreSQL's owner URL into it.
- Railway's generated domain/HTTPS removes the need to buy a domain initially.
  Actual URL is recorded only after Railway returns and verifies it.
- Web preview is protected by HTTP Basic: username `preview`, password is the
  private `EDUOPS_PREVIEW_ACCESS_KEY`. This is a preview gate, not app IAM/MFA.
  Application accounts/roles remain unseeded until their documented authority
  and synthetic-account bootstrap are separately arranged.

Official references checked 2026-11-16:
[domains and HTTPS](https://docs.railway.com/networking/public-networking),
[Dockerfile builds](https://docs.railway.com/builds/dockerfiles),
[config as code](https://docs.railway.com/config-as-code/reference),
[health checks and PORT](https://docs.railway.com/deployments/healthchecks).
[GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
hosts static files; it cannot run this Python API/PostgreSQL backend. Splitting
the frontend onto Vercel is possible later but adds cross-origin cookie/CSRF work.

## Setup once the Railway account is available

1. Create/connect a Railway account and GitHub integration. Choose a plan/budget
   yourself before provisioning resources; this document makes no free-tier or
   monthly-price guarantee. Use a separate synthetic-staging project/environment.
2. Add PostgreSQL. Keep DB access private; no public TCP proxy is required.
3. Connect this repository at root `/` to **two separate services** from the same
   tested commit/branch. Do not select `main` blindly: it still lacks the stacked
   changes. Disable automatic deploys for the one-shot migrator. Web config path
   is `/railway.json`; migrator config is `/infra/railway.migrate.json`.
4. In the migrator service only, set `EDUOPS_DATABASE_URL` to the PostgreSQL owner
   URL with scheme `postgresql+psycopg://`. Set `STAGING_RUNTIME_PASSWORD` and
   `STAGING_AUDIT_WORKER_PASSWORD` to two different random URL-safe secrets,
   at least 32 characters, stored only in Railway Variables.
5. Run migrator once. It creates the restricted roles if absent and migrates to
   head; it refuses privileged existing roles and does not automatically rotate
   existing passwords. Expected output: `Staging roles checked and migrations
   completed.` Do not repeatedly restart a completed one-shot service.
6. Set web Variables below. Generate Domain in web Settings → Networking → Public
   Networking, then use the actual assigned hostname in `EDUOPS_ALLOWED_HOSTS`.
   A first start before variables/DB are ready may fail; that is fail-closed.
7. Deploy web from the tested commit. Railway injects `PORT`; the entrypoint
   binds `0.0.0.0:$PORT`. Readiness must return 200 before activation.
8. Visit the generated HTTPS URL, enter preview credentials, verify `/`, `/users`
   and `/system`. Confirm `/api/v1/health/ready` reports DB `ok`; health is the
   only preview-auth exception and contains no credentials or user records.

## Web Variables (names/examples only, never secret values in Git)

| Key | Value / source |
| --- | --- |
| `EDUOPS_ENVIRONMENT` | `staging` |
| `EDUOPS_DATABASE_URL` | `postgresql+psycopg://eduops_runtime:<runtime-password>@<private-pg-host>:5432/<database>`; URI-encode credentials when necessary |
| `EDUOPS_CORS_ORIGINS` | `[]` (same-origin frontend/API) |
| `EDUOPS_ALLOWED_HOSTS` | JSON array `["<actual-generated-hostname>","healthcheck.railway.app"]`; no scheme, wildcard or path |
| `EDUOPS_SESSION_COOKIE_SECURE` | `true` |
| `EDUOPS_PREVIEW_ACCESS_KEY` | Random private URL-safe key, at least 32 characters; not an app password |

Never set `STAGING_*PASSWORD`, owner/migrator URL or DB-admin credentials on the
web service. Do not put secrets in Docker build arguments, image layers, Git,
chat or screenshots. `.env` files are not needed by this deployment.

Only one web replica is intended for this preview: current rate-limit state is
in-process. Trusted proxy/IP policy remains R42-F02; shared proxy peers may share
the IP limiter. Do not change that policy or scale horizontally from this guide.

## Verification and rollback

- Build locally: `docker build -f infra/Dockerfile.railway -t eduops360-online:edu0069 .`.
  This builds frontend assets inside Docker; it does not overwrite host `frontend/dist/`.
- Unit regression: backend venv `python -m pytest backend/tests/test_staging_config.py -q`.
- Retain the tested commit SHA, Railway deployment ID, image identity and assigned
  URL in EDU-0069 when available. A config file or local smoke is not a live URL.
- For a bad app release, roll web back to the prior immutable deployment. Do not
  automatically downgrade the database or delete its volume. Stop if the previous
  app is incompatible with the migrated schema; use a reviewed forward fix.
- Removing an online preview means stopping the web service first. Retain the DB
  until its synthetic/disposable status and deletion target are explicitly checked.

The earlier phase/security/business acceptance, MFA custody, operational audit
archive, monitoring and backup/restore gates remain open for real production.
Railway's deploy-time health check is not continuous uptime monitoring. No real
student data or unrestricted admin accounts are authorized for this preview.
