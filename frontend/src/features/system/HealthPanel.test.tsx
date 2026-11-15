import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { HealthPanel } from './HealthPanel';
import { readSystemHealth } from '../../shared/api/client';

vi.mock('../../shared/api/client', () => ({ readSystemHealth: vi.fn() }));

describe('health states', () => {
  it('shows loading and supports retry after a network failure', async () => {
    const read = vi.mocked(readSystemHealth);
    read.mockRejectedValueOnce(new Error('network')).mockResolvedValue({
      live: {
        status: 'ok',
        service: 'eduops360-api',
        version: '0.1.0',
        checked_at: '2026-11-12T05:00:00Z',
      },
      ready: { status: 'ready', database: 'ok', checked_at: '2026-11-12T05:00:00Z' },
    });
    render(<HealthPanel />);
    expect(screen.getByRole('status')).toHaveTextContent('Đang kiểm tra kết nối');
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa kết nối được API');
    fireEvent.click(screen.getByRole('button', { name: /Kiểm tra lại/ }));
    expect(await screen.findByText('Đã kết nối')).toBeInTheDocument();
    expect(read).toHaveBeenCalledTimes(2);
  });

  it('shows a database outage without claiming readiness', async () => {
    vi.mocked(readSystemHealth).mockResolvedValue({
      live: {
        status: 'ok',
        service: 'eduops360-api',
        version: '0.1.0',
        checked_at: '2026-11-12T05:00:00Z',
      },
      ready: { status: 'unavailable', database: 'unavailable', checked_at: '2026-11-12T05:00:00Z' },
    });
    render(<HealthPanel />);
    expect(await screen.findByText('Chưa sẵn sàng')).toBeInTheDocument();
    expect(screen.getByText('Đang hoạt động')).toBeInTheDocument();
  });
});
