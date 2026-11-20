import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { TimetablesPage } from './TimetablesPage';

function jsonResponse(body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

describe('TimetablesPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('loads jobs with selected school and academic-year scope', async () => {
    const fetchMock = vi.fn((input: string | URL | Request) => {
      const url = String(input);
      if (url === '/api/v1/admin/schools') {
        return jsonResponse([
          { id: '10000000-0000-4000-8000-000000000001', name: 'Trường A' },
        ]);
      }
      if (url === '/api/v1/admin/academic-years') {
        return jsonResponse([
          { id: '20000000-0000-4000-8000-000000000001', name: '2026-2027' },
        ]);
      }
      if (url.startsWith('/api/v1/admin/timetables/jobs')) {
        return jsonResponse([]);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<TimetablesPage />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/v1/admin/timetables/jobs?school_id=10000000-0000-4000-8000-000000000001&academic_year_id=20000000-0000-4000-8000-000000000001',
        expect.any(Object),
      );
    });

    fireEvent.change(screen.getByLabelText('Trường'), {
      target: { value: '10000000-0000-4000-8000-000000000001' },
    });
    fireEvent.change(screen.getByLabelText('Năm học'), {
      target: { value: '20000000-0000-4000-8000-000000000001' },
    });
  });

  it('submits no client-controlled slots or closed slots', async () => {
    const fetchMock = vi.fn((input: string | URL | Request, init?: RequestInit) => {
      const url = String(input);
      if (init?.method === 'POST') {
        return jsonResponse({
          id: '30000000-0000-4000-8000-000000000001',
          school_id: '10000000-0000-4000-8000-000000000001',
          academic_year_id: '20000000-0000-4000-8000-000000000001',
          status: 'completed',
          solver_status: 'feasible',
          snapshot_checksum: 'synthetic',
          result: {},
          error: null,
          time_limit_seconds: 10,
          created_at: '2026-11-20T18:00:00Z',
          started_at: '2026-11-20T18:00:00Z',
          completed_at: '2026-11-20T18:00:01Z',
        });
      }
      if (url === '/api/v1/admin/schools') {
        return jsonResponse([
          { id: '10000000-0000-4000-8000-000000000001', name: 'Trường A' },
        ]);
      }
      if (url === '/api/v1/admin/academic-years') {
        return jsonResponse([
          { id: '20000000-0000-4000-8000-000000000001', name: '2026-2027' },
        ]);
      }
      if (url.startsWith('/api/v1/admin/timetables/jobs')) {
        return jsonResponse([]);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<TimetablesPage />);
    await screen.findByRole('option', { name: 'Trường A' });

    fireEvent.click(screen.getByRole('button', { name: 'Chạy CP-SAT' }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/v1/admin/timetables/jobs',
        expect.objectContaining({ method: 'POST' }),
      );
    });

    const postCall = fetchMock.mock.calls.find(([, init]) => init?.method === 'POST');
    expect(postCall).toBeDefined();
    const body = JSON.parse(String((postCall?.[1] as RequestInit).body));
    expect(body).not.toHaveProperty('slots');
    expect(body).not.toHaveProperty('closed_slot_ids');
  });
});
