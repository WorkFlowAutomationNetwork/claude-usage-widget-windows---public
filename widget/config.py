"""Read/write ~/.claude/claude-usage-widget.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DEFAULTS: dict[str, Any] = {
    "session_key": None,
    "org_id": None,
    "refresh_interval": 300,
    "win_x": None,
    "win_y": None,
    "theme": "default",
}

DEFAULT_PATH = Path.home() / ".claude" / "claude-usage-widget.json"


def load(path: Path = DEFAULT_PATH) -> dict:
    cfg = dict(_DEFAULTS)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update({k: v for k, v in data.items() if k in _DEFAULTS})
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save(cfg: dict, path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({k: cfg.get(k) for k in _DEFAULTS}, indent=2),
        encoding="utf-8",
    )
