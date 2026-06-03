# Theme Switching — Design Spec
_Date: 2026-06-03_

## Overview

Add a theme registry and tray-menu theme switcher to the Claude Usage Widget. The user picks a theme from a "Theme →" submenu in the system tray; the window rebuilds immediately with the new theme applied and the choice persists across restarts.

## Scope

First pass ships four themes (color/font-only, no structural changes):
- `default` — current dark theme (unchanged)
- `neon` — dark bg, hot-pink/cyan accents
- `light` — white background, professional/clean
- `minimal` — stripped-back dark, less chrome

Structural layout variants (dials, flip-clock, HUD) are explicitly out of scope for this spec.

## Architecture

### New file: `widget/themes.py`

- Contains all named THEME dicts
- The current `THEME` constant in `ui.py` moves here verbatim as `"default"`
- `get_theme(name: str) -> dict` returns the named theme, falling back to `"default"` for unknown names
- Adding a new theme in future = add one dict to this file, nothing else

### `widget/ui.py`

- Remove module-level `THEME` constant
- Import `get_theme` from `widget/themes.py`
- `UsageWindow.__init__` already accepts `theme: dict` — no signature change needed
- `_build` references `THEME` throughout; rename all references to `self._theme` (already the pattern in some methods)

### `widget/config.py`

- Add `"theme": "default"` to `_DEFAULTS`
- No other changes — existing load/save handles it automatically

### `widget/tray.py`

- Add `on_theme_change: Callable[[str], None]` parameter to `TrayIcon.__init__`
- `_build_menu` adds a "Theme →" submenu; one `MenuItem` per theme name from a `THEME_NAMES` list imported from `widget/themes.py`
- Each item calls `on_theme_change(name)`
- `_theme` on the tray icon stays as-is (used only for the tray icon colour logic)

### `main.py`

- Add `_rebuild_window(theme_name: str)` function:
  1. Save current window position via `window.get_position()`
  2. Call `window.destroy()`
  3. Create new `UsageWindow` with `get_theme(theme_name)`
  4. Restore position and show
  5. Re-bind `poller.on_update`
  6. Save `cfg["theme"] = theme_name` and call `save_cfg(cfg)`
- Pass `_rebuild_window` as `on_theme_change` to `TrayIcon`
- On startup, load `cfg.get("theme", "default")` and pass `get_theme(...)` to the initial `UsageWindow`

## Data Flow

```
User clicks tray → "Theme" → "neon"
  → on_theme_change("neon") in main.py
  → save position
  → destroy old UsageWindow
  → create new UsageWindow(theme=get_theme("neon"))
  → restore position
  → rebind poller.on_update
  → save cfg["theme"] = "neon"
```

## Constraints

- No new folders — `widget/themes.py` sits alongside existing widget files
- No restart required — change takes effect immediately
- Brief window flicker (~100ms) on theme change is acceptable
- `THEME_NAMES` list in `themes.py` is the single source of truth for what appears in the tray submenu — no duplication

## Out of Scope

- Theme previews in the tray menu
- Hot-swap (in-place widget reconfiguration)
- Structural layout variants (separate spec)
