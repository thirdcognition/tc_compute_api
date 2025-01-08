import logging
import os
import time
import warnings
import textwrap
from celery.app.log import Logging

IN_PRODUCTION = os.getenv("TC_PRODUCTION", "False") == "True" or False


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    LEVEL_SYMBOLS = {
        "DEBUG": "D",  # Bug
        "INFO": "I",  # Information
        "WARNING": "W",  # Warning
        "ERROR": "E",  # Cross mark
        "CRITICAL": "C",  # Fire
    }
    RESET = "\033[0m"

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        datefmt = datefmt or "%y%m%d %H:%M:%S.%f"
        s = time.strftime(datefmt, ct)
        if datefmt and "%f" in datefmt:
            s = s.replace(".f", f".{int(record.msecs):03d}")
        return s

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS and levelname in self.LEVEL_SYMBOLS:
            record.levelname = (
                f"{self.COLORS[levelname]}{self.LEVEL_SYMBOLS[levelname]}{self.RESET}"
            )
        # Truncate processName to ensure fixed length before message
        # Ensure processName is fixed width
        procName = (
            record.processName.replace("Process", "")
            .replace("Spawn", "S")
            .replace("ForkPoolWork", "Work")
        )
        record.processName = (procName[:-4]) if len(procName) > 4 else procName.ljust(4)
        formatted_message = super().format(record)
        if len(record.message) > 84:
            separator_index = formatted_message.rindex("|") - 9
            indent = " " * separator_index
            wrapped_lines = textwrap.wrap(record.message, width=84)

            whitespace = (
                record.message[: (len(record.message) - len(record.message.lstrip()))]
                + "\t"
            ).replace("\t", "    ")[:12]

            wrapped_message = (
                wrapped_lines[0]
                + "\n"
                + "\n".join(
                    [
                        indent + "| " + whitespace + (line).strip()
                        for line in wrapped_lines[1:]
                    ]
                )
            )
            formatted_message = formatted_message.replace(
                record.message, wrapped_message
            )
        return formatted_message


log_format = ColoredFormatter(
    "%(processName)s - %(levelname)-8s: %(asctime)s| %(message)s",
    datefmt="%y%m%d %H:%M:%S.%f",
)

logging.captureWarnings(True)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# root logger
root_logger = logging.getLogger()

root_logger.setLevel(logging.INFO if not IN_PRODUCTION else logging.WARNING)

# standard stream handler
# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)


class CeleryLogger(Logging):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    def setup_logging_subsystem(
        self,
        loglevel=None,
        logfile=None,
        format=None,
        colorize=None,
        hostname=None,
        **kwargs,
    ):
        if self.already_setup:
            return
        super().setup_logging_subsystem(
            loglevel, logfile, format, colorize, hostname, **kwargs
        )
        self.logger.info("Celery logging subsystem initialized.")


logger = logging.getLogger(__name__)
