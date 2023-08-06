import datetime
import logging
import logging.handlers as lh
from typing import Any, Generator, Iterable, List, Optional


class Logger(object):

    def __init__(self, name: str, level: str,
                 exception: Optional[Exception]) -> None:
        super().__init__()
        self._logger = logging.getLogger(name)
        self._level = level
        self._parts = []
        self._exception = exception

    def __lshift__(self, part: Any) -> 'Logger':
        self._parts.append(str(part))
        return self

    def __del__(self) -> None:
        msg = ' '.join(self._parts)
        log = getattr(self._logger, self._level)
        log(msg, exc_info=self._exception)


def DEBUG(name: str) -> Logger:
    return Logger(name, 'debug', None)


def INFO(name: str) -> Logger:
    return Logger(name, 'info', None)


def WARNING(name: str) -> Logger:
    return Logger(name, 'warning', None)


def ERROR(name: str) -> Logger:
    return Logger(name, 'error', None)


def CRITICAL(name: str) -> Logger:
    return Logger(name, 'critical', None)


def EXCEPTION(name: str, exception: Exception = None) -> Logger:
    return Logger(name, 'exception', exception)


def setup(log_name_list: Iterable[str],
          file_path: str = None) -> List[logging.Logger]:
    formatter = logging.Formatter(
        '{asctime}|{threadName:_<10.10}|{levelname:_<1.1}|{name:_<16.16}|{message}',
        style='{')
    handler = create_handler(file_path, formatter)
    loggers = [create_logger(name, handler) for name in log_name_list]
    return loggers


def create_handler(path: Optional[str],
                   formatter: logging.Formatter) -> logging.Handler:
    if path:
        # alias
        TRFHandler = lh.TimedRotatingFileHandler
        # rotate on Sunday
        handler = TRFHandler(path, when='w6', atTime=datetime.time())
    else:
        handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def create_logger(name: str, handler: logging.Handler) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
