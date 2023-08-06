import torch
from torch import nn

class TextMCNN(torch.nn.Module):
    def __init__(self, args):
        super(TextMCNN, self).__init__()

        self.char_embedding = nn.Embedding(args.char_vocab_size, args.embedding_dim, args.char_sentence_length)
        self.word_embedding = nn.Embedding(args.word_vocab_size, args.embedding_dim, args.word_sentence_length)

        # CNN layer
        self.relu = nn.ReLU(inplace=True)
        self.char_conv_1 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.embedding_dim, args.num_filter, k, args.char_sentence_length)
            for k in args.filter_size_1
        ])
        self.char_conv_2 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.num_filter, args.num_filter, k, len(args.filter_size_1))
            for k in args.filter_size_2
        ])

        self.word_conv_1 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.embedding_dim, args.num_filter, k, args.word_sentence_length)
            for k in args.filter_size_1
        ])
        self.word_conv_2 = nn.ModuleList([
            self.conv1d_relu_bn_pool(args.num_filter, args.num_filter, k, len(args.filter_size_1))
            for k in args.filter_size_2
        ])

        self.layer_2_dim = len(args.filter_size_2) * args.num_filter
        self.cnn_bn = nn.BatchNorm1d(self.layer_2_dim * 2)
        self.cnn_fc = nn.Linear(self.layer_2_dim * 2, args.num_class)

    def conv1d_relu_bn_pool(self, in_channel, out_channel, kernel_size, dim):
        return nn.Sequential(
            nn.Conv1d(in_channel, out_channel, kernel_size),
            self.relu,
            nn.BatchNorm1d(out_channel),
            nn.MaxPool1d(dim - kernel_size + 1),
        )

    def forward(self, input_char, input_word):
        char_embeded = self.char_embedding(input_char).transpose(1, 2)
        char_hidden = torch.cat([conv(char_embeded) for conv in self.char_conv_1], 2)
        char_hidden = torch.cat([conv(char_hidden) for conv in self.char_conv_2], 2)

        word_embeded = self.word_embedding(input_word).transpose(1, 2)
        word_hidden = torch.cat([conv(word_embeded) for conv in self.word_conv_1], 2)
        word_hidden = torch.cat([conv(word_hidden) for conv in self.word_conv_2], 2)

        hidden = self.cnn_bn(torch.cat([char_hidden.view(-1, self.layer_2_dim),
                                    word_hidden.view(-1, self.layer_2_dim)], 1))
        return self.cnn_fc(hidden)
