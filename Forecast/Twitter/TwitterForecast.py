import os
import json
from datetime import datetime
from datetime import timedelta
from Managers.DatabaseManager.ElasticSearchDB import ElasticSearch
from Predictor.NewsDnnBase.NewsDnnBaseWordEmbedding import WordEmbedding


class TwitterForecast(object):
    def __init__(self, word_embedding_path="/Users/kaaneksen/Downloads/glove/glove.6B.100d.txt"):
        self.embedding: WordEmbedding = WordEmbedding(word_embedding_path)

    def get_popularity_from_elastic_search(self, date, title, pre, maxsize=10000):
        tweets = self.get_tweets_before_date_from_elastic_search(date, title, maxsize=maxsize)
        total_tweets = tweets["hits"]["total"]["value"]
        if total_tweets == 0:
            return 0, 0
        else:
            count = 0
            for es_tweet in tweets["hits"]["hits"]:
                tweet = es_tweet["_source"]
                try:
                    tweet_filtered = pre.preprocess(tweet["tweet_text"])
                    cosine = self.embedding.get_similarity_sentence(title, tweet_filtered)
                except Exception as exception:
                    print("Exeption")
                    cosine = 6

                if cosine < 5.1:
                    count += 1
                    if tweet["tweet_user_verified"]:
                        count += 1
            if count == 0:
                return total_tweets, 0
            return total_tweets, count / total_tweets

    @staticmethod
    def get_tweets_before_date_from_elastic_search(date: datetime,
                                                   hashtags,
                                                   collection="twitter",
                                                   days=5,
                                                   maxsize=10000):
        start = date - timedelta(days=days)
        end = date
        es = ElasticSearch()
        query = {
            "size": maxsize,
            "query":
                {
                    "bool": {
                        "filter": {
                            "range": {
                                "tweet_created_at": {
                                    "gte": start,  #"2014-03-31T20:03:12.963",
                                    "lte": end,  #"2014-04-03T20:03:12.963"
                                }
                            }
                        },
                        "should": [
                            {
                                "terms": {
                                    "tweet_entities.hashtags.text": hashtags  # []
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                        "boost": 1.0
                    }
                }
        }
        return es.search(index=collection, body=query)

    @staticmethod
    def get_tweets_before_date_from_mongo(db, date: datetime, collection="Tweet", days=7):
        start = date - timedelta(days=5)
        end = date
        query = {
            "tweet_created_at":
                {
                    "$gte": start,
                    "$lt": end
                }
        }
        fields = {"tweet_text": 1, "tweet_user_fallowers_count": 1, "tweet_user_verified": 1, "tweet_created_at": 1, "_id": 0}
        return db.get_data(collection, query, fields).limit(1000)

    @staticmethod
    def get_pre_defined_tags():
        pwd = os.path.dirname(os.path.abspath(__file__))
        return json.load(open(pwd + '/tags_pre_defined.json', 'r'))
