# TextClassify

## Model

* fastText char
* fastText word
* CNN char embedding
* CNN word embedding
* CNN char & word embedding
* CNN + BiGRU + char & word embedding

## Segment Model

* pyltp
* jieba

## Embedding

* fastText (CBOW / skip-gram)
* gensim

char or word embedding

## Usage

```python
from text_classify import TextClassify

# default params
t = TextClassify()
text = ''
logtis = t.predict(text, precision='16')

# get index2label
t.index2label

# get top label
t.get_top_label(text, k=5, precision='16')
```

## Parameters

### `TextClassify`

* model: 'fasttext' (default), 'cnn', 'mcnn', 'mgcnn'
* cut: True, False (default)
* cut_model: 'pyltp' (default), 'jieba'
* pyltp_model: '/data_hdd/ltp_data/cws.model'
* fasttext_char_model: '/data_hdd/embedding/fasttext/zhihu_char_model.bin'
* fasttext_word_model: '/data_hdd/embedding/fasttext/zhihu_word_model.bin'
* cnn_char_model: '/home/keming/GitHub/custom_recom/cnn_char_fulltext_best.pth'
* cnn_word_model: '/home/keming/GitHub/custom_recom/cnn_word_fulltext_best.pth'
* mcnn_model: '/home/keming/GitHub/custom_recom/mcnn_fulltext_best.pth'
* mgcnn_model: '/home/keming/GitHub/custom_recom/mgcnn_fulltext_best.pth'
* char_embedding_model: '/data_hdd/embedding/wiki_char_256.model'
* word_embedding_model: '/data_hdd/embedding/wiki_word_256.model'
* words_index: '/data_hdd/zhihu/topic/words.csv'
* chars_index: '/data_hdd/zhihu/topic/chars.csv'
* labels_index: '/data_hdd/zhihu/topic/topics.csv'
* delete_char: '/data_hdd/zhihu/del_chars.txt'
* num_class: 384
* embedding_dim: 256
* num_filter: 128
* char_sentence_length: 256
* word_sentence_length: 128
* char_vocab_size: 12592
* word_vocab_size: 727811
* filter_size_1: [2, 3, 4, 5]
* filter_size_2: [2, 3, 4]
* rnn_num_unit: 128
* rnn_num_layer: 2

### `TextClassify.predict`

* text
* precision: '16' (default), '32', '64'

### `TextClassify.get_top_label`

* text
* k: 5 (default), numbers of label to return
* precision: '16' (default), '32', '64'

