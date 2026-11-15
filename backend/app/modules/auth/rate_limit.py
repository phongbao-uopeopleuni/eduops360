from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import islice
from threading import Lock
from time import monotonic


@dataclass
class _AttemptWindow:
    attempts: deque[float] = field(default_factory=deque)


class LoginRateLimiter:
    """Bounded per-process sliding-window limiter for the local deployment.

    Account lockout remains the durable control. This limiter protects the login
    endpoint from short bursts and caps key storage to avoid memory exhaustion.
    """

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: int,
        max_keys: int = 10_000,
        eviction_scan_limit: int = 64,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if limit < 1 or window_seconds < 1 or max_keys < 1 or eviction_scan_limit < 1:
            raise ValueError("Rate-limit values must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_keys = max_keys
        self.eviction_scan_limit = eviction_scan_limit
        self._clock = clock
        self._windows: OrderedDict[str, _AttemptWindow] = OrderedDict()
        self._lock = Lock()

    def check(self, key: str) -> int | None:
        """Return retry-after seconds when blocked, otherwise None."""
        now = self._clock()
        cutoff = now - self.window_seconds
        with self._lock:
            window = self._windows.get(key)
            if window is None:
                return None
            while window.attempts and window.attempts[0] <= cutoff:
                window.attempts.popleft()
            if not window.attempts:
                del self._windows[key]
                return None
            self._windows.move_to_end(key)
            if len(window.attempts) < self.limit:
                return None
            return max(1, int(window.attempts[0] + self.window_seconds - now) + 1)

    def record_failure(self, key: str) -> None:
        now = self._clock()
        cutoff = now - self.window_seconds
        with self._lock:
            window = self._windows.get(key)
            if window is None:
                if len(self._windows) >= self.max_keys:
                    candidate_to_evict: str | None = None
                    for candidate, candidate_window in islice(
                        self._windows.items(), self.eviction_scan_limit
                    ):
                        while candidate_window.attempts and candidate_window.attempts[0] <= cutoff:
                            candidate_window.attempts.popleft()
                        if (
                            not candidate_window.attempts
                            or len(candidate_window.attempts) < self.limit
                        ):
                            candidate_to_evict = candidate
                            break
                    if candidate_to_evict is None:
                        # Preserve existing blocked identities. Durable account lockout remains
                        # the fallback when the bounded scan finds no evictable slot. The new
                        # identity is intentionally not tracked instead of doing O(max_keys)
                        # synchronous work while holding the process-wide limiter lock.
                        return
                    del self._windows[candidate_to_evict]
                window = _AttemptWindow()
                self._windows[key] = window
            while window.attempts and window.attempts[0] <= cutoff:
                window.attempts.popleft()
            window.attempts.append(now)
            self._windows.move_to_end(key)

    def reset(self, key: str) -> None:
        with self._lock:
            self._windows.pop(key, None)
