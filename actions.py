from __future__ import annotations

import logging
import threading
import time
import webbrowser
from urllib.parse import ParseResult, parse_qsl, urlencode, urlparse, urlunparse

from scheduler import ReminderConfig

try:
    from win10toast import ToastNotifier
except ImportError:  # pragma: no cover - optional on non-Windows platforms
    ToastNotifier = None

try:
    import winsound
except ImportError:  # pragma: no cover - only non-Windows environments
    winsound = None


class ActionEngine:
    """Executes reminder actions without blocking the UI thread."""

    def __init__(self) -> None:
        self._notifier = ToastNotifier() if ToastNotifier is not None else None

    def execute(self, config: ReminderConfig) -> None:
        if config.play_sound:
            self._play_sound_async()

        if config.show_notification:
            self._show_notification(config)

        if config.open_browser or config.refresh_page:
            self._open_or_refresh_browser(config)

    def _play_sound_async(self) -> None:
        def worker() -> None:
            try:
                if winsound is None:
                    logging.warning("winsound unavailable; sound alert skipped on this platform")
                    return

                # Play a recognizable non-blocking Windows system alert.
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as exc:  # noqa: BLE001
                logging.error("Unable to play reminder sound: %s", exc)

        threading.Thread(target=worker, daemon=True, name="SoundThread").start()

    def _show_notification(self, config: ReminderConfig) -> None:
        title = f"Agent Nudge Reminder - {config.name}"
        msg = f"Time for your scheduled check: {config.dashboard_url}"

        if self._notifier is None:
            logging.warning("win10toast unavailable; toast notification skipped on this platform")
            return

        try:
            self._notifier.show_toast(title, msg, duration=5, threaded=True)
        except Exception as exc:  # noqa: BLE001
            logging.error("Unable to show Windows notification: %s", exc)

    def _open_or_refresh_browser(self, config: ReminderConfig) -> None:
        url_to_open = config.dashboard_url
        if config.refresh_page:
            url_to_open = self._with_cache_buster(config.dashboard_url)

        try:
            webbrowser.open(url_to_open, new=0, autoraise=True)
        except Exception as exc:  # noqa: BLE001
            logging.error("Unable to open browser URL '%s': %s", url_to_open, exc)

    @staticmethod
    def _with_cache_buster(url: str) -> str:
        parsed: ParseResult = urlparse(url)
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query_params["_agent_nudge_ts"] = str(int(time.time()))
        new_query = urlencode(query_params)
        updated = parsed._replace(query=new_query)
        return urlunparse(updated)
