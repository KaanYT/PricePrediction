import os
import json
import torch
from torch import nn, optim
from Helper.JsonDateHelper import DateTimeDecoder
from Helper.Timer import Timer
from Predictor.LstmTA.NewArchitecture.TaModel import TaModel
from Predictor.LstmTA.NewArchitecture.TaDataReader import TaDataReader
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt


class TaMain(object):

    """
    If I really hate pressing `enter` and
    typing all those hash marks, I could
    just do this instead
    """
    def __init__(self, epochs, batch_size, seq_length):
        self.model = TaModel()
        self.config = self.get_config()
        self.reader = TaDataReader(self.config['data'], batch_size, seq_length)
        print(self.reader.get_train_count())
        print(self.reader.get_test_count())
        self.timer = Timer()
        # Network Information
        self.criterion = nn.MSELoss()  #nn.CrossEntropyLoss() - nn.NLLLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.003)
        self.epochs = epochs

    def train(self, epochs=10, batch_size=10, seq_length=50, lr=0.001, clip=5, val_frac=0.1, print_every=10):
        ''' Training a network

            Arguments
            ---------
            data: text data to train the network
            epochs: Number of epochs to train
            batch_size: Number of mini-sequences per mini-batch, aka batch size
            seq_length: Number of character steps per mini-batch
            lr: learning rate
            clip: gradient clipping
            val_frac: Fraction of data to hold out for validation
            print_every: Number of steps for printing training and validation loss

        '''
        self.timer.start()
        self.model.train()

        if self.model.train_on_gpu:
            self.model.cuda()

        counter = 0
        for e in range(epochs):
            # initialize hidden state
            h = self.model.init_hidden(batch_size)

            for x, y in self.reader.get_train_data():  # get_batches(data, batch_size, seq_length):
                counter += 1
                inputs, targets = torch.from_numpy(x), torch.from_numpy(y)

                if self.model.train_on_gpu:
                    inputs, targets = inputs.cuda(), targets.cuda()

                # Creating new variables for the hidden state, otherwise
                # we'd backprop through the entire training history
                h = tuple([each.data for each in h])

                # zero accumulated gradients
                self.model.zero_grad()
                # get the output from the model -
                output, h = self.model(inputs, h)  # Input Should Be 3-Dimensional: seq_len, batch, input_size
                # calculate the loss and perform back propagation
                loss = self.criterion(output, targets.view(batch_size * seq_length))
                loss.backward()
                # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
                nn.utils.clip_grad_norm_(self.model.parameters(), clip)
                self.optimizer.step()

                # loss stats
                if counter % print_every == 0:
                    # Get validation loss
                    val_h = self.model.init_hidden(batch_size)
                    val_losses = []
                    self.model.eval()
                    for x, y in self.reader.get_train_data():  # get_batches(val_data, batch_size, seq_length):

                        x, y = torch.from_numpy(x), torch.from_numpy(y)

                        # Creating new variables for the hidden state, otherwise
                        # we'd backprop through the entire training history
                        val_h = tuple([each.data for each in val_h])

                        inputs, targets = x, y
                        if self.model.train_on_gpu:
                            inputs, targets = inputs.cuda(), targets.cuda()

                        output, val_h = self.model(inputs, val_h)
                        val_loss = self.criterion(output, targets.view(batch_size * seq_length))

                        val_losses.append(val_loss.item())

                    self.model.train()  # reset to train mode after iterationg through validation data

                    print("Epoch: {}/{}...".format(e + 1, epochs),
                          "Step: {}...".format(counter),
                          "Loss: {:.4f}...".format(loss.item()),
                          "Val Loss: {:.4f}".format(np.mean(val_losses)))
        self.timer.stop()
        self.save_model()

    def test(self):
        # Test the network
        for data in self.reader.get_test_data():
            # Format Data
            print(data)
            # Train

    def save_model(self):
        # serialize model to JSON
        save_file_name = os.path.join(self.config["model"]["save_dir"],
                                      '%s-e%s.h5' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'), str(self.epochs)))
        model_json = self.model.to_json()
        with open(save_file_name + "_model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights(save_file_name + "_weights.h5")
        print("Saved model to disk")

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        return json.load(open(pwd+'/config.json', 'r'), cls=DateTimeDecoder)
