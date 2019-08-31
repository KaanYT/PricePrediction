import os
from Archive.Market.FinancialDataCollector import FDC
from ConfigManager import Config


def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    Config.add_config_ini('%s/main.ini' % pwd)


def main():
    print("Loading Config...")
    load_config()
    print("Loading is loaded. Loading Database...")
    collector = FDC()
    collector.collect()


"""
    cnn_paper = newspaper.build('https://tradingeconomics.com/turkey/news')
    print(newspaper.popular_urls())
    for article in cnn_paper.articles:
        print(article.url)
"""

if __name__ == "__main__":
    main()
