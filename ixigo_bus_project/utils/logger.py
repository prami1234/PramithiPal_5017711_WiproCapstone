import logging
import os


class LogGen:

    @staticmethod
    def loggen(name=__name__):

        if not os.path.exists("logs"):
            os.makedirs("logs")

        logging.getLogger("WDM").setLevel(logging.WARNING)

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # UTF-8 encoding prevents UnicodeEncodeError on Windows
            file_handler = logging.FileHandler(
                "logs/automation.log", encoding="utf-8"
            )
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger