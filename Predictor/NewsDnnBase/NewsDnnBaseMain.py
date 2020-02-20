from Helper.Timer import Timer
from Helper.DateHelper import DateHelper
from torch import nn
from sklearn import metrics
from Helper.LoggerHelper import LoggerHelper
import numpy as np


class NewsDnnBaseMain(object):

    def __init__(self, config, epochs=None, batch_size=None, seq_length=None, use_gpu=None, lr=None, hidden_size=None):
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
        if lr is None:
            self.lr = self.config["networkConfig"]["learning_rate"]
        else:
            self.lr = lr

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
        elif "BCEWithLogitsLoss" == self.config["networkConfig"]["criterion"]:
            return nn.BCEWithLogitsLoss()
        else:
            print("Criterion Not Found - NLLLoss is used")
            return nn.NLLLoss()

    @staticmethod
    def get_output(output):
        arr = []
        for i, out in enumerate(output):
            top_n, top_i = out.topk(1)
            arr.append(top_i[0].item())
        return np.asarray(arr)

    @staticmethod
    def calculate_scores(result_expected, result):
        f1 = metrics.f1_score(result_expected, result, average='weighted')
        precision = metrics.precision_score(result_expected, result, average='weighted')
        recall = metrics.recall_score(result_expected, result, average='weighted')
        accuracy = metrics.accuracy_score(result_expected, result)
        hamming = metrics.hamming_loss(result_expected, result)
        jaccard = metrics.jaccard_score(result_expected, result)
        # roc_auc_score, matthews_corrcoef and zero_one_loss could be added.
        return {
            "f1": f1,
            "precision": precision,
            "recall": recall,
            "accuracy": accuracy,
            "hamming": hamming,
            "jaccard": jaccard
        }

    def log_validate(self, df, epoch, counter, loss, val_losses, validate_count, scores):
        LoggerHelper.info("Epoch: {}/{}...".format(epoch + 1, self.epochs) +
                          "Step: {}...".format(counter) +
                          "Loss: {:.4f}...".format(loss.item()) +
                          "Accuracy In Step: {:.4f}...".format(scores["accuracy"]) +
                          "F1 : {:.4f}...".format(scores["f1"]) +
                          "Precision : {:.4f}...".format(scores["precision"]) +
                          "Recall : {:.4f}...".format(scores["recall"]) +
                          "Hamming : {:.4f}...".format(scores["hamming"]) +
                          "Jaccard : {:.4f}...".format(scores["jaccard"]) +
                          "Val Count: {:.4f}...".format(validate_count) +
                          "Val Loss: {:.4f}".format(np.mean(val_losses)))
        df = df.append({
            'Epoch': "{}/{}".format(epoch + 1, self.epochs),
            'Step': counter,
            'Last Train Loss': loss.item(),
            'Mean Test Loss': np.mean(val_losses),
            'Accuracy In Step': scores["accuracy"],
            'F1 In Step': scores["f1"],
            'Precision In Step': scores["precision"],
            'Recall In Step': scores["recall"],
            'Hamming In Step': scores["hamming"],
            'Jaccard In Step': scores["jaccard"]
        }, ignore_index=True)
        return df

    def log_test(self, df, accuracy, test_count, val_losses, scores):
        df = df.append({
            'Accuracy': "{}/{}".format(accuracy, test_count),
            'Mean Test Loss': np.mean(val_losses),
            'Accuracy Score': scores["accuracy"],
            'F1': scores["f1"],
            'Precision': scores["precision"],
            'Recall': scores["recall"],
            'Hamming': scores["hamming"],
            'Jaccard': scores["jaccard"]
        }, ignore_index=True)
        return df
