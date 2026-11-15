import createClient from 'openapi-fetch';
import type { components, paths } from './generated/schema';
import { parseTimestamp } from '../lib/dates';

export const api = createClient<paths>({ baseUrl: '', credentials: 'include' });

export type AuthenticatedUser = components['schemas']['UserRead'];
export type AdminRole = components['schemas']['RoleRead'];
export type UserRoleGrant = components['schemas']['UserRoleRead'];
export type AccountTokenIssue = components['schemas']['AccountTokenIssue'];

function csrfToken() {
  const prefix = 'eduops_csrf=';
  const value = document.cookie
    .split(';')
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix));
  return value ? decodeURIComponent(value.slice(prefix.length)) : null;
}

function csrfHeaders() {
  const token = csrfToken();
  if (!token) throw new Error('Phiên đăng nhập thiếu mã bảo vệ CSRF.');
  return { 'X-CSRF-Token': token };
}

function apiError(error: unknown, fallback: string): Error {
  if (error && typeof error === 'object' && 'error' in error) {
    const detail = (error as { error?: { message?: unknown } }).error;
    if (detail && typeof detail.message === 'string') return new Error(detail.message);
  }
  return new Error(fallback);
}

export async function loginUser(email: string, password: string, mfaCode?: string) {
  const { data, error } = await api.POST('/api/v1/auth/login', {
    body: { email, password, mfa_code: mfaCode || null },
  });
  if (!data) throw apiError(error, 'Không thể đăng nhập.');
  return data;
}

export async function readCurrentUser() {
  const { data, error } = await api.GET('/api/v1/auth/me');
  if (!data) throw apiError(error, 'Phiên đăng nhập không hợp lệ.');
  return data;
}

export async function logoutUser() {
  const { response, error } = await api.POST('/api/v1/auth/logout', {
    headers: csrfHeaders(),
  });
  if (!response.ok) throw apiError(error, 'Không thể đăng xuất.');
}

export async function listAdminRoles() {
  const { data, error } = await api.GET('/api/v1/admin/roles');
  if (!data) throw apiError(error, 'Không thể tải danh sách vai trò.');
  return data;
}

export async function createAdminInvitation(input: {
  email: string;
  display_name: string;
  valid_hours?: number;
}) {
  const { data, error } = await api.POST('/api/v1/admin/users/invitations', {
    body: { ...input, valid_hours: input.valid_hours ?? 24 },
    headers: csrfHeaders(),
  });
  if (!data) throw apiError(error, 'Không thể tạo lời mời người dùng.');
  return data;
}

export async function reissueAdminInvitation(userId: string, validHours = 24) {
  const { data, error } = await api.POST('/api/v1/admin/users/{user_id}/invitation', {
    params: { path: { user_id: userId } },
    body: { valid_hours: validHours },
    headers: csrfHeaders(),
  });
  if (!data) throw apiError(error, 'Không thể phát hành lại lời mời.');
  return data;
}

export async function cancelAdminInvitation(userId: string) {
  const { response, error } = await api.POST('/api/v1/admin/users/{user_id}/invitation/cancel', {
    params: { path: { user_id: userId } },
    headers: csrfHeaders(),
  });
  if (!response.ok) throw apiError(error, 'Không thể hủy lời mời.');
}

export async function changeAdminUserStatus(
  userId: string,
  status: 'active' | 'suspended',
  reason: string,
) {
  const { data, error } = await api.PATCH('/api/v1/admin/users/{user_id}/status', {
    params: { path: { user_id: userId } },
    body: { status, reason: reason || null },
    headers: csrfHeaders(),
  });
  if (!data) throw apiError(error, 'Không thể cập nhật trạng thái.');
  return data;
}

export async function grantAdminRole(
  userId: string,
  input: {
    role_id: string;
    school_id: string;
    academic_year_id: string;
    grade_id?: number | null;
  },
) {
  const { data, error } = await api.POST('/api/v1/admin/users/{user_id}/roles', {
    params: { path: { user_id: userId } },
    body: input,
    headers: csrfHeaders(),
  });
  if (!data) throw apiError(error, 'Không thể cấp vai trò.');
  return data;
}

export async function revokeAdminRole(userId: string, grantId: string, reason: string) {
  const { data, error } = await api.POST('/api/v1/admin/users/{user_id}/roles/revoke', {
    params: { path: { user_id: userId } },
    body: { user_role_id: grantId, reason },
    headers: csrfHeaders(),
  });
  if (!data) throw apiError(error, 'Không thể thu hồi vai trò.');
  return data;
}

export async function readSystemHealth(signal: AbortSignal) {
  const requestSignal = AbortSignal.any([signal, AbortSignal.timeout(8000)]);
  const [live, ready] = await Promise.all([
    api.GET('/api/v1/health/live', { signal: requestSignal }),
    api.GET('/api/v1/health/ready', { signal: requestSignal }),
  ]);
  const readiness = ready.data ?? ready.error;
  if (
    !live.data ||
    live.data.status !== 'ok' ||
    !readiness ||
    !('database' in readiness) ||
    ![200, 503].includes(ready.response.status)
  ) {
    throw new Error('Không thể kiểm tra kết nối hệ thống.');
  }
  parseTimestamp(live.data.checked_at);
  parseTimestamp(readiness.checked_at);
  return { live: live.data, ready: readiness };
}
