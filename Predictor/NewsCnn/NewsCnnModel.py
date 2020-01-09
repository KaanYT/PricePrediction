import torch
from torch import nn
import torch.nn.functional as F
from Helper.LoggerHelper import LoggerHelper

NumberOfClasses = 7


class NewsCnnModel(nn.Module):

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
                 input_size=102,
                 n_layers=2,
                 drop_prob=0.2,
                 n_filters=100,
                 filter_sizes=[3, 4, 5],
                 lr=0.001,
                 output_size=3,
                 use_gpu=True):
        super().__init__()
        self.should_use_gpu = use_gpu
        self.input_size = input_size
        self.output_size = output_size
        self.num_layers = n_layers
        self.drop_prob = drop_prob
        self.lr = lr

        # 2D Convolution Layer
        self.conv_0 = nn.Conv1d(in_channels=input_size,
                                out_channels=n_filters,
                                kernel_size=filter_sizes[0])

        self.conv_1 = nn.Conv1d(in_channels=input_size,
                                out_channels=n_filters,
                                kernel_size=filter_sizes[1])

        self.conv_2 = nn.Conv1d(in_channels=input_size,
                                out_channels=n_filters,
                                kernel_size=filter_sizes[2])

        # Additional Dropout Layer
        self.dropout = nn.Dropout(drop_prob)
        # Fully-Connected Output Layer
        self.fc = nn.Linear(len(filter_sizes) * n_filters, output_size)
        # Sigmoid Layer
        self.sig = nn.Softmax(dim=1)
        # Check GPU Usage
        self.can_use_gpu = torch.cuda.is_available()
        if self.can_use_gpu:
            if self.should_use_gpu:
                LoggerHelper.info('Training on GPU!')
            else:
                LoggerHelper.info('GPU usage is disabled by config.json')
        else:
            LoggerHelper.info('No GPU available, training on CPU; consider making n_epochs very small.')

    def forward(self, x):
        ''' Forward pass through the network.
            These inputs are x, and the hidden/cell state `hidden`. '''

        conved_0 = F.relu(self.conv_0(x))
        conved_1 = F.relu(self.conv_1(x))
        conved_2 = F.relu(self.conv_2(x))

        pooled_0 = F.max_pool1d(conved_0, conved_0.shape[2]).squeeze(2)
        pooled_1 = F.max_pool1d(conved_1, conved_1.shape[2]).squeeze(2)
        pooled_2 = F.max_pool1d(conved_2, conved_2.shape[2]).squeeze(2)

        # Dropout layer
        cat = self.dropout(torch.cat((pooled_0, pooled_1, pooled_2), dim=1))

        # Fully-Connected Layer
        out = self.fc(cat)

        # Sigmoid Layer
        sig_out = self.sig(out)

        # return the final output
        return sig_out

