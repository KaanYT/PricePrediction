import os
from Archive.Collector import AC
from ConfigManager import Config
import newspaper


def load_config():
    pwd = os.path.dirname(os.path.abspath(__file__))
    Config.add_config_ini('%s/main.ini' % pwd)


def main():
    print("Loading Config...")
    load_config()
    print("Loading is loaded. Loading Database...")
    collector = AC()
    collector.collect()


"""
    cnn_paper = newspaper.build('https://tradingeconomics.com/turkey/news')
    print(newspaper.popular_urls())
    for article in cnn_paper.articles:
        print(article.url)
"""

if __name__ == "__main__":
    main()
