from __future__ import print_function
from contextlib import contextmanager
from functools import wraps
import os
import inspect
import logging

# basic settings
APPDATA_PATH = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "GridGarage")
LOG_FILE = os.path.join(APPDATA_PATH, "gg3.log")

LOGGER = None


def debug(message):
    if not isinstance(message, list):
        message = [message]

    if LOGGER:
        [LOGGER.debug(msg) for msg in message]
    else:
        [print("DEBUG: " + str(msg)) for msg in message]


def info(message):
    if not isinstance(message, list):
        message = [message]

    if LOGGER:
        [LOGGER.info(msg) for msg in message]
    else:
        [print("INFO: " + str(msg)) for msg in message]


def warn(message):
    if not isinstance(message, list):
        message = [message]

    if LOGGER:
        [LOGGER.warn(msg) for msg in message]
    else:
        [print("WARNING: " + str(msg)) for msg in message]


def error(message):
    if not isinstance(message, list):
        message = [message]

    if LOGGER:
        [LOGGER.error(msg) for msg in message]
    else:
        [print("ERROR: " + str(msg)) for msg in message]


# set after import by base tool class
_ARC_MESSAGES = None


class ArcStreamHandler(logging.StreamHandler):
    """ Logging handler to log messages to ArcGIS
    """
    def emit(self, record):
        """ Emit the record to the ArcGIS messages object

        Args:
            record (): The message record

        Returns:

        """
        if not _ARC_MESSAGES:
            return

        msg = self.format(record)
        msg = msg.replace("\n", ", ").replace("\t", " ").replace("  ", " ")
        lvl = record.levelno

        if lvl in [logging.ERROR, logging.CRITICAL]:
            _ARC_MESSAGES.addWarningMessage(msg)

        elif lvl == logging.WARNING:
            _ARC_MESSAGES.addWarningMessage(msg)

        else:
            _ARC_MESSAGES.addMessage(msg)

        return


def configure_logging(arc_messages):

    global _ARC_MESSAGES
    _ARC_MESSAGES = arc_messages

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a').close()

    global LOGGER
    LOGGER = logging.getLogger('gg3')
    LOGGER.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s", datefmt="%Y%m%d %H%M%S")

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)
    LOGGER.debug("FileHandler added")

    ah = ArcStreamHandler()
    ah.setLevel(logging.INFO)
    LOGGER.addHandler(ah)
    LOGGER.debug("ArcLogHandler added")

    LOGGER.debug("Logging configured")

    return


@contextmanager
def error_trap(identifier=None):
    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """
    identifier = identifier or inspect.getframeinfo(inspect.currentframe())[2]
    _in = "IN  " + identifier
    _out = "OUT " + identifier

    if not LOGGER:
        say = print
        err = print
    else:
        say = LOGGER.debug
        err = LOGGER.error

    try:
        say(_in)
        yield
        say(_out)
    except Exception as e:
        err(str(e))

    return


def log(f):
    """ A decorator to trap and log exceptions """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with error_trap(f.__name__):
                return f(*args, **kwargs)

    return wrapper


def main():
    pass

if __name__ == '__main__':
    main()
