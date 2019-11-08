import os
from Managers.ConfigManager import Config
from elasticsearch import Elasticsearch


class ElasticSearch(object):
    def __new__(cls, test=1):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ElasticSearch, cls).__new__(cls)
            print(Config.database_es.url)
            print(Config.database_es.port)
            cls.instance.client = Elasticsearch(hosts=[{"host": Config.database_es.url, "port": int(Config.database_es.port)}])
        return cls.instance

    def search(self, index="twitter", body={"query": {"match_all": {}}}):
        return self.instance.client.search(index=index, body=body)

def main():
    #print("Hello World!")
    pwd = os.path.dirname(os.path.abspath(__file__))
    print('%s/DB-Test.ini' % pwd)
    Config.add_config_ini('%s/DB-Test.ini' % pwd)
    print(Config.database.database)
    mango = ElasticSearch()
    result = mango.search()
    for es_tweet in result ["hits"]["hits"]:
        tweet = es_tweet["_source"]
        print(tweet)
    print(mango.search())





if __name__ == "__main__":
    main()
    exit(0)
