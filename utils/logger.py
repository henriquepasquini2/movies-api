import logging
import logging.handlers
import sys
import time
import traceback

from pythonjsonlogger import jsonlogger

from config import Configuration, settings
from utils.singleton import Singleton

LOG_STRING_FORMAT = (
    "%(asctime)s %(filename)-12s:" "%(lineno)d %(levelname)-8s %(message)s"
)


def is_not_healthcheck(record: logging.LogRecord):
    """
    Retorna True se record *não* for de rota usada em healthcheck.
    """
    msg = record.getMessage()

    is_health_route = msg.find("/health") != -1
    is_openapi_route = msg.find("/openapi.json") != -1
    is_healthcheck = is_health_route or is_openapi_route
    result = not is_healthcheck

    return result


class StackdriverJsonFormatter(jsonlogger.JsonFormatter, object):
    def __init__(
        self,
        fmt="%(levelname) %(message) %(filename) %(lineno) %(funcName)",
        style="%",
        *args,
        **kwargs,
    ):
        super().__init__(fmt=fmt, *args, **kwargs)

    def process_log_record(self, log_record):
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]

        return super().process_log_record(log_record)


class Logger(logging.Logger, metaclass=Singleton):

    def __init__(self):
        super().__init__("logger")
        self.configuration = Configuration()
        self.enable_logs = settings.LOGS_ENABLED
        LOG_LEVEL = settings.LOG_LEVEL
        level = (
            getattr(logging, LOG_LEVEL.upper(), logging.INFO)
            if self.enable_logs
            else logging.CRITICAL
        )

        handlers = []
        self.enable_stackdriver = settings.STACKDRIVER_LOGGER

        if self.enable_stackdriver:
            handler = logging.StreamHandler()
            formatter = StackdriverJsonFormatter()
            handler.setFormatter(formatter)
            handlers.append(handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT))
            console_handler.setLevel(level)
            handlers.append(console_handler)

            file_handler = logging.handlers.RotatingFileHandler(
                "data.log", maxBytes=1048576 * 10 * 1, backupCount=3
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT))
            handlers.append(file_handler)

        if self.hasHandlers():
            self.handlers.clear()

        self.setLevel(level)

        for handler in handlers:
            self.addHandler(handler)
            handler.setLevel(level)

        self.addFilter(is_not_healthcheck)

    def log_progress(self, method_name, started_at_epoch, done, total):
        if total and done:
            remaining_chunks = total - done
            elapsed_dt = time.time() - started_at_epoch
            chunks_per_sec = done / (elapsed_dt or sys.float_info.min)
            done_percentage = 100 * done / (total or float("nan"))
            if chunks_per_sec == 0:
                eta = "INF"
            else:
                remaining_secs = remaining_chunks / chunks_per_sec
                eta = time.strftime("%H:%M:%S", time.gmtime(remaining_secs))
            msg = (
                f"{method_name}: {done}/{total} "
                f"({done_percentage:.1f}%) - ETA {eta}"
            )
            self.info(msg)

    def error(self, msg, *args, exc_info=True, **kwargs):
        if exc_info:
            msg = f"{msg}\n{traceback.format_exc()}"

        # Call the original .error method with the formatted message
        super().error(msg, *args, **kwargs)
