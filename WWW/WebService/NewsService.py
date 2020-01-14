from WWW.WebService.Base.BaseService import BaseService

from Helper.JsonDateHelper import JSONEncoder


from aiohttp import web


class NewsService(BaseService):

    def __init__(self):
        super().__init__()
        self.news_collection = self.db.create_collection(self.config["database"]["collection"])
        self.news_query = self.config["database"]["query"]

    def add_news(self, app):
        app.router.add_get('/random_news', self.__random_news_handler)

    async def __random_news_handler(self, request):
        news = self.news_collection.find_one(self.news_query)
        res = {
            'id': str(news.get('_id')),
            'title': news.get('title'),
            'summery': news.get('summery'),
            'category': news.get('category'),
            'article': news.get('article'),
            'url': news.get('url'),
            'authors': news.get('authors'),
            'news_date': str(news.get('date'))
        }
        res = JSONEncoder().encode(res)
        return web.json_response(res)

    @staticmethod
    async def __save_updated_news(request):
        res = {"q": "qqq", "a": "aaa"}
        return web.json_response(res)
