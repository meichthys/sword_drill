"""Contains main method and caller functions."""
import logging

from app import SwordDrill
from utils import setup_logging


if __name__ == '__main__':
    """ Call application """
    setup_logging()
    logging.info("Starting Sword Drill.")
    SwordDrill().run()

