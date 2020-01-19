from Managers.DatabaseManager.MongoDB import Mongo

from Predictor.NewsDnnBase.NewsDnnBaseWordEmbedding import WordEmbedding


class WikiForecast(object):

    def __init__(self, word_embedding_path="/Users/kaaneksen/Downloads/glove/glove.6B.100d.txt"):
        self.embedding: WordEmbedding = WordEmbedding(word_embedding_path)

    def get_similarity(self, summery, title="Brent Crude"):
        wiki_page = self.get_wiki(title=title)
        return self.embedding.get_similarity_sentence(wiki_page["summary_p"], summery)

    @staticmethod
    def get_wiki(collection="Wiki", title="Brent Crude"):
        db = Mongo()
        query = {
            "title": title
        }
        fields = {"summary_p": 1, "_id": 0}
        return db.get_data_one(collection, query, fields)

