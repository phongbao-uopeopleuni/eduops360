import { defineConfig, devices } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const temporaryDirectory = fileURLToPath(new URL('../.local/playwright-tmp', import.meta.url));
mkdirSync(temporaryDirectory, { recursive: true });
Object.assign(process.env, {
  TEMP: temporaryDirectory,
  TMP: temporaryDirectory,
  TMPDIR: temporaryDirectory,
});

const backendDirectory = fileURLToPath(new URL('../backend/', import.meta.url));
const python = fileURLToPath(
  new URL(
    process.platform === 'win32'
      ? '../backend/.venv/Scripts/python.exe'
      : '../backend/.venv/bin/python',
    import.meta.url,
  ),
);
const apiPort = process.env.PLAYWRIGHT_API_PORT || '58080';
const frontendPort = process.env.PLAYWRIGHT_FRONTEND_PORT || '5173';
const externalServer = process.env.PLAYWRIGHT_EXTERNAL_SERVER === '1';
const reuseExistingServer = process.env.PLAYWRIGHT_REUSE_SERVER === '1';

if (!externalServer && !process.env.EDUOPS_DATABASE_URL) {
  throw new Error('EDUOPS_DATABASE_URL is required when Playwright starts the backend');
}

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${frontendPort}`,
    trace: 'retain-on-failure',
    ...devices['Desktop Chrome'],
    channel: process.env.PLAYWRIGHT_CHANNEL || 'chromium',
  },
  reporter: [['list'], ['json', { outputFile: 'test-results/results.json' }]],
  webServer: externalServer
    ? []
    : [
        {
          command: `"${python}" -m app --host 127.0.0.1 --port ${apiPort}`,
          cwd: backendDirectory,
          url: `http://127.0.0.1:${apiPort}/api/v1/health/live`,
          reuseExistingServer,
          timeout: 30000,
        },
        {
          command: `npm run dev -- --host 127.0.0.1 --port ${frontendPort}`,
          env: {
            ...process.env,
            API_PROXY_TARGET: `http://127.0.0.1:${apiPort}`,
          },
          url: `http://127.0.0.1:${frontendPort}`,
          reuseExistingServer,
          timeout: 30000,
        },
      ],
});
