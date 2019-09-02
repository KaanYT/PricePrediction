from Database.MongoDB import Mongo
from Helper.DateHelper import DateHelper
from newspaper import Article
from Archive.News import News
import archivecdx
import pandas as pd
from Logger.Log import Logger
import sqlite3
import re
from Archive.News.MultiThreadHelper import NewsPool  #Multi Thread


class FileCollector(object):
    SQL_LOCATION = "C:\\Users\\eksen\\Downloads\\all-the-news.db"

    Title = 0
    Author = 1
    Date = 2
    Publication = 3
    Category = 4
    Digital = 5
    Section = 6
    Url = 7

    def collect(self):
        db = Mongo()
        conn = sqlite3.connect(self.SQL_LOCATION)
        c = conn.cursor()
        c.execute('SELECT title, author, date, publication, category, digital, section, url FROM longform')
        line_count = 0
        date_count = 0
        newslist = []
        for row in c:
            url = row[self.Url]
            date = DateHelper.str2date(row[self.Date])
            title = row[self.Title]
            if url == "" or url is None or date == "":  # Is There Url Or Date
                continue
            if db.is_title_url_exists(title, url):
                continue
            allUrls = FileCollector.extract_url_from_text(url)
            article = Article(allUrls[1])
            category = row[self.Category]
            section = row[self.Section]
            newslist.append(News.RssNews(title=title,
                                         time=date,
                                         summery='',
                                         category=FileCollector.get_category(category, section),
                                         tags='',
                                         url=allUrls[1],
                                         iaurl=allUrls[0],
                                         article=article))
            print(line_count)
            if len(newslist)==20:
                pool = NewsPool()
                pool.set(newslist)
                pool.join()
                newslist = []
            line_count += 1
        print(f'\t{line_count}')
        print(f'\t{len(newslist)}')

    @staticmethod
    def get_category(category,section):
        if category == "business" or section == "business" or section == "realestate":
            return category
        elif section == "politics":
            return "Politics"
        elif section == "markets":
            return "Market"
        elif section == "tech" or section == "technology":
            return "Tech"
        elif section == "money":
            return "Money"
        elif section == "news" or section == "world-news" or section == "us-news" or section == "uk-news":
            return "News"
        elif category == "newspaper":
            return "News"
        else:
            return "Kaggle"

    @staticmethod
    def extract_url_from_text(url):
        urls = re.split('https|http', url)
        if urls.__len__() == 2:
            return [FileCollector.getArchiveOrgLink(url), "http" + urls[1]]
        elif urls.__len__() == 3:
            return [url, "http" + urls[2]]
        else:
            print(url)

    @staticmethod
    def getArchiveOrgLink(url):
        try:
            siteHistory = archivecdx.Listing(url,
                                             fl=["original", "timestamp", "digest", "statuscode"],
                                             filter=["statuscode:200"])

            for history in siteHistory:
                return 'http://web.archive.org/web/%sid_/%s' % (history.timestamp, history.original)
        except Exception as exception:
            Logger().get_logger().error(type(exception).__name__, exc_info=True)
        return None

    @staticmethod
    def split_list(alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    @staticmethod
    def split_list_with_size(arr, size):
        arrs = []
        while len(arr) > size:
            pice = arr[:size]
            arrs.append(pice)
            arr = arr[size:]
        arrs.append(arr)
        return arrs
