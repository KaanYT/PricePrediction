from WWW.WebService.Base.BaseService import BaseService

from Helper.JsonDateHelper import JSONEncoder


from aiohttp import web


class NewsService(BaseService):

    def __init__(self):
        super().__init__()
        self.collection = self.db.create_collection(self.config["database"]["collection"])
        self.text_collection = self.config["database"]["text_collection"]
        self.news_query = self.config["database"]["query"]
        self.check_for = self.config["check_for"]

    def add_news(self, app):
        app.router.add_get('/random_news', self.__random_news_handler)

    async def __random_news_handler(self, request):
        filtered_news = list(self.collection.aggregate(self.news_query))[0]
        news_text = self.get_news_data(self.db, self.text_collection, filtered_news["url"])
        res = {
            'id': str(news_text.get('_id')),
            'title': news_text.get('title'),
            'summery': news_text.get('summery'),
            'category': news_text.get('category'),
            'article': news_text.get('article'),
            'url': news_text.get('url'),
            'authors': news_text.get('authors'),
            'news_date': str(news_text.get('date')),
            'wiki_relatedness': filtered_news.get('wiki_relatedness'),
            'tweet_count': filtered_news.get('tweet_count'),
            'tweet_percentage': filtered_news.get('tweet_percentage'),
            'wiki_relatedness_nor': self.get_key_from("wiki_relatedness_nor", filtered_news),
            'tweet_count_nor': self.get_key_from("tweet_count_nor", filtered_news),
            'check_for': self.check_for
        }
        res = JSONEncoder().encode(res)
        return web.json_response(res)

    @staticmethod
    def get_key_from(key, array):
        if key in array:
            return array.get(key)
        else:
            return "Not Found"

    @staticmethod
    def get_news_data(db, collection, object_id):
        query = {"url": object_id}
        return db.get_data_one(collection, query)