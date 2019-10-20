import os
import json
from pymongo import IndexModel
from Managers.WikipediaManager.Wikipedia import Wikipedia
from Managers.LogManager.Log import Logger
from Managers.DatabaseManager.MongoDB import Mongo
from Helper.WordPreProcessing import PreProcessing


class WikiRecorder(object):

    def __init__(self, collection_name="Wiki"):
        self.col = Mongo().create_collection(collection_name, WikiRecorder.get_index_models())
        self.preprocessor = PreProcessing()
        self.config = WikiRecorder.get_config()
        self.total = 0

    def collect_all(self):
        name_list = self.config["Wiki"]["Corporations"]
        for cor_name in name_list:
            self.collect(cor_name)

    def collect(self, title, page_id=None):
        page = Wikipedia.get_page(title, pageid=page_id)

        title = page.original_title
        title_p = self.preprocessor.preprocess(title)
        summary = page.summary
        summary_p = self.preprocessor.preprocess(summary)
        content = page.content
        page_id = page.pageid
        data = {
            'title': title,
            'title_p': title_p,
            'summary': summary,
            'summary_p': summary_p,
            'content': content,
            'page_id': page_id
        }
        print(data)
        try:
            self.col.insert(data)
        except Exception as exception:
            Logger().get_logger().error(type(exception).__name__, exc_info=True)

    @staticmethod
    def get_index_models():
        return [IndexModel("title", name="index_title"),
                IndexModel("page_id", name="index_page_id")]

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        return json.load(open(pwd + '/config.json', 'r'))
