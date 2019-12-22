from Helper.Timer import Timer
from Helper.DateHelper import DateHelper
from torch import nn, optim


class NewsDnnBaseMain(object):

    def __init__(self, config, epochs=None, batch_size=None, seq_length=None, use_gpu=None, lr=0.005, hidden_size=None):
        self.config = config
        if epochs is None:
            self.epochs = config["networkConfig"]["epochs"]
        else:
            self.epochs = epochs
        if batch_size is None:
            self.batch_size = config["networkConfig"]["batch_size"]
        else:
            self.batch_size = batch_size
        if seq_length is None:
            self.seq_length = self.config["networkConfig"]["sequence_length"]
        else:
            self.seq_length = seq_length
        if use_gpu is None:
            self.use_gpu = self.config["networkConfig"]["useGPU"]
        else:
            self.use_gpu = use_gpu
        if hidden_size is None:
            if self.config["networkConfig"]["hidden_size"] < 0:
                self.hidden_size = None
            else:
                self.hidden_size = self.config["networkConfig"]["hidden_size"]

        else:
            self.hidden_size = hidden_size

        self.timer = Timer()
        self.current_date = DateHelper.get_current_date()
        self.criterion = self.load_criterion()

    def load_criterion(self):
        if "NLLLoss" == self.config["networkConfig"]["criterion"]:
            return nn.NLLLoss()
        elif "CrossEntropyLoss" == self.config["networkConfig"]["criterion"]:
            return nn.CrossEntropyLoss()
        elif "KLDivLoss" == self.config["networkConfig"]["criterion"]:
            return nn.KLDivLoss()
        elif "MSELoss" == self.config["networkConfig"]["criterion"]:
            return nn.MSELoss()
        else:
            print("Criterion Not Found - NLLLoss is used")
            return nn.NLLLoss()


