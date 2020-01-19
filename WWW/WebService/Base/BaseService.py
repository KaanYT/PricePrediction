import os
import json
import platform

from Helper.JsonDateHelper import DateTimeDecoder

from Managers.DatabaseManager.MongoDB import Mongo


class BaseService(object):

    def __init__(self):
        self.config = self.__get_config()
        self.db = Mongo()

    @staticmethod
    def __get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return json.load(open(pwd + '/config_w.json', 'r'), cls=DateTimeDecoder)
        else:
            return json.load(open(pwd+'/config.json', 'r'), cls=DateTimeDecoder)
