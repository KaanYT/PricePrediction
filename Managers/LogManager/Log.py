import logging
from Managers.ConfigManager import Config
from mongolog.handlers import MongoHandler

"""LogManager Example Usage: 
from LogManager.Log import LogManager

            try:
                1 / 0
            except:
                Log.LogManager().get_logger().error('test zero division', exc_info=True)
"""


class Logger(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
            cls.instance.logger = logging.getLogger('MScThesis')
            cls.instance.logger.addHandler(MongoHandler.to(db=Config.database.database, collection='log'))
            cls.instance.logger.setLevel(logging.DEBUG)
        return cls.instance

    def get_logger(self):
        return self.instance.logger



