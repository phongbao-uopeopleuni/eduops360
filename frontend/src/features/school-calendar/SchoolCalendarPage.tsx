import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

interface School {
  id: string;
  name: string;
}

interface AcademicYear {
  id: string;
  name: string;
  school_id: string;
}

interface Template {
  id: string;
  name: string;
  status: string;
  revision: number;
}

interface Holiday {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
}

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
  const response = await fetch(url, {
    credentials: 'include',
    ...init,
    headers: {
      ...(token ? { 'X-CSRF-Token': token } : {}),
      ...(init?.headers as Record<string, string> | undefined),
    },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.error?.message || `Lỗi ${response.status}`);
  return body as T;
}

async function apiPost<T>(url: string, body: unknown): Promise<T> {
  return apiFetch<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

export function SchoolCalendarPage() {
  const [schools, setSchools] = useState<School[]>([]);
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    setError(null);
    try {
      const [schoolRows, yearRows, templateRows, holidayRows] = await Promise.all([
        apiFetch<School[]>('/api/v1/admin/schools'),
        apiFetch<AcademicYear[]>('/api/v1/admin/academic-years'),
        apiFetch<Template[]>('/api/v1/admin/calendar/templates'),
        apiFetch<Holiday[]>('/api/v1/admin/calendar/holidays'),
      ]);
      setSchools(schoolRows);
      setYears(yearRows);
      setTemplates(templateRows);
      setHolidays(holidayRows);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải lịch học.');
    }
  }

  useEffect(() => {
    void Promise.resolve().then(load);
  }, []);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : 'Yêu cầu không thành công.');
    } finally {
      setBusy(false);
    }
  }

  function handleCreateTemplateActual(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const fd = new FormData(form);
    run(async () => {
      await apiPost('/api/v1/admin/calendar/templates', {
        school_id: fd.get('school_id'),
        academic_year_id: fd.get('academic_year_id'),
        name: fd.get('name'),
        slots: [
          {
            weekday: 1,
            label: String(fd.get('label') || 'Tiết 1'),
            period: 'AM',
            start_time: String(fd.get('start_time')),
            end_time: String(fd.get('end_time')),
            slot_order: 1,
          },
        ],
      });
      form.reset();
      setNotice('Đã tạo mẫu lịch.');
      await load();
    });
  }

  function handleCreateHoliday(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const fd = new FormData(form);
    run(async () => {
      await apiPost('/api/v1/admin/calendar/holidays', {
        school_id: fd.get('school_id'),
        academic_year_id: fd.get('academic_year_id'),
        name: fd.get('name'),
        start_date: fd.get('start_date'),
        end_date: fd.get('end_date'),
        source_reference: fd.get('source_reference') || null,
      });
      form.reset();
      setNotice('Đã tạo khoảng nghỉ ở trạng thái nháp.');
      await load();
    });
  }

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
      <section className="panel" aria-label="Mẫu lịch học">
        <h2>Mẫu lịch học</h2>
        {templates.length === 0 ? (
          <p>Chưa có mẫu lịch nào.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Tên</th>
                <th>Phiên bản</th>
                <th>Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {templates.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.revision}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <h3>Tạo một tiết mẫu</h3>
        <form className="form-stack" onSubmit={handleCreateTemplateActual}>
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
            Tên mẫu <input name="name" required maxLength={100} />
          </label>
          <label>
            Tên tiết <input name="label" defaultValue="Tiết 1" required maxLength={100} />
          </label>
          <label>
            Giờ bắt đầu <input name="start_time" type="time" required />
          </label>
          <label>
            Giờ kết thúc <input name="end_time" type="time" required />
          </label>
          <button className="button" type="submit" disabled={busy}>
            Tạo mẫu lịch
          </button>
        </form>
      </section>

      <section className="panel" aria-label="Kỳ nghỉ học">
        <h2>Khoảng nghỉ</h2>
        {holidays.length === 0 ? (
          <p>Chưa có khoảng nghỉ nào.</p>
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
              {holidays.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.start_date}</td>
                  <td>{item.end_date}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <h3>Tạo khoảng nghỉ nháp</h3>
        <form className="form-stack" onSubmit={handleCreateHoliday}>
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
            Tên kỳ nghỉ <input name="name" required maxLength={200} />
          </label>
          <label>
            Ngày bắt đầu <input name="start_date" type="date" required />
          </label>
          <label>
            Ngày kết thúc <input name="end_date" type="date" required />
          </label>
          <label>
            Trích dẫn nguồn <input name="source_reference" maxLength={1000} />
          </label>
          <button className="button" type="submit" disabled={busy}>
            Tạo kỳ nghỉ
          </button>
        </form>
      </section>
    </>
  );
}
