import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';

interface Job {
  id: string;
  status: string;
  solver_status: string | null;
  snapshot_checksum: string;
  result: Record<string, unknown>;
  error: string | null;
  created_at: string;
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
  const response = await fetch(url, {
    credentials: 'include',
    ...init,
    headers: {
      ...(csrfToken() ? { 'X-CSRF-Token': csrfToken() as string } : {}),
      ...(init?.headers as Record<string, string> | undefined),
    },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.error?.message || `Lỗi ${response.status}`);
  return body as T;
}

export function TimetablesPage() {
  const [schools, setSchools] = useState<{ id: string; name: string }[]>([]);
  const [years, setYears] = useState<{ id: string; name: string }[]>([]);
  const [selectedSchoolId, setSelectedSchoolId] = useState('');
  const [selectedYearId, setSelectedYearId] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const loadJobs = useCallback(async (schoolId: string, yearId: string) => {
    if (!schoolId || !yearId) {
      setJobs([]);
      return;
    }
    const params = new URLSearchParams({
      school_id: schoolId,
      academic_year_id: yearId,
    });
    const jobRows = await apiFetch<Job[]>(`/api/v1/admin/timetables/jobs?${params}`);
    setJobs(jobRows);
  }, []);

  const load = useCallback(async () => {
    try {
      const [schoolRows, yearRows] = await Promise.all([
        apiFetch<{ id: string; name: string }[]>('/api/v1/admin/schools'),
        apiFetch<{ id: string; name: string }[]>('/api/v1/admin/academic-years'),
      ]);
      setSchools(schoolRows);
      setYears(yearRows);
      const schoolId = schoolRows[0]?.id || '';
      const yearId = yearRows[0]?.id || '';
      setSelectedSchoolId(schoolId);
      setSelectedYearId(yearId);
      await loadJobs(schoolId, yearId);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Không thể tải thời khóa biểu.');
    }
  }, [loadJobs]);

  useEffect(() => {
    void Promise.resolve().then(load);
  }, [load]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const fd = new FormData(form);
    setBusy(true);
    setError(null);
    setNotice(null);
    void (async () => {
      try {
        const classCount = Number(fd.get('class_count') || 5);
        const assignments = Array.from({ length: classCount }, (_, index) => ({
          assignment_id: `assignment-${index + 1}`,
          teacher_id: `teacher-${index + 1}`,
          class_id: `class-${index + 1}`,
          subject_id: 'subject-demo',
          room_id: `room-${index + 1}`,
          required_lessons: 2,
        }));
        const job = await apiFetch<Job>('/api/v1/admin/timetables/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            school_id: fd.get('school_id'),
            academic_year_id: fd.get('academic_year_id'),
            assignments,
            time_limit_seconds: 10,
            random_seed: 360,
          }),
        });
        setNotice(`Đã chạy solver: ${job.solver_status || job.status}`);
        await load();
      } catch (submitError) {
        setError(submitError instanceof Error ? submitError.message : 'Không thể chạy solver.');
      } finally {
        setBusy(false);
        form.reset();
      }
    })();
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
      <section className="panel" aria-label="Tạo thời khóa biểu">
        <h2>Chạy solver giả lập</h2>
        <form className="form-stack" onSubmit={handleSubmit}>
          <label>
            Trường
            <select
              name="school_id"
              required
              value={selectedSchoolId}
              onChange={(event) => {
                const schoolId = event.target.value;
                setSelectedSchoolId(schoolId);
                void loadJobs(schoolId, selectedYearId);
              }}
            >
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
            <select
              name="academic_year_id"
              required
              value={selectedYearId}
              onChange={(event) => {
                const yearId = event.target.value;
                setSelectedYearId(yearId);
                void loadJobs(selectedSchoolId, yearId);
              }}
            >
              <option value="">— Chọn —</option>
              {years.map((year) => (
                <option key={year.id} value={year.id}>
                  {year.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Số lớp giả lập
            <input name="class_count" type="number" min={1} max={80} defaultValue={5} required />
          </label>
          <button className="button" type="submit" disabled={busy}>
            Chạy CP-SAT
          </button>
        </form>
      </section>
      <section className="panel" aria-label="Job solver">
        <h2>Job gần đây</h2>
        {jobs.length === 0 ? (
          <p>Chưa có job nào.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Thời điểm</th>
                <th>Trạng thái</th>
                <th>Solver</th>
                <th>Lỗi</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id}>
                  <td>{new Date(job.created_at).toLocaleString('vi-VN')}</td>
                  <td>{job.status}</td>
                  <td>{job.solver_status || '—'}</td>
                  <td>{job.error || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </>
  );
}
