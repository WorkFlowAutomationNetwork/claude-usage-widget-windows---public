"""Calls claude.ai's internal usage API using a stored session cookie."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

_BASE = "https://claude.ai"
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36"
)


class WidgetAPIError(Exception):
    pass


def _get(path: str, session_key: str) -> object:
    req = urllib.request.Request(_BASE + path)
    req.add_header("Cookie", f"sessionKey={session_key}")
    req.add_header("User-Agent", _UA)
    req.add_header("Accept", "application/json")
    req.add_header("Referer", "https://claude.ai/new")
    req.add_header("anthropic-client-platform", "web_claude_ai")
    req.add_header("anthropic-client-version", "1.0.0")
    req.add_header("sec-ch-ua", '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"')
    req.add_header("sec-ch-ua-mobile", "?0")
    req.add_header("sec-ch-ua-platform", '"Windows"')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise WidgetAPIError(f"HTTP {e.code}: {e.reason}") from e
    except urllib.error.URLError as e:
        raise WidgetAPIError(f"Network error: {e.reason}") from e


def get_org_id(session_key: str) -> Optional[str]:
    """Return UUID of first org with 'chat' capability."""
    orgs = _get("/api/organizations", session_key)
    if not isinstance(orgs, list) or not orgs:
        return None
    for org in orgs:
        if "chat" in org.get("capabilities", []):
            uuid = org.get("uuid")
            if uuid:
                return uuid
    return orgs[0].get("uuid")


def get_usage(session_key: str, org_id: str) -> dict:
    """Return raw usage dict. utilization values are already percentages (0-100)."""
    return _get(f"/api/organizations/{org_id}/usage", session_key)
