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
        price_start = self.configs["database"]["price"]["start"]
        for row in cursor:
            nor_open = self.normalize_data(row[price_start], price_start)
            self.x_sequence.append(np.asarray([nor_open], dtype=np.float32))
            #self.y_sequence.append(np.asarray([nor_open], dtype=np.float32))  # row["High"]
            sequence_count += 1
            if sequence_count % (self.sequence_length + 1) == 0:
                end = self.x_sequence[self.sequence_length]
                self.x_sequence.pop()
                start = self.x_sequence[self.sequence_length-1]
                #self.y_sequence.pop(0)
                self.x.append(np.asarray(self.x_sequence, dtype=np.float32))
                self.y.append(self.get_classification(start[0],
                                                      end[0],
                                                      self.configs['database']['price']['buffer_percent']))
                self.clear_sequence()
                batch_count += 1
                if batch_count % self.batch_size == 0:
                    yield np.asarray(self.x, dtype=np.float32), np.asarray(self.y, dtype=np.float32)
                    self.clear_data()

    def normalize_data(self, value, field):
        return (value - self.max_min[field]["min"][field])/(self.max_min[field]["max"][field]-self.max_min[field]["min"][field])

    def de_normalize_data(self, value, field):
        return value * (self.max_min[field]["max"][field] - self.max_min[field]["min"][field]) + self.max_min[field]["min"][field]

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

    @staticmethod
    def get_classification(start, end, buffer_percent):
        diff = start - end
        total = start + end / 2
        percentage = (diff/total)*100
        if percentage > buffer_percent:
            return 2  # Increase
        elif percentage < -buffer_percent:
            return 1  # Decrease
        else:
            return 0  # Same Value
