import logging
import time
from inspect import getframeinfo, stack
from typing import Dict

from pythonjsonlogger import jsonlogger


class CogniteLogger:
    log_level = "INFO"
    """
    Class to manage logging. Default log_level is set to INFO.
    """
    def __init__(self, logger_name: str):
        self.logger_name = logger_name

        # Setup logger
        self.logger = logging.getLogger(logger_name)
        if not self.logger.hasHandlers():
            log_handler = logging.StreamHandler()
            formatter = jsonlogger.JsonFormatter()
            log_handler.setFormatter(formatter)
            self.logger.addHandler(log_handler)
            self.logger.setLevel(self.log_level)

    def add_standard_fields(self, extra: Dict = {}):
        extra["timestamp"] = int(time.time())

        # Get information about who called the logger, so that we can add information about which filename, line number,
        # and function led to the log statement.
        caller = getframeinfo(stack()[2][0])
        source_location = {
            "file": str(caller.filename),
            "function": str(caller.function),
            "line": str(caller.lineno),
            "logger name": self.logger_name
        }
        extra["sourceLocation"] = source_location

        return extra

    def debug(self, msg, extra: Dict = {}):
        extra["severity"] = "DEBUG"
        extra = self.add_standard_fields(extra)
        self.logger.debug(msg, extra=extra)

    def info(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "INFO"
        extra = self.add_standard_fields(extra)
        self.logger.info(msg, extra=extra, exc_info=exc_info)

    def warning(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "WARNING"
        extra = self.add_standard_fields(extra)
        self.logger.warning(msg, extra=extra, exc_info=exc_info)

    def error(self, msg, extra: Dict = {}, exc_info=None):
        extra["severity"] = "ERROR"
        extra = self.add_standard_fields(extra)
        self.logger.error(msg, extra=extra, exc_info=exc_info)

