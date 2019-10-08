from datetime import datetime
import pandas as pd


class DateHelper(object):

    @staticmethod
    def is_time_of_date_exist(date):
        if date.hour == 0 and date.minute == 0 and date.second == 0 and date.microsecond == 0:
            return False
        else:
            return True

    @staticmethod
    def str2date(string):
        "Parse a string into a datetime object."
        if string == '' or pd.isnull(string) or string == 'nan' or string is None:
            return ""
        string = string.split('"', 1)[0]
        for fmt in DateHelper.date_formats():
            try:
                return datetime.strptime(string, fmt)
            except ValueError:
                pass
        raise ValueError("'%s' is not a recognized date/time" % string)

    @staticmethod
    def date_formats():
        #2014-03-12T16:07:40Z
        return ["%Y-%m-%dT%H:%M:%SZ", "%Y%m%d%H:%M:%S", "%Y%m%d% H:%M:%S", "%Y.%m.%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d", "%Y/%m/%-d"]

    @staticmethod
    def get_current_date():
        return '%s' % datetime.now().strftime('%d%m%Y-%H%M%S')
