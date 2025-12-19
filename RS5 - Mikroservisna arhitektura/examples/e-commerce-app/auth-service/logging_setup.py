# Custom logger komponenta za više razina u boji :)


import logging
import os


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(name)s | %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ColorFormatter(logging.Formatter):

    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    COLORS = {
        logging.DEBUG: DIM + "\033[37m",  # dim gray
        logging.INFO: "\033[36m",  # cyan
        logging.WARNING: "\033[33m",  # yellow
        logging.ERROR: "\033[31m",  # red
        logging.CRITICAL: BOLD + "\033[31m",  # bold red
    }

    def __init__(self, fmt: str, datefmt: str | None = None, use_colors: bool = True):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        if not self.use_colors:
            return super().format(record)

        original_levelname = record.levelname
        try:
            color = self.COLORS.get(record.levelno, "")
            record.levelname = f"{color}{original_levelname}{self.RESET}"
            return super().format(record)
        finally:
            record.levelname = original_levelname


class LoggingSetup:
    def __init__(self, logger_name: str | None = None):
        self.logger = logging.getLogger(
            logger_name or os.getenv("LOGGER_NAME", "auth-service")
        )
        self.logger.propagate = False

        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        if level_name.isdigit():
            level = int(level_name)
        else:
            level_map = logging.getLevelNamesMapping()
            level = level_map.get(
                level_name, level_map.get("WARNING") if level_name == "WARN" else None
            )
            if level is None:
                level = logging.INFO
        self.logger.setLevel(level)

        stream_handler = next(
            (h for h in self.logger.handlers if isinstance(h, logging.StreamHandler)),
            None,
        )
        if stream_handler is None:
            stream_handler = logging.StreamHandler()
            self.logger.addHandler(stream_handler)
        stream = getattr(stream_handler, "stream", None)
        is_tty = bool(getattr(stream, "isatty", lambda: False)())
        use_colors = is_tty and not os.getenv("NO_COLOR")

        stream_handler.setFormatter(
            ColorFormatter(
                DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT, use_colors=use_colors
            )
        )

    def get_logger(self) -> logging.Logger:
        return self.logger


logging_setup = LoggingSetup()

logger = logging_setup.get_logger()

if __name__ == "__main__":
    logger.info("Hello, world! I'm logging_setup.py and this is a test INFO message.")
    logger.warning(
        "Hello, world! I'm logging_setup.py and this is a test WARNING message."
    )
    logger.error("Hello, world! I'm logging_setup.py and this is a test ERROR message.")
    logger.critical(
        "Hello, world! I'm logging_setup.py and this is a test CRITICAL message."
    )
    logger.debug("Hello, world! I'm logging_setup.py and this is a test DEBUG message.")
