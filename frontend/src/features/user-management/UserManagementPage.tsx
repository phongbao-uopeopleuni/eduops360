import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import {
  changeAdminUserStatus,
  createAdminInvitation,
  grantAdminRole,
  listAdminRoles,
  loginUser,
  logoutUser,
  readCurrentUser,
  reissueAdminInvitation,
  cancelAdminInvitation,
  revokeAdminRole,
} from '../../shared/api/client';
import type {
  AccountTokenIssue,
  AdminRole,
  AuthenticatedUser,
  UserRoleGrant,
} from '../../shared/api/client';

// Mirrors the backend transition rule (A0102-F03); the server remains authoritative.
const STATUS_CHANGE_OPTIONS: Record<
  AuthenticatedUser['status'],
  { value: 'active' | 'suspended'; label: string }[]
> = {
  pending: [],
  active: [{ value: 'suspended', label: 'Đình chỉ' }],
  suspended: [{ value: 'active', label: 'Kích hoạt' }],
  locked: [
    { value: 'active', label: 'Kích hoạt' },
    { value: 'suspended', label: 'Đình chỉ' },
  ],
};

type SessionState =
  | { status: 'loading' }
  | { status: 'signed-out' }
  | { status: 'signed-in'; user: AuthenticatedUser };

function message(error: unknown) {
  return error instanceof Error ? error.message : 'Yêu cầu không thành công.';
}

export function UserManagementPage() {
  const [session, setSession] = useState<SessionState>({ status: 'loading' });
  const [roles, setRoles] = useState<AdminRole[]>([]);
  const [createdUser, setCreatedUser] = useState<AuthenticatedUser | null>(null);
  const [invitation, setInvitation] = useState<AccountTokenIssue | null>(null);
  const [grant, setGrant] = useState<UserRoleGrant | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    readCurrentUser()
      .then((user) => {
        if (!controller.signal.aborted) setSession({ status: 'signed-in', user });
      })
      .catch(() => {
        if (!controller.signal.aborted) setSession({ status: 'signed-out' });
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (session.status !== 'signed-in') return;
    listAdminRoles()
      .then(setRoles)
      .catch((caught) => {
        setRoles([]);
        setError(message(caught));
      });
  }, [session.status]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
    } catch (caught) {
      setError(message(caught));
    } finally {
      setBusy(false);
    }
  }

  function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    void run(async () => {
      const result = await loginUser(
        String(data.get('email')),
        String(data.get('password')),
        String(data.get('mfa_code') || ''),
      );
      setSession({ status: 'signed-in', user: result.user });
      setNotice('Đăng nhập thành công.');
    });
  }

  function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    void run(async () => {
      const issued = await createAdminInvitation({
        email: String(data.get('email')),
        display_name: String(data.get('display_name')),
        valid_hours: Number(data.get('valid_hours')),
      });
      setCreatedUser(issued.user);
      setInvitation(issued);
      setGrant(null);
      setNotice('Đã tạo lời mời. Mã bên dưới chỉ được hiển thị trong lần phát hành này.');
      form.reset();
    });
  }

  function submitStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!createdUser) return;
    const data = new FormData(event.currentTarget);
    const status = String(data.get('status')) as 'active' | 'suspended';
    void run(async () => {
      const user = await changeAdminUserStatus(
        createdUser.id,
        status,
        String(data.get('reason') || ''),
      );
      setCreatedUser(user);
      setNotice(status === 'active' ? 'Đã kích hoạt tài khoản.' : 'Đã đình chỉ tài khoản.');
    });
  }

  function submitGrant(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!createdUser) return;
    const data = new FormData(event.currentTarget);
    const grade = String(data.get('grade_id') || '');
    void run(async () => {
      const result = await grantAdminRole(createdUser.id, {
        role_id: String(data.get('role_id')),
        school_id: String(data.get('school_id')),
        academic_year_id: String(data.get('academic_year_id')),
        grade_id: grade ? Number(grade) : null,
      });
      setGrant(result);
      setNotice('Đã cấp vai trò trong scope được chọn.');
    });
  }

  function submitRevoke(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!createdUser || !grant) return;
    const data = new FormData(event.currentTarget);
    void run(async () => {
      const result = await revokeAdminRole(createdUser.id, grant.id, String(data.get('reason')));
      setGrant(result);
      setNotice('Đã thu hồi vai trò; quyền mới có hiệu lực ngay.');
    });
  }

  if (session.status === 'loading') {
    return <p className="loading-message">Đang kiểm tra phiên đăng nhập…</p>;
  }

  if (session.status === 'signed-out') {
    return (
      <section className="panel auth-panel" aria-labelledby="login-title">
        <div className="panel-heading">
          <div>
            <h2 id="login-title">Đăng nhập quản trị</h2>
            <p>Phiên dùng cookie HttpOnly; mã CSRF không được nhập thủ công.</p>
          </div>
        </div>
        <form className="form-grid" onSubmit={submitLogin}>
          <label>
            Email
            <input name="email" type="email" autoComplete="username" required />
          </label>
          <label>
            Mật khẩu
            <input name="password" type="password" autoComplete="current-password" required />
          </label>
          <label>
            Mã MFA (nếu đã bật)
            <input name="mfa_code" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} />
          </label>
          {error && (
            <p className="inline-error" role="alert">
              {error}
            </p>
          )}
          <button className="button" disabled={busy}>
            Đăng nhập
          </button>
        </form>
      </section>
    );
  }

  return (
    <div className="admin-stack">
      <section className="panel session-summary" aria-label="Phiên quản trị">
        <div>
          <strong>{session.user.display_name}</strong>
          <span>{session.user.email}</span>
        </div>
        <button
          className="button button-secondary"
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await logoutUser();
              setSession({ status: 'signed-out' });
              setCreatedUser(null);
              setInvitation(null);
            })
          }
        >
          Đăng xuất
        </button>
      </section>

      {(error || notice) && (
        <p className={error ? 'inline-error' : 'inline-success'} role={error ? 'alert' : 'status'}>
          {error ?? notice}
        </p>
      )}

      <section className="panel" aria-labelledby="create-user-title">
        <div className="panel-heading">
          <div>
            <h2 id="create-user-title">Mời người dùng</h2>
            <p>
              Tài khoản mới chờ người nhận đặt mật khẩu bằng mã một lần; mã không được lưu dạng rõ.
            </p>
          </div>
        </div>
        <form className="form-grid form-grid-wide" onSubmit={submitCreate}>
          <label>
            Họ tên
            <input name="display_name" required maxLength={100} />
          </label>
          <label>
            Email
            <input name="email" type="email" required />
          </label>
          <label>
            Thời hạn lời mời (giờ)
            <input name="valid_hours" type="number" min={1} max={168} defaultValue={24} required />
          </label>
          <button className="button" disabled={busy}>
            Tạo lời mời
          </button>
        </form>
        {invitation && (
          <div className="credential-notice" role="status">
            <strong>Mã lời mời dùng một lần</strong>
            <code>{invitation.one_time_token}</code>
            <span>Hết hạn: {new Date(invitation.expires_at).toLocaleString('vi-VN')}</span>
            <span>Chuyển qua kênh được phê duyệt; không chụp màn hình hoặc đưa vào log.</span>
          </div>
        )}
      </section>

      {createdUser && (
        <section className="panel managed-user" aria-labelledby="managed-user-title">
          <div className="panel-heading">
            <div>
              <h2 id="managed-user-title">Tài khoản vừa mời</h2>
              <p>
                {createdUser.display_name} · {createdUser.email} · {createdUser.status}
              </p>
            </div>
          </div>
          {STATUS_CHANGE_OPTIONS[createdUser.status].length === 0 ? (
            <div>
              <p>Tài khoản đang chờ phải hoàn tất lời mời trước khi đổi trạng thái.</p>
              <div className="button-row">
                <button
                  className="button button-secondary"
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      const issued = await reissueAdminInvitation(createdUser.id);
                      setInvitation(issued);
                      setNotice('Đã phát hành lại lời mời; mã cũ không còn hiệu lực.');
                    })
                  }
                >
                  Phát hành lại lời mời
                </button>
                <button
                  className="button button-secondary"
                  disabled={busy}
                  onClick={() =>
                    void run(async () => {
                      await cancelAdminInvitation(createdUser.id);
                      setInvitation(null);
                      setNotice('Đã hủy mã lời mời đang còn hiệu lực.');
                    })
                  }
                >
                  Hủy mã lời mời
                </button>
              </div>
            </div>
          ) : (
            <form
              key={createdUser.status}
              className="form-grid compact-form"
              onSubmit={submitStatus}
            >
              <label>
                Trạng thái
                <select name="status" required defaultValue="">
                  <option value="" disabled>
                    Chọn trạng thái
                  </option>
                  {STATUS_CHANGE_OPTIONS[createdUser.status].map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Lý do
                <input name="reason" maxLength={500} />
              </label>
              <button className="button button-secondary" disabled={busy}>
                Cập nhật trạng thái
              </button>
            </form>
          )}

          <form className="form-grid role-form" onSubmit={submitGrant}>
            <h3>Cấp vai trò có scope</h3>
            <label>
              Vai trò
              <select name="role_id" required defaultValue="">
                <option value="" disabled>
                  Chọn vai trò
                </option>
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name_vi}
                  </option>
                ))}
              </select>
            </label>
            <label>
              School ID
              <input name="school_id" required pattern="[0-9a-fA-F-]{36}" />
            </label>
            <label>
              Academic year ID
              <input name="academic_year_id" required pattern="[0-9a-fA-F-]{36}" />
            </label>
            <label>
              Khối (tùy chọn)
              <input name="grade_id" type="number" min={1} max={12} />
            </label>
            <p className="form-note">Scope toàn cục bị chặn cho đến khi OD-008 được chốt.</p>
            <button className="button button-secondary" disabled={busy}>
              Cấp vai trò
            </button>
          </form>

          {grant && grant.is_active && (
            <form className="form-grid compact-form" onSubmit={submitRevoke}>
              <h3>Thu hồi vai trò vừa cấp</h3>
              <label>
                Lý do thu hồi
                <input name="reason" required maxLength={500} />
              </label>
              <button className="button button-secondary" disabled={busy}>
                Thu hồi
              </button>
            </form>
          )}
        </section>
      )}
    </div>
  );
}
