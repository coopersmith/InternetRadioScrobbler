"""Tests for the nightly kill switch in PersonalScrobbler.

No network: LastFMClient is stubbed and a fake station fetcher is registered.
The clock is faked by patching PersonalScrobbler._now_in_stop_tz.

Run with:  python -m unittest tests.test_nightly_stop -v
"""

import sys
import threading
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

import personal_scrobbler  # noqa: E402
from personal_scrobbler import PersonalScrobbler  # noqa: E402
from stations.base import BaseStationFetcher, TrackInfo  # noqa: E402

ET = ZoneInfo("America/New_York")
STATION = "_test_station"


class FakeFetcher(BaseStationFetcher):
    """Returns a fixed track and records how often it was polled."""

    def __init__(self):
        super().__init__(STATION)
        self.polls = 0
        self.polled = threading.Event()

    def get_current_track(self):
        self.polls += 1
        self.polled.set()
        return TrackInfo(artist="Artist", title="Title")


class FakeLastFM:
    def __init__(self, *args, **kwargs):
        self.scrobbles = []

    def test_connection(self):
        return True

    def scrobble(self, artist, title, album=None):
        self.scrobbles.append((artist, title))
        return True


def et(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=ET)


class NightlyStopTests(unittest.TestCase):
    def setUp(self):
        self.fetcher = FakeFetcher()
        personal_scrobbler.STATION_FETCHERS[STATION] = lambda: self.fetcher
        self.addCleanup(personal_scrobbler.STATION_FETCHERS.pop, STATION, None)

        lastfm_patch = mock.patch.object(personal_scrobbler, "LastFMClient", FakeLastFM)
        lastfm_patch.start()
        self.addCleanup(lastfm_patch.stop)

        self.now = et(2026, 9, 5, 22, 0)  # 10 PM ET by default
        clock_patch = mock.patch.object(
            PersonalScrobbler, "_now_in_stop_tz", lambda s: self.now
        )
        clock_patch.start()
        self.addCleanup(clock_patch.stop)

    def make(self, **kwargs):
        kwargs.setdefault("poll_interval", 0.02)
        s = PersonalScrobbler("u", "k", "s", lastfm_password="p", **kwargs)
        self.addCleanup(s.stop)
        return s

    def wait_until(self, predicate, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.01)
        return predicate()

    # -- behaviour -----------------------------------------------------------

    def test_stops_when_clock_reaches_2am(self):
        s = self.make()
        self.assertTrue(s.start(STATION))
        self.assertTrue(self.fetcher.polled.wait(1.0))
        self.assertTrue(s.get_status().is_active)

        self.now = et(2026, 9, 6, 2, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

        status = s.get_status()
        self.assertIsNone(status.station_name if status.is_active else None)
        self.assertIn("nightly kill switch", status.error)
        self.assertTrue(self.wait_until(lambda: not s._thread.is_alive()))

        # No further polling once stopped.
        polls = self.fetcher.polls
        time.sleep(0.1)
        self.assertEqual(self.fetcher.polls, polls)

    def test_does_not_stop_before_2am(self):
        s = self.make()
        s.start(STATION)
        self.now = et(2026, 9, 6, 1, 59)
        time.sleep(0.15)
        self.assertTrue(s.get_status().is_active)

    def test_fires_after_cutoff_hour_if_a_poll_was_late(self):
        # Spring-forward night: 02:00 ET never happens, clock goes 01:59 -> 03:00.
        s = self.make()
        s.start(STATION)
        self.now = et(2026, 3, 8, 3, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

    def test_start_after_cutoff_waits_for_next_night(self):
        self.now = et(2026, 9, 6, 2, 30)
        s = self.make()
        s.start(STATION)
        time.sleep(0.15)
        self.assertTrue(s.get_status().is_active, "must not stop immediately")

        self.now = et(2026, 9, 6, 23, 0)
        time.sleep(0.1)
        self.assertTrue(s.get_status().is_active)

        self.now = et(2026, 9, 7, 2, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

    def test_restart_after_nightly_stop_runs_until_next_night(self):
        s = self.make()
        s.start(STATION)
        self.now = et(2026, 9, 6, 2, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

        self.now = et(2026, 9, 6, 2, 10)
        self.assertTrue(s.start(STATION))
        time.sleep(0.15)
        self.assertTrue(s.get_status().is_active)
        self.assertIsNone(s.get_status().error)

        self.now = et(2026, 9, 7, 2, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

    def test_disabled_when_hour_is_none(self):
        s = self.make(nightly_stop_hour=None)
        s.start(STATION)
        self.now = et(2026, 9, 6, 2, 0)
        time.sleep(0.15)
        self.assertTrue(s.get_status().is_active)

    def test_custom_hour(self):
        s = self.make(nightly_stop_hour=5)
        s.start(STATION)
        self.now = et(2026, 9, 6, 2, 0)
        time.sleep(0.1)
        self.assertTrue(s.get_status().is_active)
        self.now = et(2026, 9, 6, 5, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

    def test_status_endpoint_reports_stop(self):
        import web_app
        s = self.make()
        web_app.scrobbler = s
        self.addCleanup(setattr, web_app, "scrobbler", None)
        s.start(STATION)
        self.now = et(2026, 9, 6, 2, 0)
        self.assertTrue(self.wait_until(lambda: not s.get_status().is_active))

        client = web_app.app.test_client()
        body = client.get("/api/status").get_json()
        self.assertFalse(body["is_active"])
        self.assertIn("nightly kill switch", body["error"])

    def test_real_clock_is_timezone_aware_eastern(self):
        with mock.patch.object(PersonalScrobbler, "_now_in_stop_tz",
                               PersonalScrobbler.__dict__["_now_in_stop_tz"]):
            s = self.make()
            now = s._now_in_stop_tz()
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(now.tzname(), datetime.now(ET).tzname())


class EnvParsingTests(unittest.TestCase):
    """web_main.py parses NIGHTLY_STOP_HOUR_ET; exercise the same rules."""

    def parse(self, raw):
        raw = raw.strip().lower()
        if raw in ('', 'off', 'none', 'disabled', 'false'):
            return None
        try:
            h = int(raw)
            if not 0 <= h <= 23:
                raise ValueError
            return h
        except ValueError:
            return 2

    def test_values(self):
        self.assertEqual(self.parse("2"), 2)
        self.assertEqual(self.parse(" 5 "), 5)
        self.assertIsNone(self.parse("off"))
        self.assertIsNone(self.parse(""))
        self.assertEqual(self.parse("25"), 2)
        self.assertEqual(self.parse("abc"), 2)


if __name__ == "__main__":
    unittest.main()
