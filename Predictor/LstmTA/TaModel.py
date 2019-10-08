import torch
from torch import nn


class TaModel(nn.Module):

    """TaModel

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
    def __init__(self, input_size=1, hidden=256, n_layers=2,
                               drop_prob=0.2, lr=0.001):
        super().__init__()
        self.input_size = input_size
        self.hidden = hidden
        self.num_layers = n_layers
        self.drop_prob = drop_prob
        self.lr = lr

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
        self.fc = nn.Linear(self.hidden, 1)

        self.train_on_gpu = torch.cuda.is_available()
        if self.train_on_gpu:
            print('Training on GPU!')
        else:
            print('No GPU available, training on CPU; consider making n_epochs very small.')

    def forward(self, x, hidden):
        ''' Forward pass through the network.
            These inputs are x, and the hidden/cell state `hidden`. '''

        # New Hidden State From the LSTM
        r_output, hidden = self.lstm(x, hidden)

        # Dropout layer
        out = self.dropout(r_output)

        # Stack Up LSTM Outputs - Reshape the output
        out = out.contiguous().view(-1, self.hidden)

        # Fully-Connected Layer
        out = self.fc(out)

        # return the final output and the hidden state
        return out, hidden

    def init_hidden(self, batch_size):
        # Create two new tensors with sizes n_layers x batch_size x n_hidden,
        # initialized to zero, for hidden state and cell state of LSTM
        weight = next(self.parameters()).data

        if self.train_on_gpu:
            hidden = (weight.new(self.num_layers, batch_size, self.hidden).zero_().cuda(),
                      weight.new(self.num_layers, batch_size, self.hidden).zero_().cuda())
        else:
            hidden = (weight.new(self.num_layers, batch_size, self.hidden).zero_(),
                      weight.new(self.num_layers, batch_size, self.hidden).zero_())

        return hidden


