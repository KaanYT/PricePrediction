from Helper.DateHelper import DateHelper

from WWW.WebService.Base.BaseService import BaseService

from Helper.JsonDateHelper import JSONEncoder

from aiohttp import web


class WikiTweetService(BaseService):

    def __init__(self):
        super().__init__()
        self.wt_collection = self.config["database"]["wiki_tweet"]

    def add_wt(self, app):
        app.router.add_post('/wt', self.__wt_handler)

    async def __wt_handler(self, request):
        request = await request.json()
        object_id = request['object_id']
        info = list(self.get_news_data(self.db, self.wt_collection, object_id))
        res={}
        if len(info) == 0:
            res = {
                'isError': True,
                'Message': "Object Is Not Found."
            }
        else:
            print(info)
            res = {
                'isError': False,
                'Message': None,
                'wiki_relatedness': info[0]['wiki_relatedness'],
                'tweet_count': info[0]['tweet_count'],
                'tweet_percentage': info[0]['tweet_percentage']
            }
        res = JSONEncoder().encode(res)
        return web.json_response(res)

    @staticmethod
    def get_news_data(db, collection, object_id):
        query = {"url": object_id}
        return db.get_data(collection, query)
