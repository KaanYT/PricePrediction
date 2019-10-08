"""
Read the output of a zipped twitter archive from:
https://archive.org/details/twitterstream
"""
import bz2
import json
import os
from pymongo import IndexModel
from datetime import datetime
from Managers.LogManager.Log import Logger
from Managers.DatabaseManager.MongoDB import Mongo


class TweetRecorder(object):

    def __init__(self, directory="/Users/kaaneksen/Desktop/Master Project/Twitter/02", collection_name="Tweet"):
        self.directory = directory
        self.col = Mongo().create_collection(collection_name, TweetRecorder.get_index_models())
        self.total = 0

    def load_all_tweets_in_directory(self, directory=None):
        """Walk all files in directory and loads all tweets into a MongoDb"""
        files_processed = 0
        if directory is None:
            directory = self.directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                files_processed += 1
                filename = os.path.join(root, file)
                if not filename.endswith('.bz2'):
                    continue
                print('Starting work on file ' + str(files_processed) + '): ' + filename)
                self.handle_file(filename)
                if files_processed % 20 == 0:
                    print("Total Tweets Processed : {}".format(self.total))

    def handle_file(self, filename):
        """Takes a filename, loads all tweets into a MongoDb"""
        tweets = TweetRecorder.load_bz2_json(filename)
        tweet_dicts = []
        tweets_saved = 0
        for tweet in tweets:
            tweet_dict, tweets_saved = TweetRecorder.load_tweet(tweet, tweets_saved)  # Extracts proper items and places them in database
            if tweet_dict:
                tweet_dicts.append(tweet_dict)
        self.total = self.total + len(tweet_dicts)
        try:
            self.col.insert_many(tweet_dicts, ordered=False, bypass_document_validation=True)
        except Exception:
            Logger().get_logger().error('Insert Error - Twitter', exc_info=True)
        return True

    @staticmethod
    def load_bz2_json(filename):
        """ Takes a bz2 filename, returns the tweets as a list of tweet dictionaries"""
        data = open(filename, "rb").read()
        lines = bz2.decompress(data).decode("utf-8").split("\n")
        tweets = []
        for line in lines:
            try:
                if line == "":
                    continue
                tweets.append(json.loads(line))
            except:  # I'm kind of lenient as I have millions of tweets, most errors were due to encoding or so)
                continue
        return tweets

    @staticmethod
    def load_tweet(tweet, tweets_saved):
        """Takes a tweet (dictionary) and convert to appropriate dictionary"""
        try:
            tweet_lang = tweet['lang']
            data = {
                '_id': tweet['id'],
                'tweet_text': tweet['text'],
                'tweet_location': tweet['coordinates'],
                'tweet_created_at': datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'),
                'tweet_entities': tweet['entities'],
                'tweet_replay_to_tweet': tweet['in_reply_to_status_id'],
                'tweet_replay_to_user': tweet['in_reply_to_user_id'],
                'tweet_user_id': tweet['user']['id'],
                'tweet_user_lang': tweet['user']['lang'],
                'tweet_user_name': tweet['user']['name'],
                'tweet_user_time_zone': tweet['user']['time_zone'],
                'tweet_user_followers_count': tweet['user']['followers_count'],
                'tweet_user_verified': tweet['user']['verified'],
                'tweet_user_all_tweet_count': tweet['user']['statuses_count']
            }
            if tweet_lang != "en":
                return {}, tweets_saved
            else:
                tweets_saved += 1
                return data, tweets_saved
        except KeyError:
            return {}, tweets_saved

    @staticmethod
    def get_index_models():
        return [IndexModel("tweet_created_at", name="index_date"),
                IndexModel("tweet_replay_to_tweet", name="index_replay_to"),
                IndexModel("tweet_user_id", name="index_user_id")]
    # IndexModel([("Date", 1), ("Key", 1)], unique=True, name="index_date_key"),
