import os
import platform
import argparse
import traceback

from Managers.ConfigManager import Config

from Archive.Wiki.WikiRecorder import WikiRecorder
from Archive.News.Organizer.NewsOrganizer import NewsOrganizer
from Archive.Market.FinancialDataCollector import FDC
from Archive.Indicator.IndicatorsCollector import IndicatorsCollector
from Archive.Statistics.Statistics import Statistics

from Test.Transformers.TransformersTest import TransformersTest

from Predictor.NewsDnnGeneral.NewsDnnGeneralMain import NewsDnnGeneralMain
from Predictor.NewsCnn.NewsCnnMain import NewsDnnGeneralMain as NewsCnnMain
from Predictor.NewsCategorization.NewsCateMain import NewsCateMain
from Predictor.PriceRNN.PriceRnnMain import PriceRnnMain
from Predictor.LstmTA.TaMain import TaMain

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
    parser.add_argument("-i", "--ind", help="Run Indicators Collector recorder. Record various resources to database "
                                            "collection which contains economical information such as employment.",
                        metavar='zip')
    parser.add_argument("-n", "--news", help="Run News DNN to predict possible stock price.", metavar='general')
    parser.add_argument("-f", "--fdc", help="Run Financial Data Collector.", action="store_true")
    parser.add_argument("-www", "--webservice", help="This is a web service with default startup page. "
                                                     "You can edit news' metadata.", action="store_true")
    parser.add_argument("-s", "--statistics", help="This is statistic collector. Give information about "
                                                   "collection statistic.", action="store_true")
    parser.add_argument("-t", "--test", help="Run Financial Data Collector.", action="store_true")

    # Read Arguments
    return parser.parse_args()


def get_news_type(dnn_type):
    dnn_type = dnn_type.strip()
    if dnn_type == "CNN":
        return NewsCnnMain()
    elif dnn_type == "RNN":
        return NewsDnnGeneralMain()
    elif dnn_type == "TA":
        return TaMain()
    elif dnn_type == "PriceRNN":
        return PriceRnnMain()
    elif dnn_type == "CATE":
        return NewsCateMain()
    else:  # Default RNN
        LoggerHelper.error("DNN type (" + dnn_type + ") is not found. Default RNN (NewsDnnGeneralMain) is used.")
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
        collector.dnn_organizer_for_dnn_filtered_news()
        LoggerHelper.info("News Organizer Mode is ended.")

    if args.ind:
        LoggerHelper.info("Starting Indicators Collector Mode...")
        ind_collector = IndicatorsCollector()
        if args.ind == "zip":
            ind_collector.collect_from_zip()
        else:
            ind_collector.collect()
        LoggerHelper.info("Indicators Collector Mode is ended.")

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
                                # lr=float(Config.training.lr))3
    if args.statistics:
        LoggerHelper.info("Starting Statistic Collection Mode...")
        Statistics().collect()
        LoggerHelper.info("Statistic Collection is ended...")

    if args.test:
        LoggerHelper.info("Starting Test Mode...")
        TransformersTest.sentiment_analysis_test()
        LoggerHelper.info("Test Mode is ended...")

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
