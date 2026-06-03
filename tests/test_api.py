import json
import unittest
import urllib.error
from unittest.mock import patch


class FakeResponse:
    def __init__(self, data):
        self._data = json.dumps(data).encode()
    def read(self):
        return self._data
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass


class TestGetOrgId(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_returns_chat_org(self, mock_open):
        from widget.api import get_org_id
        mock_open.return_value = FakeResponse([
            {"uuid": "org-1", "capabilities": ["api"]},
            {"uuid": "org-2", "capabilities": ["chat", "api"]},
        ])
        self.assertEqual(get_org_id("key"), "org-2")

    @patch("urllib.request.urlopen")
    def test_falls_back_to_first_org(self, mock_open):
        from widget.api import get_org_id
        mock_open.return_value = FakeResponse([{"uuid": "org-1", "capabilities": []}])
        self.assertEqual(get_org_id("key"), "org-1")

    @patch("urllib.request.urlopen")
    def test_raises_on_http_error(self, mock_open):
        from widget.api import get_org_id, WidgetAPIError
        mock_open.side_effect = urllib.error.HTTPError(
            url=None, code=403, msg="Forbidden", hdrs=None, fp=None
        )
        with self.assertRaises(WidgetAPIError) as ctx:
            get_org_id("key")
        self.assertIn("403", str(ctx.exception))


class TestGetUsage(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_returns_usage_dict(self, mock_open):
        from widget.api import get_usage
        mock_open.return_value = FakeResponse({
            "five_hour": {"utilization": 37.0, "resets_at": "2026-06-03T01:19:59+00:00"},
            "seven_day": {"utilization": 31.0, "resets_at": "2026-06-04T21:59:59+00:00"},
        })
        result = get_usage("key", "org-2")
        self.assertAlmostEqual(result["five_hour"]["utilization"], 37.0)
        self.assertAlmostEqual(result["seven_day"]["utilization"], 31.0)

    @patch("urllib.request.urlopen")
    def test_raises_on_auth_error(self, mock_open):
        from widget.api import get_usage, WidgetAPIError
        mock_open.side_effect = urllib.error.HTTPError(
            url=None, code=401, msg="Unauthorized", hdrs=None, fp=None
        )
        with self.assertRaises(WidgetAPIError):
            get_usage("key", "org-1")


if __name__ == "__main__":
    unittest.main()
