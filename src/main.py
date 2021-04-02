"""Contains main method and caller functions."""
import logging

import sys

from PyQt5.QtWidgets import QApplication

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