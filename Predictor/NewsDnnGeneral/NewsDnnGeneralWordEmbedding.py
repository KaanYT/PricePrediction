import numpy as np

from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from gensim.test.utils import get_tmpfile
from gensim.scripts.glove2word2vec import glove2word2vec


class WordEmbedding(object):
    Model = None
    Words = {}

    def __new__(cls, path=''):

        if not hasattr(cls, 'instance'):
            cls.instance = super(WordEmbedding, cls).__new__(cls)
            if path.endswith(".bin"):
                cls.instance.Model = KeyedVectors.load_word2vec_format(path, binary=True)
            else:
                cls.instance.Model = KeyedVectors.load_word2vec_format(path, binary=False)
        return cls.instance

    def get_vec(self, word):
        return self.instance.Model[word]

    def find_most_similar_words(self, word):
        self.instance.Model.most_similar(word)

    def get_similarity(self, word1, word2):
        self.instance.Model.similarity(word1, word2)

    def get_similarity_sentence(self, sentence1, sentence2):
        self.instance.Model.wmdistance(sentence1, sentence2)

    def get_weight_matrix(self, article):
        vocabulary_size = len(article)
        embedding_matrix = np.zeros((vocabulary_size, self.instance.Model.vector_size), dtype=np.double)
        index = 0
        for word in article:
            try:
                embedding_matrix[index] = self.instance.Model.get_vector(word)
            except KeyError:
                print(f"{word} is not found.")
                continue
            index += 1
        return embedding_matrix

    def get_weight_matrix_all(self, article, wiki=None, wiki_multiply_factors=0, tweet=None, tweet_multiply_factors=0):
        vocabulary_size = len(article)
        vector_size = self.instance.Model.vector_size + wiki_multiply_factors + tweet_multiply_factors
        embedding_matrix = np.zeros((vocabulary_size, vector_size), dtype=np.double)
        for index in range(vocabulary_size):
            word = article[index]
            embedding_vector = WordEmbedding.Words.get(word)
            if embedding_vector is not None:
                embedding_matrix[index] = embedding_vector
                if wiki is not None:
                    wiki_array = np.full(wiki_multiply_factors, wiki / 100)
                    embedding_matrix[index] = np.append(embedding_vector, wiki_array)
                if tweet is not None:
                    tweet_array = np.full(wiki_multiply_factors, tweet)
                    embedding_matrix[index] = np.append(embedding_vector, tweet_array)
        return embedding_matrix

    @staticmethod
    def convert_glove_word2vec(glove_path, dest_path):
        glove_file = datapath(glove_path)
        tmp_file = get_tmpfile(dest_path)
        _ = glove2word2vec(glove_file, tmp_file)

