"""
This logger is configured to log SDK behaviors.

Each api request and answer are logged at level ``DEBUG`` and each api resource
created is logged at level ``INFO``. Warnings and errors are logged at the
expected level: ``WARNING`` and ``ERROR``.

If you meet some unexpected behavior or bugs then please use the following lines
to store in a file the behavior::

    >>> import os.path as path
    >>> path_logfile = path.join( # similar to /home/my_nickname/.mang-sdk.log
    ...     path.expanduser('~'),
    ...     '.mang-sdk.log'
    ... )
    >>> from mangrove.logger import logger, logging
    >>> from logging.handlers import RotatingFileHandler
    >>> file_handler = RotatingFileHandler(
    ...     path_to_your_logfile, 'a', 1000000, 1
    ... )
    >>> file_handler.setLevel(logging.DEBUG)
    >>> logger.addHandler(file_handler)

Run your script/code (with the unexpected behavior) and send it to our support
(support@mangrove.ai).
"""
import logging


# create logger
logger = logging.getLogger('MANGROVE-SURFACE-SDK')
logger.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# create console handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def log_exception(func):
    def _inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(repr(e))
            raise
    _inner.__name__ = func.__name__
    _inner.__doc__ = func.__doc__
    return _inner
