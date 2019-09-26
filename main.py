import os
from Archive.News.NewsOrganizer import NewsOrganizer
from Predictor.LstmTA.LSTMTechnicalAnalysis import LstmTechnicalAnalysis
from Managers.ConfigManager import Config
from Predictor.LstmTA.NewArchitecture.TaMain import TaMain


def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    Config.add_config_ini('%s/main.ini' % pwd)


def main():
    print("Loading Config...")
    load_config()
    print("Loading is loaded. Loading DatabaseManager...")
    #collector = NewsOrganizer()
    ta = TaMain(5, 5, 10)
    ta.train(epochs=10, batch_size=5, seq_length=10)
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
