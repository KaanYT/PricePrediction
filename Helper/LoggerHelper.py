import sys
import time
import logging
import logging.handlers


class LoggerHelper(object):
    loaded = False

    @staticmethod
    def setup_logger(filepath='logs'):
        # Add Std. Out
        root_logger = logging.getLogger()
        root_logger.addHandler(logging.StreamHandler(sys.stdout))

        # Setup Formatter
        # Ex: 2012-12-05 16:58:26,618 [MainThread] [INFO] Message
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        # Add File Output
        file_handler = logging.FileHandler("{0}/{1}.log".format(filepath, LoggerHelper.__get_filename()))
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        # Add Console Output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

    @staticmethod
    def __get_filename():
        date = time.strftime("%Y%m%d-%H%M%S")
        return date

    @staticmethod
    def critical(msg, *args, **kwargs):
        LoggerHelper.__check_setup()
        logging.critical(msg, args, kwargs)

    @staticmethod
    def info(msg, *args, **kwargs):
        LoggerHelper.__check_setup()
        logging.info(msg, args, kwargs)

    @staticmethod
    def debug(msg, *args, **kwargs):
        LoggerHelper.__check_setup()
        logging.debug(msg, args, kwargs)

    @staticmethod
    def error(msg, *args, **kwargs):
        LoggerHelper.__check_setup()
        logging.error(msg, args, kwargs)

    @staticmethod
    def __check_setup():
        if not LoggerHelper.loaded:
            LoggerHelper.setup_logger()
