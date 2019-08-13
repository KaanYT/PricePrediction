import logging
from ConfigManager import Config
from mongolog.handlers import MongoHandler

"""Logger Example Usage: 
from Logger.Log import Logger

            try:
                1 / 0
            except:
                Log.Logger().get_logger().error('test zero division', exc_info=True)
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



