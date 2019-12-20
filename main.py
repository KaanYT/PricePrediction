import os
import sys
import platform
import argparse

from Managers.ConfigManager import Config

from Archive.Wiki.WikiRecorder import WikiRecorder
from Archive.News.Organizer.NewsOrganizer import NewsOrganizer
from Archive.Market.FinancialDataCollector import FDC

from Predictor.NewsDnnGeneral.NewsDnnGeneralMain import NewsDnnGeneralMain

from Helper.LoggerHelper import LoggerHelper


def load_config():
    LoggerHelper.info("Loading Config...")
    pwd = os.path.dirname(os.path.abspath(__file__))
    if platform.system() == "Windows":
        Config.add_config_ini('%s\\initialization\\main_w.ini' % pwd)
    else:
        Config.add_config_ini('%s/initialization/main.ini' % pwd)
    LoggerHelper.info("Loading is loaded.")


def load_arg():
    # initiate the parser
    parser = argparse.ArgumentParser()

    # Add Argument
    parser.add_argument("--organize", "-o", help="Run News Organizer. Pre process news to new collection. "
                                                 "Settings can be accessible from config.json", action="store_true")
    parser.add_argument("-v", "--version", help="Show Program Version", action="store_true")
    parser.add_argument("-w", "--wiki", help="Run Wiki Recorder. Record Wikipedia pages to collection.")
    parser.add_argument("-n", "--news", help="Run News DNN to predict possible stock price. Types: general")
    parser.add_argument("-f", "--fdc", help="Run Financial Data Collector.", action="store_true")
    # Read Arguments
    return parser.parse_args()


def main():
    # Config Variables
    organize = False
    dnn_type = None
    # Load Config
    load_config()
    # Load arg
    args = load_arg()

    if args.version:
        LoggerHelper.info("Program Version is 0.1")
        sys.exit(0)

    if args.fdc:
        LoggerHelper.info("Starting Financial Data Collector Mode...")
        fdc = FDC()
        fdc.collect()
        LoggerHelper.info("Financial Data Collector Mode is ended.")

    if args.wiki:
        LoggerHelper.info("Starting Wikipedia Load Mode...")
        wiki = WikiRecorder()
        wiki.collect_all()
        LoggerHelper.info("Wikipedia Load Mode is ended.")

    if args.organize:
        LoggerHelper.info("Starting News Organizer Mode...")
        collector = NewsOrganizer()
        collector.dnn_organizer_with_wiki_tweets()
        LoggerHelper.info("News Organizer Mode is ended.")

    if args.news is not None:  # ToDo: Initialize based on dnn_type
        LoggerHelper.info("Starting Stock Prediction Mode...")
        news_dnn = NewsDnnGeneralMain()
        news_dnn.train(print_every=int(Config.training.print_every))
        news_dnn.test()
        LoggerHelper.info("News Stock Prediction is ended.")
        # WordEmbedding(path=Config.word_embedding.path)
        # news_dnn = NewsDnnMain(epochs=int(Config.training.epochs),
                                # batch_size=int(Config.training.batch_size),
                                # seq_length=int(Config.training.sequence_length),
                                # lr=float(Config.training.lr))


if __name__ == "__main__":
    main()
    exit()
