""" Call main function """

import logging

from src.sworddrill.app import main
from src.sworddrill.utils import setup_logging


if __name__ == '__main__':
    """ Kick off application """
    setup_logging()
    logging.debug("Logging started...")
    main().main_loop()
