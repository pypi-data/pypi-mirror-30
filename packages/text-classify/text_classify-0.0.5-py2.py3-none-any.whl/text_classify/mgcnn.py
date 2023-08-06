import torch
from torch import nn

class TextMGCNN(torch.nn.Module):
    def __init__(self, args):
        super(TextMGCNN, self).__init__()

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

        # Bi-GRU layer
        self.char_bigru_1 = nn.GRU(args.embedding_dim, args.rnn_num_unit, args.rnn_num_layer, bidirectional=True, batch_first=True)
        self.char_bigru_2 = nn.GRU(args.embedding_dim, args.rnn_num_unit, args.rnn_num_layer, bidirectional=True, batch_first=True)

        self.word_bigru_1 = nn.GRU(args.embedding_dim, args.rnn_num_unit, args.rnn_num_layer, bidirectional=True, batch_first=True)
        self.word_bigru_2 = nn.GRU(args.embedding_dim, args.rnn_num_unit, args.rnn_num_layer, bidirectional=True, batch_first=True)

        self.pool = nn.MaxPool1d(args.rnn_num_unit * 2)
        self.rnn_bn = nn.BatchNorm1d(args.char_sentence_length + args.word_sentence_length)
        self.rnn_fc = nn.Linear(args.char_sentence_length + args.word_sentence_length, args.num_class)


    def conv1d_relu_bn_pool(self, in_channel, out_channel, kernel_size, length):
        return nn.Sequential(
            nn.Conv1d(in_channel, out_channel, kernel_size),
            self.relu,
            nn.BatchNorm1d(out_channel),
            nn.MaxPool1d(length - kernel_size + 1),
        )

    def forward(self, input_char, input_word):
        # embedding
        char_embeded = self.char_embedding(input_char)
        word_embeded = self.word_embedding(input_word)

        # RNN
        char_middle, _ = self.char_bigru_1(char_embeded)
        char_middle, _ = self.char_bigru_2(char_middle)
        char_middle = self.pool(char_middle)

        word_middle, _ = self.word_bigru_1(word_embeded)
        word_middle, _ = self.word_bigru_2(word_middle)
        word_middle = self.pool(word_middle)

        middle = torch.squeeze(torch.cat([char_middle, word_middle], 1), 2)
        middle = self.rnn_bn(middle)
        rnn_result = self.rnn_fc(middle)

        # cnn
        char_embeded = char_embeded.transpose(1, 2)
        char_hidden = torch.cat([conv(char_embeded) for conv in self.char_conv_1], 2)
        char_hidden = torch.cat([conv(char_hidden) for conv in self.char_conv_2], 2)

        word_embeded = word_embeded.transpose(1, 2)
        word_hidden = torch.cat([conv(word_embeded) for conv in self.word_conv_1], 2)
        word_hidden = torch.cat([conv(word_hidden) for conv in self.word_conv_2], 2)

        hidden = self.cnn_bn(torch.cat([char_hidden.view(-1, self.layer_2_dim),
                                    word_hidden.view(-1, self.layer_2_dim)], 1))
        cnn_result = self.cnn_fc(hidden)


        return (cnn_result + rnn_result) / 2
