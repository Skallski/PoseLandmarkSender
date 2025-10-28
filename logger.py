import sys
import logging
from logging.handlers import RotatingFileHandler


class Logger:
    _logger = None

    @classmethod
    def get(
        cls,
        name: str = "PoseLandmarkSender",
        filename: str = "PoseLandmarkSender.log",
        level: int = logging.INFO,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3,
    ):
        if cls._logger is not None:
            return cls._logger
        
        try:
            with open(filename, "w", encoding="utf-8"):
                pass
        except Exception:
            pass

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False
        logger.disabled = False

        for h in list(logger.handlers):
            logger.removeHandler(h)

        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        file_handler = RotatingFileHandler(
            filename, 
            mode = "a", 
            maxBytes = max_bytes, 
            backupCount = backup_count,
            encoding = "utf-8", 
            delay = False
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(fmt)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

        cls._logger = logger
        return cls._logger