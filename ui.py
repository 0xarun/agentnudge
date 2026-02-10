from __future__ import annotations

import logging
from dataclasses import asdict
from urllib.parse import urlparse

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from actions import ActionEngine
from scheduler import ReminderConfig, ReminderScheduler
from tray import AgentNudgeTray


class MainWindow(QMainWindow):
    def __init__(self, scheduler: ReminderScheduler, action_engine: ActionEngine) -> None:
        super().__init__()
        self.scheduler = scheduler
        self.action_engine = action_engine
        self._allow_close = False

        self.setWindowTitle("Agent Nudge Reminder")
        self.setMinimumWidth(520)

        self._build_ui()
        self._apply_styles()

        self.tray = AgentNudgeTray(self)
        self.tray.exit_action.triggered.connect(self._exit_app)
        self.tray.show()

        self.scheduler.triggered.connect(self._on_reminder_triggered)
        self.scheduler.started.connect(self._on_scheduler_started)
        self.scheduler.stopped.connect(self._on_scheduler_stopped)

    def _build_ui(self) -> None:
        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        heading = QLabel("Dashboard Reminder", root)
        heading.setObjectName("heading")
        subtitle = QLabel("Configure a lightweight nudge loop and run it from the tray.", root)
        subtitle.setObjectName("subtitle")

        card = QFrame(root)
        form = QFormLayout(card)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        self.name_input = QLineEdit(card)
        self.name_input.setPlaceholderText("Example: Daily Ops Check")
        self.name_input.setText("Daily Check")

        self.interval_input = QSpinBox(card)
        self.interval_input.setRange(1, 1440)
        self.interval_input.setSuffix(" min")
        self.interval_input.setValue(15)

        self.url_input = QLineEdit(card)
        self.url_input.setPlaceholderText("https://example.com/dashboard")

        self.sound_checkbox = QCheckBox("Play sound", card)
        self.sound_checkbox.setChecked(True)
        self.notify_checkbox = QCheckBox("Show notification", card)
        self.notify_checkbox.setChecked(True)
        self.open_checkbox = QCheckBox("Open/focus browser", card)
        self.open_checkbox.setChecked(True)
        self.refresh_checkbox = QCheckBox("Refresh page", card)
        self.refresh_checkbox.setChecked(False)

        form.addRow("Reminder name", self.name_input)
        form.addRow("Interval", self.interval_input)
        form.addRow("Target URL", self.url_input)
        form.addRow(self.sound_checkbox)
        form.addRow(self.notify_checkbox)
        form.addRow(self.open_checkbox)
        form.addRow(self.refresh_checkbox)

        actions = QHBoxLayout()
        self.start_button = QPushButton("Start", root)
        self.stop_button = QPushButton("Stop", root)
        self.stop_button.setEnabled(False)
        actions.addWidget(self.start_button)
        actions.addWidget(self.stop_button)

        self.start_button.clicked.connect(self._start_reminder)
        self.stop_button.clicked.connect(self.scheduler.stop)

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addWidget(card)
        layout.addLayout(actions)

        status_bar = QStatusBar(self)
        status_bar.showMessage("Ready")
        self.setStatusBar(status_bar)

        self.setCentralWidget(root)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background-color: #1e222a; color: #e6e8eb; }
            QLabel#heading { font-size: 20px; font-weight: 600; color: #f3f5f7; }
            QLabel#subtitle { color: #b7bec8; }
            QFrame { background-color: #2a2f3a; border: 1px solid #3c4352; border-radius: 8px; }
            QLabel, QCheckBox { color: #e6e8eb; }
            QLineEdit, QSpinBox {
                background-color: #171a21;
                border: 1px solid #4d5668;
                border-radius: 4px;
                padding: 6px;
                color: #e6e8eb;
            }
            QPushButton {
                background-color: #3b82f6;
                border: none;
                border-radius: 6px;
                color: white;
                min-height: 34px;
                min-width: 110px;
                font-weight: 600;
            }
            QPushButton:disabled { background-color: #4a5468; color: #c4cad3; }
            QPushButton#danger { background-color: #ef4444; }
            QStatusBar { color: #dce1e8; }
            """
        )
        self.stop_button.setObjectName("danger")

    def _start_reminder(self) -> None:
        try:
            config = self._build_config_from_form()
            self.scheduler.start(config)
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Reminder Configuration", str(exc))

    def _build_config_from_form(self) -> ReminderConfig:
        name = self.name_input.text().strip()
        if not name:
            raise ValueError("Reminder name is required.")

        url = self.url_input.text().strip()
        if not self._is_valid_url(url):
            raise ValueError("Target URL must be a valid http:// or https:// URL.")

        if not any(
            [
                self.sound_checkbox.isChecked(),
                self.notify_checkbox.isChecked(),
                self.open_checkbox.isChecked(),
                self.refresh_checkbox.isChecked(),
            ]
        ):
            raise ValueError("Enable at least one action (sound, notification, browser, or refresh).")

        config = ReminderConfig(
            name=name,
            interval_minutes=self.interval_input.value(),
            dashboard_url=url,
            play_sound=self.sound_checkbox.isChecked(),
            show_notification=self.notify_checkbox.isChecked(),
            open_browser=self.open_checkbox.isChecked(),
            refresh_page=self.refresh_checkbox.isChecked(),
        )
        logging.debug("ReminderConfig created: %s", asdict(config))
        return config

    def _on_reminder_triggered(self, config: ReminderConfig) -> None:
        self.action_engine.execute(config)
        self.statusBar().showMessage(f"Triggered: {config.name}")

    def _on_scheduler_started(self, config: ReminderConfig) -> None:
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage(f"Running every {config.interval_minutes} minute(s)")
        self.tray.show_message(
            "Agent Nudge Reminder",
            f"'{config.name}' started. Running every {config.interval_minutes} minute(s).",
        )

    def _on_scheduler_stopped(self) -> None:
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("Stopped")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._allow_close:
            event.accept()
            return

        event.ignore()
        self.hide()
        self.tray.show_message(
            "Agent Nudge Reminder",
            "App minimized to tray. Use the tray icon to restore or exit.",
        )

    def _exit_app(self) -> None:
        self.scheduler.stop()
        self._allow_close = True
        self.close()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
