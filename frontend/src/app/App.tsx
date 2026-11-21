import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { HealthPanel } from '../features/system/HealthPanel';
import { UserManagementPage } from '../features/user-management/UserManagementPage';
import { StudentManagementPage } from '../features/student-management/StudentManagementPage';
import { SchoolCalendarPage } from '../features/school-calendar/SchoolCalendarPage';
import { TimetablesPage } from '../features/timetables/TimetablesPage';
import { useTheme } from './ThemeProvider';

type TileKind = 'students' | 'calendar';

// Decorative "soft" icons for feature tiles: gradient only on icons, per the UI spec.
function TileIcon({ kind }: { kind: TileKind }) {
  const gradient = `tile-gradient-${kind}`;
  return (
    <svg viewBox="0 0 96 96" width="96" height="96" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id={gradient} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="var(--accent)" />
          <stop offset="1" stopColor="var(--accent-lavender)" />
        </linearGradient>
      </defs>
      <rect x="14" y="18" width="60" height="62" rx="14" fill="var(--surface)" />
      {kind === 'students' && (
        <>
          <circle cx="44" cy="40" r="10" fill={`url(#${gradient})`} />
          <rect x="28" y="56" width="32" height="10" rx="5" fill={`url(#${gradient})`} />
        </>
      )}
      {kind === 'calendar' && (
        <>
          <rect x="26" y="32" width="36" height="6" rx="3" fill={`url(#${gradient})`} />
          <rect x="26" y="44" width="10" height="10" rx="3" fill={`url(#${gradient})`} />
          <rect x="39" y="44" width="10" height="10" rx="3" fill="var(--accent-soft)" />
          <rect x="52" y="44" width="10" height="10" rx="3" fill={`url(#${gradient})`} />
          <rect x="26" y="57" width="10" height="10" rx="3" fill="var(--accent-soft)" />
          <rect x="39" y="57" width="10" height="10" rx="3" fill={`url(#${gradient})`} />
        </>
      )}
      <circle cx="74" cy="22" r="12" fill={`url(#${gradient})`} />
      <path
        d="M74 16.5V22l3.5 2.5"
        fill="none"
        stroke="var(--on-accent)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Overview() {
  return (
    <>
      <section className="section hero">
        <div className="container hero__inner">
          <p className="eyebrow">Môi trường vận hành local</p>
          <h1>Không gian làm việc của nhà trường</h1>
          <p className="lead">
            Quản lý học sinh, lịch học và thời khóa biểu trên một nền tảng thống nhất.
          </p>
          <div className="hero__actions">
            <Link className="button" to="/users">
              Quản trị người dùng
            </Link>
            <Link className="button button-secondary" to="/system">
              Xem trạng thái hệ thống
            </Link>
          </div>
        </div>
      </section>

      <section className="section section--alt" aria-labelledby="roadmap-title">
        <div className="container">
          <div className="section__intro">
            <h2 id="roadmap-title">Các phân hệ đang hoạt động</h2>
            <p className="lead">Học vụ và lịch học được cung cấp trong môi trường local.</p>
          </div>
          <ul className="feature-grid">
            <li className="feature-tile">
              <div className="tile-art">
                <TileIcon kind="students" />
              </div>
              <h3>Học sinh và nhập CSV</h3>
              <p>Quản lý, nhập CSV và xuất dữ liệu</p>
            </li>
            <li className="feature-tile">
              <div className="tile-art">
                <TileIcon kind="calendar" />
              </div>
              <h3>Lịch học và thời khóa biểu</h3>
              <p>Lịch học, mẫu tiết và CP-SAT</p>
            </li>
          </ul>
        </div>
      </section>

      <section className="section" aria-labelledby="security-title">
        <div className="container zigzag">
          <div>
            <h2 id="security-title">Bảo mật là nền móng</h2>
            <ul className="bullet-list">
              <li>Backend kiểm tra quyền cho mọi thao tác; giao diện chỉ hỗ trợ người dùng.</li>
              <li>Phiên đăng nhập dùng cookie HttpOnly kèm mã chống CSRF.</li>
              <li>Mọi thay đổi tài khoản và phân quyền đều được ghi nhật ký kiểm toán.</li>
            </ul>
            <Link className="text-link" to="/users">
              Mở trang quản trị người dùng <span aria-hidden="true">→</span>
            </Link>
          </div>
          <div className="fragment" aria-hidden="true">
            <div className="fragment__card">
              <div className="fragment__header">
                <strong>Vai trò có phạm vi</strong>
                <span className="fragment__pill">Đã ghi audit</span>
              </div>
              <div className="fragment__chips">
                <span>Trường</span>
                <span>Năm học</span>
                <span>Khối 1</span>
              </div>
              <span className="skeleton" />
              <span className="skeleton skeleton--short" />
              <div className="fragment__progress">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

const isGitHubPagesPreview = import.meta.env.VITE_GITHUB_PAGES === 'true';

function PreviewNotice() {
  return (
    <div className="container" role="status">
      <p className="preview-notice">
        Bản xem trước giao diện công khai · Backend chưa được kết nối. Không nhập thông tin đăng
        nhập hoặc dữ liệu thật.
      </p>
    </div>
  );
}

function PreviewUnavailable({ title }: { title: string }) {
  return (
    <section className="panel" aria-label={title}>
      <h2>{title}</h2>
      <p>Chức năng này chưa khả dụng trong bản xem trước tĩnh vì chưa kết nối backend.</p>
    </section>
  );
}

function SystemPage() {
  return (
    <section className="page">
      <div className="container">
        <div className="page-intro">
          <p className="eyebrow">Vận hành local</p>
          <h1>Trạng thái hệ thống</h1>
          <p className="lead lead--left">Kiểm tra kết nối trước khi làm việc với hệ thống.</p>
        </div>
        {isGitHubPagesPreview ? (
          <PreviewUnavailable title="Trạng thái dịch vụ" />
        ) : (
          <HealthPanel />
        )}
      </div>
    </section>
  );
}

function UsersPage() {
  return (
    <section className="page">
      <div className="container">
        <div className="page-intro">
          <p className="eyebrow">IAM · Phase 02</p>
          <h1>Người dùng và phân quyền</h1>
          <p className="lead lead--left">
            Quản trị tài khoản, trạng thái và vai trò có scope. Backend luôn quyết định quyền.
          </p>
        </div>
        {isGitHubPagesPreview ? (
          <PreviewUnavailable title="Quản trị người dùng" />
        ) : (
          <UserManagementPage />
        )}
      </div>
    </section>
  );
}

function StudentsPage() {
  return (
    <section className="page">
      <div className="container">
        <div className="page-intro">
          <p className="eyebrow">Học vụ · Phase 03</p>
          <h1>Quản lý học sinh</h1>
          <p className="lead lead--left">Trường, năm học, lớp, học sinh và ghi danh.</p>
        </div>
        {isGitHubPagesPreview ? (
          <PreviewUnavailable title="Quản lý học sinh" />
        ) : (
          <StudentManagementPage />
        )}
      </div>
    </section>
  );
}

function CalendarPage() {
  return (
    <section className="page">
      <div className="container">
        <div className="page-intro">
          <p className="eyebrow">Thời khóa biểu · Phase 05</p>
          <h1>Lịch học và kỳ nghỉ</h1>
          <p className="lead lead--left">
            Mẫu tiết học theo năm và khoảng nghỉ trong phạm vi trường.
          </p>
        </div>
        {isGitHubPagesPreview ? <PreviewUnavailable title="Lịch học" /> : <SchoolCalendarPage />}
      </div>
    </section>
  );
}

function TimetablesPageWrapper() {
  return (
    <section className="page">
      <div className="container">
        <div className="page-intro">
          <p className="eyebrow">Thời khóa biểu · Phase 06</p>
          <h1>CP-SAT thời khóa biểu</h1>
          <p className="lead lead--left">
            Chạy giải thuật có giới hạn thời gian; kết quả ở trạng thái draft.
          </p>
        </div>
        {isGitHubPagesPreview ? <PreviewUnavailable title="Thời khóa biểu" /> : <TimetablesPage />}
      </div>
    </section>
  );
}

function NotFound() {
  return (
    <section className="section">
      <div className="container section__intro">
        <p className="eyebrow">404</p>
        <h1>Không tìm thấy trang</h1>
        <p className="lead">Đường dẫn này chưa có trong không gian làm việc.</p>
        <div className="hero__actions">
          <Link className="button" to="/">
            Về tổng quan
          </Link>
        </div>
      </div>
    </section>
  );
}

export function App() {
  const { mode, setMode } = useTheme();
  const darkMode = mode === 'dark';
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const name =
      location.pathname === '/'
        ? 'Tổng quan'
        : location.pathname === '/system'
          ? 'Trạng thái hệ thống'
          : location.pathname === '/users'
            ? 'Người dùng và phân quyền'
            : location.pathname === '/students'
              ? 'Quản lý học sinh'
              : location.pathname === '/calendar'
                ? 'Lịch học và kỳ nghỉ'
                : location.pathname === '/timetables'
                  ? 'CP-SAT thời khóa biểu'
                  : 'Không tìm thấy trang';
    document.title = `${name} · EduOps 360`;
  }, [location.pathname]);

  useEffect(() => {
    const update = () => setScrolled(window.scrollY > 8);
    update();
    window.addEventListener('scroll', update, { passive: true });
    return () => window.removeEventListener('scroll', update);
  }, []);

  return (
    <div className="app-shell">
      {isGitHubPagesPreview && <PreviewNotice />}
      <a className="skip-link" href="#main-content">
        Đến nội dung chính
      </a>
      <header className="navbar" data-scrolled={scrolled ? 'true' : undefined}>
        <div className="container navbar__inner">
          <Link className="brand" to="/" aria-label="EduOps 360 — Trang tổng quan">
            <span className="brand-mark" aria-hidden="true">
              e
            </span>
            <span>
              EduOps <strong>360</strong>
            </span>
          </Link>
          <nav aria-label="Điều hướng chính">
            <NavLink end to="/">
              Tổng quan
            </NavLink>
            <NavLink to="/system">Hệ thống</NavLink>
            <NavLink to="/users">Người dùng</NavLink>
            <NavLink to="/students">Học sinh</NavLink>
            <NavLink to="/calendar">Lịch học</NavLink>
            <NavLink to="/timetables">Thời khóa biểu</NavLink>
          </nav>
          <button
            className="theme-toggle"
            type="button"
            aria-label={darkMode ? 'Chuyển sang giao diện sáng' : 'Chuyển sang giao diện tối'}
            aria-pressed={darkMode}
            title={darkMode ? 'Giao diện sáng' : 'Giao diện tối'}
            onClick={() => setMode(darkMode ? 'light' : 'dark')}
          >
            {darkMode ? (
              <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.66 6.34l1.41-1.41" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path d="M20.4 15.1A8.5 8.5 0 0 1 8.9 3.6 8.5 8.5 0 1 0 20.4 15.1Z" />
              </svg>
            )}
          </button>
        </div>
      </header>
      <main id="main-content" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/system" element={<SystemPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/students" element={<StudentsPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/timetables" element={<TimetablesPageWrapper />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <div className="container app-footer__inner">
          <span>EduOps 360</span>
          <span>Quản lý học vụ</span>
        </div>
      </footer>
    </div>
  );
}
