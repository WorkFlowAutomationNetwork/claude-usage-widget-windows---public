"""Background thread that polls the claude.ai usage API."""
from __future__ import annotations

import threading
from typing import Callable, Optional


class Poller:
    """Calls `fetch_fn()` every `interval` seconds, fires `on_update(data)`.

    `fetch_fn` must return a dict:
        {"session_pct": float, "session_secs": int|None,
         "weekly_pct": float|None, "weekly_secs": int|None,
         "error": str|None}
    or raise any exception (which becomes {"error": str, ...}).
    """

    def __init__(self, fetch_fn: Callable, interval: float = 300):
        self._fetch = fetch_fn
        self._interval = interval
        self._stop_event = threading.Event()
        self._refresh_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.on_update: Callable[[dict], None] = lambda d: None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._refresh_event.set()

    def refresh(self) -> None:
        """Trigger an immediate poll without waiting for the interval."""
        self._refresh_event.set()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._do_fetch()
            self._refresh_event.wait(timeout=self._interval)
            self._refresh_event.clear()

    def _do_fetch(self) -> None:
        try:
            data = self._fetch()
            if not isinstance(data, dict):
                data = {}
            data.setdefault("error", None)
        except Exception as e:
            data = {
                "session_pct": None, "session_secs": None,
                "weekly_pct": None, "weekly_secs": None,
                "error": str(e),
            }
        self.on_update(data)
