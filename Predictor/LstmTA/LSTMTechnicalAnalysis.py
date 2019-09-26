import json
import pandas as pd
import numpy as np
import os
from Predictor.LstmTA.LSTMTADataConverter import LSTMTADataConverter
import math
from Helper.Timer import Timer
from Helper.FileHelper import FileHelper
from Helper.JsonDateHelper import DateTimeDecoder
from Managers.DatabaseManager.MongoDB import Mongo
from Predictor.KerasHelper import KerasHelper
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint


class LstmTechnicalAnalysis(object):

    def __init__(self):
        self.configs = None
        self.train_df = None
        self.test_df = None

    def create_model(self):
        self.setup_env()  # Setup Environment
        self.get_data(self.configs['data'])  # Load Data
        self.model = KerasHelper.createModel(self.configs['model']['save_dir'])  # Create a model
        KerasHelper.build_model(self.model, self.configs)  # Create Model
        # out-of memory generative training
        steps_per_epoch = 1049
        # num_rows = int(self.train_df.rowcount)
        # steps_per_epoch = math.ceil(
            #(len(self.train_df) - self.configs['data']['sequence_length']) / self.configs['training']['batch_size'])
        testData = LSTMTADataConverter.generate_data(self.train_df, 50)
        steps_per_epoch = math.ceil(
            (self.train_df.count() - self.configs['data']['sequence_length']) / self.configs['training']['batch_size'])
        steps_per_epoch = 123
        print("END----")
        KerasHelper.train_generator(model=self.model,
                                    data_gen=testData,
                                    epochs=self.configs['training']['epochs'],
                                    batch_size=self.configs['training']['batch_size'],
                                    steps_per_epoch=steps_per_epoch,
                                    save_dir=self.configs['model']['save_dir'])

    def setup_env(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        self.configs = json.load(open(pwd+'/config.json', 'r'), cls=DateTimeDecoder)
        FileHelper.create_path_if_not_exists(self.configs['model']['save_dir'])

    def get_data(self, data):
        db = Mongo()
        print(data['train_query'])
        self.train_df = db.get_data(data['db'], data['train_query'], data['train_query_fields'])
        self.train_df.batch_size(50)
        self.test_df = db.get_data(data['db'], data['test_query'], data['test_query_fields'])
        self.test_df.batch_size(50)
        print(type(self.train_df))

    @staticmethod
    def row_as_dict(cursor):
        for row in cursor:
            rowlist = [row["Open"], row["High"]]
            print(rowlist)
            print(type(rowlist))
            yield pd.DataFrame(row)
