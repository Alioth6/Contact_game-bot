import compress_fasttext
from pymystem3 import Mystem
import re


class Word2vec:
    def get_word_vector(self, word):
        raise Exception('Not implemented')


class FastText(Word2vec):
    def __init__(self, path):
        self.model = compress_fasttext.models.CompressedFastTextKeyedVectors.load(path)
    
    def get_word_vector(self, word):
        return self.model[word]      


class Text2Lemms:
    def __init__(self):
        self.mystem = Mystem()
    
    def get_lemms(self, text, tag=None):
        list_lemm = []
        for lemma in self.mystem.analyze(text):
            if 'analysis' in lemma and len(lemma['analysis']):
                analysis = lemma['analysis'][0]
                if analysis.get('qual', None) == 'bastard':
                    continue
                pos_tag = re.match('[A-Z]+', analysis['gr']).group(0)
                if tag and pos_tag==tag:
                    list_lemm.append(analysis['lex'])
                elif not tag:
                    list_lemm.append({'lex': analysis['lex'], 'pos': pos_tag})
        return list_lemm


class WordTrie:
    '''
        How use 

        wt = WordTrie(FastText())
        wt.build_dict(['word', 'world', 'cat', 'cats'])
        for word, vector in wt.search_by_prefix('cats'): 
            print(word)
    '''
    def __init__(self, word2vec:Word2vec):
        self.root = _Node('*')
        self.get_vector = word2vec.get_word_vector

    def add(self, word):
        tmp_node = self.root

        for char in word:
            child = tmp_node.children.get(char, None)
            if child is None:
                child = _Node(char)
                tmp_node.children[char] = child
                child.parent = tmp_node
            tmp_node = child

        tmp_node.value = self.get_vector(word)

    def build_dict(self, words):
        for word in words:
            self.add(word)
        return self

    def search_by_prefix(self, prefix):
        tmp_node = self.root

        for char in prefix:
            tmp_node = tmp_node.children.get(char, None)
            if tmp_node is None:
                return
        yield from tmp_node.get_childs()


#####################
##### for WordTrie
#####################


class _Node:
    def __init__(self, char: str):
        self.char = char
        self.children = {}
        self.value = None
        self.parent = None

    def _get_prefix(self):
        tmp_node = self
        prefix = ''
        while tmp_node.parent:
            prefix = tmp_node.char + prefix
            tmp_node = tmp_node.parent

        return prefix

    def get_childs(self):
        stack = [(self, self._get_prefix())]

        while stack:
            tmp_node, prefix = stack.pop(0)
            if tmp_node.value is not None:
                yield prefix, tmp_node.value
            
            for char, child in tmp_node.children.items():
                stack.append((child, prefix+char))
