import { expect, test } from '@playwright/test';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

test('test-worker temporary storage is inside the workspace', async ({}, testInfo) => {
  const expected = fileURLToPath(new URL('../../../.local/playwright-tmp', import.meta.url));
  expect(tmpdir()).toBe(expected);
  await testInfo.attach('temporary-directory', {
    body: JSON.stringify({ temporaryDirectory: tmpdir() }),
    contentType: 'application/json',
  });
});

test('light and dark text palettes meet normal-text contrast', async ({ page }) => {
  await page.goto('/');
  for (const mode of ['light', 'dark']) {
    await expect(page.locator('html')).toHaveAttribute('data-theme', mode);
    const ratios = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      const luminance = (token: string) => {
        const hex = styles.getPropertyValue(token).trim().replace('#', '');
        const channels = [0, 2, 4].map((offset) => {
          const value = parseInt(hex.slice(offset, offset + 2), 16) / 255;
          return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
        });
        return channels[0]! * 0.2126 + channels[1]! * 0.7152 + channels[2]! * 0.0722;
      };
      return [
        ['--text', '--page'],
        ['--text', '--surface'],
        ['--muted', '--page'],
        ['--muted', '--surface'],
        ['--accent', '--surface'],
        ['--positive', '--surface'],
        ['--warning', '--surface'],
        ['--error', '--error-bg'],
      ].map(([foreground, background]) => {
        const first = luminance(foreground!);
        const second = luminance(background!);
        return {
          foreground,
          background,
          ratio: (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05),
        };
      });
    });
    for (const pair of ratios)
      expect(pair.ratio, `${mode} ${pair.foreground}/${pair.background}`).toBeGreaterThanOrEqual(
        4.5,
      );
    if (mode === 'light') {
      await page.getByRole('button', { name: 'Chuyển sang giao diện tối' }).click();
    }
  }
});

test('light is the default and the icon toggle persists dark mode', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  const darkToggle = page.getByRole('button', { name: 'Chuyển sang giao diện tối' });
  await expect(darkToggle).toBeVisible();
  await darkToggle.click();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await expect(page.getByRole('button', { name: 'Chuyển sang giao diện sáng' })).toBeVisible();
});

test('Vietnamese navigation, keyboard, theme persistence and mobile layout', async ({
  page,
}, testInfo) => {
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 200,
      json: { status: 'ready', database: 'ok', checked_at: '2026-11-12T05:00:00Z' },
    }),
  );
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(
    'Không gian làm việc của nhà trường',
  );
  await expect(page.locator('html')).toHaveAttribute('lang', 'vi');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Đến nội dung chính' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('main')).toBeFocused();
  await page.getByRole('heading', { level: 1 }).click();

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
  await page.screenshot({ path: testInfo.outputPath('light.png'), fullPage: true });
  await page.getByRole('button', { name: 'Chuyển sang giao diện tối' }).click();
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.screenshot({ path: testInfo.outputPath('dark.png'), fullPage: true });

  await page.getByRole('link', { name: 'Hệ thống', exact: true }).click();
  await expect(page.getByText('Đang hoạt động')).toBeVisible();
  await expect(page.getByRole('term').filter({ hasText: 'Cơ sở dữ liệu' })).toBeVisible();
  await expect(page.getByText('Đã kết nối', { exact: true })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole('button', { name: /Kiểm tra lại/ })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: testInfo.outputPath('mobile.png'), fullPage: true });
});

test('database unavailable, network error and retry recovery', async ({ page }) => {
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 503,
      json: { status: 'unavailable', database: 'unavailable', checked_at: '2026-11-12T05:00:00Z' },
    }),
  );
  await page.goto('/system');
  await expect(page.getByText('Chưa sẵn sàng')).toBeVisible();
  await page.route('**/api/v1/health/live', (route) => route.abort());
  await page.getByRole('button', { name: /Kiểm tra lại/ }).click();
  await expect(page.getByRole('alert')).toContainText('Chưa kết nối được API');
  await page.unroute('**/api/v1/health/live');
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 200,
      json: { status: 'ready', database: 'ok', checked_at: '2026-11-12T05:00:00Z' },
    }),
  );
  await page.getByRole('button', { name: /Kiểm tra lại/ }).click();
  await expect(page.getByText('Đã kết nối')).toBeVisible();
});

test('design system fonts load with Vietnamese glyphs and pages fit 360–1280 px', async ({
  page,
}) => {
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 200,
      json: { status: 'ready', database: 'ok', checked_at: '2026-11-12T05:00:00Z' },
    }),
  );
  for (const width of [360, 390, 768, 1280]) {
    await page.setViewportSize({ width, height: 800 });
    for (const path of ['/', '/system', '/users', '/missing']) {
      await page.goto(path);
      await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1);
      const fits = await page.evaluate(async () => {
        await document.fonts.ready;
        return document.documentElement.scrollWidth <= innerWidth;
      });
      expect(fits, `${width}px ${path} has no horizontal scroll`).toBe(true);
    }
  }
  await page.goto('/');
  const faces = await page.evaluate(async () => {
    await document.fonts.ready;
    return [...document.fonts]
      .filter((face) => face.status === 'loaded')
      .map((face) => ({
        family: face.family.replace(/["']/g, ''),
        weight: face.weight,
        // Browsers normalise unicode-range to lowercase (u+1ea0-1ef9).
        vietnamese: face.unicodeRange.toUpperCase().includes('1EA0'),
      }));
  });
  expect(faces).toContainEqual({ family: 'Be Vietnam Pro', weight: '700', vietnamese: true });
  expect(faces.some((face) => face.family === 'Inter' && face.weight === '400')).toBe(true);
});

test('unknown route provides a working return link', async ({ page }) => {
  await page.goto('/unknown');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Không tìm thấy trang');
  await page.getByRole('link', { name: 'Về tổng quan' }).click();
  await expect(page).toHaveURL('/');
});

test('malformed health timestamp stays recoverable', async ({ page }) => {
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 200,
      json: { status: 'ready', database: 'ok', checked_at: 'invalid' },
    }),
  );
  await page.goto('/system');
  await expect(page.getByRole('alert')).toContainText('Chưa kết nối được API');
  await page.unroute('**/api/v1/health/ready');
  await page.route('**/api/v1/health/ready', (route) =>
    route.fulfill({
      status: 200,
      json: { status: 'ready', database: 'ok', checked_at: '2026-11-12T05:00:00Z' },
    }),
  );
  await page.getByRole('button', { name: /Kiểm tra lại/ }).click();
  await expect(page.getByText('Đã kết nối', { exact: true })).toBeVisible();
});
