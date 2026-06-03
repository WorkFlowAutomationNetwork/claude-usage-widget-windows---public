"""Claude Usage Widget — entry point."""
from __future__ import annotations

import datetime
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.messagebox as mb

from widget.api import get_org_id, get_usage, WidgetAPIError
from widget.config import load as load_cfg, save as save_cfg, DEFAULT_PATH
from widget.poller import Poller
from widget.tray import TrayIcon
from widget.ui import UsageWindow, THEME


def _make_fetch(cfg: dict):
    """Return a callable that fetches usage and returns normalised data dict."""
    def fetch() -> dict:
        sk  = cfg.get("session_key")
        oid = cfg.get("org_id")
        if not sk:
            return {"session_pct": None, "session_secs": None,
                    "weekly_pct": None, "weekly_secs": None,
                    "error": "No session key — open tray menu to set one"}
        if not oid:
            oid = get_org_id(sk)
            if oid:
                cfg["org_id"] = oid
                save_cfg(cfg)
            else:
                return {"session_pct": None, "session_secs": None,
                        "weekly_pct": None, "weekly_secs": None,
                        "error": "Could not resolve org ID"}

        raw = get_usage(sk, oid)
        five_h  = raw.get("five_hour") or {}
        seven_d = raw.get("seven_day") or {}

        def _secs(resets_at):
            if not resets_at:
                return None
            try:
                dt  = datetime.datetime.fromisoformat(resets_at.replace("Z", "+00:00"))
                now = datetime.datetime.now(datetime.timezone.utc)
                return max(0, int((dt - now).total_seconds()))
            except ValueError:
                return None

        return {
            "session_pct":  five_h.get("utilization"),
            "session_secs": _secs(five_h.get("resets_at")),
            "weekly_pct":   seven_d.get("utilization"),
            "weekly_secs":  _secs(seven_d.get("resets_at")),
            "error": None,
        }
    return fetch


def _ask_session_key(cfg: dict) -> bool:
    """Show dialog asking for session key. Returns True if key was saved."""
    root = tk.Tk()
    root.withdraw()
    key = sd.askstring(
        "Claude Usage Widget — Session Key",
        "Paste your claude.ai sessionKey cookie value.\n\n"
        "How to find it:\n"
        "1. Open claude.ai in Chrome and log in\n"
        "2. Press F12 -> Application -> Cookies -> https://claude.ai\n"
        "3. Copy the value of the 'sessionKey' cookie",
        parent=root,
    )
    root.destroy()
    if not key or not key.strip():
        return False
    cfg["session_key"] = key.strip()
    cfg["org_id"] = None
    save_cfg(cfg)
    return True


def main():
    cfg = load_cfg()

    # First-run: no session key
    if not cfg.get("session_key"):
        root = tk.Tk()
        root.withdraw()
        want_key = mb.askyesno(
            "Claude Usage Widget",
            "No session key found.\n\nWould you like to set one now?\n\n"
            "(You can also do this later via the system tray menu)",
            parent=root,
        )
        root.destroy()
        if want_key:
            _ask_session_key(cfg)

    fetch_fn = _make_fetch(cfg)

    # Quit handler -- defined early so tray can reference it
    def _quit():
        x, y = window.get_position()
        cfg["win_x"], cfg["win_y"] = x, y
        save_cfg(cfg)
        poller.stop()
        tray.stop()
        window.destroy()

    window = UsageWindow(
        on_close_to_tray=lambda: None,
        on_refresh=lambda: poller.refresh(),
    )
    if cfg.get("win_x") is not None and cfg.get("win_y") is not None:
        window.show(cfg["win_x"], cfg["win_y"])
    else:
        window.show(x=40, y=40)

    poller = Poller(fetch_fn=fetch_fn, interval=cfg.get("refresh_interval", 300))

    tray = TrayIcon(
        on_show_hide=lambda: window.hide() if window.is_visible() else window.show(),
        on_refresh=lambda: poller.refresh(),
        on_set_key=lambda: _ask_session_key(cfg) and poller.refresh(),
        on_quit=_quit,
        theme=THEME,
    )

    def _on_data(data: dict):
        window.update_data(data)
        pct = data.get("session_pct")
        if pct is not None:
            tray.update(pct)

    poller.on_update = _on_data
    poller.start()
    tray.start()

    window.run()  # blocks until window.destroy()


if __name__ == "__main__":
    main()
