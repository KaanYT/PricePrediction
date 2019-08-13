import logging
import queue
import traceback
from Logger.Log import Logger

from threading import Thread

log = logging.getLogger(__name__)


class ConcurrencyException(Exception):
    pass


class Worker(Thread):
    """
    Thread executing tasks from a given tasks queue.
    """
    def __init__(self, tasks, timeout_seconds):
        Thread.__init__(self)
        self.tasks = tasks
        self.timeout = timeout_seconds
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                func, args, kargs = self.tasks.get(timeout=self.timeout)
            except queue.Empty:
                # Extra thread allocated, no job, exit gracefully
                break
            try:
                func(*args, **kargs)
            except Exception as exception:
                Logger().get_logger().error(type(exception).__name__, exc_info=True)
                traceback.print_exc()

            self.tasks.task_done()


class ThreadPool:
    def __init__(self, num_threads, timeout_seconds):
        self.tasks = queue.Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks, timeout_seconds)

    def add_task(self, func, *args, **kargs):
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        self.tasks.join()


class NewsPool(object):

    def __init__(self, config=None):
        self.pool = None

    def join(self):
        """
        Runs the mtheading and returns when all threads have joined
        resets the task.
        """
        if self.pool is None:
            raise ConcurrencyException('Call set(..) with a list of source objects '
                                       'before calling .join(..)')
        self.pool.wait_completion()
        self.pool = None

    def set(self, news_list, threads_per_source=1):
        num_threads = threads_per_source * len(news_list)
        timeout = 600  # Timeout In Seconds - 10 minutes

        self.pool = ThreadPool(num_threads, timeout)

        for news_object in news_list:
            self.pool.add_task(news_object.download)
