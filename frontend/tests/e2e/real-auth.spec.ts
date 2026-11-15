import { expect, test } from '@playwright/test';

const email = process.env.PLAYWRIGHT_REAL_AUTH_EMAIL;
const password = process.env.PLAYWRIGHT_REAL_AUTH_PASSWORD;
const fixtureMissing = !email || !password;
if (process.env.PLAYWRIGHT_REQUIRE_REAL_AUTH === '1' && fixtureMissing) {
  throw new Error(
    'PLAYWRIGHT_REQUIRE_REAL_AUTH=1 requires PLAYWRIGHT_REAL_AUTH_EMAIL and PLAYWRIGHT_REAL_AUTH_PASSWORD',
  );
}

test('real backend login uses the session CSRF token and logout revokes the session', async ({
  page,
}) => {
  test.skip(fixtureMissing, 'requires an isolated synthetic real-auth fixture');

  await page.goto('/users');
  await page.getByLabel('Email').fill(email!);
  await page.getByLabel('Mật khẩu').fill(password!);
  await page.getByRole('button', { name: 'Đăng nhập' }).click();
  await expect(page.getByText(email!)).toBeVisible();
  await expect(page.getByText('Đăng nhập thành công.')).toBeVisible();

  await page.getByRole('button', { name: 'Đăng xuất' }).click();
  await expect(page.getByRole('heading', { name: 'Đăng nhập quản trị' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Đăng nhập quản trị' })).toBeVisible();
});
