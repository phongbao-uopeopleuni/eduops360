import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

function csrfToken() {
  const prefix = 'eduops_csrf=';
  const value = document.cookie
    .split(';')
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix));
  return value ? decodeURIComponent(value.slice(prefix.length)) : null;
}

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const token = csrfToken();
  const headers: Record<string, string> = {
    ...(token ? { 'X-CSRF-Token': token } : {}),
    ...(init?.headers as Record<string, string> | undefined),
  };
  const res = await fetch(url, { credentials: 'include', ...init, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const msg = body?.error?.message || `Lỗi ${res.status}`;
    throw new Error(msg);
  }
  return res.json();
}

async function apiPost<T>(url: string, body: unknown): Promise<T> {
  const token = csrfToken();
  return apiFetch<T>(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-CSRF-Token': token } : {}),
    },
    body: JSON.stringify(body),
  });
}

interface School {
  id: string;
  code: string;
  name: string;
  timezone: string;
  address: string | null;
}

interface AcademicYear {
  id: string;
  school_id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
}

interface SchoolClass {
  id: string;
  school_id: string;
  academic_year_id: string;
  name: string;
  grade: number;
  homeroom_teacher_name: string | null;
}

interface Student {
  id: string;
  school_id: string;
  student_code: string;
  full_name: string;
  date_of_birth: string | null;
  gender: string | null;
  status: string;
}

interface Enrollment {
  id: string;
  student_id: string;
  school_class_id: string;
  academic_year_id: string;
  status: string;
  enrolled_at: string;
}

interface ImportPreviewRow {
  row_number: number;
  student_code: string | null;
  status: string;
  normalized_values: Record<string, string>;
  errors: { column: string; code: string }[];
}

interface ImportPreview {
  id: string;
  state: string;
  checksum: string;
  counts: Record<string, number>;
  rows: ImportPreviewRow[];
}

type Tab = 'schools' | 'years' | 'classes' | 'students' | 'enrollments' | 'import';

function msg(e: unknown) {
  return e instanceof Error ? e.message : 'Yêu cầu không thành công.';
}

export function StudentManagementPage() {
  const [tab, setTab] = useState<Tab>('schools');
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [schools, setSchools] = useState<School[]>([]);
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [classes, setClasses] = useState<SchoolClass[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [importPreview, setImportPreview] = useState<ImportPreview | null>(null);

  async function loadSchools() {
    try {
      setSchools(await apiFetch('/api/v1/admin/schools'));
    } catch (e) {
      setError(msg(e));
    }
  }
  async function loadYears() {
    try {
      setYears(await apiFetch('/api/v1/admin/academic-years'));
    } catch (e) {
      setError(msg(e));
    }
  }
  async function loadClasses() {
    try {
      setClasses(await apiFetch('/api/v1/admin/classes'));
    } catch (e) {
      setError(msg(e));
    }
  }
  async function loadStudents() {
    try {
      setStudents(await apiFetch('/api/v1/admin/students'));
    } catch (e) {
      setError(msg(e));
    }
  }
  async function loadEnrollments() {
    try {
      setEnrollments(await apiFetch('/api/v1/admin/enrollments'));
    } catch (e) {
      setError(msg(e));
    }
  }

  useEffect(() => {
    void Promise.resolve().then(() => {
      loadSchools();
      loadYears();
    });
  }, []);

  useEffect(() => {
    void Promise.resolve().then(() => {
      if (tab === 'classes') loadClasses();
      if (tab === 'students') loadStudents();
      if (tab === 'enrollments') {
        loadEnrollments();
        loadStudents();
        loadClasses();
      }
    });
  }, [tab]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
    } catch (e) {
      setError(msg(e));
    } finally {
      setBusy(false);
    }
  }

  function handleCreateSchool(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      await apiPost('/api/v1/admin/schools', {
        code: fd.get('code'),
        name: fd.get('name'),
        timezone: fd.get('timezone') || 'Asia/Ho_Chi_Minh',
      });
      setNotice('Đã tạo trường.');
      form.reset();
      await loadSchools();
    });
  }

  function handleCreateYear(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      await apiPost('/api/v1/admin/academic-years', {
        school_id: fd.get('school_id'),
        name: fd.get('name'),
        start_date: fd.get('start_date'),
        end_date: fd.get('end_date'),
      });
      setNotice('Đã tạo năm học.');
      form.reset();
      await loadYears();
    });
  }

  function handleCreateClass(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      await apiPost('/api/v1/admin/classes', {
        school_id: fd.get('school_id'),
        academic_year_id: fd.get('academic_year_id'),
        name: fd.get('name'),
        grade: Number(fd.get('grade')),
      });
      setNotice('Đã tạo lớp.');
      form.reset();
      await loadClasses();
    });
  }

  function handleCreateStudent(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      await apiPost('/api/v1/admin/students', {
        school_id: fd.get('school_id'),
        student_code: fd.get('student_code'),
        full_name: fd.get('full_name'),
        date_of_birth: fd.get('date_of_birth') || null,
        gender: fd.get('gender') || null,
      });
      setNotice('Đã tạo học sinh.');
      form.reset();
      await loadStudents();
    });
  }

  function handleCreateEnrollment(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      await apiPost('/api/v1/admin/enrollments', {
        student_id: fd.get('student_id'),
        school_class_id: fd.get('school_class_id'),
        academic_year_id: fd.get('academic_year_id'),
      });
      setNotice('Đã ghi danh.');
      form.reset();
      await loadEnrollments();
    });
  }

  function handlePreviewImport(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const form = e.currentTarget;
    run(async () => {
      const res = await fetch('/api/v1/admin/student-import/preview', {
        method: 'POST',
        credentials: 'include',
        headers: csrfToken() ? { 'X-CSRF-Token': csrfToken() as string } : {},
        body: fd,
      });
      const body = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(body?.error?.message || `Lỗi ${res.status}`);
      }
      setImportPreview(body as ImportPreview);
      setNotice(
        body.state === 'ready'
          ? 'Đã kiểm tra lô. Có thể xác nhận nhập.'
          : 'Lô cần sửa các dòng lỗi hoặc xung đột.',
      );
      form.reset();
    });
  }

  function handleCommitImport() {
    if (!importPreview) return;
    run(async () => {
      const result = await apiPost<{ id: string; state: string; counts: Record<string, number> }>(
        `/api/v1/admin/student-import/${importPreview.id}/commit`,
        {},
      );
      setImportPreview((previous) =>
        previous ? { ...previous, state: result.state, counts: result.counts } : previous,
      );
      setNotice(
        `Đã nhập lô: ${result.counts.created ?? 0} học sinh mới, ${result.counts.enrolled ?? 0} ghi danh mới.`,
      );
      await loadStudents();
    });
  }

  function handleExportStudents(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    run(async () => {
      const schoolId = String(fd.get('school_id') || '');
      const yearId = String(fd.get('academic_year_id') || '');
      const url = `/api/v1/admin/students/export?school_id=${encodeURIComponent(schoolId)}&academic_year_id=${encodeURIComponent(yearId)}`;
      const res = await fetch(url, {
        credentials: 'include',
        headers: csrfToken() ? { 'X-CSRF-Token': csrfToken() as string } : {},
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.error?.message || `Lỗi ${res.status}`);
      }
      const blob = await res.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = downloadUrl;
      anchor.download = 'students.csv';
      anchor.click();
      URL.revokeObjectURL(downloadUrl);
      setNotice('Đã tải CSV xuất học sinh.');
    });
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'schools', label: 'Trường' },
    { key: 'years', label: 'Năm học' },
    { key: 'classes', label: 'Lớp' },
    { key: 'students', label: 'Học sinh' },
    { key: 'enrollments', label: 'Ghi danh' },
    { key: 'import', label: 'Nhập/Xuất CSV' },
  ];

  return (
    <>
      {error && (
        <p className="flash flash--error" role="alert">
          {error}
        </p>
      )}
      {notice && (
        <p className="flash flash--ok" role="status">
          {notice}
        </p>
      )}

      <nav className="tab-bar" aria-label="Mục quản lý">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            className={`tab-btn${tab === t.key ? ' tab-btn--active' : ''}`}
            onClick={() => {
              setTab(t.key);
              setError(null);
              setNotice(null);
            }}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'schools' && (
        <section className="panel" aria-label="Trường">
          <h2>Danh sách trường</h2>
          {schools.length === 0 ? (
            <p>Chưa có trường nào. Tạo trường đầu tiên bên dưới.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Mã</th>
                  <th>Tên trường</th>
                  <th>Múi giờ</th>
                </tr>
              </thead>
              <tbody>
                {schools.map((s) => (
                  <tr key={s.id}>
                    <td>{s.code}</td>
                    <td>{s.name}</td>
                    <td>{s.timezone}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <h3>Tạo trường mới</h3>
          <form className="form-stack" onSubmit={handleCreateSchool}>
            <label>
              Mã trường <input name="code" required maxLength={50} />
            </label>
            <label>
              Tên trường <input name="name" required maxLength={200} />
            </label>
            <label>
              Múi giờ <input name="timezone" defaultValue="Asia/Ho_Chi_Minh" maxLength={100} />
            </label>
            <button type="submit" className="button" disabled={busy}>
              Tạo trường
            </button>
          </form>
        </section>
      )}

      {tab === 'years' && (
        <section className="panel" aria-label="Năm học">
          <h2>Danh sách năm học</h2>
          {years.length === 0 ? (
            <p>Chưa có năm học nào.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Tên</th>
                  <th>Bắt đầu</th>
                  <th>Kết thúc</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {years.map((y) => (
                  <tr key={y.id}>
                    <td>{y.name}</td>
                    <td>{y.start_date}</td>
                    <td>{y.end_date}</td>
                    <td>{y.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <h3>Tạo năm học mới</h3>
          <form className="form-stack" onSubmit={handleCreateYear}>
            <label>
              Trường
              <select name="school_id" required>
                <option value="">— Chọn trường —</option>
                {schools.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Tên năm học <input name="name" required placeholder="2026-2027" maxLength={50} />
            </label>
            <label>
              Ngày bắt đầu <input name="start_date" type="date" required />
            </label>
            <label>
              Ngày kết thúc <input name="end_date" type="date" required />
            </label>
            <button type="submit" className="button" disabled={busy}>
              Tạo năm học
            </button>
          </form>
        </section>
      )}

      {tab === 'classes' && (
        <section className="panel" aria-label="Lớp học">
          <h2>Danh sách lớp</h2>
          {classes.length === 0 ? (
            <p>Chưa có lớp nào.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Tên lớp</th>
                  <th>Khối</th>
                  <th>GVCN</th>
                </tr>
              </thead>
              <tbody>
                {classes.map((c) => (
                  <tr key={c.id}>
                    <td>{c.name}</td>
                    <td>{c.grade}</td>
                    <td>{c.homeroom_teacher_name || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <h3>Tạo lớp mới</h3>
          <form className="form-stack" onSubmit={handleCreateClass}>
            <label>
              Trường
              <select name="school_id" required>
                <option value="">— Chọn —</option>
                {schools.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Năm học
              <select name="academic_year_id" required>
                <option value="">— Chọn —</option>
                {years.map((y) => (
                  <option key={y.id} value={y.id}>
                    {y.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Tên lớp <input name="name" required placeholder="1A" maxLength={50} />
            </label>
            <label>
              Khối <input name="grade" type="number" min={1} max={12} required />
            </label>
            <button type="submit" className="button" disabled={busy}>
              Tạo lớp
            </button>
          </form>
        </section>
      )}

      {tab === 'students' && (
        <section className="panel" aria-label="Học sinh">
          <h2>Danh sách học sinh</h2>
          {students.length === 0 ? (
            <p>Chưa có học sinh nào.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Mã HS</th>
                  <th>Họ tên</th>
                  <th>Ngày sinh</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id}>
                    <td>{s.student_code}</td>
                    <td>{s.full_name}</td>
                    <td>{s.date_of_birth || '—'}</td>
                    <td>{s.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <h3>Thêm học sinh</h3>
          <form className="form-stack" onSubmit={handleCreateStudent}>
            <label>
              Trường
              <select name="school_id" required>
                <option value="">— Chọn —</option>
                {schools.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Mã học sinh <input name="student_code" required maxLength={50} />
            </label>
            <label>
              Họ tên <input name="full_name" required maxLength={200} />
            </label>
            <label>
              Ngày sinh <input name="date_of_birth" type="date" />
            </label>
            <label>
              Giới tính
              <select name="gender">
                <option value="">— Không chọn —</option>
                <option value="nam">Nam</option>
                <option value="nữ">Nữ</option>
              </select>
            </label>
            <button type="submit" className="button" disabled={busy}>
              Thêm học sinh
            </button>
          </form>
        </section>
      )}

      {tab === 'enrollments' && (
        <section className="panel" aria-label="Ghi danh">
          <h2>Danh sách ghi danh</h2>
          {enrollments.length === 0 ? (
            <p>Chưa có bản ghi nào.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Học sinh</th>
                  <th>Lớp</th>
                  <th>Trạng thái</th>
                  <th>Ngày ghi danh</th>
                </tr>
              </thead>
              <tbody>
                {enrollments.map((en) => {
                  const st = students.find((s) => s.id === en.student_id);
                  const cl = classes.find((c) => c.id === en.school_class_id);
                  return (
                    <tr key={en.id}>
                      <td>{st?.full_name || en.student_id.slice(0, 8)}</td>
                      <td>{cl?.name || en.school_class_id.slice(0, 8)}</td>
                      <td>{en.status}</td>
                      <td>{new Date(en.enrolled_at).toLocaleDateString('vi-VN')}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
          <h3>Ghi danh học sinh</h3>
          <form className="form-stack" onSubmit={handleCreateEnrollment}>
            <label>
              Học sinh
              <select name="student_id" required>
                <option value="">— Chọn —</option>
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.full_name} ({s.student_code})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Lớp
              <select name="school_class_id" required>
                <option value="">— Chọn —</option>
                {classes.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} (Khối {c.grade})
                  </option>
                ))}
              </select>
            </label>
            <label>
              Năm học
              <select name="academic_year_id" required>
                <option value="">— Chọn —</option>
                {years.map((y) => (
                  <option key={y.id} value={y.id}>
                    {y.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className="button" disabled={busy}>
              Ghi danh
            </button>
          </form>
        </section>
      )}

      {tab === 'import' && (
        <section className="panel" aria-label="Nhập và xuất CSV học sinh">
          <h2>Nhập CSV học sinh</h2>
          <p>Tệp phải dùng UTF-8 hoặc UTF-8 BOM và đúng mẫu 8 cột của hệ thống.</p>
          <form className="form-stack" onSubmit={handlePreviewImport}>
            <label>
              Trường
              <select name="school_id" required>
                <option value="">— Chọn —</option>
                {schools.map((school) => (
                  <option key={school.id} value={school.id}>
                    {school.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Năm học
              <select name="academic_year_id" required>
                <option value="">— Chọn —</option>
                {years.map((year) => (
                  <option key={year.id} value={year.id}>
                    {year.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Khóa idempotency
              <input name="idempotency_key" required minLength={8} maxLength={128} />
            </label>
            <label>
              Tệp CSV
              <input name="file" type="file" accept=".csv,text/csv" required />
            </label>
            <button type="submit" className="button" disabled={busy}>
              Kiểm tra trước
            </button>
          </form>

          {importPreview && (
            <div className="import-preview">
              <h3>Kết quả xem trước</h3>
              <p>
                Tổng: {importPreview.counts.total ?? 0} · Mới: {importPreview.counts.new ?? 0} · Đã
                tồn tại: {importPreview.counts.existing ?? 0} · Xung đột:{' '}
                {importPreview.counts.conflicting ?? 0} · Lỗi: {importPreview.counts.error ?? 0}
              </p>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Dòng</th>
                    <th>Mã HS</th>
                    <th>Trạng thái</th>
                    <th>Lỗi</th>
                  </tr>
                </thead>
                <tbody>
                  {importPreview.rows.map((row) => (
                    <tr key={row.row_number}>
                      <td>{row.row_number}</td>
                      <td>{row.student_code || '—'}</td>
                      <td>{row.status}</td>
                      <td>
                        {row.errors.length
                          ? row.errors.map((error) => `${error.column}:${error.code}`).join(', ')
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button
                type="button"
                className="button"
                disabled={
                  busy ||
                  importPreview.state !== 'ready' ||
                  (importPreview.counts.error ?? 0) > 0 ||
                  (importPreview.counts.conflicting ?? 0) > 0
                }
                onClick={handleCommitImport}
              >
                Xác nhận nhập create-only
              </button>
            </div>
          )}

          <h2>Xuất CSV học sinh</h2>
          <form className="form-stack" onSubmit={handleExportStudents}>
            <label>
              Trường
              <select name="school_id" required>
                <option value="">— Chọn —</option>
                {schools.map((school) => (
                  <option key={school.id} value={school.id}>
                    {school.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Năm học
              <select name="academic_year_id" required>
                <option value="">— Chọn —</option>
                {years.map((year) => (
                  <option key={year.id} value={year.id}>
                    {year.name}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit" className="button" disabled={busy}>
              Tải CSV BOM
            </button>
          </form>
        </section>
      )}
    </>
  );
}
