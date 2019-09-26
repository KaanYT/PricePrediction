from Managers.DatabaseManager.MongoDB import Mongo
from pymongo import IndexModel
from Helper.DateHelper import DateHelper
from Helper.FileHelper import FileHelper
from bs4 import BeautifulSoup
import re
from datetime import datetime
from Managers.LogManager.Log import Logger
import traceback


class NewsOrganizer(object):
    DATE_START = datetime.strptime("2014-01-01", '%Y-%m-%d')
    DATE_END = datetime.strptime("2017-01-01", '%Y-%m-%d')
    FIND_FILTER = {'RSS_Date': {'$gte': DATE_START, '$lt': DATE_END}}

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

