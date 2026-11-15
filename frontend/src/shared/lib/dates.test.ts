import { describe, expect, it } from 'vitest';
import { formatCalendarDate, formatTimestamp, parseCalendarDate } from './dates';

describe('calendar dates', () => {
  it('keeps a Vietnamese calendar date without shifting the day', () => {
    expect(parseCalendarDate('2026-11-12')).toBe('2026-11-12');
    expect(formatCalendarDate('2026-11-12')).toBe('12/11/2026');
    expect(formatCalendarDate('2024-02-29')).toBe('29/02/2024');
  });

  it.each(['2026-02-29', '2026-13-01', '0000-01-01', '20261112', '2026-11-12T00:00:00Z', ''])(
    'rejects invalid calendar date %s',
    (value) => expect(() => parseCalendarDate(value)).toThrow(),
  );
});

describe('offset-aware timestamps', () => {
  it('formats equivalent instants consistently in Vietnam time', () => {
    expect(formatTimestamp('2026-11-12T05:00:00Z')).toBe(
      formatTimestamp('2026-11-12T12:00:00+07:00'),
    );
  });

  it.each(['2026-11-12', '2026-11-12T12:00:00', '2026-02-30T00:00:00Z', 'invalid'])(
    'rejects invalid or timezone-free timestamps %s',
    (value) => expect(() => formatTimestamp(value)).toThrow(),
  );
});
