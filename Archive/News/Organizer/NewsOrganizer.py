import re
import os
import json
import platform
import traceback

from pymongo import IndexModel
from pymongo.errors import CursorNotFound
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

from Managers.DatabaseManager.MongoDB import Mongo

from Helper.DateHelper import DateHelper
from Helper.FileHelper import FileHelper
from Helper.WordPreProcessing import PreProcessing
from Helper.JsonDateHelper import DateTimeDecoder
from Managers.LogManager.Log import Logger

from Forecast.Wiki.WikiForecast import WikiForecast
from Forecast.Twitter.TwitterForecast import TwitterForecast

from Predictor.NewsDnnGeneral.NewsDnnGeneralWordEmbedding import WordEmbedding


class NewsOrganizer(object):

    def __init__(self, word_embedding_path=None):
        self.config = self.get_config()
        if word_embedding_path is None:
            word_embedding_path = self.config["wordEmbedding"]["path"]
        self.embedding = WordEmbedding(word_embedding_path)

    def organize(self):
        db = Mongo()
        news_collection = db.create_collection("News")
        news_filtered = db.create_collection("FilteredNews", NewsOrganizer.get_index_models())

        for news in news_collection.find():
            article = NewsOrganizer.get_article(news)
            if article is None:
                FileHelper.append_to_file(self.config["log"]["Article_None"], news["_id"])
                continue
            if article == "":
                FileHelper.append_to_file(self.config["log"]["Article_Empty"], news["_id"])
                continue
            date = NewsOrganizer.get_date(news)
            if not date:
                FileHelper.append_to_file(self.config["Log"]["Date_None"], news["_id"])
                continue
            summery = NewsOrganizer.get_summery(news)
            if not summery:
                FileHelper.append_to_file(self.config["Log"]["Summery_None"], news["_id"])
                continue
            try:
                news_filtered.insert({
                    "title": NewsOrganizer.get_title(news),
                    "summery": summery,
                    "category": NewsOrganizer.get_category(news),
                    "date": date,
                    "article": article,
                    "url": news['URL'],
                    "canonical_link": news['Canonical_Link'],
                    "authors": news['Authors']
                })
            except Exception as exception:
                Logger().get_logger().error(type(exception).__name__, exc_info=True)
                traceback.print_exc()

    def dnn_organizer(self, collection="Product", key="BRTUSD"):
        db = Mongo()
        pre_processing = PreProcessing()
        news_collection = db.create_collection(self.config["database"]["collection"])
        news_filtered = db.create_collection(self.config["database"]["destination"], NewsOrganizer.get_index_models())

        for news in news_collection.find(self.config["database"]["query"]):
            date = news.get('date')
            before = self.get_price_before_date(db, collection, key, date)
            minute = self.get_price_at_date(db, collection, key, date)
            hour = self.get_price_at_date(db, collection, key, date, minutes=60)
            day = self.get_price_at_date(db, collection, key, date, add_day=True)
            try:
                news_filtered.insert({
                    "_id": news.get('_id'),
                    "title": pre_processing.preprocess(news.get('title')),
                    "summery": pre_processing.preprocess(news.get('summery')),
                    "article": pre_processing.preprocess(news.get('article')),
                    "url": news.get('url'),
                    "category": news.get('category'),
                    "price_after_minute": minute,
                    "price_after_hour": hour,
                    "price_after_day": day,
                    "price_before": before,
                    "date": date,
                    "authors": news['authors']
                })
            except Exception as exception:
                Logger().get_logger().error(type(exception).__name__, exc_info=True)
                traceback.print_exc()

    def dnn_organizer_with_wiki_tweets(self, collection="Product", key="BRTUSD", name="Brent Crude"):
        db = Mongo()
        pre_processing = PreProcessing()
        news_collection = db.create_collection(self.config["database"]["collection"])
        news_filtered = db.create_collection(self.config["database"]["destination"], NewsOrganizer.get_index_models())
        wiki_forecast = WikiForecast()
        twitter_forecast = TwitterForecast()
        if self.config["elasticSearch"]["enableTag"]:
            tags = twitter_forecast.get_pre_defined_tags()
        else:
            tags = {"tags": []}
        count = 0
        while True:
            processed = 0
            try:
                cursor = news_collection.find(self.config["database"]["query"], no_cursor_timeout=True).skip(processed)
                for news in cursor:
                    try:
                        summery = pre_processing.preprocess(news.get('summery'))
                        summery_similarity = wiki_forecast.get_similarity(summery, title=name)
                        date = news.get('date')
                        title = pre_processing.preprocess(news.get('title'))
                        before = self.get_price_before_date(db, collection, key, date)
                        minute = self.get_price_at_date(db, collection, key, date)
                        hour = self.get_price_at_date(db, collection, key, date, minutes=60)
                        day = self.get_price_at_date(db, collection, key, date, add_day=True)
                        total, percentage = twitter_forecast.get_popularity_from_elastic_search(date,
                                                                                                title + tags["tags"],
                                                                                                pre_processing,
                                                                                                maxsize=self.config["elasticSearch"]["maxSize"])
                        news_filtered.insert({
                            "_id": news.get('_id'),
                            "title": title,
                            "summery": pre_processing.preprocess(news.get('summery')),
                            "article": pre_processing.preprocess(news.get('article')),
                            "url": news.get('url'),
                            "category": news.get('category'),
                            "price_after_minute": minute,
                            "price_after_hour": hour,
                            "price_after_day": day,
                            "price_before": before,
                            "wiki_relatedness": summery_similarity,
                            "tweet_count": total,
                            "tweet_percentage": percentage,
                            "date": date,
                            "authors": news['authors']
                        })
                    except Exception as exception:
                        Logger().get_logger().error(type(exception).__name__, exc_info=True)
                        traceback.print_exc()
                    count = count + 1
                    if count % 500 == 0:
                        print(count)
                    processed += 1
                cursor.close()
                break
            except CursorNotFound:
                processed += 1
                print("Lost cursor. Retry with skip")

    @staticmethod
    def get_index_models():
        return [IndexModel("url", name="index_url", unique=True),
                IndexModel("date", name="index_date")]

    @staticmethod
    def get_summery(news):
        summery_rss = news['RSS_Summery']
        summery_generated = news['Summery_Generated']
        selected_summery = summery_rss
        if not summery_rss:
            if summery_generated:
                selected_summery = summery_generated
            else:
                return None  # Record For Later Use
        elif re.search(r"<[a-z][\s\S]*>", summery_rss, re.IGNORECASE):
            selected_summery = BeautifulSoup(summery_rss).text.strip()
            if not selected_summery:
                selected_summery = summery_generated
        return selected_summery

    @staticmethod
    def get_article(news):
        article = news.get('Article')
        if re.search("404 not found", article, re.IGNORECASE):
            return None
        return article

    @staticmethod
    def get_category(news):
        category = news.get('RSS_Category')
        if category is None:
            category = "News_"
        return category

    @staticmethod
    def get_title(news):
        rss_title = news['RSS_Title']
        title = news['Title']
        selected_title = rss_title
        if title is not None:
            if len(title) > len(rss_title):
                selected_title = title
        return selected_title

    @staticmethod
    def get_date(news):
        date = news['Date']
        rss_date = news['RSS_Date']
        selected_date = rss_date
        if date:
            if DateHelper.is_time_of_date_exist(date):
                try:
                    if date > rss_date:
                        selected_date = rss_date
                    else:
                        selected_date = date
                except:
                    selected_date = date
        elif rss_date:
            selected_date = rss_date
        else:
            try:
                metadata = news['Meta_Data'].get("pubdate")
                if metadata:
                    return DateHelper.str2date(metadata)
                else:
                    html = news['HTML']
                    sub_index = html.find('publishDate')
                    print(news['Meta_Data']["pubdate"])
                    if sub_index > 0:
                        date = html[sub_index:(sub_index + 100)]
                        result = re.search('publishDate":"(.*?)",', date)
                        if result:
                            print(result.group(1))
                            selected_date = DateHelper.str2date(result.group(1))
                        else:
                            return None
                    else:
                        return None
            except Exception:
                return None
        return selected_date

    @staticmethod
    def get_price_at_date(db, collection, key, date: datetime, add_day=False, minutes=1):
        if add_day:
            start = date + timedelta(days=1)
        else:
            start = date + timedelta(minutes=minutes)
        end = start + timedelta(days=7)
        query = {
            "Date":
                {
                    "$gte": start,
                    "$lt": end
                },
            "Key": key
        }
        fields = {"Date": 1, "Open": 1, "Volume": 1, "High": 1, "_id": 0}
        return db.get_data_one(collection, query, fields, sort=[('Date', 1)])

    @staticmethod
    def get_price_before_date(db, collection, key, date: datetime):
        start = date - timedelta(days=7)
        end = date
        query = {
            "Date":
                {
                    "$gte": start,
                    "$lt": end
                },
            "Key": key
        }
        fields = {"Date": 1, "Open": 1, "Volume": 1, "High": 1, "_id": 0}
        return db.get_data_one(collection, query, fields, sort=[('Date', -1)])

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return json.load(open(pwd + '/config_w.json', 'r'), cls=DateTimeDecoder)
        else:
            return json.load(open(pwd+'/config.json', 'r'), cls=DateTimeDecoder)
