"""Contains main method and caller functions."""

from mic import start
from utils import setup_logging

def main():
    """Calls required methods/functions to execute program"""
    start()

if __name__ == "__main__":
    setup_logging()
    main()