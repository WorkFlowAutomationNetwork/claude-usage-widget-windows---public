"""Floating always-on-top usage widget.

RESTYLING GUIDE
---------------
Change THEME values only — nothing else needs touching for visual changes.
Colors: any hex string.
Fonts: any font name installed on Windows.
Sizes: integers (pixels).
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional

# ─── THEME ────────────────────────────────────────────────────────────────────
# Edit this dict to restyle the widget. Touch nothing else for visual changes.

THEME = {
    # Window
    "width": 280,
    "alpha": 0.95,           # 0.0 transparent → 1.0 opaque

    # Colors
    "bg":        "#0A0E14",
    "panel":     "#0F1419",
    "border":    "#1F2630",
    "text":      "#E6EDF3",
    "muted":     "#8B98A6",
    "good":      "#3FB68B",  # green  — below warn threshold
    "warn":      "#E8A23B",  # amber  — 50–80%
    "bad":       "#E5484D",  # red    — 80%+
    "accent":    "#4A9EFF",

    # Fonts (Windows-safe)
    "font":       ("Segoe UI", 10),
    "font_small": ("Segoe UI", 9),
    "font_mono":  ("Consolas", 9),
    "font_title": ("Segoe UI Semibold", 10),

    # Layout (pixels)
    "pad":        12,        # outer padding
    "bar_h":       6,        # progress bar height
    "gap":        10,        # gap between bars
    "title_h":    28,        # titlebar height

    # Thresholds
    "warn_at":    50,        # % where bar turns amber
    "bad_at":     80,        # % where bar turns red
}
# ──────────────────────────────────────────────────────────────────────────────


def _bar_color(pct: float) -> str:
    if pct >= THEME["bad_at"]:  return THEME["bad"]
    if pct >= THEME["warn_at"]: return THEME["warn"]
    return THEME["good"]


def _fmt_countdown(secs: Optional[int]) -> str:
    if secs is None:
        return ""
    if secs <= 0:
        return "now"
    h, rem = divmod(secs, 3600)
    m = rem // 60
    return f"{h}h {m}m" if h else f"{m}m"


class UsageWindow:
    """Floating always-on-top tkinter window."""

    def __init__(self, on_close_to_tray, on_refresh):
        self._on_close_to_tray = on_close_to_tray
        self._on_refresh = on_refresh
        self._data: dict = {}
        self._session_secs: Optional[int] = None
        self._weekly_secs: Optional[int] = None
        self._tick_job = None

        self._root = tk.Tk()
        self._build()

    def _build(self) -> None:
        r = self._root
        r.overrideredirect(True)          # no OS titlebar
        r.attributes("-topmost", True)   # always on top
        r.attributes("-alpha", THEME["alpha"])
        r.configure(bg=THEME["bg"])
        r.resizable(False, False)

        w = THEME["width"]
        r.geometry(f"{w}x200")            # height auto-adjusts after draw

        # ── Custom titlebar ──────────────────────────────────────────────────
        tb = tk.Frame(r, bg=THEME["panel"], height=THEME["title_h"])
        tb.pack(fill="x")
        tb.pack_propagate(False)

        tk.Label(tb, text="Claude Usage", bg=THEME["panel"],
                 fg=THEME["text"], font=THEME["font_title"],
                 anchor="w").pack(side="left", padx=THEME["pad"])

        # Minimize → hide to tray
        tk.Button(tb, text="−", bg=THEME["panel"], fg=THEME["muted"],
                  relief="flat", bd=0, font=THEME["font"],
                  activebackground=THEME["border"], cursor="hand2",
                  command=self._minimize).pack(side="right", padx=(0, 4))

        # Drag support
        tb.bind("<ButtonPress-1>",   self._drag_start)
        tb.bind("<B1-Motion>",       self._drag_move)

        # ── Separator ────────────────────────────────────────────────────────
        tk.Frame(r, bg=THEME["border"], height=1).pack(fill="x")

        # ── Body ─────────────────────────────────────────────────────────────
        self._body = tk.Frame(r, bg=THEME["bg"],
                              padx=THEME["pad"], pady=THEME["pad"])
        self._body.pack(fill="both", expand=True)

        # Session row
        self._sess_label  = self._make_label("Session (5h)")
        self._sess_pct    = self._make_pct_label()
        self._sess_canvas = self._make_bar_canvas()
        self._sess_reset  = self._make_reset_label()

        tk.Frame(self._body, bg=THEME["border"], height=1).pack(
            fill="x", pady=(THEME["gap"], THEME["gap"]))

        # Weekly row
        self._week_label  = self._make_label("Week")
        self._week_pct    = self._make_pct_label()
        self._week_canvas = self._make_bar_canvas()
        self._week_reset  = self._make_reset_label()

        # Status / error line
        self._status = tk.Label(self._body, text="", bg=THEME["bg"],
                                fg=THEME["muted"], font=THEME["font_small"],
                                anchor="w")
        self._status.pack(fill="x", pady=(THEME["gap"], 0))

        # ── Window dragging state ─────────────────────────────────────────
        self._drag_x = self._drag_y = 0

    # ── Widget factory helpers ────────────────────────────────────────────────

    def _make_label(self, text: str) -> tk.Label:
        row = tk.Frame(self._body, bg=THEME["bg"])
        row.pack(fill="x")
        lbl = tk.Label(row, text=text, bg=THEME["bg"],
                       fg=THEME["muted"], font=THEME["font_small"], anchor="w")
        lbl.pack(side="left")
        return lbl

    def _make_pct_label(self) -> tk.Label:
        lbl = tk.Label(self._body, text="—", bg=THEME["bg"],
                       fg=THEME["text"], font=THEME["font_mono"], anchor="e")
        lbl.pack(fill="x")
        return lbl

    def _make_bar_canvas(self) -> tk.Canvas:
        c = tk.Canvas(self._body, height=THEME["bar_h"],
                      bg=THEME["panel"], highlightthickness=0)
        c.pack(fill="x", pady=(2, 0))
        return c

    def _make_reset_label(self) -> tk.Label:
        lbl = tk.Label(self._body, text="", bg=THEME["bg"],
                       fg=THEME["muted"], font=THEME["font_small"], anchor="e")
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

        if err:
            self._status.config(text=f"Error: {err[:50]}", fg=THEME["bad"])
            self._sess_pct.config(text="—")
            self._week_pct.config(text="—")
            self._sess_reset.config(text="")
            self._week_reset.config(text="")
            self._draw_bar(self._sess_canvas, 0, THEME["muted"])
            self._draw_bar(self._week_canvas, 0, THEME["muted"])
        else:
            self._status.config(text="", fg=THEME["muted"])

            s_pct  = data.get("session_pct") or 0
            s_secs = data.get("session_secs")
            w_pct  = data.get("weekly_pct") or 0
            w_secs = data.get("weekly_secs")

            self._sess_pct.config(text=f"{s_pct:.1f}%", fg=_bar_color(s_pct))
            self._week_pct.config(text=f"{w_pct:.1f}%" if w_pct else "—",
                                  fg=_bar_color(w_pct) if w_pct else THEME["muted"])

            self._draw_bar(self._sess_canvas, s_pct, _bar_color(s_pct))
            self._draw_bar(self._week_canvas, w_pct, _bar_color(w_pct))

            self._session_secs = s_secs
            self._weekly_secs  = w_secs
            self._tick()  # restart countdown

    def _draw_bar(self, canvas: tk.Canvas, pct: float, color: str) -> None:
        canvas.update_idletasks()
        w = canvas.winfo_width() or THEME["width"] - THEME["pad"] * 2
        h = THEME["bar_h"]
        canvas.delete("all")
        canvas.create_rectangle(0, 0, w, h, fill=THEME["panel"], outline="")
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

    def run(self) -> None:
        """Blocks — call from main thread. Returns when window is destroyed."""
        self._root.mainloop()

    def destroy(self) -> None:
        self._root.destroy()
