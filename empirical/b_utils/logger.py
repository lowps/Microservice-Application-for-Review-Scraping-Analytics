import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class Logger:

    def __init__(self, loggername: str) -> logging.Logger:
        # create logger object
        self.logger = logging.getLogger(loggername)
        self.logger.setLevel(logging.DEBUG)

        # create file_handler
        log_path = os.path.dirname(os.path.dirname(__file__))
        log_path_output = log_path + "/c_logs/" + "out.log"
        file_handler = logging.FileHandler(log_path_output)
        file_handler.setLevel(logging.DEBUG)

        # create stream_handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        # create RotatingFileHandler
        rotating_file_handler = RotatingFileHandler(
            filename=log_path_output, mode="w", maxBytes=1024, backupCount=3
        )
        rotating_file_handler.setLevel(logging.DEBUG)

        # configure Formatter
        formatter = logging.Formatter(
            "%(levelname)s: %(asctime)s from %(name)s: %(process)s: %(funcName)s: %(lineno)s: %(message)s"
        )

        # set formatter ot handlers
        # set formatter to handlers
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # add handler to logger object
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def get_log(self):
        return self.logger


if __name__ == "__main":
    pass
