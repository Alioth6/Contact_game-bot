import sys
import os
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
from .additional_structures import Text2Lemms, WordTrie, FastText

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_DIR, '../data')

PATH_TO_WIGHT_FASTTEXT = os.path.join(DATA_PATH, 'ft_freqprune_400K_100K_pq_300.bin')
PATH_TO_WIKI = os.path.join(DATA_PATH, 'wiktionary_data0.csv')
DICTIONARY_SIZE = 10000

BAD_WORDS = stopwords.words("russian")
text2LemmsModel = Text2Lemms()
fastTextModel = FastText(PATH_TO_WIGHT_FASTTEXT)


def get_wiki_words(is_all_words_list=None):
    df = pd.read_csv(PATH_TO_WIKI, delimiter='\\')
    text_id = df.keys()[2]
    list_defs = df[text_id]
    set_words = []

    for text in list_defs:
        if is_all_words_list is None:
            set_words += text2LemmsModel.get_lemms(text, 'S')
        else:
            set_words += text2LemmsModel.get_lemms(text)

    return Counter(set_words)


def get_prefix_trie(is_all_words_list=None):
    stopwords.words("russian")
    words = get_wiki_words(is_all_words_list)

    for w in BAD_WORDS:
        words.pop(w, 0)

    words = [w for w,i in words.most_common(DICTIONARY_SIZE)]
    word_trie = WordTrie(fastTextModel)
    word_trie.build_dict(words)

    return word_trie
