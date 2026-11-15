export function parseCalendarDate(value: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || value.startsWith('0000')) {
    throw new Error('Ngày phải có dạng YYYY-MM-DD với năm từ 0001.');
  }
  const date = new Date(`${value}T00:00:00Z`);
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== value) {
    throw new Error('Ngày không hợp lệ.');
  }
  return value;
}

export function formatCalendarDate(value: string): string {
  const date = new Date(`${parseCalendarDate(value)}T00:00:00Z`);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(date);
}

export function parseTimestamp(value: string): Date {
  const pattern =
    /^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/i;
  if (typeof value !== 'string' || !pattern.test(value)) {
    throw new Error('Thời điểm phải có ngày, giờ và múi giờ.');
  }
  parseCalendarDate(value.slice(0, 10));
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) throw new Error('Thời điểm không hợp lệ.');
  return date;
}

export function formatTimestamp(value: string): string {
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'medium',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(parseTimestamp(value));
}
