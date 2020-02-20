import numpy as np
from Helper.LoggerHelper import LoggerHelper
from Helper.ListHelper import ListHelper
from Managers.DatabaseManager.MongoDB import Mongo
from Predictor.NewsDnnBase.NewsDnnBaseWordEmbedding import WordEmbedding


class NewsDnnBaseDataReader(object):
    DictDataTerm = {'Train': 1,
                    'Validate': 2,
                    'Test': 3}

    DictDataType = {'News': 1,
                    'Wiki': 2,
                    'WikiAndTweet': 3}

    ArticleMinSize = 10

    # LSTM Applied On Sequential Data - It unrolls, In the Sequence Dimension
    # Batch Size :
    # Sequence Length : Memorize (Hidden and Cell State) -> Article Size
    def __init__(self, config, batch_size, sequence_length, word_emb_enabled=True):
        self.db = Mongo()
        self.configs = config
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.clear_data()
        if word_emb_enabled:
            self.word_embedding = WordEmbedding(path=self.configs["wordEmbedding"]["path"])
        self.__test_cursor = None
        self.test_count = 0
        self.__train_cursor = None
        self.train_count = 0
        self.__validate_cursor = None
        self.validate_count = 0

    '''
        Data Fetch
    '''
    def fetch_data(self, fetch_type=1):
        if fetch_type == NewsDnnBaseDataReader.DictDataTerm["Train"]:
            self.__train_cursor = self.db.get_data(self.configs['database']['name'],
                                                   self.configs['database']['train']['query'],
                                                   self.configs['database']['fields'], notimeout=True)
            if self.configs['database']['sort'] is not None:
                self.__train_cursor = self.__train_cursor.sort(
                    ListHelper.convert_dict_list(self.configs['database']['sort']))
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Validate"]:
            self.__validate_cursor = self.db.get_data(self.configs['database']['name'],
                                                      self.configs['database']['validate']['query'],
                                                      self.configs['database']['fields'], notimeout=True)
            if self.configs['database']['sort'] is not None:
                self.__validate_cursor = self.__validate_cursor.sort(
                    ListHelper.convert_dict_list(self.configs['database']['sort']))
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Test"]:
            self.__test_cursor = self.db.get_data(self.configs['database']['name'],
                                                  self.configs['database']['test']['query'],
                                                  self.configs['database']['fields'], notimeout=True)
            if self.configs['database']['sort'] is not None:
                self.__test_cursor = self.__test_cursor.sort(
                    ListHelper.convert_dict_list(self.configs['database']['sort']))
        else:
            LoggerHelper.critical('Unable To Fetch')

    '''
        Get Count
    '''
    def get_count(self, fetch_type=1):
        if fetch_type == NewsDnnBaseDataReader.DictDataTerm["Train"]:
            if self.__train_cursor is None:
                self.fetch_data(NewsDnnBaseDataReader.DictDataTerm["Train"])
            self.train_count = self.__train_cursor.count()
            return self.train_count
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Validate"]:
            if self.__validate_cursor is None:
                self.fetch_data(NewsDnnBaseDataReader.DictDataTerm["Validate"])
            self.validate_count = self.__validate_cursor.count()
            return self.validate_count
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Test"]:
            if self.__test_cursor is None:
                self.fetch_data(NewsDnnBaseDataReader.DictDataTerm["Test"])
            self.test_count = self.__test_cursor.count()
            return self.test_count
        else:
            LoggerHelper.critical('Unable To Fetch')

    '''
        Get Data
    '''
    def get_data(self, fetch_type=1, data_type=1):
        if fetch_type == NewsDnnBaseDataReader.DictDataTerm["Train"]:
            cursor = self.__train_cursor
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Validate"]:
            cursor = self.__validate_cursor
        elif fetch_type == NewsDnnBaseDataReader.DictDataTerm["Test"]:
            cursor = self.__test_cursor
        else:
            LoggerHelper.critical('Unable To Get Cursor (Check Fetch Type)')
            return None
        cursor.rewind()
        self.clear_data()
        if data_type == NewsDnnBaseDataReader.DictDataType["News"]:
            return self.get_data_news(cursor)
        elif data_type == NewsDnnBaseDataReader.DictDataType["Wiki"]:
            return self.get_data_wiki(cursor)
        elif data_type == NewsDnnBaseDataReader.DictDataType["WikiAndTweet"]:
            return self.get_data_wiki_and_tweet(cursor)
        else:
            LoggerHelper.critical('Unknown Data Type (data_type)')
            return None

    '''
        NEWS
    '''
    def get_data_news(self, cursor):
        batch_count = 0
        price_start = self.configs["database"]["price"]["start"]
        price_end = self.configs["database"]["price"]["end"]
        for row in cursor:
            embedded_article = self.word_embedding.get_weight_matrix(row["article"])
            if len(embedded_article) < NewsDnnBaseDataReader.ArticleMinSize:
                continue
            self.x.append(self.pad_embedded_article(embedded_article))
            self.y.append(NewsDnnBaseDataReader.get_classification(row[price_start],
                                                                   row[price_end],
                                                                   self.configs['database']['price']['buffer_percent']))
            batch_count = batch_count + 1
            if batch_count % self.batch_size == 0:
                yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                self.clear_data()

    '''
        WIKI
    '''
    def get_data_wiki(self, cursor):
        batch_count = 0
        price_start = self.configs["database"]["price"]["start"]
        price_end = self.configs["database"]["price"]["end"]
        wiki_column = self.configs['options']['wiki']['wiki_column']
        for row in cursor:
            embedded_article = self.word_embedding.\
                get_weight_matrix_all(article=row["article"],
                                      wiki=row[wiki_column],
                                      wiki_multiply_factors=self.configs['options']['wiki']['multiply_factors'])
            if len(embedded_article) < NewsDnnBaseDataReader.ArticleMinSize:
                continue
            self.x.append(self.pad_embedded_article(embedded_article))
            self.y.append(NewsDnnBaseDataReader.get_classification(row[price_start],
                                                                   row[price_end],
                                                                   self.configs['database']['price']['buffer_percent']))
            batch_count = batch_count + 1
            if batch_count % self.batch_size == 0:
                yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                self.clear_data()

    '''
        WIKI & TWEET
    '''
    def get_data_wiki_and_tweet(self, cursor):
        batch_count = 0
        price_start = self.configs["database"]["price"]["start"]
        price_end = self.configs["database"]["price"]["end"]
        wiki_column = self.configs['options']['wiki']['wiki_column']
        tweet_column = self.configs['options']['twitter']['tweet_column']
        wiki_multiply_factors = self.configs['options']['wiki']['multiply_factors']
        tweet_multiply_factors = self.configs['options']['twitter']['multiply_factors']
        for row in cursor:
            embedded_article = self.word_embedding. \
                get_weight_matrix_all(article=row["article"],
                                      wiki=row[wiki_column],
                                      wiki_multiply_factors=wiki_multiply_factors,
                                      tweet=row[tweet_column],
                                      tweet_multiply_factors=tweet_multiply_factors)
            if len(embedded_article) < NewsDnnBaseDataReader.ArticleMinSize:
                continue
            # Article
            self.x.append(self.pad_embedded_article(embedded_article))
            # Price
            self.y.append(NewsDnnBaseDataReader.get_classification(row[price_start],
                                                                   row[price_end],
                                                                   self.configs['database']['price']['buffer_percent']))
            batch_count = batch_count + 1
            if batch_count % self.batch_size == 0:
                yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                self.clear_data()

    '''
        HELPER METHODS
    '''
    def pad_embedded_article(self, embedded_article):
        # Calculate Difference
        padding_difference = (embedded_article.shape[0] - self.sequence_length)
        if padding_difference == 0:
            return embedded_article
        if padding_difference >= 0:
            return embedded_article[:-padding_difference]
        else:  # Add Padding
            return np.pad(embedded_article, ((abs(padding_difference), 0), (0, 0)), 'constant')

    def clear_data(self):
        self.x = []
        self.y = []

    @staticmethod
    def get_classification(start, end, buffer_percent):
        diff = float(start["Open"]) - float(end["Open"])
        total = float(start["Open"]) + float(end["Open"]) / 2
        percentage = (diff/total)*100
        if percentage > buffer_percent:
            return 2  # Increase
        elif percentage < -buffer_percent:
            return 1  # Decrease
        else:
            return 0  # Same Value
