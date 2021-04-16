"""Contains main method and caller functions."""


# Currently Required for Qt to work with MacOS Big Sur
import os
os.environ["QT_MAC_WANTS_LAYER"] = "1"

import logging

import sys

from PySide2.QtWidgets import QApplication

from app.utils import setup_logging
from app.sword_drill import MainWindow


def run_application():
    """Start application."""
    qt_app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    try:
        setup_logging()
        run_application()
    except Exception as error:
        logging.error(str(error))