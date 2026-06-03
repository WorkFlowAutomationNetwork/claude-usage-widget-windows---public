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
        from widget.themes import get_theme, THEME_NAMES
        required = {
            "width", "alpha", "bg", "panel", "border", "text", "muted",
            "good", "warn", "bad", "accent", "font", "font_small",
            "font_mono", "font_title", "pad", "bar_h", "gap",
            "title_h", "warn_at", "bad_at",
        }
        for name in THEME_NAMES:
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
