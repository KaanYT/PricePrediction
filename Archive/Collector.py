import os
import feedparser
import archivecdx
from newspaper import Article

from datetime import datetime
from time import mktime
from Archive import News
from Archive.MultiThreadHelper import NewsPool  #Multi Thread


class AC(object):

    def collect(self):
        sites = self.read_website_collection()
        for site in sites:
            siteHistory = archivecdx.Listing(site,
                                             fl=["original", "timestamp", "digest", "statuscode"],
                                             filter=["statuscode:200"])
            print("Size of List :" + str(len(siteHistory.listing)))
            for history in siteHistory:
                timestamp = datetime.strptime(history.timestamp, "%Y%m%d%H%M%S")
                link = 'http://web.archive.org/web/%sid_/%s' % (history.timestamp, history.original)
                d = feedparser.parse(link)
                newslist = []
                for post in d.entries:
                    if post.published_parsed:
                        dt = datetime.fromtimestamp(mktime(post.published_parsed))
                    else:
                        dt = ''
                    article = Article(post.link)
                    print(post.link)
                    newslist.append(News.RssNews(title=post.title,
                                                 time=dt,
                                                 summery=post.summary,
                                                 tags='',
                                                 url=post.link,
                                                 iaurl=('http://web.archive.org/web/%sid_/%s' % (history.timestamp, post.link)),
                                                 article=article))
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



