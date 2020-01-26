import traceback

from pymongo import IndexModel
from WWW.WebService.Base.BaseService import BaseService

from Helper.JsonDateHelper import JSONEncoder
from Helper.LoggerHelper import LoggerHelper

from aiohttp import web


class NewsRecordService(BaseService):

    def __init__(self):
        super().__init__()
        self.defaultCollection = self.config["database"]["collection"]
        self.toCollection = self.db.create_collection(self.config["database"]["record_collection"],
                                                      NewsRecordService.get_index_models())

    def add_record(self, app):
        app.router.add_post('/record_news', self.__random_news_handler)
        app.router.add_post('/incorrect_news', self.__incorrect_news_handler)
        app.router.add_get('/recorded_news', self.__news_count_handler)

    async def __incorrect_news_handler(self, request):
        request = await request.json()
        default = self.get_news_data(self.db, self.defaultCollection, request['object_id'])
        if default is None:
            res = {
                'isError': True,
                'Message': "Object Is Not Found."
            }
            res = JSONEncoder().encode(res)
            return web.json_response(res)
        else:
            default['is_controlled'] = True
            default['is_incorrect'] = True
            self.record_one_field(self.defaultCollection, default)
            res = {
                'isError': False,
                'Message': "Success"
            }
            res = JSONEncoder().encode(res)
            return web.json_response(res)

    async def __random_news_handler(self, request):
        request = await request.json()
        print(request)
        default = self.get_news_data(self.db, self.defaultCollection, request['object_id'])
        if default is None:
            res = {
                'isError': True,
                'Message': "Object Is Not Found."
            }
            res = JSONEncoder().encode(res)
            return web.json_response(res)
        else:
            try:
                self.toCollection.insert({
                    "_id": default["_id"],
                    "title": default["title"],
                    "summery": default["summery"],
                    "article": default['authors'],
                    "url": default["url"],
                    "category": request["categories"],
                    "price_after_minute": default["price_after_minute"],
                    "price_after_hour": default["price_after_hour"],
                    "price_after_day": default["price_after_day"],
                    "price_before": default["price_before"],
                    "wiki_relatedness": default["wiki_relatedness"],
                    "tweet_count": default["tweet_count"],
                    "tweet_percentage": default["tweet_percentage"],
                    "wiki_relatedness_nor": default["wiki_relatedness_nor"],
                    "tweet_count_nor": default["tweet_count_nor"],
                    "date": default["date"],
                    "authors": default["authors"],
                    "comment": request['comment'],
                    "price_effect": request['effect']
                })
                default['is_controlled'] = True
                default['is_incorrect'] = False
                self.record_one_field(self.defaultCollection, default)
                # price_effect effect
                res = {
                    'isError': False,
                    'Message': "Success"
                }
            except Exception as exception:
                res = {
                    'isError': True,
                    'Message': "Insert Error. Please inform the Admin"
                }
                LoggerHelper.error(type(exception).__name__)
                LoggerHelper.error("Ex: " + str(exception))
                LoggerHelper.error(traceback.format_exc())
            res = JSONEncoder().encode(res)
            return web.json_response(res)

    async def __news_count_handler(self, request):
        news_count = self.toCollection.count()
        res = {
            'news_count': str(news_count)
        }
        res = JSONEncoder().encode(res)
        return web.json_response(res)

    def record_one_field(self,collection_name, field):
        collection = self.db.create_collection(collection_name)
        collection.save(field)

    @staticmethod
    def get_news_data(db, collection, object_id):
        query = {"url": object_id}
        return db.get_data_one(collection, query)

    @staticmethod
    def get_index_models():
        return [IndexModel("url", name="index_url", unique=True),
                IndexModel("date", name="index_date")]
