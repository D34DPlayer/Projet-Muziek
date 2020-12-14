import logging


def setup_logger():
    """Sets up the parent logger of the app.

    :author: Carlos
    :PRE: _
    :POST: The logger "muziek" will be available and configured.
    """
    handler = logging.FileHandler("muziek.log", "a", encoding="utf-8")
    formatter = logging.Formatter('[Muziek] %(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger("muziek")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def get_logger(name):
    """Returns a logger child of the parent logger set up previously.

    :param name: name of the child logger.
    :PRE: The parent logger needs to be set up first.
    :POST: Returns the requested logger.
    """
    return logging.getLogger(f"muziek.{name}")
