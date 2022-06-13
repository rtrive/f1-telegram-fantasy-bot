import logging


def create_logger(name: str, level: str, format: str) -> logging.Logger:
    # To be cancell, just to log seleniumwire calls
    logging.basicConfig(format=format, level="INFO")
    logger = logging.getLogger(name=name)
    # logger.setLevel(level=level)
    return logger
