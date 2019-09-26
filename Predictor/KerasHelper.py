import os
import datetime as dt
from Helper.Timer import Timer
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint


class KerasHelper(object):

    @staticmethod
    def createModel(type):
        if type == "Sequential":
            return Sequential()
        else:
            return Sequential()

    @staticmethod
    def build_model(model, configs):
        timer = Timer()
        timer.start()

        for layer in configs['model']['layers']:
            neurons = layer['neurons'] if 'neurons' in layer else None  # Number of connections
            dropout_rate = layer['rate'] if 'rate' in layer else None  # linear etc
            activation = layer['activation'] if 'activation' in layer else None
            return_seq = layer['return_seq'] if 'return_seq' in layer else None  # return the Last hidden state output.
            # Ex : classification or regression model
            input_timesteps = layer['input_timesteps'] if 'input_timesteps' in layer else None  # Number of inputs
            input_dim = layer['input_dim'] if 'input_dim' in layer else None  # Volume High Low etc.

            if layer['type'] == 'dense':
                model.add(Dense(neurons, activation=activation))
            if layer['type'] == 'lstm':
                model.add(LSTM(neurons, input_shape=(input_timesteps, input_dim), return_sequences=return_seq))
            if layer['type'] == 'dropout':
                model.add(Dropout(dropout_rate))

        model.compile(loss=configs['model']['loss'], optimizer=configs['model']['optimizer'])

        print('[Model] Model Compiled')
        timer.stop()

    @staticmethod
    def train_generator(model, data_gen, epochs, batch_size, steps_per_epoch, save_dir):
        timer = Timer()
        timer.start()
        print('[Model] Training Started')
        print('[Model] %s epochs, %s batch size, %s batches per epoch' % (epochs, batch_size, steps_per_epoch))

        save_file_name = os.path.join(save_dir, '%s-e%s.h5' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'), str(epochs)))
        callbacks = [
            ModelCheckpoint(filepath=save_file_name, monitor='loss', save_best_only=True)
        ]
        model.fit_generator(
            data_gen,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            callbacks=callbacks,
            workers=1
        )

        print('[Model] Training Completed. Model saved as %s' % save_file_name)
        timer.stop()
