import os
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~’’“”"""


class PreProcessing(object):

    def __init__(self):
        self.stopwords = PreProcessing.get_stopwords()
        self.punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~’’“”"""

    def preprocess(self, content):
        content = content.lower()
        words = word_tokenize(content)
        words_filtered = []
        for w in words:
            if (w not in self.stopwords) and (w not in self.punctuation):
                w = ''.join([c for c in w if c not in punctuation])
                if w.isalpha() and len(w) > 1:  # filter out short tokens and not alphabetic
                    words_filtered.append(w)
        return words_filtered

    def preprocess_extra(self, content):
        content = content.lower()
        words = word_tokenize(content)
        sentence_filtered = ""
        words_filtered = []
        for w in words:
            if (w not in self.stopwords) and (w not in self.punctuation):
                w = ' '.join([c for c in w if c not in punctuation])
                if w.isalpha() and len(w) > 1:  # filter out short tokens and not alphabetic
                    sentence_filtered += " " + w
                    words_filtered.append(w)
        return words_filtered, sentence_filtered

    def is_stop_word_or_punctuation(self, word):
        if (word in self.stopwords) or (word in self.punctuation):
            return True
        return False

    @staticmethod
    def get_stopwords():
        pwd = os.path.dirname(os.path.abspath(__file__))
        return json.load(open(pwd+'/stopwords.json', 'r'))
