import time
import unittest


class TestPoller(unittest.TestCase):

    def test_calls_on_update_with_data(self):
        from widget.poller import Poller
        results = []
        def fake_fetch():
            return {"session_pct": 37.0, "session_secs": 1000,
                    "weekly_pct": 31.0, "weekly_secs": 80000,
                    "error": None}
        p = Poller(fetch_fn=fake_fetch, interval=0.05)
        p.on_update = lambda d: results.append(d)
        p.start()
        time.sleep(0.15)
        p.stop()
        self.assertGreater(len(results), 0)
        self.assertAlmostEqual(results[0]["session_pct"], 37.0)

    def test_on_update_called_with_error_on_exception(self):
        from widget.poller import Poller
        results = []
        def bad_fetch():
            raise RuntimeError("API down")
        p = Poller(fetch_fn=bad_fetch, interval=0.05)
        p.on_update = lambda d: results.append(d)
        p.start()
        time.sleep(0.15)
        p.stop()
        self.assertGreater(len(results), 0)
        self.assertIsNotNone(results[0]["error"])

    def test_stop_terminates_thread(self):
        from widget.poller import Poller
        p = Poller(fetch_fn=lambda: {}, interval=60)
        p.start()
        self.assertTrue(p._thread.is_alive())
        p.stop()
        p._thread.join(timeout=1.0)
        self.assertFalse(p._thread.is_alive())

    def test_refresh_fires_immediately(self):
        from widget.poller import Poller
        results = []
        p = Poller(fetch_fn=lambda: {"session_pct": 10.0, "session_secs": 0,
                                      "weekly_pct": 5.0, "weekly_secs": 0,
                                      "error": None},
                   interval=60)
        p.on_update = lambda d: results.append(d)
        p.start()
        p.refresh()
        time.sleep(0.1)
        p.stop()
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
