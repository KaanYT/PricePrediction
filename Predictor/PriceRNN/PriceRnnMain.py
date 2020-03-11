import os
import platform
import json
import torch
from torch import nn, optim
from Helper.JsonDateHelper import DateTimeDecoder
from Helper.Timer import Timer
from Helper.DateHelper import DateHelper
from Helper.LoggerHelper import LoggerHelper
from Predictor.PriceRNN.PriceRnnModel import PriceRnnModel
from Predictor.PriceRNN.PriceRnnDataReader import PriceRnnDataReader
from Predictor.NewsDnnBase.NewsDnnBaseMain import NewsDnnBaseMain
from Managers.ExportManager.Export import Export
import numpy as np
import datetime as dt
import pandas


class PriceRnnMain(NewsDnnBaseMain):

    """ Initializer

            Arguments
            ---------
            epochs: Number of epochs to train
            batch_size: Number of mini-sequences per mini-batch, aka batch size
            seq_length: Number of character steps per mini-batch
    """
    def __init__(self, epochs=None, batch_size=None, seq_length=None, use_gpu=None, lr=0.00005, hidden_size=None):
        super().__init__(self.get_config(), epochs, batch_size, seq_length, use_gpu, lr, hidden_size=hidden_size)
        # Load DB
        self.reader = PriceRnnDataReader(self.config, self.batch_size, self.seq_length)
        self.train_count = self.reader.get_count(PriceRnnDataReader.DictDataTerm["Train"])
        self.test_count = self.reader.get_count(PriceRnnDataReader.DictDataTerm["Test"])
        self.validate_count = self.reader.get_count(PriceRnnDataReader.DictDataTerm["Validate"])
        self.maxmin = self.reader.get_max_min()
        # Create Model
        self.model: PriceRnnModel = PriceRnnModel(
            input_size=self.get_network_input_size(),
            lr=lr,
            hidden=self.hidden_size,
            use_gpu=self.use_gpu)
        # Optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.device = self.create_device()

    def create_device(self):
        if self.config["networkConfig"]["useGPU"]:
            if torch.cuda.is_available():
                self.model.to("cuda")
                return torch.device("cuda")
            else:
                return torch.device("cpu")
        else:
            return torch.device("cpu")

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
        if torch.cuda.is_available():
            self.model.cuda(device=self.device)

        counter = 0
        h = None
        for e in range(self.epochs):
            h = self.model.init_hidden(self.reader.batch_size)

            print(self.config["options"]["network_type"])
            print(PriceRnnDataReader.DictDataType[
                      self.config["options"]["network_type"]])
            # Batch Loop
            for x, y in self.reader.get_data(fetch_type=PriceRnnDataReader.DictDataTerm["Train"],
                                             data_type=PriceRnnDataReader.DictDataType[self.config["options"]["network_type"]]):
                counter += 1
                inputs, targets = torch.from_numpy(x), torch.from_numpy(y)

                if self.model.can_use_gpu and self.config["networkConfig"]["useGPU"]:
                    inputs, targets = inputs.cuda(), targets.cuda()

                # Creating new variables for the hidden state, otherwise
                # we'd backprop through the entire training history
                h = tuple([each.data for each in h])

                # zero accumulated gradients
                self.model.zero_grad()

                # get the output from the model -
                output, h = self.model(inputs, h)  # Input Should Be 3-Dimensional: seq_len, batch, input_size

                # calculate the loss and perform back propagation
                #loss = self.criterion(output, targets)
                loss = self.criterion(output.squeeze(), targets.long())
                loss.backward()

                # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
                nn.utils.clip_grad_norm_(self.model.parameters(), clip)
                self.optimizer.step()

                # Validate
                if counter % print_every == 0:
                    timer = Timer()
                    timer.start()
                    df = self.validate(df, e, counter, loss)
                    timer.stop(time_for="Validate")
                self.model.train()
        self.timer.stop(time_for="Train")
        self.save_model()
        self.current_date = DateHelper.get_current_date()
        Export.append_df_to_excel(df, self.current_date)
        Export.append_df_to_excel(self.get_info(), self.current_date)

    def validate(self, df, epoch, counter, loss):
        # Get Validation Loss
        val_h = self.model.init_hidden(self.reader.batch_size)
        val_losses = []
        self.model.eval()
        result = np.asarray([])
        result_expected = np.asarray([])
        for x, y in self.reader.get_data(PriceRnnDataReader.DictDataTerm["Validate"],
                                         PriceRnnDataReader.DictDataType[
                                             self.config["options"]["network_type"]]):
            # get_batches(val_data, batch_size, seq_length):
            x, y = torch.from_numpy(x), torch.from_numpy(y)

            # Creating new variables for the hidden state, otherwise
            # we'd backprop through the entire training history
            val_h = tuple([each.data for each in val_h])

            inputs, targets = x, y
            if self.model.can_use_gpu and self.config["networkConfig"]["useGPU"]:
                inputs, targets = inputs.cuda(), targets.cuda()

            output, val_h = self.model(inputs, val_h)
            val_loss = self.criterion(output, targets.view(self.reader.batch_size * self.reader.sequence_length))
            #val_loss = self.criterion(output, targets.long())
            val_losses.append(val_loss.item())
            # Sum and divide total value !
            result = np.append(result, self.get_output(output))
            result_expected = np.append(result_expected, targets.numpy())
        self.model.train()  # reset to train mode after iterationg through validation data
        scores = self.calculate_scores(result_expected, result)
        return self.log_validate(df, epoch, counter, loss, val_losses, self.validate_count, scores)

    def test(self):
        print("Test Started")
        self.timer.start()
        df = pandas.DataFrame(columns=['Accuracy', 'Mean Test Loss'])
        val_h = self.model.init_hidden(self.reader.batch_size)
        val_losses = []
        self.model.eval()
        counter = 0
        accuracy = 0
        result = np.asarray([])
        result_expected = np.asarray([])
        for x, y in self.reader.get_data(PriceRnnDataReader.DictDataTerm["Test"],
                                         PriceRnnDataReader.DictDataType[
                                             self.config["options"]["network_type"]]):
            counter += 1
            x, y = torch.from_numpy(x), torch.from_numpy(y)

            # Creating new variables for the hidden state, otherwise
            # we'd backprop through the entire training history
            val_h = tuple([each.data for each in val_h])

            inputs, targets = x, y
            if self.model.can_use_gpu and self.config["networkConfig"]["useGPU"]:
                inputs, targets = inputs.cuda(), targets.cuda()

            output, val_h = self.model(inputs, val_h)
            #val_loss = self.criterion(output, targets.view(self.reader.batch_size * self.reader.sequence_length))
            val_loss = self.criterion(output, targets.long())
            val_losses.append(val_loss.item())
            acc, res = self.calculate_accuracy(output, targets)
            accuracy += acc
            result = np.append(result, res)
            result_expected = np.append(result_expected, targets.numpy())
        scores = self.calculate_scores(result_expected, result)
        df = self.log_test(df, accuracy, self.test_count, val_losses, scores)
        Export.append_df_to_excel(df, self.current_date)
        self.timer.stop(time_for="Test")

    @staticmethod
    def calculate_accuracy(output, targets):
        accuracy = 0
        results = []
        for i, out in enumerate(output):
            top_n, top_i = out.topk(1)
            result = top_i[0].item()
            results.append(result)
            if result == targets[i]:
                accuracy = accuracy + 1
        return accuracy, results

    def get_info(self):
        info = pandas.DataFrame(columns=['Database',
                                         'Key',
                                         'Batch Size',
                                         'Sequence Length',
                                         'Input Size',
                                         'Input Wiki Factor',
                                         'Input Twitter Factor',
                                         'Hidden',
                                         'Number of Layers',
                                         'Dropout Prob',
                                         'Learning Rate',
                                         'Train Size',
                                         'Validation Size',
                                         'Test Size',
                                         'Price Buffer Percent',
                                         'Word Vector',
                                         'Network Type',
                                         'Wiki Column',
                                         'Tweet Column'])

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
            'Input Wiki Factor': self.config["options"]["wiki"]["multiply_factors"],
            'Input Twitter Factor': self.config["options"]["twitter"]["multiply_factors"],
            'Hidden': self.model.hidden,
            'Number of Layers': self.model.num_layers,
            'Dropout Prob': self.model.drop_prob,
            'Learning Rate': self.model.lr,
            'Train Size': self.reader.train_count,
            'Validation Size': self.reader.validate_count,
            'Test Size': self.reader.test_count,
            'Price Buffer Percent': self.config['database']['price']['buffer_percent'],
            'Network Type': self.config["options"]["network_type"],
            'Wiki Column': self.config['options']['wiki']['wiki_column'],
            'Tweet Column': self.config['options']['twitter']['tweet_column']
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
            'model': PriceRnnModel(),
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
        size = 1
        LoggerHelper.info("Network Input Size :" + str(size))
        return size

    @staticmethod
    def get_config():
        pwd = os.path.dirname(os.path.abspath(__file__))
        if platform.system() == "Windows":
            return json.load(open(pwd + '/config_w.json', 'r'), cls=DateTimeDecoder)
        else:
            return json.load(open(pwd + '/config.json', 'r'), cls=DateTimeDecoder)
