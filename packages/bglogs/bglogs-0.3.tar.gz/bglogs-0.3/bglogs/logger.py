"""
Override logging base functions
"""


import inspect
import logging
from os import path


_LOGGER = None


def _get_logger_parent(level=2):
    global _LOGGER

    curframe = inspect.currentframe()
    frame = inspect.getouterframes(curframe)[level].frame
    logger_name = frame.f_globals['__name__'].split('.')[0]
    # print('>>>', inspect.getframeinfo(frame))
    # print('<<<', frame.f_globals['__name__'])
    if logger_name == '__main__':  # replace main for
        logger_name = path.basename(frame.f_globals['__file__'])  # Do not split the extension to avoid collision with other loggers

    _LOGGER = logging.getLogger(logger_name)
    return _LOGGER


def get_logger(name=None):
    return _LOGGER if name is None else logging.getLogger(name)


def critical(msg, *args, _name=None, **kwargs):
    _LOGGER.critical(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    _LOGGER.error(msg, *args, **kwargs)


def exception(msg, *args, exc_info=True, _name=None, **kwargs):
    error(msg, *args, exc_info=exc_info, **kwargs)


def warning(msg, *args, **kwargs):
    _LOGGER.warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    _LOGGER.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    _LOGGER.debug(msg, *args, **kwargs)
