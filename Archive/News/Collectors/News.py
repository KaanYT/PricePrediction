from newspaper import Article
from Managers.DatabaseManager.MongoDB import Mongo
from urllib.request import urlopen
from Managers.LogManager.Log import Logger


class RssNews(object):

    """News objects abstract an online news article page
    """
    def __init__(self, title='', time='', summery='', category='', url='', iaurl='', tags=[], article=Article('')):
        self.RssTitle = title
        self.RssTime = time
        self.RssSummery = summery
        self.RssTags = tags
        self.RssCategory = category
        self.URL = url
        self.IA_URL = iaurl
        self.article = article
        self.row = ''
        self.selected_url = ''

    def download(self):
        self.selected_url = self.check_url()
        self.article.url = self.selected_url
        self.article.config.request_timeout = 180
        try:
            self.article.build()
            self.create_database_object()
            self.save_to_db()
        except Exception:
            Logger().get_logger().error('Article Build Error', exc_info=True)

    def save_to_db(self):
        mongo = Mongo()
        try:
            mongo.insert(self.row)
        except Exception:
            print(self.row)
            Logger().get_logger().error('Insert Error', exc_info=True)

    def create_database_object(self):
        for key, value in self.article.meta_data:
            if key.find('.') != -1:
                self.article.meta_data.pop(key)
        self.row = {
            'RSS_Title': self.RssTitle,
            'RSS_Date': self.RssTime,
            'RSS_Summery': self.RssSummery,
            'RSS_Category': self.RssCategory,
            'URL': self.URL,
            'DownloadUrl': self.selected_url,
            'Title': self.article.title,
            'Date': self.article.publish_date,
            'HTML': self.article.html,
            'Article': self.article.text,
            'Summery_Generated': self.article.summary,
            'Keywords_Generated': self.article.keywords,
            'Authors': self.article.authors,
            'Meta_Lang': self.article.meta_lang,
            'Meta_Data': self.article.meta_data,
            'Meta_Desc': self.article.meta_description,
            'Canonical_Link': self.article.canonical_link
        }

    def check_url(self):
        try:
            resp = urlopen(self.URL)
            if resp.getcode() == 200:
                return self.URL
            else:
                return self.IA_URL
        except:
            print("URL:" + self.URL)
            Logger().get_logger().error('URL Exception', exc_info=True)
            return self.IA_URL
