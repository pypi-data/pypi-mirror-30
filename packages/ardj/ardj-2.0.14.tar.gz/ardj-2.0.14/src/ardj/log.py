# encoding=utf-8

"""ARDJ, an artificial DJ.

This module installs a custom logger that writes messages to a text file.

To use the module, call the install() method before logging anything.  This is
done automatically when you use the CLI interface, so you only need to use this
module explicitly if you're importing parts of ardj into your existing code.
"""

import logging
import logging.handlers

from ardj.util import get_user_path


installed = False


def get_level():
    return logging.DEBUG


def install_file_logger():
    """
    Adds a custom formatter and a rotating file handler to the default logger.
    """
    path = get_user_path("ardj.log")

    max_size = 1000000
    max_count = 5

    logger = logging.getLogger()
    logger.setLevel(get_level())

    h = logging.handlers.RotatingFileHandler(path, maxBytes=max_size, backupCount=max_count)

    name = "ardj"
    h.setFormatter(logging.Formatter('%%(asctime)s - %s[%%(process)6d] - %%(levelname)s - %%(message)s' % name))
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)


def log_message(func, msg, args, kwargs):
    msg = msg.format(*args, **kwargs)

    global installed
    if not installed:
        install_file_logger()
        installed = True

    func(msg)


def log_info(msg, *args, **kwargs):
    return log_message(logging.info, msg, args, kwargs)


def log_debug(msg, *args, **kwargs):
    return log_message(logging.debug, msg, args, kwargs)


def log_warning(msg, *args, **kwargs):
    return log_message(logging.warning, msg, args, kwargs)


def log_error(msg, *args, **kwargs):
    return log_message(logging.error, msg, args, kwargs)


def log_exception(msg, *args, **kwargs):
    return log_message(logging.exception, msg, args, kwargs)


__all__ = ["log_debug", "log_info", "log_warning", "log_error", "log_exception"]
