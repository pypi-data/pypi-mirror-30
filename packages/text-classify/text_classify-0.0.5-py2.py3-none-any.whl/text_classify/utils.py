import os
import csv
import numpy as np
from gensim.models import Word2Vec

def zero_padding(x, length):
    result = np.zeros((len(x), length))
    for i, row in enumerate(x):
        for j, val in enumerate(row):
            if j >= length:
                break
            result[i][j] = val
    return result

def load_index(filename):
    if not os.path.exists(filename):
        raise ValueError('File not exists.')

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        word2index, index2word = {}, {}
        for i, row in enumerate(reader):
            word = row[0]
            word2index[word] = i
            index2word[i] = word

    return word2index, index2word


def load_embedding(embedding_model, index2word, vocab_size, dim):
    word2vec = Word2Vec.load(embedding_model)
    embedding = [[]] * vocab_size
    embedding[0] = np.zeros(dim)
    bound = np.sqrt(6.0) / np.sqrt(vocab_size)
    count_exist, count_not_exist = 0, 0
    for i in range(1, vocab_size):
        word = index2word[i]
        try:
            embedding[i] = word2vec.wv[word]
            count_exist += 1
        except:
            embedding[i] = np.random.uniform(-bound, bound, dim)
            count_not_exist += 1

    print('word exists embedding:', count_exist, '\tword not exists:', count_not_exist)
    embedding = np.array(embedding)
    return embedding

def scaler(x, minimal=0, maximal=1):
    std = (x - np.min(x)) / (np.max(x) - np.min(x))
    return std * (maximal - minimal) + minimal

def reverse_softmax(x):
    """ ugly """
    ln = np.log(x)
    return ln - np.min(x)
