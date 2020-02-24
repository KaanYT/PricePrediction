import os
import platform
import json
import torch
import random
import traceback
import numpy as np
import datetime as dt
import pandas
from pymongo.errors import CursorNotFound

from Helper.JsonDateHelper import DateTimeDecoder
from Helper.DateHelper import DateHelper
from Helper.LoggerHelper import LoggerHelper
from Helper.FileHelper import FileHelper
from Helper.Timer import Timer

from Predictor.NewsCategorization.NewsCateDataReader import NewsCateDataReader
from Predictor.NewsDnnBase.NewsDnnBaseMain import NewsDnnBaseMain

from Managers.DatabaseManager.MongoDB import Mongo
from Managers.LogManager.Log import Logger
from Managers.ExportManager.Export import Export

from Archive.News.Organizer.NewsOrganizer import NewsOrganizer

from transformers import BertForSequenceClassification, BertTokenizer, AdamW  # Models
from transformers import get_linear_schedule_with_warmup
from transformers import pipeline


class NewsCateMain(NewsDnnBaseMain):

    """ Initializer

            Arguments
            ---------
            epochs: Number of epochs to train
            batch_size: Number of mini-sequences per mini-batch, aka batch size
            seq_length: Number of character steps per mini-batch
    """
    def __init__(self, epochs=None, batch_size=None, seq_length=None, use_gpu=None, lr=2e-5, hidden_size=None,
                 pretrained_weights='bert-base-uncased'):
        super().__init__(self.get_config(), epochs, batch_size, seq_length, use_gpu, lr, hidden_size=hidden_size)
        # Load DB
        self.reader = NewsCateDataReader(self.config, self.batch_size, self.seq_length, pretrained_weights)
        self.train_count = self.reader.get_count(NewsCateDataReader.DictDataTerm["Train"])
        self.test_count = self.reader.get_count(NewsCateDataReader.DictDataTerm["Test"])
        self.validate_count = self.reader.get_count(NewsCateDataReader.DictDataTerm["Validate"])

        # Create Model
        self.model = BertForSequenceClassification.from_pretrained(pretrained_weights,  # Load Pre-Trained model
                                                                   num_labels=2,
                                                                   output_hidden_states=False,
                                                                   output_attentions=False,
                                                                   torchscript=True)
        self.optimizer = AdamW(self.model.parameters(),
                               lr=lr,  # args.learning_rate - default is 5e-5, our notebook had 2e-5
                               eps=1e-8  # args.adam_epsilon  - default is 1e-8.
                               )
        self.scheduler = self.create_schedular()
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

    def create_schedular(self):
        # Total number of training steps is number of batches * number of epochs.
        total_steps = self.epochs * self.train_count
        # Create the learning rate scheduler.
        return get_linear_schedule_with_warmup(self.optimizer,
                                               num_warmup_steps=0,  # Default value in run_glue.py
                                               num_training_steps=total_steps)

    def train(self, print_every=20):
        df = pandas.DataFrame(columns=['Epoch', 'Step',
                                       'Train Mean Loss Cumulative', 'Train Accuracy',
                                       'Val Mean Loss', 'Val Accuracy'])
        self.timer.start()
        self.model.train()  # Set mode of model
        losses = []
        train_set = self.reader.get_data(fetch_type=NewsCateDataReader.DictDataTerm["Train"],
                                         data_type=NewsCateDataReader.DictDataType[
                                             self.config["options"]["network_type"]])
        for e in range(self.epochs):
            print(self.config["options"]["network_type"])
            print(NewsCateDataReader.DictDataType[
                      self.config["options"]["network_type"]])
            self.model.train()  # Set to Train Mode
            total_loss_for_epoch = 0

            epoch_timer = Timer()
            epoch_timer.start()
            for step, batch in enumerate(train_set): # For each batch of training data...
                # Progress update every 40 batches.
                if step % print_every == 0:
                    # Report progress.
                    print('  Batch {:>5,}  of  {:>5,}.'.format(step, len(train_set)))
                # Get Data
                b_input_ids = batch[0].to(self.device)
                b_input_mask = batch[1].to(self.device)
                b_labels = batch[2].to(self.device)

                # (source: https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch)
                self.model.zero_grad()

                # Perform a forward pass (evaluate the model on this training batch).
                # https://huggingface.co/transformers/v2.2.0/model_doc/bert.html#transformers.BertForSequenceClassification
                outputs = self.model(b_input_ids,
                                     token_type_ids=None,
                                     attention_mask=b_input_mask,
                                     labels=b_labels)
                loss = outputs[0]
                total_loss_for_epoch += loss.item()

                # Perform a backward pass to calculate the gradients.
                loss.backward()

                # This is to help prevent the "exploding gradients" problem.
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                # modified based on their gradients, the learning rate, etc.
                self.optimizer.step()

                # Update the learning rate.
                self.scheduler.step()

            # Calculate the average loss over the training data.
            avg_train_loss = total_loss_for_epoch / len(train_set)

            # Store the loss value for plotting the learning curve.
            losses.append(avg_train_loss)
            LoggerHelper.info("  Average training loss: {0:.2f}".format(avg_train_loss))
            epoch_timer.stop(time_for="Epoch")

            timer = Timer(start=True)
            df = self.validate(df, e, losses)
            timer.stop(time_for="Validate")
            self.model.train()
        self.timer.stop(time_for="Train")
        self.save_model()
        self.current_date = DateHelper.get_current_date()
        Export.append_df_to_excel(df, self.current_date)
        Export.append_df_to_excel(self.get_info(), self.current_date)

    def validate(self, df, epoch, losses):
        LoggerHelper.info("Validation Started...")
        # Get validation loss
        val_losses = []
        predictions, true_labels = [], []
        self.model.eval()
        accuracy = 0
        steps = 0
        validate_set = self.reader.get_data(NewsCateDataReader.DictDataTerm["Validate"],
                                            NewsCateDataReader.DictDataType[
                                                self.config["options"]["network_type"]])
        for batch in validate_set:  # Evaluate data for one epoch
            # Add batch to GPU
            batch = tuple(t.to(self.device) for t in batch)
            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask, b_labels = batch
            with torch.no_grad():  # Not to compute or store gradients
                outputs = self.model(b_input_ids,
                                     token_type_ids=None,
                                     attention_mask=b_input_mask)
                logits = outputs[0]
                # Move logits and labels to CPU
                logits = logits.detach().cpu().numpy()
                label_ids = b_labels.to('cpu').numpy()
                # Calculate the accuracy for this batch of test sentences.
                label, tmp_eval_accuracy = self.calculate_accuracy(logits, label_ids)
                # Accumulate the total accuracy.
                accuracy += tmp_eval_accuracy
                # Track the number of batches
                steps += 1
                # Store predictions and true labels
                predictions.append(label)
                true_labels.append(label_ids)
        # Report the final accuracy for this validation run.
        LoggerHelper.info("Accuracy: {0:.2f}".format(accuracy / steps))
        scores = self.calculate_scores(predictions, true_labels)
        self.model.train()  # reset to train mode after iterationg through validation data
        return self.log_validate_without_loss(df, epoch, 0, self.validate_count, scores)

    def test(self):
        LoggerHelper.info("Test Started...")
        self.timer.start()
        df = pandas.DataFrame(columns=['Accuracy', 'Test Accuracy', 'Mean Test Loss'])
        # Tracking variables
        val_losses = []
        predictions, true_labels = [], []

        test_set = self.reader.get_data(NewsCateDataReader.DictDataTerm["Test"],
                                        NewsCateDataReader.DictDataType[
                                            self.config["options"]["network_type"]])
        self.model.eval()
        accuracy = 0
        for batch in test_set:
            # Add batch to GPU
            batch = tuple(t.to(self.device) for t in batch)

            # Unpack the inputs from our dataloader
            b_input_ids, b_input_mask, b_labels = batch

            with torch.no_grad():
                # Forward pass, calculate logit predictions
                outputs = self.model(b_input_ids, token_type_ids=None,
                                     attention_mask=b_input_mask)

                logits = outputs[0]

                # Move logits and labels to CPU
                logits = logits.detach().cpu().numpy()
                label_ids = b_labels.to('cpu').numpy()

                # Calculate the accuracy for this batch of test sentences.
                label, acc = self.calculate_accuracy(logits, label_ids)
                accuracy += acc

                # Store predictions and true labels
                predictions.append(label)
                true_labels.append(label_ids)
        scores = self.calculate_scores(predictions, true_labels)
        df = self.log_test(df, accuracy, self.test_count, val_losses, scores)
        Export.append_df_to_excel(df, self.current_date)
        self.timer.stop(time_for="Test")

    def evaluate(self):
        LoggerHelper.info("Evaluation Started...")
        nlp = pipeline('sentiment-analysis')
        self.load_model(self.config["evaluation"]["load"])
        self.model.eval()
        self.timer.start()
        db = Mongo()
        news_collection = db.create_collection(self.config["evaluation"]["collection"])
        news_filtered = db.create_collection(self.config["evaluation"]["destination"], NewsOrganizer.get_index_models())
        count = 0
        processed = 0
        while True:
            try:
                cursor = news_collection.find(self.config["evaluation"]["query"], no_cursor_timeout=True).skip(
                    processed)
                for news in cursor:
                    try:
                        summery = news.get('summery')
                        b_input_ids, b_input_mask = self.reader.get_one_news(summery)
                        b_input_ids, b_input_mask = b_input_ids.to(self.device), b_input_mask.to(self.device)
                        outputs = self.model(b_input_ids, token_type_ids=None,
                                             attention_mask=b_input_mask)
                        logits = outputs[0].detach().cpu().numpy()  # Move result to CPU
                        result = np.argmax(logits, axis=1).flatten()  #
                        sentiment = nlp(summery)
                        if result[0] == 1:
                            news_filtered.insert({
                                "_id": news.get('_id'),
                                "title": news.get('title'),
                                "summery": news.get('summery'),
                                "article": news.get('article'),
                                "url": news.get('url'),
                                "category": news.get('category'),
                                "price_after_minute": news.get('price_after_minute'),
                                "price_after_hour": news.get('price_after_hour'),
                                "price_after_day": news.get('price_after_day'),
                                "sentiment": sentiment,
                                "price_before": news.get('price_before'),
                                "wiki_relatedness": news.get('wiki_relatedness'),
                                "tweet_count": news.get('tweet_count'),
                                "tweet_percentage": news.get('tweet_percentage'),
                                "date": news.get('date'),
                                "authors": news.get('authors'),
                                "comment": news.get('comment'),
                                "price_effect": news.get('price_effect')
                            })
                    except Exception as exception:
                        Logger().get_logger().error(type(exception).__name__, exc_info=True)
                        traceback.print_exc()
                    count = count + 1
                    if count % 500 == 0:
                        print(count)
                    processed += 1
                cursor.close()
                break
            except CursorNotFound:
                processed += 1
                print("Lost cursor. Retry with skip")
        self.timer.stop(time_for="Evaluation")

    @staticmethod
    def set_seed_value(seed_val=42):
        random.seed(seed_val)
        np.random.seed(seed_val)
        torch.manual_seed(seed_val)

    @staticmethod
    def calculate_accuracy(preds, labels):
        pred_flat = np.argmax(preds, axis=1).flatten()
        labels_flat = labels.flatten()
        accuracy = np.sum(pred_flat == labels_flat) / len(labels_flat)
        return labels_flat, accuracy

    def get_info(self):
        info = pandas.DataFrame(columns=['Database',
                                         'Key',
                                         'Batch Size',
                                         'Sequence Length',
                                         'Input Size',
                                         'Input Wiki Factor',
                                         'Input Twitter Factor',
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
            'Number of Layers': self.model.num_labels,
            'Input Wiki Factor': self.config["options"]["wiki"]["multiply_factors"],
            'Input Twitter Factor': self.config["options"]["twitter"]["multiply_factors"],
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
                                      '%s-e%s(%s)' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'),
                                                       str(self.epochs),
                                                       self.config["database"]["name"]))

        return save_file_name

    def save_model(self):
        save_file_name = self.get_save_file_name()
        FileHelper.create_path_if_not_exists(save_file_name)
        self.model.save_pretrained(save_file_name)  # save
        self.reader.tokenizer.save_pretrained(save_file_name)  # save
        LoggerHelper.info("Model Saved to disk")

    def load_model(self, path):
        self.model = BertForSequenceClassification.from_pretrained(path)  # re-load
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # re-load
        LoggerHelper.info("**Model Info**"
                          + "\nbatch_size : " + str(self.reader.batch_size)
                          + "\nsequence_length : " + str(self.reader.sequence_length))
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
