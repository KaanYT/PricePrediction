import numpy as np
from Managers.DatabaseManager.MongoDB import Mongo
from Helper.WordEmbedding import WordEmbedding


class NewsDnnDataReader(object):
    DictNumber = {1: 'Next_Hour', 2: 'Next_Day',
                  3: 'Next_Week', 4: 'Next_Month'}

    DictClasses = {1: 'Increase',
                   2: 'Decrease',
                   3: 'Stable'}
    ArticleMinSize = 10

    # LSTM Applied On Sequential Data - It unrolls, In the Sequence Dimension
    # Batch Size :
    # Sequence Length : Memorize (Hidden and Cell State) -> Article Size
    def __init__(self, config, batch_size, sequence_length):
        self.db = Mongo()
        self.configs = config
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.clear_data()
        self.word_embedding = WordEmbedding(self.configs["WordEmbeddingPath"])
        self.__test_cursor = None
        self.__train_cursor = None

    def fetch_train_data(self):
        self.__train_cursor = self.db.get_data(self.configs['db'],
                                               self.configs['train_query'],
                                               self.configs['train_query_fields'])
        self.__train_cursor = self.__train_cursor.sort(NewsDnnDataReader.get_sort_list(self.configs['train_query_sort']))
        self.__train_cursor.batch_size(self.batch_size * self.sequence_length)  # DB To Local Length

    def fetch_test_data(self):
        self.__test_cursor = self.db.get_data(self.configs['db'],
                                              self.configs['test_query'],
                                              self.configs['test_query_fields'])
        self.__test_cursor = self.__test_cursor.sort(NewsDnnDataReader.get_sort_list(self.configs['test_query_sort']))
        self.__test_cursor.batch_size(self.batch_size * self.sequence_length)  # DB To Local Length

    def get_train_count(self):
        if self.__train_cursor is None:
            self.fetch_train_data()
        return self.__train_cursor.count()

    def get_train_data(self):
        self.__train_cursor.rewind()
        self.clear_data()
        batch_count = 0
        price_start = self.configs["price"]["start"]
        price_end = self.configs["price"]["end"]
        for row in self.__train_cursor:
            embedded_article = self.word_embedding.get_weight_matrix(row["article"])
            if len(embedded_article) < NewsDnnDataReader.ArticleMinSize:
                continue
            self.x.append(self.pad_embedded_article(embedded_article))
            self.y.append(NewsDnnDataReader.get_classification(row[price_start],
                                                               row[price_end]))
            batch_count = batch_count + 1
            if batch_count % self.batch_size == 0:
                yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                self.clear_data()

    def get_test_count(self):
        if self.__test_cursor is None:
            self.fetch_test_data()
        return self.__test_cursor.count()

    def get_test_data(self):
        self.__test_cursor.rewind()
        self.clear_data()
        batch_count = 0
        for row in self.__test_cursor:
            embedded_article = self.word_embedding.get_weight_matrix(row["article"])
            if len(embedded_article) < NewsDnnDataReader.ArticleMinSize:
                continue
            self.x.append(self.pad_embedded_article(embedded_article))
            self.y.append(NewsDnnDataReader.get_classification(row["price_before"],
                                                               row["price_after_day"]))
            batch_count = batch_count + 1
            if batch_count % self.batch_size == 0:
                yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.long)
                self.clear_data()

    def pad_embedded_article(self, embedded_article):
        # Calculate Difference
        padding_difference = (embedded_article.shape[0] - self.sequence_length)
        if padding_difference >= 0:
            return embedded_article[:-padding_difference]
        else:  # Add Padding
            return np.pad(embedded_article, ((abs(padding_difference), 0), (0, 0)), 'constant')

    def clear_data(self):
        self.x = []
        self.y = []

    @staticmethod
    def get_classification(start, end):
        diff = float(start["Open"]) - float(end["Open"])
        total = float(start["Open"]) + float(end["Open"]) / 2
        percentage = (diff/total)*100
        if percentage > 0.005:
            return 0  #
        elif percentage < -0.005:
            return 1
        else:
            return 2

    @staticmethod
    def get_sort_list(properties):
        sort_list = list()
        for property in properties:
            for key, value in property.items():
                sort_list.append((key, value))
        return sort_list


