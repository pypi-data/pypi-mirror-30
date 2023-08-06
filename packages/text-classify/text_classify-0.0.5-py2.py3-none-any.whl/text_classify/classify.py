import os
import torch
import fastText
import numpy as np
import jieba
import plane
from pyltp import Segmentor
from uuid import uuid4

from text_classify.cnn import TextCNN
from text_classify.mcnn import TextMCNN
from text_classify.mgcnn import TextMGCNN
from text_classify.config import Config
from text_classify.utils import zero_padding, load_index, scaler, reverse_softmax


class TextClassify(object):
    def __init__(self, model='fasttext', cut=False, cut_model='pyltp', **kwargs):
        # update args
        self.args = type(str(uuid4()), Config.__bases__, dict(Config.__dict__))
        if kwargs:
            for k in kwargs:
                if k in dir(self.args):
                    setattr(self.args, k, kwargs[k])
                else:
                    raise NameError(k)

        # print('TextClassify args updated.')
        # print(args)
        self.cut = cut
        self.args.cut = cut # used in model
        self.cut_model = cut_model
        self.model_type = model

        # load word2index, char2index, index2label
        if self.cut or self.model_type in ['mcnn', 'mgcnn']:
            self.word2index, self.index2word = load_index(self.args.words_index)
        self.char2index, self.index2char = load_index(self.args.chars_index)
        self.label2index, self.index2label = load_index(self.args.labels_index)

        # load model
        if model == 'fasttext':
            if self.cut:
                self.model = fastText.load_model(self.args.fasttext_word_model)
            else:
                self.model = fastText.load_model(self.args.fasttext_char_model)
        else:
            if model == 'cnn':
                self.model = TextCNN(self.args)
                if self.cut:
                    self.model.load_state_dict(torch.load(self.args.cnn_word_model))
                else:
                    self.model.load_state_dict(torch.load(self.args.cnn_char_model))
            elif model == 'mcnn':
                self.model = TextMCNN(self.args)
                self.model.load_state_dict(torch.load(self.args.mcnn_model))
            elif model == 'mgcnn':
                self.model = TextMGCNN(self.args)
                self.model.load_state_dict(torch.load(self.args.mgcnn_model))

            self.model.eval()

        # load segment model
        if self.cut or model in ['mcnn', 'mgcnn']:
            if self.cut_model == 'pyltp':
                self.seg = Segmentor()
                self.seg.load(self.args.pyltp_model)
            elif self.cut_model == 'jieba':
                self.seg = jieba
                list(self.seg.cut('初始化结巴分词'))

        # load delete chars
        self.delete_chars = []
        if os.path.isfile(self.args.delete_char):
            with open(self.args.delete_char, encoding='utf-8') as f:
                delete_chars = f.readlines()
                self.delete_chars = [d.strip() for d in delete_chars]
        self.delete_chars = set(self.delete_chars)

    def predict(self, text, precision='16'):
        if precision not in ['16', '32', '64']:
            raise NameError('precision: {}'.format(precision))

        if self.model_type == 'fasttext':
            if self.cut:
                text = ' '.join(self.segment(text))
            else:
                text = ' '.join(plane.segment(text))
            preds = self.model.predict(text, self.args.num_class)
            if precision == '16':
                preds = (preds[0], np.array(preds[1], np.float16))
            elif precision == '32':
                preds = (preds[0], np.array(preds[1], np.float32))
            result = (preds[0], scaler(reverse_softmax(preds[1]), 0, 1))
            return self.align_label(result)

        # precess text
        char_feature = [self.char2index.get(t, 0) for t in plane.segment(text) if t not in self.delete_chars]
        char_feature = zero_padding([char_feature], self.args.char_sentence_length)
        char_feature = torch.from_numpy(char_feature).type(torch.LongTensor)
        char_feature = torch.autograd.Variable(char_feature, requires_grad=False, volatile=True)

        if self.cut or self.model_type != 'cnn':
            word_feature = [self.word2index.get(t, 0) for t in self.segment(text) if t not in self.delete_chars]
            word_feature = zero_padding([word_feature], self.args.word_sentence_length)
            word_feature = torch.from_numpy(word_feature).type(torch.LongTensor)
            word_feature = torch.autograd.Variable(word_feature, requires_grad=False, volatile=True)

        if self.model_type == 'cnn':
            if self.cut:
                logits = self.model(word_feature).data.numpy()[0]
            else:
                logits = self.model(char_feature).data.numpy()[0]
        else:
            logits = self.model(char_feature, word_feature).data.numpy()[0]
        if precision == '16':
            logits = np.array(logits, np.float16)
        elif precision == '32':
            logits = np.array(logits, np.float32)
        return scaler(logits, 0, 1)


    def align_label(self, preds):
        logits = {}
        for i, label in enumerate(preds[0]):
            logits[label[9:].replace('_', ' ')] = preds[1][i]

        result = [[]] * self.args.num_class
        for label in self.label2index:
            result[self.label2index[label]] = logits[label]

        return result

    def segment(self, text):
        if self.cut_model == 'pyltp':
            return self.seg.segment(text)
        elif self.cut_model == 'jieba':
            return self.seg.cut(text)

    def get_top_label(self, text, k=5, precision='16'):
        if self.model_type == 'fasttext':
            if self.cut:
                text = ' '.join(self.segment(text))
            else:
                text = ' '.join(plane.segment(text))
            preds = self.model.predict(text, k)
            if precision == '16':
                preds = (preds[0], np.array(preds[1], np.float16))
            elif precision == '32':
                preds = (preds[0], np.array(preds[1], np.float32))
            return (preds[0], scaler(reverse_softmax(preds[1]), 0, 1))

        preds = self.predict(text, precision=precision)
        top_index = np.argsort(preds)[::-1]
        result = []
        result.append([self.index2label[i] for i in top_index[:k]])
        result.append([preds[i] for i in top_index[:k]])
        return result
