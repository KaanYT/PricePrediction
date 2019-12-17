import sys
import time
import os, os.path
import logging
import logging.handlers


class LoggerHelper(object):
    loaded = False

    @staticmethod
    def setup_logger(filepath='logs'):
        # Add Std. Out
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        # Setup Formatter
        # Ex: 2012-12-05 16:58:26,618 [MainThread] [INFO] Message
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        # Add File Output
        path = LoggerHelper.get_file_path(filepath)
        file_handler = logging.FileHandler(path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        # Add Console Output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)
        LoggerHelper.loaded = True

    @staticmethod
    def get_file_path(path):
        if path == "logs":
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path,
                                LoggerHelper.__get_filename() + ".log")
        else:
            path = os.path.join(path,
                                LoggerHelper.__get_filename() + ".log")
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        return path

    @staticmethod
    def __get_filename():
        date = time.strftime("%Y%m%d-%H%M%S")
        return date

    @staticmethod
    def critical(msg):
        LoggerHelper.__check_setup()
        logging.critical(msg)

    @staticmethod
    def info(msg):
        LoggerHelper.__check_setup()
        logging.info(msg)

    @staticmethod
    def debug(msg):
        LoggerHelper.__check_setup()
        logging.debug(msg)

    @staticmethod
    def error(msg):
        LoggerHelper.__check_setup()
        logging.error(msg)

    @staticmethod
    def __check_setup():
        if not LoggerHelper.loaded:
            LoggerHelper.setup_logger()
