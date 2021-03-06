import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_sequence
from Helper.LoggerHelper import LoggerHelper

NumberOfClasses = 7


class PriceRnnModel(nn.Module):

    """NewsDnnWikiAndTwitterModel
            input_size: The number of expected features in the input `x`
            hidden_size: The number of features in the hidden state `h`
            num_layers: Stacked LSTM Default: 1
            bias: If ``False``, then the layer does not use bias weights `b_ih` and `b_hh`.
                Default: ``True``
            batch_first: If ``True``, then the input and output tensors are provided
                as (batch, seq, feature). Default: ``False``
            dropout: If non-zero, introduces a `Dropout` layer on the outputs of each
                LSTM layer except the last layer, with dropout probability equal to
                :attr:`dropout`. Default: 0
            bidirectional: If ``True``, becomes a bidirectional LSTM. Default: ``False``
    """
    def __init__(self,
                 input_size=1,
                 hidden=None,
                 n_layers=2,
                 drop_prob=0.2,
                 lr=0.001,
                 training_data_size=100000,
                 output_size=3,
                 use_gpu=True):
        super().__init__()
        self.should_use_gpu = use_gpu
        self.input_size = input_size
        self.training_data_size = training_data_size
        self.num_layers = n_layers
        self.drop_prob = drop_prob
        self.lr = lr
        self.output_size = output_size
        if hidden is None:
            self.hidden = self.calculate_hidden_size()
        else:
            self.hidden = hidden

        self.lstm = nn.LSTM(self.input_size,        # Expected features in the input
                            self.hidden,            # Features in the hidden state
                            self.num_layers,        # Stacked LSTM's
                            bias=True,              # Bias weights should be used or not
                            dropout=drop_prob,      # Dropout layer of each LSTM
                            batch_first=True,       # Input and output tensors are provided as (batch, seq, feature)
                            bidirectional=False)    # Bidirectional LSTM

        # Additional Dropout Layer
        self.dropout = nn.Dropout(drop_prob)

        # Fully-Connected Output Layer
        self.fc = nn.Linear(self.hidden, output_size)

        # Sigmoid Layer
        self.sig = nn.LogSoftmax(dim=1)

        # Check GPU Usage
        self.can_use_gpu = torch.cuda.is_available()
        if self.can_use_gpu:
            if self.should_use_gpu:
                LoggerHelper.info('Training on GPU!')
            else:
                LoggerHelper.info('GPU usage is disabled by config.json')
        else:
            LoggerHelper.info('No GPU available, training on CPU; consider making n_epochs very small.')

    def forward(self, x, hidden):
        ''' Forward pass through the network.
            These inputs are x, and the hidden/cell state `hidden`. '''

        # New Hidden State From the LSTM
        r_output, hidden = self.lstm(x, hidden)
        r_output = r_output[:, -1, :]  # Stack Up LSTM Outputs - Reshape the output

        # Dropout layer
        out = self.dropout(r_output)

        # Fully-Connected Output Layer
        out = self.fc(out)

        # Sigmoid Layer
        sig_out = self.sig(out)

        # return the final output and the hidden state
        return sig_out, hidden

    def init_hidden(self, batch_size):
        # Create two new tensors with sizes n_layers x batch_size x n_hidden,
        # initialized to zero, for hidden state and cell state of LSTM

        if self.can_use_gpu and self.should_use_gpu:
            hidden = (torch.zeros(self.num_layers, batch_size, self.hidden).cuda(),
                      torch.zeros(self.num_layers, batch_size, self.hidden).cuda())
        else:
            hidden = (torch.zeros(self.num_layers, batch_size, self.hidden),
                      torch.zeros(self.num_layers, batch_size, self.hidden))
        return hidden

    def calculate_hidden_size(self):
        samples_in_training_data = 10000
        scaling_factor = 5
        input_neurons = self.input_size
        output_neurons = self.output_size
        size = int(samples_in_training_data / (scaling_factor * (input_neurons + output_neurons)))
        LoggerHelper.info('Calculated hidden size is ' + str(size))
        if size == 0:
            LoggerHelper.error('Calculated hidden size is changed to 2')
            return 2
        else:
            return size

