import traceback
from transformers import pipeline
from Helper.DateHelper import DateHelper
from Forecast.Twitter.TwitterForecast import TwitterForecast


class TransformersTest(object):

    def __init__(self):
        super().__init__(self)

    @staticmethod
    def sentiment_analysis_test(date=None, hashtags=None):
        nlp = pipeline('sentiment-analysis')
        if date is None:
            date = DateHelper.str2date("2015-05-12T16:07:40Z")
        if hashtags is None:
            hashtags = ["oil", "crude", "crude oil"]
        tweets = TwitterForecast.get_tweets_before_date_from_elastic_search(date, hashtags, days=5, maxsize=10000)
        total_tweets = tweets["hits"]["total"]["value"]
        if total_tweets == 0:
            print("No Tweet Found")
        else:
            for es_tweet in tweets["hits"]["hits"]:
                tweet = es_tweet["_source"]
                try:
                    text = tweet["tweet_text"].replace("\n", "")
                    username = tweet['tweet_user_name']
                    sentiment = nlp(text)[0]
                    if sentiment['score'] > 0.98:
                        if tweet["tweet_user_verified"]:
                            print('[%s-%s] - %s (%s)' % (u"\U0001F44D", sentiment['label'], text, username))
                        else:
                            print('[%s] - %s (%s)' % (sentiment['label'], text, username))
                except Exception as exception:
                    print(exception)
                    traceback.print_exc()
