import torch
from torch import nn

from text_classify.utils import load_embedding

class TextCNN(torch.nn.Module):
    def __init__(self, args):
        super(TextCNN, self).__init__()

        if args.cut:
            vocab_size = args.word_vocab_size
            sentence_length = args.word_sentence_length
        else:
            vocab_size = args.char_vocab_size
            sentence_length = args.char_sentence_length

        self.embedding = nn.Embedding(vocab_size, args.embedding_dim, sentence_length)
        self.relu = nn.ReLU(inplace=True)
        self.conv_layer_1 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.embedding_dim, args.num_filter, k, sentence_length)
            for k in args.filter_size_1
        ])
        self.conv_layer_2 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.num_filter, args.num_filter, k, len(args.filter_size_1))
            for k in args.filter_size_2
        ])
        self.layer_2_dim = len(args.filter_size_2) * args.num_filter
        self.bn = nn.BatchNorm1d(self.layer_2_dim)
        self.fc = nn.Linear(self.layer_2_dim, args.num_class)

    def conv1d_relu_bn_pool(self, in_channel, out_channel, kernel_size, dim):
        return nn.Sequential(
            nn.Conv1d(in_channel, out_channel, kernel_size),
            self.relu,
            nn.BatchNorm1d(out_channel),
            nn.MaxPool1d(dim - kernel_size + 1),
        )

    def forward(self, input_data):
        embeded = self.embedding(input_data).transpose(1, 2)
        hidden = torch.cat([conv(embeded) for conv in self.conv_layer_1], 2)
        hidden = torch.cat([conv(hidden) for conv in self.conv_layer_2], 2)
        hidden = self.bn(hidden.view(-1, self.layer_2_dim))
        return self.fc(hidden)
