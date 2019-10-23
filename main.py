import os
import json
import datetime

from Helper.Timer import Timer
from Managers.ConfigManager import Config
#from Archive.Market.FinancialDataCollector import FDC
from Archive.News.NewsOrganizer import NewsOrganizer
#from Predictor.NewsDNN.NewsDnnDataReader import NewsDnnDataReader
#from Predictor.NewsDNN.NewsDnnMain import NewsDnnMain
#from Helper.JsonDateHelper import DateTimeDecoder
from Archive.Wiki.WikiRecorder import WikiRecorder


from Helper.Timer import Timer
from Helper.WordEmbedding import WordEmbedding

def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    Config.add_config_ini('%s/main.ini' % pwd)

def main():
    timer = Timer()
    print("Loading Config...")
    load_config()
    print("Loading is loaded. Loading DatabaseManager...")
    #wiki = WikiRecorder()
    #wiki.collect_all()
    WordEmbedding(path="/Users/kaaneksen/Downloads/glove/glove.6B.100d.txt")
    collector = NewsOrganizer()
    collector.dnn_organizer_with_wiki_tweets()
    #page = Wikipedia.get_page("Starbucks")
    #print(page)
    #fdc  = FDC()
    #fdc.collect()
    #pwd = os.path.dirname(os.path.abspath(__file__))
    #config = json.load(open(pwd + '/Predictor/NewsDNN/config.json', 'r'), cls=DateTimeDecoder)["data"]
    #tst = NewsDnnDataReader(config, batch_size=10, sequence_length=100)
    #print(tst.get_train_count())
    count = 0
    ##newsdnn = NewsDnnMain(5, 10, 200)
    ##newsdnn.train()


    #tr = TweetRecorder()
    #tr.load_tweets()

    #ta = NewsDnnMain(5, 50, 10)
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
