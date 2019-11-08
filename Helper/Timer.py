import datetime as dt


class Timer(object):

    def __init__(self):
        self.start_dt = None

    def start(self):
        self.start_dt = dt.datetime.now()

    def stop(self, time_for=None):
        end_dt = dt.datetime.now()
        if time_for is None:
            print('Time taken: %s' % (end_dt - self.start_dt))
        else:
            print('Time taken for ' + time_for + ' : %s' % (end_dt - self.start_dt))
