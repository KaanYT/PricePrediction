from datetime import datetime
from datetime import timedelta
from Helper.DateHelper import DateHelper

from WWW.WebService.Base.BaseService import BaseService

from Helper.JsonDateHelper import JSONEncoder

from aiohttp import web


class PriceService(BaseService):

    def __init__(self):
        super().__init__()
        self.price_collection = self.db.create_collection(self.config["database"]["price"])

    def add_price(self, app):
        app.router.add_post('/get_price', self.__price_handler)

    async def __price_handler(self, request):
        request = await request.json()
        date = DateHelper.str2date(request['news_date'])
        info = self.get_price_before_date(self.db, request['collection'], request['key'], date, request['range'])
        date_list = []
        open_list = []
        high_list = []
        low_list = []
        close_list = []
        volume_list = []
        for a in info:
            date_list.append(str(a.get('Date')))
            open_list.append(a.get('Open'))
            high_list.append(a.get('High'))
            low_list.append(a.get('Low'))
            close_list.append(a.get('Close'))
            volume_list.append(a.get('Volume'))
        res = {
            'Title': request['collection'] + " - " + request['key'],
            'PriceDate': date_list,
            'OpenPrice': open_list,
            'HighPrice': high_list,
            'LowPrice': low_list,
            'ClosePrice': close_list,
            'Volume': volume_list
        }
        res = JSONEncoder().encode(res)
        return web.json_response(res)

    @staticmethod
    def get_price_before_date(db, collection, key, date: datetime, range=1):
        start = date - timedelta(days=range)
        end = date + timedelta(days=range)
        query = {
            "Date":
                {
                    "$gte": start,
                    "$lt": end
                },
            "Key": key
        }
        fields = {"Date": 1, "Open": 1, "Close": 1, "Volume": 1, "High": 1, "Low": 1, "_id": 0}
        return db.get_data(collection, query, fields, sort=[('Date', -1)])
