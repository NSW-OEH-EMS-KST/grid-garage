from os import makedirs, environ
from os.path import join, exists
import logging

# basic settings
APPDATA_PATH = join(environ["USERPROFILE"], "AppData", "Local", "GridGarage")
LOG_FILE = join(APPDATA_PATH, "gg3.log")
LOG = logging

# set after import by base tool class
ARC_MESSAGES = None


class ArcLogHandler(logging.StreamHandler):
    """ Logging handler to log messages to ArcGIS
    """
    def emit(self, record):
        """ Emit the record to the ArcGIS messages object

        Args:
            record (): The message record

        Returns:

        """
        if not ARC_MESSAGES:
            return

        msg = self.format(record)
        msg = msg.replace("\n", ", ").replace("\t", " ").replace("  ", " ")
        lvl = record.levelno

        if lvl in [logging.ERROR, logging.CRITICAL]:
            ARC_MESSAGES.addWarningMessage(msg)

        elif lvl == logging.WARNING:
            ARC_MESSAGES.addWarningMessage(msg)

        else:
            ARC_MESSAGES.addMessage(msg)

        return


def set_messages(msgs):
    """ Set the arc messages object for use by tools

    Args:
        msgs (): A ref to the messages

    Returns:

    """
    global ARC_MESSAGES
    ARC_MESSAGES = msgs
    return


try:
    # check if the app data folder is there, if not create
    if not exists(APPDATA_PATH):
        makedirs(APPDATA_PATH)

    logging.basicConfig(filename=LOG_FILE,
                        filemode="w",
                        level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logging.debug("logging module load")

    ah = ArcLogHandler()
    ah.setLevel(logging.INFO)
    logging.getLogger().addHandler(ah)

    logging.debug("ArcLogHandler added")

except:
    pass

