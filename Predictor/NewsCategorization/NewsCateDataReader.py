import torch
from transformers import BertTokenizer  # Tokonizer
from Predictor.NewsDnnBase.NewsDnnBaseDataReader import NewsDnnBaseDataReader
from torch.utils.data import TensorDataset, DataLoader, RandomSampler


class NewsCateDataReader(NewsDnnBaseDataReader):

    def __init__(self, config, batch_size, sequence_length, pretrained_weights):
        super().__init__(config, batch_size, sequence_length, word_emb_enabled=False)
        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(pretrained_weights)  # Load tokenizer

    '''
        NEWS
    '''
    def get_data_news(self, cursor):
        text_key = self.configs['networkConfig']['text_column']
        label_key = self.configs['networkConfig']['cate_column']
        label = []
        input_ids = []
        attention_mask = []
        for row in cursor:
            encoded_sent = self.tokenizer.encode_plus(
                row[text_key],  # Sentence to encode.
                add_special_tokens=True,  # Add '[CLS]' and '[SEP]'
                pad_to_max_length=True,
                max_length=128,
            )
            label.append(self.get_label(row[label_key]))
            input_ids.append(encoded_sent['input_ids'])
            attention_mask.append(encoded_sent['attention_mask'])
        # Move Data to Tensors
        label = torch.tensor(label)
        input_ids = torch.tensor(input_ids)
        attention_mask = torch.tensor(attention_mask)
        # Create the DataLoader for our set.
        train_data = TensorDataset(input_ids, attention_mask, label)
        train_sampler = RandomSampler(train_data)
        train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=self.batch_size)
        return train_dataloader

    @staticmethod
    def get_label(label):
        if label == -1:
            return 0
        else:
            return 1
