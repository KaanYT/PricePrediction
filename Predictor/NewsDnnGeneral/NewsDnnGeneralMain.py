import os
import platform
import json
import torch
from torch import nn, optim
from Helper.JsonDateHelper import DateTimeDecoder
from Helper.Timer import Timer
from Helper.DateHelper import DateHelper
from Helper.LoggerHelper import LoggerHelper
from Predictor.NewsDnnGeneral.NewsDnnGeneralModel import NewsDnnGeneralModel
from Predictor.NewsDnnGeneral.NewsDnnGeneralDataReader import NewsDnnGeneralDataReader
from Predictor.NewsDnnBase.NewsDnnBaseMain import NewsDnnBaseMain
from Managers.ExportManager.Export import Export
import numpy as np
import datetime as dt
import pandas


class NewsDnnGeneralMain(NewsDnnBaseMain):

    """ Initializer

            Arguments
            ---------
            epochs: Number of epochs to train
            batch_size: Number of mini-sequences per mini-batch, aka batch size
            seq_length: Number of character steps per mini-batch
    """
    def __init__(self, epochs=None, batch_size=None, seq_length=None, use_gpu=None, lr=0.005, hidden_size=None):
        super().__init__(self.get_config(), epochs, batch_size, seq_length, use_gpu, lr, hidden_size=hidden_size)
        # Load DB
        self.reader = NewsDnnGeneralDataReader(self.config, self.batch_size, self.seq_length)
        self.train_count = self.reader.get_count(NewsDnnGeneralDataReader.DictDataTerm["Train"])
        self.test_count = self.reader.get_count(NewsDnnGeneralDataReader.DictDataTerm["Test"])
        self.validate_count = self.reader.get_count(NewsDnnGeneralDataReader.DictDataTerm["Validate"])
        # Create Model
        self.model: NewsDnnGeneralModel = NewsDnnGeneralModel(
            input_size=self.get_network_input_size(),
            lr=lr,
            hidden=hidden_size,
            use_gpu=self.use_gpu)
        # Optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

    def train(self, clip=5, val_frac=0.1, print_every=20):
        """ Training a network

            Arguments
            ---------
            clip: gradient clipping
            val_frac: Fraction of data to hold out for validation
            print_every: Number of steps for printing training and validation loss

        """
        df = pandas.DataFrame(columns=['Epoch', 'Step', 'Last Train Loss', 'Mean Test Loss'])
        self.timer.start()
        self.model.train()

        if self.model.train_on_gpu and self.config["networkConfig"]["useGPU"]:
            self.model.cuda()

        counter = 0
        h = None
        for e in range(self.epochs):
            h = self.model.init_hidden(self.reader.batch_size)

            print(self.config["options"]["network_type"])
            print(NewsDnnGeneralDataReader.DictDataType[
                      self.config["options"]["network_type"]])
            # Batch Loop
            for x, y in self.reader.get_data(fetch_type=NewsDnnGeneralDataReader.DictDataTerm["Train"],
                                             data_type=NewsDnnGeneralDataReader.DictDataType[self.config["options"]["network_type"]]):
                counter += 1
                inputs, targets = torch.from_numpy(x), torch.from_numpy(y)

                if self.model.train_on_gpu and self.config["networkConfig"]["useGPU"]:
                    inputs, targets = inputs.cuda(), targets.cuda()

                # Creating new variables for the hidden state, otherwise
                # we'd backprop through the entire training history
                h = tuple([each.data for each in h])

                # zero accumulated gradients
                self.model.zero_grad()

                # get the output from the model -
                output, h = self.model(inputs, h)  # Input Should Be 3-Dimensional: seq_len, batch, input_size

                # calculate the loss and perform back propagation
                loss = self.criterion(output.squeeze(), targets.long())
                loss.backward()

                # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
                nn.utils.clip_grad_norm_(self.model.parameters(), clip)
                self.optimizer.step()

                # loss stats
                if counter % print_every == 0:
                    timer = Timer()
                    timer.start()
                    # Get validation loss
                    val_h = self.model.init_hidden(self.reader.batch_size)
                    val_losses = []
                    self.model.eval()
                    accuracy = 0
                    for x, y in self.reader.get_data(NewsDnnGeneralDataReader.DictDataTerm["Validate"],
                                                     NewsDnnGeneralDataReader.DictDataType[
                                                         self.config["options"]["network_type"]]):
                        # get_batches(val_data, batch_size, seq_length):
                        x, y = torch.from_numpy(x), torch.from_numpy(y)

                        # Creating new variables for the hidden state, otherwise
                        # we'd backprop through the entire training history
                        val_h = tuple([each.data for each in val_h])

                        inputs, targets = x, y
                        if self.model.train_on_gpu and self.config["networkConfig"]["useGPU"]:
                            inputs, targets = inputs.cuda(), targets.cuda()

                        output, val_h = self.model(inputs, val_h)
                        val_loss = self.criterion(output, targets.long())

                        val_losses.append(val_loss.item())
                        accuracy += self.calculate_accuracy(output, targets)
                    self.model.train()  # reset to train mode after iterationg through validation data
                    LoggerHelper.info("Epoch: {}/{}...".format(e + 1, self.epochs) +
                                      "Step: {}...".format(counter) +
                                      "Loss: {:.4f}...".format(loss.item()) +
                                      "Accuracy In Step: {:.4f}...".format(accuracy) +
                                      "Val Count: {:.4f}...".format(self.validate_count) +
                                      "Val Loss: {:.4f}".format(np.mean(val_losses)))
                    df = df.append({
                        'Epoch': "{}/{}".format(e + 1, self.epochs),
                        'Step': counter,
                        'Last Train Loss': loss.item(),
                        'Mean Test Loss': np.mean(val_losses),
                        'Accuracy In Step': accuracy,
                    }, ignore_index=True)
                    timer.stop()
                self.model.train()
        self.timer.stop()
        self.save_model()
        self.current_date = DateHelper.get_current_date()
        Export.append_df_to_excel(df, self.current_date)
        Export.append_df_to_excel(self.get_info(), self.current_date)

    def test(self):
        print("Test Started")
        self.timer.start()
        df = pandas.DataFrame(columns=['Accuracy', 'Mean Test Loss'])
        val_h = self.model.init_hidden(self.reader.batch_size)
        val_losses = []
        self.model.eval()
        counter = 0
        accuracy = 0
        for x, y in self.reader.get_data(NewsDnnGeneralDataReader.DictDataTerm["Test"],
                                         NewsDnnGeneralDataReader.DictDataType[
                                             self.config["options"]["network_type"]]):
            counter += 1
            x, y = torch.from_numpy(x), torch.from_numpy(y)

            # Creating new variables for the hidden state, otherwise
            # we'd backprop through the entire training history
            val_h = tuple([each.data for each in val_h])

            inputs, targets = x, y
            if self.model.train_on_gpu and self.config["networkConfig"]["useGPU"]:
                inputs, targets = inputs.cuda(), targets.cuda()

            output, val_h = self.model(inputs, val_h)
            val_loss = self.criterion(output, targets.long())
            val_losses.append(val_loss.item())
            accuracy += self.calculate_accuracy(output, targets)
        df = df.append({
            'Accuracy': "{}/{}".format(accuracy, self.test_count),
            'Mean Test Loss': np.mean(val_losses)
        }, ignore_index=True)

        Export.append_df_to_excel(df, self.current_date)
        self.timer.stop()

    @staticmethod
    def calculate_accuracy(output, targets):
        accuracy = 0
        for i, out in enumerate(output):
            top_n, top_i = out.topk(1)
            result = top_i[0].item()
            if result == targets[i]:
                accuracy = accuracy + 1
        return accuracy

    def get_info(self):
        info = pandas.DataFrame(columns=['Database',
                                         'Key',
                                         'Batch Size',
                                         'Sequence Length',
                                         'Input Size',
                                         'Hidden',
                                         'Number of Layers',
                                         'Dropout Prob',
                                         'Learning Rate',
                                         'Train Size',
                                         'Validation Size',
                                         'Test Size',
                                         'Price Buffer Percent'])

        db = (self.config["database"]["name"]
              if 'name' in self.config["database"] else "Unknown")
        key = (self.config["database"]["train"]["query"]["category"]
               if 'category' in self.config["database"]["train"]["query"] else "All")

        info = info.append({
            'Database': db,
            'Key': key,
            'Batch Size': self.reader.batch_size,
            'Sequence Length': self.reader.sequence_length,
            'Input Size': self.model.input_size,
            'Hidden': self.model.hidden,
            'Number of Layers': self.model.num_layers,
            'Dropout Prob': self.model.drop_prob,
            'Learning Rate': self.model.lr,
            'Train Size': self.reader.train_count,
            'Validation Size': self.reader.validate_count,
            'Test Size': self.reader.test_count,
            'Price Buffer Percent': self.config['database']['price']['buffer_percent']
        }, ignore_index=True)
        return info

    def get_save_file_name(self):
        # serialize model to JSON
        save_file_name = os.path.join(self.config["networkConfig"]["save_dir"],
                                      '%s-e%s(%s).pth' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'),
                                                          str(self.epochs),
                                                          self.config["database"]["name"]))

        return save_file_name

    def save_model(self):
        # serialize model to JSON
        save_file_name = self.get_save_file_name()
        checkpoint = {
            'model': NewsDnnGeneralModel(),
            'model_state_dict': self.model.state_dict(),
            'optimizer': optim.Adam(self.model.parameters(), lr=self.model.lr),
            'optimizer_state_dict': self.optimizer.state_dict()
        }

        torch.save(checkpoint, save_file_name)
        LoggerHelper.info("Model Saved to disk")

    def load_model(self, path):
        checkpoint = torch.load(path)
        self.model = checkpoint['model']
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer = checkpoint['optimizer']
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        LoggerHelper.info("**Model Info**"
                          + "\nbatch_size : " + str(self.reader.batch_size)
                          + "\nsequence_length : " + str(self.reader.sequence_length)
                          + "\ninput_size : " + str(self.model.input_size)
                          + "\nhidden : " + str(self.model.hidden)
                          + "\nnum_layers : " + str(self.model.num_layers)
                          + "\ndrop_prob : " + str(self.model.drop_prob)
                          + "\nlr : " + str(self.model.lr)
                          + "\nHidden Size : " + str(self.model.hidden))
        LoggerHelper.info("Model loaded from disk")

    def get_network_input_size(self):
        size = self.config["wordEmbedding"]["size"]
        if self.config["options"]["wiki"]["enabled"]:
            size = size + self.config["options"]["wiki"]["multiply_factors"]
        if self.config["options"]["twitter"]["enabled"]:
            size = size + self.config["options"]["twitter"]["multiply_factors"]
        LoggerHelper.info("Network Input Size :" + str(size))
        return size

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return json.load(open(pwd + '/config_w.json', 'r'), cls=DateTimeDecoder)
        else:
            return json.load(open(pwd + '/config.json', 'r'), cls=DateTimeDecoder)
