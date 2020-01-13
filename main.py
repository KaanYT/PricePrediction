import os
import platform
import argparse
import traceback

from Managers.ConfigManager import Config

from Archive.Wiki.WikiRecorder import WikiRecorder
from Archive.News.Organizer.NewsOrganizer import NewsOrganizer
from Archive.Market.FinancialDataCollector import FDC

from Predictor.NewsDnnGeneral.NewsDnnGeneralMain import NewsDnnGeneralMain
from Predictor.NewsCnn.NewsCnnMain import NewsDnnGeneralMain as NewsCnnMain

from WWW.WebManager import WebManager

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
    parser.add_argument("-o", "--organize", help="Run news organizer. Pre-Process news to new database collection. "
                                                 "Settings can be accessible from config.json", action="store_true")
    parser.add_argument('-v', '--version', action='version', help="Show program version and exit",
                        version='Program Version is 0.1')
    parser.add_argument("-w", "--wiki", help="Run wiki recorder. Record Wikipedia pages to database collection.",
                        action="store_true")
    parser.add_argument("-n", "--news", help="Run News DNN to predict possible stock price.", metavar='general')
    parser.add_argument("-f", "--fdc", help="Run Financial Data Collector.", action="store_true")
    parser.add_argument("-www", "--webservice", help="This is a web service with default startup page. "
                                                     "You can edit news' metadata.", action="store_true")
    # Read Arguments
    return parser.parse_args()


def get_news_type(dnn_type):
    if dnn_type == "CNN":
        return NewsCnnMain()
    elif dnn_type == "RNN":
        return NewsDnnGeneralMain()
    else:  # Default RNN
        LoggerHelper.error("DNN type is not found. Default RNN (NewsDnnGeneralMain) is used.")
        return NewsDnnGeneralMain()


def main():
    # Load Config
    load_config()
    # Load arg
    args = load_arg()

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

    if args.news is not None:
        LoggerHelper.info("Starting Stock Prediction Mode...")
        news_dnn = get_news_type(args.news)
        news_dnn.train(print_every=int(Config.training.print_every))
        news_dnn.test()
        LoggerHelper.info("News Stock Prediction is ended.")
        # WordEmbedding(path=Config.word_embedding.path)
        # news_dnn = NewsDnnMain(epochs=int(Config.training.epochs),
                                # batch_size=int(Config.training.batch_size),
                                # seq_length=int(Config.training.sequence_length),
                                # lr=float(Config.training.lr))
    if args.webservice:
        web_manager = WebManager()
        web_manager.add_static_files()
        web_manager.add_news_root()
        web_manager.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as exception:
        LoggerHelper.error("Ex: " + str(exception))
        LoggerHelper.error(traceback.format_exc())
    exit()
