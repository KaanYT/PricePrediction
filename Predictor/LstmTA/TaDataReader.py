import numpy as np
from Managers.DatabaseManager.MongoDB import Mongo


class TaDataReader(object):

    # LSTM Applied On Sequential Data - It unrolls, In the Sequence Dimension
    # Batch Size :
    # Sequence Length : Memorize (Hidden and Cell State)
    def __init__(self, config, batch_size, sequence_length):
        self.db = Mongo()
        self.configs = config
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.clear_data()
        self.__test_cursor = None
        self.__train_cursor = None

    def fetch_train_data(self):
        self.__train_cursor = self.db.get_data(self.configs['db'],
                                             self.configs['train_query'],
                                             self.configs['train_query_fields'])
        self.__train_cursor.batch_size(self.batch_size * self.sequence_length)  # DB To Local Length

    def fetch_test_data(self):
        self.__test_cursor = self.db.get_data(self.configs['db'],
                                            self.configs['test_query'],
                                            self.configs['test_query_fields'])
        self.__test_cursor.batch_size(self.batch_size * self.sequence_length)  # DB To Local Length

    def get_train_count(self):
        if self.__train_cursor is None:
            self.fetch_train_data()
        return self.__train_cursor.count()

    def get_train_data(self):
        self.__train_cursor.rewind()
        self.clear_data()
        batch_count = 0
        sequence_count = 0
        for row in self.__train_cursor:
            self.__x_sequence.append(np.asarray([row["Open"]], dtype=np.float32))
            self.__y_sequence.append(np.asarray([row["Open"]], dtype=np.float32))  # row["High"]
            sequence_count += 1
            if sequence_count % (self.sequence_length + 1) == 0:
                self.__x_sequence.pop()
                self.__y_sequence.pop(0)
                self.x.append(np.asarray(self.__x_sequence, dtype=np.float32))
                self.y.append(np.asarray(self.__y_sequence, dtype=np.float32))
                self.clear_sequence()
                batch_count += 1
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
        sequence_count = 0
        for row in self.__test_cursor:
            self.__x_sequence.append(np.asarray([row["Open"]], dtype=np.float32))
            self.__y_sequence.append(np.asarray([row["Open"]], dtype=np.float32))  # row["High"]
            sequence_count += 1
            if sequence_count % (self.sequence_length + 1) == 0:
                self.__x_sequence.pop()
                self.__y_sequence.pop(0)
                self.x.append(np.asarray(self.__x_sequence, dtype=np.float32))
                self.y.append(np.asarray(self.__y_sequence, dtype=np.float32))
                self.clear_sequence()
                batch_count += 1
                if batch_count % self.batch_size == 0:
                    yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                    self.clear_data()

    def clear_data(self):
        self.x = []
        self.y = []
        self.clear_sequence()

    def clear_sequence(self):
        self.__x_sequence = []
        self.__y_sequence = []
