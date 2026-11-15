import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ThemeProvider, useTheme } from './ThemeProvider';

function Controls() {
  const { mode, setMode } = useTheme();
  return <button onClick={() => setMode('dark')}>{mode}</button>;
}

describe('theme', () => {
  it('uses light mode by default', () => {
    render(
      <ThemeProvider>
        <Controls />
      </ThemeProvider>,
    );
    expect(screen.getByRole('button')).toHaveTextContent('light');
    expect(document.documentElement).toHaveAttribute('data-theme', 'light');
  });

  it('treats the legacy system preference as light mode', () => {
    localStorage.setItem('eduops.theme', 'system');
    render(
      <ThemeProvider>
        <Controls />
      </ThemeProvider>,
    );
    expect(screen.getByRole('button')).toHaveTextContent('light');
    expect(document.documentElement).toHaveAttribute('data-theme', 'light');
  });

  it('restores a saved preference', () => {
    localStorage.setItem('eduops.theme', 'dark');
    render(
      <ThemeProvider>
        <Controls />
      </ThemeProvider>,
    );
    expect(screen.getByRole('button')).toHaveTextContent('dark');
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
  });

  it('persists a selection', () => {
    render(
      <ThemeProvider>
        <Controls />
      </ThemeProvider>,
    );
    fireEvent.click(screen.getByRole('button'));
    expect(localStorage.getItem('eduops.theme')).toBe('dark');
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
  });

  it('works when localStorage is blocked', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    render(
      <ThemeProvider>
        <Controls />
      </ThemeProvider>,
    );
    fireEvent.click(screen.getByRole('button'));
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
  });
});
