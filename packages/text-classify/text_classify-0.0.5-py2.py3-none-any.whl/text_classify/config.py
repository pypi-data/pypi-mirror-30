class Config:
    pyltp_model = '/data_hdd/ltp_data/cws.model'
    fasttext_char_model = '/data_hdd/embedding/fasttext/zhihu_char_model.bin'
    fasttext_word_model = '/data_hdd/embedding/fasttext/zhihu_word_model.bin'
    cnn_char_model = '/home/keming/GitHub/custom_recom/cnn_char_fulltext_best.pth'
    cnn_word_model = '/home/keming/GitHub/custom_recom/cnn_word_fulltext_best.pth'
    mcnn_model = '/home/keming/GitHub/custom_recom/mcnn_fulltext_best.pth'
    mgcnn_model = '/home/keming/GitHub/custom_recom/mgcnn_fulltext_best.pth'
    char_embedding_model = '/data_hdd/embedding/wiki_char_256.model'
    word_embedding_model = '/data_hdd/embedding/wiki_word_256.model'
    words_index = '/data_hdd/zhihu/topic/words.csv'
    chars_index = '/data_hdd/zhihu/topic/chars.csv'
    labels_index = '/data_hdd/zhihu/topic/topics.csv'
    delete_char = '/data_hdd/zhihu/del_chars.txt'

    num_class = 384
    embedding_dim = 256
    num_filter = 128
    char_sentence_length = 256
    word_sentence_length = 128
    char_vocab_size = 12592
    word_vocab_size = 727811
    filter_size_1 = [2, 3, 4, 5]
    filter_size_2 = [2, 3, 4]
    rnn_num_unit = 128
    rnn_num_layer = 2

