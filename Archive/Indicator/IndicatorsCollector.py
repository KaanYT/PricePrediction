import os
import re
import csv
import ntpath
import zipfile
import traceback

from pymongo import IndexModel
from Helper.DateHelper import DateHelper
from Managers.LogManager.Log import Logger
from Managers.DatabaseManager.MongoDB import Mongo
from Managers.ConfigManager import Config

from Archive.Indicator.IndicatorBase import IndicatorsBase
from Archive.Indicator.IndicatorInfo import IndicatorsInfo
from Archive.Indicator.Model.InfoModel import InfoModel


class IndicatorsCollector(IndicatorsBase):

    def __init__(self):
        super().__init__()
        self.path = self.config["file"]["csv_path"]
        self.info = self.config["file"]["csv_info_text"]
        self.collection = Mongo().create_collection(self.config["db"]["name"], IndicatorsCollector.get_index_models())

    def collect(self):
        self.collect_from(self.path, self.info)

    def collect_from_zip(self):
        path = self.config["file"]["csv_zips"]
        for file in os.listdir(path):
            if file.endswith(".zip"):
                extract_location = self.extract_zip(os.path.join(path, file))
                info_file_path = os.path.join(extract_location, self.config["file"]["zip_info_file_name"])
                csv_file_path = os.path.join(extract_location, "data")
                print(info_file_path)
                print(csv_file_path)
                self.collect_from(csv_file_path, info_file_path)
                break

    def collect_from(self, file_path, info_path):
        # Get File Information
        indicator = IndicatorsInfo()
        indicator.read_file_info(path=info_path)
        print(indicator.file_list)
        # Get File Data
        for root, dirs, files in os.walk(file_path):
            path = root.split(os.sep)
            for file in files:
                if file.endswith(".csv"):
                    if file in indicator.file_list:
                        file_info = indicator.file_list[file]  # Get File Info
                        file_path = os.path.join(root, file)
                        self.extract_financial_indicator(file_path, file_info, self.collection)

    @staticmethod
    def extract_zip(file):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            location = os.path.join(os.path.expanduser('~'), 'Downloads', 'IndicatorOut', 'Zip')
            zip_ref.extractall(location)
        file = re.sub('\.zip$', '', ntpath.basename(file))
        return os.path.join(location, file)

    @staticmethod
    def extract_financial_indicator(csv_file, file_info:InfoModel, collection):
        name = os.path.splitext(ntpath.basename(csv_file))[0]
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                if len(row) < 2 or row[0] == "DATE":  # Check Data
                    continue
                try:
                    collection.insert({
                        "title": file_info.Title,
                        "ShortName": name,
                        "date": DateHelper.str2date(row[0]),
                        "value": float(row[1]),
                        "country": file_info.Country,
                        "country_code": file_info.CountryCode,
                        "unit": file_info.Units,
                        "frequency": file_info.Frequency,
                        "seasonal_adjustment": file_info.SeasonalAdjustment,
                        "last_update": DateHelper.str2date(file_info.LastUpdated),
                    })
                except Exception as exception:
                    Logger().get_logger().error(type(exception).__name__, exc_info=True)
                    traceback.print_exc()
                    print(row[1])
                    print(row[0])
                    print(file_info.Title)

    @staticmethod
    def get_index_models():
        return [IndexModel("title", name="index_title"),
                IndexModel("date", name="index_date"),
                IndexModel("country", name="index_country"),
                IndexModel("seasonal_adjustment", name="index_sa"),
                IndexModel("country_code", name="index_country_code")]


if __name__ == "__main__":
    try:
        Config.add_config_ini('/Users/kaaneksen/Documents/2-Project/GitHub/MScThesis/initialization/main.ini')
        ind = IndicatorsCollector()
        ind.collect_from_zip()
    except Exception as exception:
        print(exception)
        traceback.print_exc()
    exit()
