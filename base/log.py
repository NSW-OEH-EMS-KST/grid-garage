from __future__ import print_function
import contextlib
import functools
import os
import inspect
import logging


# basic settings
APPDATA_PATH = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "GridGarage")
LOG_FILE = os.path.join(APPDATA_PATH, "gg3.log")
LOGGER = None


def make_tuple(ob):

    return ob if isinstance(ob, (list, tuple)) else [ob]


def debug(message):
    message = make_tuple(message)

    if LOGGER:
        [LOGGER.debug(msg) for msg in message]
    else:
        [print("DEBUG: " + str(msg)) for msg in message]


def info(message):
    message = make_tuple(message)

    if LOGGER:
        [LOGGER.info(msg) for msg in message]
    else:
        [print("INFO: " + str(msg)) for msg in message]


def warn(message):
    message = make_tuple(message)

    if LOGGER:
        [LOGGER.warn(msg) for msg in message]
    else:
        [print("WARNING: " + str(msg)) for msg in message]


def error(message):
    message = make_tuple(message)

    if LOGGER:
        [LOGGER.error(msg) for msg in message]
    else:
        [print("ERROR: " + str(msg)) for msg in message]


# set after import by base tool class
_ARC_MESSAGES = None


class ArcStreamHandler(logging.StreamHandler):
    """ Logging handler to log messages to ArcGIS """

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

        if not os.path.exists(APPDATA_PATH):
            arc_messages.AddMessage("Creating app data path {}".format(APPDATA_PATH))
            os.makedirs(APPDATA_PATH)

        arc_messages.AddMessage("Creating log file {}".format(LOG_FILE))
        open(LOG_FILE, 'a').close()

    global LOGGER
    LOGGER = logging.getLogger('gg3')

    if len(LOGGER.handlers):  # then this has already been done for this logger instance
        return

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


@contextlib.contextmanager
def error_trap(context):

    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """

    idx = getattr(context, "__name__", None)
    if not idx:
        idx = getattr(context, "name", None)
    if not idx:
        idx = inspect.getframeinfo(inspect.currentframe())[2]

    _in = "IN context= " + idx
    _out = "OUT context= " + idx

    if not LOGGER:
        say = err = print
    else:
        say, err = LOGGER.debug, LOGGER.error

    try:
        say(_in)
        yield
        say(_out)
    except Exception as e:
        err(str(e))
        raise e

    return


def log(f):
    """ A decorator to trap and log exceptions """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with error_trap(f):
            return f(*args, **kwargs)

    return wrapper


def main():
    pass

if __name__ == '__main__':
    main()
