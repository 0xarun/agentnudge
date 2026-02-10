from __future__ import annotations

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QStyle, QSystemTrayIcon, QWidget


class AgentNudgeTray:
    """Manages tray icon, context menu and window visibility behavior."""

    def __init__(self, window: QWidget) -> None:
        self._window = window
        icon = window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self._tray = QSystemTrayIcon(QIcon(icon), window)

        menu = QMenu(window)
        self._show_action = QAction("Show Agent Nudge", window)
        self._hide_action = QAction("Hide to Tray", window)
        self._exit_action = QAction("Exit", window)

        self._show_action.triggered.connect(self.show_window)
        self._hide_action.triggered.connect(self.hide_window)

        menu.addAction(self._show_action)
        menu.addAction(self._hide_action)
        menu.addSeparator()
        menu.addAction(self._exit_action)

        self._tray.setContextMenu(menu)
        self._tray.setToolTip("Agent Nudge Reminder")
        self._tray.activated.connect(self._on_activated)

    @property
    def exit_action(self) -> QAction:
        return self._exit_action

    def show(self) -> None:
        self._tray.show()

    def show_message(self, title: str, message: str) -> None:
        self._tray.showMessage(title, message)

    def hide_window(self) -> None:
        self._window.hide()

    def show_window(self) -> None:
        self._window.showNormal()
        self._window.activateWindow()
        self._window.raise_()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            if self._window.isVisible():
                self.hide_window()
            else:
                self.show_window()
