import csv
import json

from datetime import datetime
from Logger.Log import Logger

from Archive.Market.FinancialDataType import FinancialDataType
from Archive.Market.FinancialDataLocation import FDLocations
from Archive.Market.FinancialData import FinancialData

from alpha_vantage.timeseries import TimeSeries  # Hourly values are only available for 2*3 weeks
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.techindicators import TechIndicators

from Database.MongoDB import Mongo
from ConfigManager import Config


class FDC(object):
    directory = "FDC_Files.json"

    def collect(self):
        self.local_collect()

    def local_collect(self):
        with open('Archive/Market/FDC_Files.json') as json_file:
            collection = json.load(json_file)
            print(collection)
            # For Each FX Collection (XAGUSD etc.)
            total = 0
            for key in collection:
                fx_info = collection[key]
                # For Each File In Collection
                for file in fx_info["Files"]:
                    directory = fx_info["Location"] + file
                    type = fx_info["Type"]
                    name = fx_info["Name"]
                    interval = fx_info["TimeInterval"]
                    if type is FinancialDataType.Currency.value:
                        FDC.parse_currency(key, directory, name)
                    if type is FinancialDataType.Product.value:
                        print(key)
                        #FDC.parse_product(key, directory, name, interval)
                    if type is FinancialDataType.Stock.value:
                        print(key)
                        #FDC.parse_stock(key, directory, name, interval)
                    if type is FinancialDataType.Index.value:
                        print(key)
                        #FDC.parse_index(key, directory, name, interval)
                    if type is FinancialDataType.IndexDateTime.value:
                        print(key)
                        #FDC.parse_index_datetime(key, directory, name, interval)
            print(f'Processed {total} lines.')

    @staticmethod
    def parse_currency(currency_key, directory, name):  # Type : 1 - Currency
        print("Currency")
        col = Mongo().create_collection("Currency")
        with open(directory) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            print(currency_key)
            hour = -1
            fd = None
            for row in csv_reader:
                if len(row) < 2:  # Check Data
                    continue
                date = datetime.strptime((row[0] + row[1]), "%Y%m%d%H:%M:%S")
                if hour != date.hour:
                    hour = date.hour
                    if fd is not None:
                        try:
                            col.insert(fd.get_currency())
                        except:
                            Logger().get_logger().error('Insert Error', exc_info=True)
                    fd = FinancialData(name, currency_key, date,
                                       row[FDLocations.Currency_Open.value],
                                       row[FDLocations.Currency_High.value],
                                       row[FDLocations.Currency_Low.value],
                                       row[FDLocations.Currency_Close.value])
                else:
                    fd.add(row[FDLocations.Currency_High.value],
                           row[FDLocations.Currency_Low.value],
                           row[FDLocations.Currency_Close.value])

    @staticmethod
    def parse_product(currency_key, directory, name, interval):  # Type : 2 - Product
        print("Product")
        col = Mongo().create_collection("Product")
        with open(directory) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            print(currency_key)
            hour = -1
            hour_count = 0
            fd = None
            for row in csv_reader:
                if len(row) < 2:  # Check Data
                    continue
                date = datetime.strptime((row[0] + row[1]), "%Y%m%d%H:%M:%S")
                if hour != date.hour:
                    hour = date.hour
                    hour_count = 0
                    if fd is not None:
                        print(fd)
                        try:
                            col.insert(fd.get_product())
                        except:
                            Logger().get_logger().error('Insert Error', exc_info=True)

                    fd = FinancialData(name, currency_key, date,
                                       row[FDLocations.Product_Open.value],
                                       row[FDLocations.Product_High.value],
                                       row[FDLocations.Product_Low.value],
                                       row[FDLocations.Product_Close.value])
                else:
                    fd.add(row[FDLocations.Currency_High.value],
                           row[FDLocations.Currency_Low.value],
                           row[FDLocations.Currency_Close.value])
                    hour_count += 1
                line_count += 1
            print(f'Processed {line_count} lines.')

    @staticmethod
    def parse_stock(currency_key, directory, name, interval):  # Type : 3 - Stock
        print("Stock")
        col = Mongo().create_collection("Stock")
        with open(directory) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            print(currency_key)
            for row in csv_reader:
                if len(row) < 2:  # Check Data
                    continue
                date = datetime.strptime(row[0], "%Y.%m.%d %H:%M:%S")
                if interval == 60:
                    fd = FinancialData(name, currency_key, date,
                                       row[FDLocations.Stock_Open.value],
                                       row[FDLocations.Stock_High.value],
                                       row[FDLocations.Stock_Low.value],
                                       row[FDLocations.Stock_Close.value],
                                       row[FDLocations.Stock_Volume.value],
                                       row[FDLocations.Stock_Trade.value],
                                       row[FDLocations.Stock_Avg.value])
                    col.insert(fd.get_stock())
                else:
                    print("Not Handled !!!")

    @staticmethod
    def parse_index(currency_key, directory, name, interval):  # Type : 4 - Index
        col = Mongo().create_collection("Index")
        with open(directory) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            print(currency_key)
            hour = -1
            hour_count = 0
            fd = None
            for row in csv_reader:
                if len(row) < 2:  # Check Data
                    continue
                date = datetime.strptime(row[0], "%Y.%m.%d %H:%M:%S")
                if hour != date.hour:
                    hour = date.hour
                    hour_count = 0
                    if fd is not None:
                        print(fd)
                        try:
                            col.insert(fd.get_index())
                        except:
                            Logger().get_logger().error('Insert Error', exc_info=True)

                    fd = FinancialData(name, currency_key, date,
                                       row[FDLocations.Index_Open.value],
                                       row[FDLocations.Index_High.value],
                                       row[FDLocations.Index_Low.value],
                                       row[FDLocations.Index_Close.value])
                else:
                    fd.add(row[FDLocations.Index_High.value],
                           row[FDLocations.Index_Low.value],
                           row[FDLocations.Index_Close.value])
                    hour_count += 1

    @staticmethod
    def parse_index_datetime(currency_key, directory, name, interval):  # Type : 4 - Index
        col = Mongo().create_collection("Index")
        with open(directory) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            print(currency_key)
            hour = -1
            hour_count = 0
            fd = None
            for row in csv_reader:
                if len(row) < 2:  # Check Data
                    continue
                date = datetime.strptime((row[0] + row[1]), "%Y%m%d%H:%M:%S")
                if hour != date.hour:
                    hour = date.hour
                    hour_count = 0
                    if fd is not None:
                        print(fd)
                        try:
                            col.insert(fd.get_index())
                        except:
                            Logger().get_logger().error('Insert Error', exc_info=True)
                    fd = FinancialData(name, currency_key, date,
                                       row[FDLocations.IndexDateTime_Open.value],
                                       row[FDLocations.IndexDateTime_High.value],
                                       row[FDLocations.IndexDateTime_Low.value],
                                       row[FDLocations.IndexDateTime_Close.value])
                else:
                    fd.add(row[FDLocations.IndexDateTime_High.value],
                           row[FDLocations.IndexDateTime_Low.value],
                           row[FDLocations.IndexDateTime_Close.value])
                    hour_count += 1
                line_count += 1
            print(f'Processed {line_count} lines.')

    @staticmethod
    def alpha_collect():
        ts = TimeSeries(key=Config.keys.alphaVantageApi, output_format='pandas')
        data, meta_data = ts.get_intraday(symbol='MSFT', interval='60min', outputsize='full')

    @staticmethod
    def alpha_collect_fx():
        cc = ForeignExchange(key=Config.keys.alphaVantageApi)
        data, meta_data = cc.get_currency_exchange_intraday(from_currency='BTC', to_currency='USD')

    @staticmethod
    def alpha_collect_crypto():
        cc = CryptoCurrencies(key=Config.keys.alphaVantageApi, output_format='pandas')
        data, meta_data = cc.get_digital_currency_intraday(symbol='INDEXSP', interval='60min', outputsize='full')

    @staticmethod
    def alpha_collect_technical_indicators():
        ti = TechIndicators(key='YOUR_API_KEY', output_format='pandas')
        data, meta_data = ti.get_ad(symbol='MSFT', interval='60min', time_period=60)



