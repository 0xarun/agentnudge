from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer, Signal


@dataclass(slots=True)
class ReminderConfig:
    name: str
    interval_minutes: int
    dashboard_url: str
    play_sound: bool
    show_notification: bool
    open_browser: bool
    refresh_page: bool


class ReminderScheduler(QObject):
    """Non-blocking scheduler that emits reminder events on a fixed interval."""

    triggered = Signal(object)
    started = Signal(object)
    stopped = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._on_timeout)
        self._config: ReminderConfig | None = None

    @property
    def is_running(self) -> bool:
        return self._timer.isActive()

    @property
    def config(self) -> ReminderConfig | None:
        return self._config

    def start(self, config: ReminderConfig) -> None:
        if config.interval_minutes <= 0:
            raise ValueError("Interval minutes must be greater than zero.")

        self._config = config
        interval_ms = config.interval_minutes * 60 * 1000
        self._timer.start(interval_ms)
        logging.info("Scheduler started: every %s minute(s)", config.interval_minutes)
        self.started.emit(config)

    def stop(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
            logging.info("Scheduler stopped")
        self.stopped.emit()

    def _on_timeout(self) -> None:
        if not self._config:
            return
        logging.debug("Reminder triggered for '%s'", self._config.name)
        self.triggered.emit(self._config)
