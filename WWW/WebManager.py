import pathlib
import sys
from aiohttp import web
from WWW.WebService.NewsService import NewsService
from WWW.WebService.PriceService import PriceService
from WWW.WebService.WikiTweetService import WikiTweetService
from WWW.WebService.NewsRecordService import NewsRecordService
# Mongo


class WebManager(object):

    def __init__(self):
        self.app = web.Application()
        self.news = NewsService()
        self.price = PriceService()
        self.wt = WikiTweetService()
        self.record = NewsRecordService()

    def add_static_files(self):
        path = str(pathlib.Path(__file__).parent / 'Static')
        self.app.router.add_static('/Static', path, show_index=True)
        self.app.router.add_get('/', self.home_redirect)

    @staticmethod
    async def home_redirect(request):
        return web.HTTPFound('/Static/index.html')  # Will not redirect for a few seconds.

    def add_news_root(self):
        self.news.add_news(self.app)
        self.price.add_price(self.app)
        self.wt.add_wt(self.app)
        self.record.add_record(self.app)

    def run(self):
        web.run_app(self.app)


if __name__ == "__main__":
    web_manager = WebManager()
    web_manager.add_static_files()
    web_manager.add_news_root()
    web_manager.run()
