import logging
from logging.handlers import RotatingFileHandler
from core.paths import LOG_FILE


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("parser")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | "
            "%(module)s.%(funcName)s:%(lineno)d | %(message)s"
        )
    )

    logger.addHandler(file_handler)
    return logger
