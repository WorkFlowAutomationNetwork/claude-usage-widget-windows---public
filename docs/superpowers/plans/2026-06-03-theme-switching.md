# Theme Switching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a theme registry and tray-menu "Theme →" submenu that rebuilds the widget window immediately with the selected theme and persists the choice to config.

**Architecture:** A new `widget/themes.py` holds all named theme dicts and a `get_theme(name)` lookup. `UsageWindow` is converted to a `tk.Toplevel` owned by a persistent hidden `tk.Tk` root in `main.py`, so the mainloop survives window rebuilds. The tray menu gains a "Theme →" submenu; selecting a name calls `root.after(0, _do_rebuild)` to safely rebuild on the main thread.

**Tech Stack:** Python 3.x, tkinter (Toplevel), pystray, standard unittest

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `widget/themes.py` | All named THEME dicts + `get_theme()` + `THEME_NAMES` |
| Modify | `widget/config.py` | Add `"theme": "default"` to `_DEFAULTS` |
| Modify | `widget/ui.py` | Accept `master` + `theme` params; use `Toplevel`; remove module-level `THEME` |
| Modify | `widget/tray.py` | Add `on_theme_change` param + "Theme →" submenu + `update_theme()` method |
| Modify | `main.py` | Persistent hidden root; `_do_rebuild`; `root.mainloop()` instead of `window.run()` |
| Create | `tests/test_themes.py` | Unit tests for theme registry |
| Modify | `tests/test_config.py` | Add test for "theme" default key |

---

## Task 1: Create `widget/themes.py`

**Files:**
- Create: `widget/themes.py`
- Create: `tests/test_themes.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_themes.py`:

```python
import unittest


class TestThemes(unittest.TestCase):

    def test_theme_names_is_non_empty_list(self):
        from widget.themes import THEME_NAMES
        self.assertIsInstance(THEME_NAMES, list)
        self.assertGreater(len(THEME_NAMES), 0)

    def test_default_theme_in_names(self):
        from widget.themes import THEME_NAMES
        self.assertIn("default", THEME_NAMES)

    def test_get_theme_returns_dict_with_required_keys(self):
        from widget.themes import get_theme
        required = {
            "width", "alpha", "bg", "panel", "border", "text", "muted",
            "good", "warn", "bad", "accent", "font", "font_small",
            "font_mono", "font_title", "pad", "bar_h", "gap",
            "title_h", "warn_at", "bad_at",
        }
        for name in ("default", "neon", "light", "minimal"):
            with self.subTest(theme=name):
                t = get_theme(name)
                self.assertTrue(required.issubset(t.keys()))

    def test_get_theme_falls_back_to_default_for_unknown_name(self):
        from widget.themes import get_theme
        default = get_theme("default")
        unknown = get_theme("does_not_exist")
        self.assertEqual(default, unknown)

    def test_get_theme_returns_copy(self):
        from widget.themes import get_theme
        t1 = get_theme("default")
        t2 = get_theme("default")
        t1["bg"] = "#000000"
        self.assertNotEqual(t2["bg"], "#000000")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```
python -m pytest tests/test_themes.py -v
```

Expected: errors like `ModuleNotFoundError: No module named 'widget.themes'`

- [ ] **Step 3: Create `widget/themes.py`**

```python
"""Named theme registry for the Claude Usage Widget."""
from __future__ import annotations

_THEMES: dict[str, dict] = {
    "default": {
        "width": 280,
        "alpha": 0.95,
        "bg":        "#0A0E14",
        "panel":     "#0F1419",
        "border":    "#1F2630",
        "text":      "#E6EDF3",
        "muted":     "#8B98A6",
        "good":      "#3FB68B",
        "warn":      "#E8A23B",
        "bad":       "#E5484D",
        "accent":    "#4A9EFF",
        "font":       ("Segoe UI", 10),
        "font_small": ("Segoe UI", 9),
        "font_mono":  ("Consolas", 9),
        "font_title": ("Segoe UI Semibold", 10),
        "pad":        12,
        "bar_h":       6,
        "gap":        10,
        "title_h":    28,
        "warn_at":    50,
        "bad_at":     80,
    },
    "neon": {
        "width": 280,
        "alpha": 0.95,
        "bg":        "#0D0D1A",
        "panel":     "#12122A",
        "border":    "#2D2D5E",
        "text":      "#E0E0FF",
        "muted":     "#7070AA",
        "good":      "#00FFD0",
        "warn":      "#FFD700",
        "bad":       "#FF2D78",
        "accent":    "#BD00FF",
        "font":       ("Segoe UI", 10),
        "font_small": ("Segoe UI", 9),
        "font_mono":  ("Consolas", 9),
        "font_title": ("Segoe UI Semibold", 10),
        "pad":        12,
        "bar_h":       6,
        "gap":        10,
        "title_h":    28,
        "warn_at":    50,
        "bad_at":     80,
    },
    "light": {
        "width": 280,
        "alpha": 0.97,
        "bg":        "#FFFFFF",
        "panel":     "#F5F5F5",
        "border":    "#E0E0E0",
        "text":      "#1A1A1A",
        "muted":     "#6B7280",
        "good":      "#16A34A",
        "warn":      "#D97706",
        "bad":       "#DC2626",
        "accent":    "#2563EB",
        "font":       ("Segoe UI", 10),
        "font_small": ("Segoe UI", 9),
        "font_mono":  ("Consolas", 9),
        "font_title": ("Segoe UI Semibold", 10),
        "pad":        12,
        "bar_h":       6,
        "gap":        10,
        "title_h":    28,
        "warn_at":    50,
        "bad_at":     80,
    },
    "minimal": {
        "width": 220,
        "alpha": 0.90,
        "bg":        "#111111",
        "panel":     "#111111",
        "border":    "#333333",
        "text":      "#CCCCCC",
        "muted":     "#555555",
        "good":      "#4CAF50",
        "warn":      "#FF9800",
        "bad":       "#F44336",
        "accent":    "#888888",
        "font":       ("Segoe UI", 9),
        "font_small": ("Segoe UI", 8),
        "font_mono":  ("Consolas", 9),
        "font_title": ("Segoe UI", 9),
        "pad":        8,
        "bar_h":       4,
        "gap":        8,
        "title_h":    24,
        "warn_at":    50,
        "bad_at":     80,
    },
}

THEME_NAMES: list[str] = list(_THEMES.keys())


def get_theme(name: str) -> dict:
    """Return a copy of the named theme, falling back to 'default'."""
    return dict(_THEMES.get(name, _THEMES["default"]))
```

- [ ] **Step 4: Run tests to verify they pass**

```
python -m pytest tests/test_themes.py -v
```

Expected: 5 tests PASS

- [ ] **Step 5: Commit**

```
git add widget/themes.py tests/test_themes.py
git commit -m "feat: theme registry with default/neon/light/minimal"
```

---

## Task 2: Update `widget/config.py`

**Files:**
- Modify: `widget/config.py`
- Modify: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

Add this test to `tests/test_config.py` inside `class TestConfig`:

```python
def test_load_includes_theme_default(self):
    from widget.config import load
    p = self._temp_path()
    cfg = load(p)
    self.assertEqual(cfg["theme"], "default")

def test_save_and_reload_theme(self):
    from widget.config import load, save
    p = self._temp_path()
    cfg = load(p)
    cfg["theme"] = "neon"
    save(cfg, p)
    reloaded = load(p)
    self.assertEqual(reloaded["theme"], "neon")
```

- [ ] **Step 2: Run tests to verify they fail**

```
python -m pytest tests/test_config.py::TestConfig::test_load_includes_theme_default -v
```

Expected: FAIL with `KeyError: 'theme'`

- [ ] **Step 3: Add `"theme"` to `_DEFAULTS` in `widget/config.py`**

Change the `_DEFAULTS` dict from:

```python
_DEFAULTS: dict[str, Any] = {
    "session_key": None,
    "org_id": None,
    "refresh_interval": 300,
    "win_x": None,
    "win_y": None,
}
```

To:

```python
_DEFAULTS: dict[str, Any] = {
    "session_key": None,
    "org_id": None,
    "refresh_interval": 300,
    "win_x": None,
    "win_y": None,
    "theme": "default",
}
```

- [ ] **Step 4: Run tests to verify they pass**

```
python -m pytest tests/test_config.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```
git add widget/config.py tests/test_config.py
git commit -m "feat: persist theme name in config"
```

---

## Task 3: Update `widget/ui.py`

**Files:**
- Modify: `widget/ui.py`

This task converts `UsageWindow` from owning a `tk.Tk` root to using a `tk.Toplevel` owned by an external root. It also removes the module-level `THEME` constant (moved to `widget/themes.py`) and makes `_bar_color` accept a theme dict.

There are no automated tests for this task — tkinter requires a display. Manual verification happens in Task 5.

- [ ] **Step 1: Replace `widget/ui.py` entirely**

```python
"""Floating always-on-top usage widget."""
from __future__ import annotations

import tkinter as tk
from typing import Optional


def _bar_color(pct: float, theme: dict) -> str:
    if pct >= theme["bad_at"]:  return theme["bad"]
    if pct >= theme["warn_at"]: return theme["warn"]
    return theme["good"]


def _fmt_countdown(secs: Optional[int]) -> str:
    if secs is None:
        return ""
    if secs <= 0:
        return "now"
    h, rem = divmod(secs, 3600)
    m = rem // 60
    return f"{h}h {m}m" if h else f"{m}m"


class UsageWindow:
    """Floating always-on-top tkinter Toplevel window."""

    def __init__(self, master: tk.Misc, on_close_to_tray, on_refresh, theme: dict):
        self._on_close_to_tray = on_close_to_tray
        self._on_refresh = on_refresh
        self._theme = theme
        self._data: dict = {}
        self._session_secs: Optional[int] = None
        self._weekly_secs: Optional[int] = None
        self._tick_job = None

        self._root = tk.Toplevel(master)
        self._build()

    def _build(self) -> None:
        r = self._root
        t = self._theme
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        r.attributes("-alpha", t["alpha"])
        r.configure(bg=t["bg"])
        r.resizable(False, False)

        w = t["width"]
        r.geometry(f"{w}x1")

        # ── Custom titlebar ──────────────────────────────────────────────────
        tb = tk.Frame(r, bg=t["panel"], height=t["title_h"])
        tb.pack(fill="x")
        tb.pack_propagate(False)

        tk.Label(tb, text="Claude Usage", bg=t["panel"],
                 fg=t["text"], font=t["font_title"],
                 anchor="w").pack(side="left", padx=t["pad"])

        tk.Button(tb, text="−", bg=t["panel"], fg=t["muted"],
                  relief="flat", bd=0, font=t["font"],
                  activebackground=t["border"], cursor="hand2",
                  command=self._minimize).pack(side="right", padx=(0, 4))

        tb.bind("<ButtonPress-1>",   self._drag_start)
        tb.bind("<B1-Motion>",       self._drag_move)

        # ── Separator ────────────────────────────────────────────────────────
        tk.Frame(r, bg=t["border"], height=1).pack(fill="x")

        # ── Body ─────────────────────────────────────────────────────────────
        self._body = tk.Frame(r, bg=t["bg"], padx=t["pad"], pady=t["pad"])
        self._body.pack(fill="both", expand=True)

        self._sess_label  = self._make_label("Session (5h)")
        self._sess_pct    = self._make_pct_label()
        self._sess_canvas = self._make_bar_canvas()
        self._sess_reset  = self._make_reset_label()

        tk.Frame(self._body, bg=t["border"], height=1).pack(
            fill="x", pady=(t["gap"], t["gap"]))

        self._week_label  = self._make_label("Week")
        self._week_pct    = self._make_pct_label()
        self._week_canvas = self._make_bar_canvas()
        self._week_reset  = self._make_reset_label()

        self._status = tk.Label(self._body, text="", bg=t["bg"],
                                fg=t["muted"], font=t["font_small"],
                                anchor="w")
        self._status.pack(fill="x", pady=(t["gap"], 0))

        self._drag_x = self._drag_y = 0

        r.update_idletasks()
        r.geometry(f"{w}x{r.winfo_reqheight()}")

    # ── Widget factory helpers ────────────────────────────────────────────────

    def _make_label(self, text: str) -> tk.Label:
        t = self._theme
        row = tk.Frame(self._body, bg=t["bg"])
        row.pack(fill="x")
        lbl = tk.Label(row, text=text, bg=t["bg"],
                       fg=t["muted"], font=t["font_small"], anchor="w")
        lbl.pack(side="left")
        return lbl

    def _make_pct_label(self) -> tk.Label:
        t = self._theme
        lbl = tk.Label(self._body, text="—", bg=t["bg"],
                       fg=t["text"], font=t["font_mono"], anchor="e")
        lbl.pack(fill="x")
        return lbl

    def _make_bar_canvas(self) -> tk.Canvas:
        t = self._theme
        c = tk.Canvas(self._body, height=t["bar_h"],
                      bg=t["panel"], highlightthickness=0)
        c.pack(fill="x", pady=(2, 0))
        return c

    def _make_reset_label(self) -> tk.Label:
        t = self._theme
        lbl = tk.Label(self._body, text="", bg=t["bg"],
                       fg=t["muted"], font=t["font_small"], anchor="e")
        lbl.pack(fill="x")
        return lbl

    # ── Drag ──────────────────────────────────────────────────────────────────

    def _drag_start(self, event):
        self._drag_x = event.x_root - self._root.winfo_x()
        self._drag_y = event.y_root - self._root.winfo_y()

    def _drag_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self._root.geometry(f"+{x}+{y}")

    # ── Update ────────────────────────────────────────────────────────────────

    def update_data(self, data: dict) -> None:
        """Thread-safe: schedule UI update on the main thread."""
        self._root.after(0, lambda: self._apply(data))

    def _apply(self, data: dict) -> None:
        self._data = data
        err = data.get("error")
        t = self._theme

        if err:
            self._status.config(text=f"Error: {err[:50]}", fg=t["bad"])
            self._sess_pct.config(text="—")
            self._week_pct.config(text="—")
            self._sess_reset.config(text="")
            self._week_reset.config(text="")
            self._draw_bar(self._sess_canvas, 0, t["muted"])
            self._draw_bar(self._week_canvas, 0, t["muted"])
        else:
            self._status.config(text="", fg=t["muted"])

            s_pct  = data.get("session_pct") or 0
            s_secs = data.get("session_secs")
            w_pct  = data.get("weekly_pct") or 0
            w_secs = data.get("weekly_secs")

            self._sess_pct.config(text=f"{s_pct:.1f}%", fg=_bar_color(s_pct, t))
            self._week_pct.config(text=f"{w_pct:.1f}%" if w_pct else "—",
                                  fg=_bar_color(w_pct, t) if w_pct else t["muted"])

            self._draw_bar(self._sess_canvas, s_pct, _bar_color(s_pct, t))
            self._draw_bar(self._week_canvas, w_pct, _bar_color(w_pct, t))

            self._session_secs = s_secs
            self._weekly_secs  = w_secs
            self._tick()

    def _draw_bar(self, canvas: tk.Canvas, pct: float, color: str) -> None:
        t = self._theme
        canvas.update_idletasks()
        w = canvas.winfo_width() or t["width"] - t["pad"] * 2
        h = t["bar_h"]
        canvas.delete("all")
        canvas.create_rectangle(0, 0, w, h, fill=t["panel"], outline="")
        fill_w = int(w * min(pct, 100) / 100)
        if fill_w > 0:
            canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")

    def _tick(self) -> None:
        if self._tick_job:
            self._root.after_cancel(self._tick_job)
        self._sess_reset.config(text=f"Resets in {_fmt_countdown(self._session_secs)}"
                                if self._session_secs else "")
        self._week_reset.config(text=f"Resets {_fmt_countdown(self._weekly_secs)}"
                                if self._weekly_secs else "")
        if self._session_secs and self._session_secs > 0:
            self._session_secs -= 1
        if self._weekly_secs and self._weekly_secs > 0:
            self._weekly_secs -= 1
        self._tick_job = self._root.after(1000, self._tick)

    # ── Visibility ────────────────────────────────────────────────────────────

    def show(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        if x is not None and y is not None:
            self._root.geometry(f"+{x}+{y}")
        self._root.deiconify()
        self._root.lift()

    def hide(self) -> None:
        self._root.withdraw()

    def _minimize(self) -> None:
        self.hide()
        self._on_close_to_tray()

    def is_visible(self) -> bool:
        return self._root.state() != "withdrawn"

    def get_position(self) -> tuple[int, int]:
        return self._root.winfo_x(), self._root.winfo_y()

    def destroy(self) -> None:
        if self._tick_job:
            self._root.after_cancel(self._tick_job)
        self._root.destroy()
```

- [ ] **Step 2: Commit**

```
git add widget/ui.py
git commit -m "refactor: UsageWindow uses Toplevel, accepts master + theme params"
```

---

## Task 4: Update `widget/tray.py`

**Files:**
- Modify: `widget/tray.py`

- [ ] **Step 1: Replace `widget/tray.py` entirely**

```python
"""System tray icon and menu using pystray."""
from __future__ import annotations

from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw

from widget.themes import THEME_NAMES


def _make_icon(pct: float, good: str, warn: str, bad: str,
               warn_at: int, bad_at: int) -> Image.Image:
    """Generate a 64×64 coloured circle tray icon."""
    if pct >= bad_at:
        fill = bad
    elif pct >= warn_at:
        fill = warn
    else:
        fill = good

    def h2rgb(h: str):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill=h2rgb(fill))
    return img


class TrayIcon:
    """Wraps pystray.Icon with a simple interface."""

    def __init__(
        self,
        on_show_hide: Callable,
        on_refresh: Callable,
        on_set_key: Callable,
        on_theme_change: Callable[[str], None],
        on_quit: Callable,
        theme: dict,
    ):
        self._on_show_hide = on_show_hide
        self._on_refresh = on_refresh
        self._on_set_key = on_set_key
        self._on_theme_change = on_theme_change
        self._on_quit = on_quit
        self._theme = theme
        self._pct = 0.0
        self._icon: Optional[pystray.Icon] = None

    def _build_menu(self) -> pystray.Menu:
        theme_items = tuple(
            pystray.MenuItem(
                name,
                lambda icon, item, n=name: self._on_theme_change(n),
            )
            for name in THEME_NAMES
        )
        return pystray.Menu(
            pystray.MenuItem("Show / Hide", lambda icon, item: self._on_show_hide()),
            pystray.MenuItem("Refresh now", lambda icon, item: self._on_refresh()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Theme", pystray.Menu(*theme_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Set session key…", lambda icon, item: self._on_set_key()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda icon, item: self._on_quit()),
        )

    def _current_image(self) -> Image.Image:
        t = self._theme
        return _make_icon(
            self._pct,
            good=t["good"], warn=t["warn"], bad=t["bad"],
            warn_at=t["warn_at"], bad_at=t["bad_at"],
        )

    def start(self) -> None:
        """Run the tray icon in a background thread (non-blocking)."""
        self._icon = pystray.Icon(
            "claude-usage",
            self._current_image(),
            title=f"Claude Usage — {self._pct:.0f}%",
            menu=self._build_menu(),
        )
        self._icon.run_detached()

    def update(self, session_pct: float) -> None:
        """Update icon colour and tooltip."""
        self._pct = session_pct
        if self._icon:
            self._icon.icon = self._current_image()
            self._icon.title = f"Claude — Session {session_pct:.0f}%"

    def update_theme(self, theme: dict) -> None:
        """Update the theme used for the tray icon colour."""
        self._theme = theme
        if self._icon:
            self._icon.icon = self._current_image()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
```

- [ ] **Step 2: Commit**

```
git add widget/tray.py
git commit -m "feat: tray Theme submenu and update_theme method"
```

---

## Task 5: Update `main.py`

**Files:**
- Modify: `main.py`

Key changes:
- `_ask_session_key` gains an optional `master` param so it can use the persistent root instead of creating a second `tk.Tk()`
- A persistent hidden `root = tk.Tk()` owns the mainloop
- `_do_rebuild(theme_name)` destroys the old Toplevel and creates a new one; `nonlocal window` makes `_on_data` see the new window automatically
- `_on_theme_change` safely schedules `_do_rebuild` onto the main thread via `root.after(0, ...)`
- `root.mainloop()` replaces `window.run()`

- [ ] **Step 1: Replace `main.py` entirely**

```python
"""Claude Usage Widget — entry point."""
from __future__ import annotations

import datetime
import tkinter as tk
import tkinter.simpledialog as sd
import tkinter.messagebox as mb
from typing import Optional

from widget.api import get_org_id, get_usage, WidgetAPIError
from widget.config import load as load_cfg, save as save_cfg, DEFAULT_PATH
from widget.poller import Poller
from widget.tray import TrayIcon
from widget.themes import get_theme
from widget.ui import UsageWindow


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


def _ask_session_key(cfg: dict, master: Optional[tk.Misc] = None) -> bool:
    """Show dialog asking for session key. Returns True if key was saved."""
    if master is None:
        tmp = tk.Tk()
        tmp.withdraw()
        parent: tk.Misc = tmp
    else:
        parent = master
    key = sd.askstring(
        "Claude Usage Widget — Session Key",
        "Paste your claude.ai sessionKey cookie value.\n\n"
        "How to find it:\n"
        "1. Open claude.ai in Chrome and log in\n"
        "2. Press F12 -> Application -> Cookies -> https://claude.ai\n"
        "3. Copy the value of the 'sessionKey' cookie",
        parent=parent,
    )
    if master is None:
        tmp.destroy()
    if not key or not key.strip():
        return False
    cfg["session_key"] = key.strip()
    cfg["org_id"] = None
    save_cfg(cfg)
    return True


def main():
    cfg = load_cfg()

    # First-run: no session key — use a temporary Tk before the persistent root exists
    if not cfg.get("session_key"):
        tmp = tk.Tk()
        tmp.withdraw()
        want_key = mb.askyesno(
            "Claude Usage Widget",
            "No session key found.\n\nWould you like to set one now?\n\n"
            "(You can also do this later via the system tray menu)",
            parent=tmp,
        )
        tmp.destroy()
        if want_key:
            _ask_session_key(cfg)

    fetch_fn = _make_fetch(cfg)

    # Persistent hidden root — owns the mainloop so window rebuilds don't kill it
    root = tk.Tk()
    root.withdraw()

    window = UsageWindow(
        master=root,
        on_close_to_tray=lambda: None,
        on_refresh=lambda: poller.refresh(),
        theme=get_theme(cfg.get("theme", "default")),
    )
    if cfg.get("win_x") is not None and cfg.get("win_y") is not None:
        window.show(cfg["win_x"], cfg["win_y"])
    else:
        window.show(x=40, y=40)

    poller = Poller(fetch_fn=fetch_fn, interval=cfg.get("refresh_interval", 300))

    def _on_data(data: dict):
        # 'window' is read from enclosing scope at call time, so it sees rebuilds
        window.update_data(data)
        pct = data.get("session_pct")
        if pct is not None:
            tray.update(pct)

    def _do_rebuild(theme_name: str) -> None:
        nonlocal window
        x, y = window.get_position()
        window.destroy()
        new_theme = get_theme(theme_name)
        window = UsageWindow(
            master=root,
            on_close_to_tray=lambda: None,
            on_refresh=lambda: poller.refresh(),
            theme=new_theme,
        )
        window.show(x, y)
        tray.update_theme(new_theme)
        cfg["theme"] = theme_name
        save_cfg(cfg)

    def _on_theme_change(theme_name: str) -> None:
        # pystray callbacks run on a background thread; schedule onto the Tk main thread
        root.after(0, lambda: _do_rebuild(theme_name))

    def _quit():
        x, y = window.get_position()
        cfg["win_x"], cfg["win_y"] = x, y
        save_cfg(cfg)
        poller.stop()
        tray.stop()
        window.destroy()
        root.destroy()

    tray = TrayIcon(
        on_show_hide=lambda: window.hide() if window.is_visible() else window.show(),
        on_refresh=lambda: poller.refresh(),
        on_set_key=lambda: _ask_session_key(cfg, root) and poller.refresh(),
        on_theme_change=_on_theme_change,
        on_quit=_quit,
        theme=get_theme(cfg.get("theme", "default")),
    )

    poller.on_update = _on_data
    poller.start()
    tray.start()

    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the full test suite**

```
python -m pytest tests/ -v
```

Expected: all existing tests PASS (no UI tests run headlessly)

- [ ] **Step 3: Manual smoke test**

Run `python main.py` (or `launch.bat`). Verify:
- Widget appears as normal with default theme
- Right-click tray icon → "Theme" → select "neon" → widget rebuilds with cyan/pink accents
- Right-click tray icon → "Theme" → select "light" → widget rebuilds with white background
- Right-click tray icon → "Theme" → select "minimal" → widget rebuilds smaller and stripped back
- Right-click tray icon → "Theme" → select "default" → returns to original dark theme
- Close and relaunch — the last-selected theme is remembered

- [ ] **Step 4: Commit**

```
git add main.py
git commit -m "feat: wire theme switching — tray submenu rebuilds window with selected theme"
```
