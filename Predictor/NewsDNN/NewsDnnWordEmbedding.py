import numpy as np
from scipy import spatial
from Managers.LogManager.Log import Logger


class NewsDnnWordEmbedding(object):

    def __init__(self, path=None, vector_size=100):
        self.words = {}
        self.vector_size = vector_size
        if path is None:
            self.path = 'glove.6B.100d.txt'
        else:
            self.path = path
        self.__read_embeddings()

    def __read_embeddings(self):
        self.words = {}
        with open(self.path, 'r', encoding="utf-8") as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], dtype=np.float32)
                self.words[word] = vector

    def vec(self, w):
        return self.words[w]

    def find_closest_embeddings(self, embedding):
        return sorted(self.words.keys(),
                      key=lambda word: spatial.distance.cosine(self.words[word], embedding))

    def cosine_distance_word_embedding(self, s1, s2):
        vector_1 = np.mean(self.get_vector_list(s1), axis=0)
        vector_2 = np.mean(self.get_vector_list(s2), axis=0)
        cosine = spatial.distance.cosine(vector_1, vector_2)
        print('Word Embedding method with a cosine distance asses that our two sentences are similar to',
              round((1 - cosine) * 100, 2), '%')

    def get_vector_list(self, paragraph):
        word_to_vector_list = []
        for word in paragraph:
            try:
                word_to_vector_list.append(self.vec(word))
            except:
                Logger().get_logger().error('Get Vector List - Word Not Found', exc_info=False)
        return word_to_vector_list

    def _similarity_query(self, word_vec, number):
        words_matrix = self.words.values()
        dst = (np.dot(words_matrix, word_vec)
               / np.linalg.norm(words_matrix, axis=1)
               / np.linalg.norm(word_vec))
        word_ids = np.argsort(-dst)

        return [(self.words[x].name, dst[x]) for x in word_ids[:number]
                if x in self.words]
    # return [(self.inverse_dictionary[x], dst[x]) for x in word_ids[:number]
    #            if x in self.inverse_dictionary]
    # https://github.com/maciejkula/glove-python/blob/749494290fdfd24379dcc2e244c583ee61808634/glove/glove.py#L273
    # https://stats.stackexchange.com/questions/242863/how-does-python-glove-compute-most-similar

    def get_weight_matrix(self, article):
        vocabulary_size = len(article)
        embedding_matrix = np.zeros((vocabulary_size, self.vector_size), dtype=np.double)
        for index in range(vocabulary_size):
            word = article[index]
            embedding_vector = self.words.get(word)
            if embedding_vector is not None:
                embedding_matrix[index] = embedding_vector
        return embedding_matrix
