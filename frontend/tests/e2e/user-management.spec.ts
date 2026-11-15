import { expect, test } from '@playwright/test';

const admin = {
  id: '10000000-0000-4000-8000-000000000001',
  email: 'admin@example.com',
  display_name: 'Quản trị tổng hợp',
  status: 'active',
  mfa_enabled: true,
  created_at: '2026-11-13T00:00:00Z',
};

test('Vietnamese admin login and invitation issuance send the session CSRF token', async ({
  context,
  page,
}) => {
  let csrfHeader: string | undefined;
  await context.addCookies([
    {
      name: 'eduops_csrf',
      value: 'synthetic-csrf-token',
      domain: '127.0.0.1',
      path: '/',
      sameSite: 'Strict',
    },
  ]);
  await page.route('**/api/v1/auth/me', (route) =>
    route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({
        error: { code: 'AUTH_REQUIRED', message: 'Cần đăng nhập.', request_id: 'synthetic' },
      }),
    }),
  );
  await page.route('**/api/v1/auth/login', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ user: admin, expires_at: '2026-11-14T00:00:00Z' }),
    }),
  );
  await page.route('**/api/v1/admin/roles', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
  );
  await page.route('**/api/v1/admin/users/invitations', async (route) => {
    csrfHeader = route.request().headers()['x-csrf-token'];
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        user: {
          ...admin,
          id: '10000000-0000-4000-8000-000000000002',
          email: 'giaovien@example.com',
          display_name: 'Giáo viên thử nghiệm',
          status: 'pending',
          mfa_enabled: false,
        },
        one_time_token: 'synthetic-one-time-invitation-token-123456',
        expires_at: '2026-11-14T00:00:00Z',
      }),
    });
  });

  await page.goto('/users');
  await expect(page.getByRole('heading', { name: 'Đăng nhập quản trị' })).toBeVisible();
  await page.getByLabel('Email').fill(admin.email);
  await page.getByLabel('Mật khẩu').fill('Synthetic-Password-123!');
  await page.getByLabel('Mật khẩu').press('Tab');
  await expect(page.getByLabel('Mã MFA (nếu đã bật)')).toBeFocused();
  await page.getByRole('button', { name: 'Đăng nhập' }).click();

  await expect(page.getByText(admin.email)).toBeVisible();
  const createSection = page
    .getByRole('heading', { name: 'Mời người dùng' })
    .locator('xpath=ancestor::section');
  await createSection.getByLabel('Họ tên').fill('Giáo viên thử nghiệm');
  await createSection.getByLabel('Email').fill('giaovien@example.com');
  await createSection.getByLabel('Thời hạn lời mời (giờ)').fill('24');
  await createSection.getByRole('button', { name: 'Tạo lời mời' }).click();

  await expect(page.getByRole('heading', { name: 'Tài khoản vừa mời' })).toBeVisible();
  await expect(page.getByText(/giaovien@example.com/)).toBeVisible();
  await expect(page.getByText('synthetic-one-time-invitation-token-123456')).toBeVisible();
  expect(csrfHeader).toBe('synthetic-csrf-token');
});
