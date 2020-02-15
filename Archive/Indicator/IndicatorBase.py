import os
import json
import platform


class IndicatorsBase(object):

    def __init__(self):
        self.config = self.get_config()

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return json.load(open(pwd + '/config_w.json', 'r'))
        else:
            return json.load(open(pwd + '/config.json', 'r'))
