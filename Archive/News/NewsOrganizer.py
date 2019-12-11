import re
import traceback

from pymongo import IndexModel
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

from Managers.DatabaseManager.MongoDB import Mongo

from Helper.DateHelper import DateHelper
from Helper.FileHelper import FileHelper
from Helper.WordPreProcessing import PreProcessing
from Managers.LogManager.Log import Logger

from Forecast.Wiki.WikiForecast import WikiForecast
from Forecast.Twitter.TwitterForecast import TwitterForecast

from Predictor.NewsDnnGeneral.NewsDnnGeneralWordEmbedding import WordEmbedding


class NewsOrganizer(object):
    DATE_START = datetime.strptime("2014-02-01", '%Y-%m-%d')
    DATE_END = datetime.strptime("2017-01-01", '%Y-%m-%d')
    FIND_FILTER = {'date': {'$gte': DATE_START, '$lt': DATE_END}}

    def __init__(self, word_embedding_path="/Users/kaaneksen/Downloads/glove/glove.6B.100d.txt"):
        self.embedding = WordEmbedding(word_embedding_path)

    def organize(self):
        db = Mongo()
        news_collection = db.create_collection("News")
        news_filtered = db.create_collection("FilteredNews", NewsOrganizer.get_index_models())

        for news in news_collection.find():
            article = NewsOrganizer.get_article(news)
            if article is None:
                FileHelper.append_to_file("NewsOrganizer_No_Article_List.txt", news["_id"])
                continue
            if article == "":
                FileHelper.append_to_file("NewsOrganizer_Article_Not_Found.txt", news["_id"])
                continue
            date = NewsOrganizer.get_date(news)
            if not date:
                FileHelper.append_to_file("NewsOrganizer_No_Date_List.txt", news["_id"])
                continue
            summery = NewsOrganizer.get_summery(news)
            if not summery:
                FileHelper.append_to_file("NewsOrganizer_No_Summery_List.txt", news["_id"])
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
        news_collection = db.create_collection("FilteredNews")
        news_filtered = db.create_collection("FilteredNewsForDnn", NewsOrganizer.get_index_models())

        for news in news_collection.find(self.FIND_FILTER):
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
        news_collection = db.create_collection("FilteredNews")
        news_filtered = db.create_collection("FilteredNewsWikiAndTweetForDnn", NewsOrganizer.get_index_models())
        wiki_forecast = WikiForecast()
        twitter_forecast = TwitterForecast()
        tags = twitter_forecast.get_pre_defined_tags()
        count = 0
        for news in news_collection.find(self.FIND_FILTER, no_cursor_timeout=True):
            try:
                summery = pre_processing.preprocess(news.get('summery'))
                cosine = wiki_forecast.get_similarity(summery, title=name)
                summery_percentage = round((1 - cosine) * 100, 2)
                date = news.get('date')
                title = pre_processing.preprocess(news.get('title'))
                before = self.get_price_before_date(db, collection, key, date)
                minute = self.get_price_at_date(db, collection, key, date)
                hour = self.get_price_at_date(db, collection, key, date, minutes=60)
                day = self.get_price_at_date(db, collection, key, date, add_day=True)
                total, percentage = twitter_forecast.get_popularity_from_elastic_search(date,
                                                                                        title + tags["tags"],
                                                                                        pre_processing)
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
                    "wiki_relatedness": summery_percentage,
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
