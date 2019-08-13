# -----------------------------------------------------------------------
# Singleton MongoDB Manager
# -----------------------------------------------------------------------
# Singleton pattern restricts the instantiation of a class to one object.
# -----------------------------------------------------------------------
from ConfigManager import Config
from pymongo import MongoClient
import os


class Mongo(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Mongo, cls).__new__(cls)
            cls.instance.client = MongoClient(host=Config.database.url,
                                              port=int(Config.database.port),
                                              authSource=Config.database.database)
            cls.instance.db = cls.instance.client.get_database(Config.database.database)
        return cls.instance

    def insert(self, value):
        collection = self.instance.db.get_collection(Config.database.collection)
        collection.insert(value)

def main():
    #print("Hello World!")
    pwd = os.path.dirname(os.path.abspath(__file__))
    print('%s/DB-Test.ini' % pwd)
    Config.add_config_ini('%s/DB-Test.ini' % pwd)
    print(Config.database.database)
    mango = Mongo()
    db = mango.instance.client.get_database(Config.database.database)
    collection = db.get_collection("log")
    print(Config.database.username)
    print(Config.database.password)
    print(collection.find_one())



if __name__ == "__main__":
    main()
