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
