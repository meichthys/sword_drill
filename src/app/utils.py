""" Contains various utility functions """

import logging

from app import settings

def setup_logging():
    """ Sets up logging with various handlers """

    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format='[%(levelname)s][%(asctime)s]: %(message)s',
        handlers=[
            logging.FileHandler("sword_drill.log"),
            logging.StreamHandler()
        ]
    )