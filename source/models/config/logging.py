import logging
import os
import time
import warnings
import textwrap
from celery.app.log import Logging
from dotenv import load_dotenv


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

if LOG_LEVEL == "DEBUG":
    env_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../", ".env")
    )
    load_dotenv(env_file)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


def wrap_with_indentation_preserved(message, width=84):
    # Split the text into lines so we can process each one
    lines = message.splitlines()
    wrapped_lines = []

    for line in lines:
        # Determine the leading whitespace of the line
        leading_spaces = len(line) - len(line.lstrip())
        indent = " " * leading_spaces

        # Wrap the line, ensuring subsequent lines match its indentation
        wrapped = textwrap.wrap(line.strip(), width=width, subsequent_indent=indent)
        wrapped_lines.extend(wrapped)

    return wrapped_lines


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
        formatted_message_split = formatted_message.split("|")
        formatted_message_split[0] = formatted_message_split[0].strip()
        formatted_message = " | ".join(formatted_message_split)
        if len(record.message) > 84:
            separator_index = formatted_message.rindex("|") - 9
            indent = " " * min(separator_index, 30)
            wrapped_lines = wrap_with_indentation_preserved(
                record.message.replace("\\n", "\n"), width=84
            )

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

# Use LOG_LEVEL to set the root logger level
root_logger.setLevel(LOG_LEVEL)

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


print("Set log level " + LOG_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
