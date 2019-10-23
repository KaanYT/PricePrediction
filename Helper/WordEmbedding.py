import numpy as np
import multiprocessing

from datetime import timedelta
from Helper.Timer import Timer
from Helper.WordPreProcessing import PreProcessing
from functools import partial
from scipy import spatial
from Managers.LogManager.Log import Logger
from Managers.DatabaseManager.MongoDB import Mongo


class WordEmbedding(object):

    Words={}

    def __init__(self, path=None, vector_size=100):
        self.timer = Timer()
        self.manager = multiprocessing.Manager()
        WordEmbedding.Words = self.manager.dict()
        self.vector_size = vector_size
        if path is None:
            self.path = 'glove.6B.100d.txt'
        else:
            self.path = path
        self.__read_embeddings()

    def __read_embeddings(self):
        WordEmbedding.Words = self.manager.dict()
        self.timer.start()
        with open(self.path, 'r', encoding="utf-8") as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = np.asarray(values[1:], dtype=np.float32)
                WordEmbedding.Words[word] = vector
        self.timer.stop()

    @staticmethod
    def vec(w):
        return WordEmbedding.Words[w]

    @staticmethod
    def find_closest_embeddings(embedding):
        return sorted(WordEmbedding.Words.keys(),
                      key=lambda word: spatial.distance.cosine(WordEmbedding.Words[word], embedding))

    @staticmethod
    def multi_cosine_distance_word_embedding(count, date, news_title):
        cpu_count = multiprocessing.cpu_count()
        p = multiprocessing.Pool(cpu_count)
        numbers = list()
        total = int(count / cpu_count)
        for a in range(cpu_count):
            if a == cpu_count - 1:
                info = {
                    "skip": total * a,
                    "to": (total + (count % cpu_count)),
                    "date": date,
                    "news_title": news_title
                }
                numbers.append(info)
            else:
                info = {
                    "skip": total * a,
                    "to": total,
                    "date": date,
                    "news_title": news_title
                }
                numbers.append(info)
        calculate_partial = partial(WordEmbedding.calculate_distance_for_tweet, input=input)
        result = p.map(calculate_partial, numbers)
        p.close()
        p.join()
        return sum(result)
        #p.map(mp_worker, data)

    @staticmethod
    def calculate_distance_for_tweet(info, input):
        skip = info["skip"]
        get = info["to"]
        date = info["date"]
        title = info["news_title"]
        db = Mongo(test=2)
        pre = PreProcessing()
        tweets = WordEmbedding.get_tweets_before_date(db, date).skip(skip).limit(get)
        tweetcount=0
        count = 0
        vector = WordEmbedding.get_vector_list(title)
        for tweet in tweets:
            tweetcount += 1
            try:
                cosine = WordEmbedding.cosine_distance_word_embedding_with_vector(vector, pre.preprocess(tweet["tweet_text"]))
                percentage = round((1 - cosine) * 100, 2)
            except Exception as exception:
                percentage = 0

            if percentage > 80:
                count += 1
                if tweet["tweet_user_verified"]:
                    count += 1
        db.close()
        return count

    @staticmethod
    def get_tweets_before_date(db, date, collection="Tweet", days=5):
        start = date - timedelta(days=days)
        end = date
        query = {
            "tweet_created_at":
                {
                    "$gte": start,
                    "$lt": end
                }
        }
        fields = {"tweet_text": 1, "tweet_user_fallowers_count": 1, "tweet_user_verified": 1, "tweet_created_at": 1,
                  "_id": 0}
        return db.get_data(collection, query, fields).sort([("tweet_created_at", 1)])

    @staticmethod
    def cosine_distance_word_embedding_with_vector(vector, s2):
        vector2 = WordEmbedding.get_vector_list(s2)
        if vector2 is np.NaN:
            return 0.001
        else:
            mean = np.mean(vector, axis=0)
            mean2 = np.mean(vector2, axis=0)
            cosine = spatial.distance.cosine(mean, mean2)
            return cosine

    @staticmethod
    def cosine_distance_word_embedding(s1, s2):
        try:
            vector_1 = np.mean(WordEmbedding.get_vector_list(s1), axis=0)
            vector_2 = np.mean(WordEmbedding.get_vector_list(s2), axis=0)
        except:
            return 0.001
        cosine = spatial.distance.cosine(vector_1, vector_2)
        return cosine

    @staticmethod
    def get_vector_list(paragraph):
        word_to_vector_list = []
        for word in paragraph:
            if word in WordEmbedding.Words:
                word_to_vector_list.append(WordEmbedding.vec(word))
        if len(word_to_vector_list) == 0:
            return np.NaN
        return word_to_vector_list

    def _similarity_query(self, word_vec, number):
        words_matrix = WordEmbedding.Words.values()
        dst = (np.dot(words_matrix, word_vec)
               / np.linalg.norm(words_matrix, axis=1)
               / np.linalg.norm(word_vec))
        word_ids = np.argsort(-dst)

        return [(WordEmbedding.Words[x].name, dst[x]) for x in word_ids[:number]
                if x in WordEmbedding.Words]
    # return [(self.inverse_dictionary[x], dst[x]) for x in word_ids[:number]
    #            if x in self.inverse_dictionary]
    # https://github.com/maciejkula/glove-python/blob/749494290fdfd24379dcc2e244c583ee61808634/glove/glove.py#L273
    # https://stats.stackexchange.com/questions/242863/how-does-python-glove-compute-most-similar

    def get_weight_matrix(self, article):
        vocabulary_size = len(article)
        embedding_matrix = np.zeros((vocabulary_size, self.vector_size), dtype=np.double)
        for index in range(vocabulary_size):
            word = article[index]
            embedding_vector = WordEmbedding.Words.get(word)
            if embedding_vector is not None:
                embedding_matrix[index] = embedding_vector
        return embedding_matrix
