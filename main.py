import os
import json
import platform
import datetime

from Helper.Timer import Timer
from Managers.ConfigManager import Config
#from Archive.Market.FinancialDataCollector import FDC
from Archive.News.NewsOrganizer import NewsOrganizer
#from Predictor.NewsDNN.NewsDnnWikiDataReader import NewsDnnWikiDataReader
from Predictor.NewsDNN.NewsDnnMain import NewsDnnMain
#from Helper.JsonDateHelper import DateTimeDecoder
from Archive.Wiki.WikiRecorder import WikiRecorder


from Helper.Timer import Timer
from Helper.WordEmbedding import WordEmbedding

def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    print(platform.system())
    if platform.system() == "Windows":
        Config.add_config_ini('%s\\initialization\\main_w.ini' % pwd)
    else:
        Config.add_config_ini('%s/initialization/main.ini' % pwd)

def main():
    timer = Timer()
    print("Loading Config...")
    load_config()
    print("Loading is loaded. Loading DatabaseManager...")
    #wiki = WikiRecorder()
    #wiki.collect_all()
    WordEmbedding(path=Config.word_embedding.path)
    collector = NewsOrganizer()
    collector.dnn_organizer_with_wiki_tweets()
    #page = Wikipedia.get_page("Starbucks")
    #print(page)
    #fdc  = FDC()
    #fdc.collect()
    #pwd = os.path.dirname(os.path.abspath(__file__))
    #config = json.load(open(pwd + '/Predictor/NewsDNN/config.json', 'r'), cls=DateTimeDecoder)["data"]
    #tst = NewsDnnWikiDataReader(config, batch_size=10, sequence_length=100)
    #print(tst.get_train_count())
    #newsdnn = NewsDnnMain(epochs=int(Config.training.epochs),
                          #batch_size=int(Config.training.batch_size),
                          #seq_length=int(Config.training.sequence_length),
                          #lr=float(Config.training.lr))
    #newsdnn.train(print_every=int(Config.training.print_every))
    #newsdnn.test()
    #newsdnn.load_model("saved_models\\25102019-175105-e5(FilteredNewsForDnn).pth")


    #tr = TweetRecorder()
    #tr.load_tweets()

    #ta = NewsDnnWikiMain(5, 50, 10)
    #ta.test()
    #ltsm = LstmTechnicalAnalysis()
    #ltsm.create_model()
    #collector.organize()


"""
    cnn_paper = newspaper.build('https://tradingeconomics.com/turkey/news')
    print(newspaper.popular_urls())
    for article in cnn_paper.articles:
        print(article.url)
"""

if __name__ == "__main__":
    main()
    exit()
