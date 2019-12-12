import os
import feedparser
import archivecdx
from newspaper import Article
from Managers.DatabaseManager.MongoDB import Mongo
from datetime import datetime
from time import mktime
from Archive.News.Collectors import News
from Archive.News.Collectors.MultiThreadHelper import NewsPool  #Multi Thread
from Managers.LogManager.Log import Logger
import socket


class NWC(object):
    #Pass_List = ["", "", "", "", ""]

    def collect(self):
        sites = self.read_website_collection()
        socket.setdefaulttimeout(120)  # 120 seconds
        db=Mongo()
        count = 0
        for info in sites:
            (site, category) = info.split(" ")
            siteHistory = archivecdx.Listing(site,
                                             fl=["original", "timestamp", "digest", "statuscode"],
                                             filter=["statuscode:200"])
            print("Size of List :" + str(len(siteHistory.listing)))
            for history in siteHistory:
                timestamp = datetime.strptime(history.timestamp, "%Y%m%d%H%M%S")
                link = 'http://web.archive.org/web/%sid_/%s' % (history.timestamp, history.original)
                print('(%d) - Archive Link : %s - %s' % (count, link, str(datetime.today())))
                #if site == "http://feeds.bbci.co.uk/news/business/rss.xml":
                #    if history.timestamp in self.Pass_List: #Control
                #        continue
                try:
                    d = feedparser.parse(link)
                except Exception as exception:
                    print("FeedParser Timeout ?")
                    Logger().get_logger().error(type(exception).__name__, exc_info=True)
                newslist = []
                for post in d.entries:
                    try:
                        count = count+1
                        if db.already_exists(post.link):
                            continue
                        if post.published_parsed:
                            try:
                                dt = datetime.fromtimestamp(mktime(post.published_parsed))
                            except AttributeError:
                                dt = ''
                        else:
                            dt = ''
                        article = Article(post.link)
                        newslist.append(News.RssNews(title=post.title,
                                                     time=dt,
                                                     summery=post.summary,
                                                     category=category,
                                                     tags='',
                                                     url=post.link,
                                                     iaurl=('http://web.archive.org/web/%sid_/%s' % (history.timestamp, post.link)),
                                                     article=article))
                    except Exception as exception:
                        Logger().get_logger().error(type(exception).__name__, exc_info=True)
                pool = NewsPool()
                pool.set(newslist)
                pool.join()

    @staticmethod
    def read_website_collection():
        pwd = os.path.dirname(os.path.abspath(__file__))
        with open('%s/websites.txt' % pwd) as f:
            websites = f.read().splitlines()
        print(websites)
        return websites



