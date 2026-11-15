import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { UserManagementPage } from './UserManagementPage';
import {
  changeAdminUserStatus,
  cancelAdminInvitation,
  createAdminInvitation,
  listAdminRoles,
  loginUser,
  readCurrentUser,
  reissueAdminInvitation,
} from '../../shared/api/client';

vi.mock('../../shared/api/client', () => ({
  readCurrentUser: vi.fn(),
  loginUser: vi.fn(),
  logoutUser: vi.fn(),
  listAdminRoles: vi.fn(),
  createAdminInvitation: vi.fn(),
  changeAdminUserStatus: vi.fn(),
  grantAdminRole: vi.fn(),
  revokeAdminRole: vi.fn(),
  reissueAdminInvitation: vi.fn(),
  cancelAdminInvitation: vi.fn(),
}));

const admin = {
  id: '10000000-0000-4000-8000-000000000001',
  email: 'admin@example.com',
  display_name: 'Quản trị tổng hợp',
  status: 'active' as const,
  mfa_enabled: true,
  created_at: '2026-11-13T00:00:00Z',
};

const created = {
  ...admin,
  id: '10000000-0000-4000-8000-000000000002',
  email: 'giaovien@example.com',
  display_name: 'Giáo viên thử nghiệm',
  status: 'pending' as const,
  mfa_enabled: false,
};

describe('user administration', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(readCurrentUser).mockRejectedValue(new Error('signed out'));
    vi.mocked(listAdminRoles).mockResolvedValue([]);
  });

  it('logs in then creates a one-time invitation for a pending synthetic user', async () => {
    vi.mocked(loginUser).mockResolvedValue({
      user: admin,
      expires_at: '2026-11-14T00:00:00Z',
    });
    vi.mocked(createAdminInvitation).mockResolvedValue({
      user: created,
      one_time_token: 'synthetic-one-time-invitation-token-123456',
      expires_at: '2026-11-14T00:00:00Z',
    });
    render(<UserManagementPage />);

    const login = await screen.findByRole('heading', { name: 'Đăng nhập quản trị' });
    const loginForm = login.closest('section')!;
    fireEvent.change(within(loginForm).getByLabelText('Email'), {
      target: { value: admin.email },
    });
    fireEvent.change(within(loginForm).getByLabelText('Mật khẩu'), {
      target: { value: 'Synthetic-Password-123!' },
    });
    fireEvent.click(within(loginForm).getByRole('button', { name: 'Đăng nhập' }));

    expect(await screen.findByText(admin.email)).toBeInTheDocument();
    const createHeading = screen.getByRole('heading', { name: 'Mời người dùng' });
    const createForm = createHeading.closest('section')!;
    fireEvent.change(within(createForm).getByLabelText('Họ tên'), {
      target: { value: created.display_name },
    });
    fireEvent.change(within(createForm).getByLabelText('Email'), {
      target: { value: created.email },
    });
    fireEvent.change(within(createForm).getByLabelText('Thời hạn lời mời (giờ)'), {
      target: { value: '48' },
    });
    fireEvent.click(within(createForm).getByRole('button', { name: 'Tạo lời mời' }));

    expect(await screen.findByText(/Tài khoản vừa mời/)).toBeInTheDocument();
    expect(screen.getByText(/giaovien@example.com/)).toBeInTheDocument();
    expect(screen.getByText('synthetic-one-time-invitation-token-123456')).toBeInTheDocument();
    expect(createAdminInvitation).toHaveBeenCalledWith({
      email: created.email,
      display_name: created.display_name,
      valid_hours: 48,
    });
  });

  it('does not offer or default to activation for a pending invitee', async () => {
    vi.mocked(readCurrentUser).mockResolvedValue(admin);
    vi.mocked(createAdminInvitation).mockResolvedValue({
      user: created,
      one_time_token: 'synthetic-one-time-invitation-token-123456',
      expires_at: '2026-11-14T00:00:00Z',
    });
    render(<UserManagementPage />);
    await screen.findByText(admin.email);

    const createHeading = screen.getByRole('heading', { name: 'Mời người dùng' });
    const createForm = createHeading.closest('section')!;
    fireEvent.change(within(createForm).getByLabelText('Họ tên'), {
      target: { value: created.display_name },
    });
    fireEvent.change(within(createForm).getByLabelText('Email'), {
      target: { value: created.email },
    });
    fireEvent.click(within(createForm).getByRole('button', { name: 'Tạo lời mời' }));

    const managedHeading = await screen.findByRole('heading', { name: 'Tài khoản vừa mời' });
    const managed = managedHeading.closest('section')!;
    expect(within(managed).queryByRole('option', { name: 'Kích hoạt' })).not.toBeInTheDocument();
    expect(within(managed).getByText(/hoàn tất lời mời/)).toBeInTheDocument();
    expect(changeAdminUserStatus).not.toHaveBeenCalled();
  });

  it('shows a safe authorization error from the API', async () => {
    vi.mocked(readCurrentUser).mockResolvedValue(admin);
    vi.mocked(createAdminInvitation).mockRejectedValue(
      new Error('Không có quyền thực hiện thao tác này'),
    );
    render(<UserManagementPage />);
    await screen.findByText(admin.email);

    const createHeading = screen.getByRole('heading', { name: 'Mời người dùng' });
    const createForm = createHeading.closest('section')!;
    fireEvent.change(within(createForm).getByLabelText('Họ tên'), {
      target: { value: created.display_name },
    });
    fireEvent.change(within(createForm).getByLabelText('Email'), {
      target: { value: created.email },
    });
    fireEvent.click(within(createForm).getByRole('button', { name: 'Tạo lời mời' }));

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Không có quyền');
    });
  });

  it('shows a role-catalog loading error instead of an empty silent list', async () => {
    vi.mocked(readCurrentUser).mockResolvedValue(admin);
    vi.mocked(listAdminRoles).mockRejectedValue(new Error('Không thể tải danh sách vai trò.'));
    render(<UserManagementPage />);
    expect(await screen.findByText(admin.email)).toBeInTheDocument();
    expect(await screen.findByRole('alert')).toHaveTextContent('Không thể tải danh sách vai trò.');
  });

  it('reissues and cancels a pending invitation without activating it', async () => {
    vi.mocked(readCurrentUser).mockResolvedValue(admin);
    vi.mocked(createAdminInvitation).mockResolvedValue({
      user: created,
      one_time_token: 'synthetic-first-token-1234567890123456',
      expires_at: '2026-11-14T00:00:00Z',
    });
    vi.mocked(reissueAdminInvitation).mockResolvedValue({
      user: created,
      one_time_token: 'synthetic-reissued-token-123456789012',
      expires_at: '2026-11-15T00:00:00Z',
    });
    vi.mocked(cancelAdminInvitation).mockResolvedValue(undefined);
    render(<UserManagementPage />);
    await screen.findByText(admin.email);
    const createForm = screen.getByRole('heading', { name: 'Mời người dùng' }).closest('section')!;
    fireEvent.change(within(createForm).getByLabelText('Họ tên'), {
      target: { value: created.display_name },
    });
    fireEvent.change(within(createForm).getByLabelText('Email'), {
      target: { value: created.email },
    });
    fireEvent.click(within(createForm).getByRole('button', { name: 'Tạo lời mời' }));
    await screen.findByRole('heading', { name: 'Tài khoản vừa mời' });

    fireEvent.click(screen.getByRole('button', { name: 'Phát hành lại lời mời' }));
    expect(await screen.findByText('synthetic-reissued-token-123456789012')).toBeInTheDocument();
    expect(reissueAdminInvitation).toHaveBeenCalledWith(created.id);
    fireEvent.click(screen.getByRole('button', { name: 'Hủy mã lời mời' }));
    await waitFor(() => expect(cancelAdminInvitation).toHaveBeenCalledWith(created.id));
    expect(screen.queryByText('synthetic-reissued-token-123456789012')).not.toBeInTheDocument();
    expect(changeAdminUserStatus).not.toHaveBeenCalled();
  });
});
