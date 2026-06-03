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
