from Database.MongoDB import Mongo
import socket
from datetime import datetime
from datetime import date


class Statistics(object):

    def collect(self):
        socket.setdefaulttimeout(120)  # 120 seconds
        db=Mongo()

        start = datetime.datetime(1998, 1, 1, 1, 35, 6, 764)
        end = datetime.datetime(1999, 1, 1, 1, 55, 3, 381)
        print(start)
        for doc in db.instance.db.find({'time': {'$gte': start, '$lt': end}}):
            print(doc)

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