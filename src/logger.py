import logging


def create_logger(name: str, level: str, format: str) -> logging.Logger:
    logging.basicConfig(format=format)
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)
    return logger
