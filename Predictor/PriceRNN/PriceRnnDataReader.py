import numpy as np
from Predictor.NewsDnnBase.NewsDnnBaseDataReader import NewsDnnBaseDataReader


class PriceRnnDataReader(NewsDnnBaseDataReader):

    def __init__(self, config, batch_size, sequence_length):
        super().__init__(config, batch_size, sequence_length, word_emb_enabled=False)
        self.x_sequence = []
        self.y_sequence = []
        self.x = []
        self.y = []

    '''
        NEWS
    '''
    def get_data_news(self, cursor):
        batch_count = 0
        sequence_count = 0
        for row in self.__train_cursor:
            self.x_sequence.append(np.asarray([row["Open"]], dtype=np.float32))
            self.y_sequence.append(np.asarray([row["Open"]], dtype=np.float32))  # row["High"]
            sequence_count += 1
            if sequence_count % (self.sequence_length + 1) == 0:
                self.x_sequence.pop()
                self.y_sequence.pop(0)
                self.x.append(np.asarray(self.x_sequence, dtype=np.float32))
                self.y.append(np.asarray(self.y_sequence, dtype=np.float32))
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
        self.x_sequence = []
        self.y_sequence = []

    @staticmethod
    def get_label(label):
        if label == -1:
            return 0
        else:
            return 1
