import { useEffect, useState } from 'react';
import { readSystemHealth } from '../../shared/api/client';
import { formatTimestamp } from '../../shared/lib/dates';

type Health = Awaited<ReturnType<typeof readSystemHealth>>;
type HealthState = { status: 'loading' } | { status: 'error' } | { status: 'loaded'; data: Health };

export function HealthPanel() {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<HealthState>({ status: 'loading' });

  useEffect(() => {
    const controller = new AbortController();
    readSystemHealth(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) setState({ status: 'loaded', data });
      })
      .catch(() => {
        if (!controller.signal.aborted) setState({ status: 'error' });
      });
    return () => controller.abort();
  }, [attempt]);

  function retry() {
    setState({ status: 'loading' });
    setAttempt((value) => value + 1);
  }

  return (
    <section
      className="panel health-panel"
      aria-labelledby="health-title"
      aria-busy={state.status === 'loading'}
    >
      <div className="panel-heading">
        <div>
          <h2 id="health-title">Kết nối hệ thống</h2>
          <p>Trạng thái hiện tại của các dịch vụ local.</p>
        </div>
        <button
          className="button button-secondary"
          onClick={retry}
          disabled={state.status === 'loading'}
        >
          <span aria-hidden="true">↻</span> Kiểm tra lại
        </button>
      </div>
      {state.status === 'loading' && (
        <p className="loading-message" role="status">
          Đang kiểm tra kết nối…
        </p>
      )}
      {state.status === 'error' && (
        <div className="error-message" role="alert">
          <strong>Chưa kết nối được API</strong>
          <p>Vui lòng kiểm tra dịch vụ local và chọn Kiểm tra lại.</p>
        </div>
      )}
      {state.status === 'loaded' && (
        <>
          <dl className="service-list" aria-live="polite">
            <div className="service-row">
              <dt>
                <span className="service-icon" aria-hidden="true">
                  ↔
                </span>{' '}
                Dịch vụ ứng dụng
              </dt>
              <dd className="service-status positive">
                <span className="status-dot" /> Đang hoạt động
              </dd>
            </div>
            <div className="service-row">
              <dt>
                <span className="service-icon" aria-hidden="true">
                  ▤
                </span>{' '}
                Cơ sở dữ liệu
              </dt>
              <dd
                className={`service-status ${state.data.ready.database === 'ok' ? 'positive' : 'warning'}`}
              >
                <span className="status-dot" />
                {state.data.ready.database === 'ok' ? 'Đã kết nối' : 'Chưa sẵn sàng'}
              </dd>
            </div>
          </dl>
          <div className="panel-footnote">
            Kiểm tra lúc{' '}
            <time dateTime={state.data.ready.checked_at}>
              {formatTimestamp(state.data.ready.checked_at)}
            </time>
            <span>Giờ Việt Nam · UTC+07</span>
          </div>
        </>
      )}
    </section>
  );
}
