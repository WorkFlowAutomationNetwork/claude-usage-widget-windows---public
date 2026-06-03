import json
import os
import tempfile
import unittest
from pathlib import Path


class TestConfig(unittest.TestCase):

    def _temp_path(self):
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        f.close()
        os.unlink(f.name)
        return Path(f.name)

    def test_load_returns_defaults_when_missing(self):
        from widget.config import load
        p = self._temp_path()
        cfg = load(p)
        self.assertIsNone(cfg["session_key"])
        self.assertIsNone(cfg["org_id"])
        self.assertEqual(cfg["refresh_interval"], 300)
        self.assertIsNone(cfg["win_x"])
        self.assertIsNone(cfg["win_y"])

    def test_save_and_reload(self):
        from widget.config import load, save
        p = self._temp_path()
        cfg = load(p)
        cfg["session_key"] = "test-key-123"
        cfg["org_id"] = "org-abc"
        cfg["win_x"] = 100
        cfg["win_y"] = 200
        save(cfg, p)
        reloaded = load(p)
        self.assertEqual(reloaded["session_key"], "test-key-123")
        self.assertEqual(reloaded["org_id"], "org-abc")
        self.assertEqual(reloaded["win_x"], 100)
        self.assertEqual(reloaded["win_y"], 200)

    def test_load_merges_missing_keys(self):
        from widget.config import load
        p = self._temp_path()
        p.write_text('{"session_key": "existing"}')
        cfg = load(p)
        self.assertEqual(cfg["session_key"], "existing")
        self.assertIsNone(cfg["org_id"])
        self.assertEqual(cfg["refresh_interval"], 300)

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


if __name__ == "__main__":
    unittest.main()
