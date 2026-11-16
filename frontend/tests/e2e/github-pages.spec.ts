import { expect, test } from '@playwright/test';

test('Pages preview uses hash navigation and survives direct reloads', async ({ page }) => {
  const apiRequests: string[] = [];
  page.on('request', (request) => {
    if (new URL(request.url()).pathname.startsWith('/api/')) apiRequests.push(request.url());
  });

  await page.goto('./');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(
    'Không gian làm việc của nhà trường',
  );
  await expect(page.getByRole('status')).toContainText('Backend chưa được kết nối');
  await page.getByRole('link', { name: 'Hệ thống', exact: true }).click();
  await expect(page).toHaveURL(/#\/system$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Trạng thái hệ thống');
  await expect(page.getByText('Chức năng này chưa khả dụng')).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Trạng thái hệ thống');

  await page.getByRole('link', { name: 'Người dùng', exact: true }).click();
  await expect(page).toHaveURL(/#\/users$/);
  await expect(page.getByText('Chức năng này chưa khả dụng')).toBeVisible();
  await expect(page.locator('input')).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Người dùng và phân quyền');

  await page.goto('#/missing');
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Không tìm thấy trang');
  await expect(page.getByRole('link', { name: 'Về tổng quan' })).toHaveAttribute('href', '#/');

  expect(apiRequests).toEqual([]);
});

test('Pages preview assets and self-hosted fonts load at mobile width', async ({ page }) => {
  const failedAssets: string[] = [];
  page.on('requestfailed', (request) => failedAssets.push(request.url()));
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('./');
  const result = await page.evaluate(async () => {
    await document.fonts.ready;
    const resources = performance.getEntriesByType('resource').map((entry) => entry.name);
    return {
      width: document.documentElement.scrollWidth,
      viewport: innerWidth,
      fonts: [...document.fonts]
        .filter((face) => face.status === 'loaded')
        .map((face) => face.family),
      prefixedResources: resources.filter((url) => new URL(url).origin === location.origin),
    };
  });
  expect(result.width).toBeLessThanOrEqual(result.viewport);
  expect(result.fonts.some((family) => family.includes('Be Vietnam Pro'))).toBe(true);
  expect(result.fonts.some((family) => family.includes('Inter'))).toBe(true);
  expect(
    result.prefixedResources.some((url) => new URL(url).pathname.startsWith('/eduops360/assets/')),
  ).toBe(true);
  expect(failedAssets).toEqual([]);
});
