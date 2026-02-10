from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from actions import ActionEngine
from scheduler import ReminderScheduler
from ui import MainWindow


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    configure_logging()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    scheduler = ReminderScheduler()
    action_engine = ActionEngine()
    window = MainWindow(scheduler=scheduler, action_engine=action_engine)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
