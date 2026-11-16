import { expect, test } from '@playwright/test';

test('brand and text links meet the 44px project hit-target minimum', async ({ page }) => {
  for (const width of [390, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    for (const path of ['/', '/missing']) {
      await page.goto(path);
      const links = page.locator('a.brand, a.text-link');
      expect(await links.count()).toBeGreaterThan(0);
      for (const link of await links.all()) {
        const box = await link.boundingBox();
        expect(box).not.toBeNull();
        expect(box!.height).toBeGreaterThanOrEqual(44);
        expect(box!.width).toBeGreaterThanOrEqual(44);
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true,
      );
    }
  }
});
