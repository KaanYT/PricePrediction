from Managers.DatabaseManager.MongoDB import Mongo
import socket
from datetime import datetime
from datetime import date
import calendar
import os
from Managers.ConfigManager import Config


def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    Config.add_config_ini('%s/main.ini' % pwd)


class Statistics(object):
    START_YEAR = 2014
    END_YEAR = 2018
    categories = ['business', 'politics', 'energy', 'commodities', 'stocks', 'exclusive', 'economy', 'world', 'technology', 'money',
     'news', 'economics', 'tech', 'bonds', '', 'News_']

    def collect(self):
        socket.setdefaulttimeout(120)  # 120 seconds
        db=Mongo()

        start = datetime(self.START_YEAR, 1, 1, 0, 0, 0, 0)
        end = datetime(self.START_YEAR, 1+1, 1, 0, 0, 0, 0)
        collection = db.create_collection("FilteredNews")
        print("\t", end='\t')
        for category in self.categories:
            print(category, end='\t')
        print()
        while end.year < self.END_YEAR:
            count = collection.find({'RSS_Date': {'$gte': start, '$lt': end}}).count(False)
            # Get Category Count
            result = collection.aggregate([{ '$match': { 'date': {'$gte': start, '$lt': end},} },
                                { "$group": { "_id": { "$toLower": "$category" }, "count": { "$sum": 1 } } },
                                { "$group": { "_id": None, "counts": { "$push": { "k": "$_id", "v": "$count" } } } },
                                { "$replaceRoot": { "newRoot": { "$arrayToObject": "$counts" } } } ])
            print(str(start.year) + "." + str(start.month) + " \t " + str(count), end='\t')
            list_result = list(result)
            for item in list_result:
                for category in self.categories:
                    if category in item:
                        print(item[category], end='\t')
                    else:
                        print('0', end='\t')
            print()
            start = Statistics.add_one_month(start)
            end = Statistics.add_one_month(end)
        #for doc in db.instance.db.find({'time': {'$gte': start, '$lt': end}}):
        #    print(doc)

    @staticmethod
    def add_years(d, years):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).

        """
        try:
            return d.replace(year = d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    def add_one_month(orig_date):
        # advance year and month by one month
        new_year = orig_date.year
        new_month = orig_date.month + 1
        # note: in datetime.date, months go from 1 to 12
        if new_month > 12:
            new_year += 1
            new_month -= 12

        last_day_of_month = calendar.monthrange(new_year, new_month)[1]
        new_day = min(orig_date.day, last_day_of_month)

        return orig_date.replace(year=new_year, month=new_month, day=new_day)
