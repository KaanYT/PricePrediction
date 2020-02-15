import ntpath
import pycountry


class InfoModel(object):
    FileName = ""
    SeasonalAdjustment = ""
    Frequency = ""
    Title = ""
    Units = ""
    LastUpdated = ""
    IsEstimate = False
    Country = None
    CountryCode = None
    CountryHelper = {"Curacao": "Curaçao",
                     "Iran": "Iran, Islamic Republic of",
                     "Korea": "Korea, Democratic People's Republic of",
                     "Sint Maarten": "Sint Maarten (Dutch part)"}

    def __init__(self, file, title, units, frequency, seasonal_adjustment, last_updated):
        self.FileName = ntpath.basename(file.strip())
        self.Title = title.strip()
        self.Units = units.strip()
        self.Frequency = frequency.strip()
        self.SeasonalAdjustment = seasonal_adjustment.strip()
        self.LastUpdated = last_updated.strip()

    def set_country(self, country):
        try:
            if country in InfoModel.CountryHelper:
                country = InfoModel.CountryHelper[country]
            country_name = pycountry.countries.get(name=country)
            if country_name is None:
                country_list = pycountry.countries.search_fuzzy(country)
                if country_list is None:
                    print("Country Not Found! :" + country)
                    self.Country = country
                if len(country_list) == 1:
                    self.Country = country_list[0].name
                    self.CountryCode = country_list[0].alpha_3
                else:
                    print("Multiple Country" + country + " - " + str(len(country_list)))
                    print("Title:" + self.Title)
                    print(country_list)
            else:
                self.Country = country_name.name
                self.CountryCode = country_name.alpha_3
        except LookupError as exception:
            self.Country = country



    def __str__(self):
        return "File Name :%s, " \
               "Title: %s" \
               "Units: %s " \
               "Frequency: %s" \
               "SeasonalAdjustment: %s" \
               "LastUpdated: %s" % (self.FileName, self.Title, self.Units,
                                    self.Frequency, self.SeasonalAdjustment, self.LastUpdated)

    def json(self):
        return {
            "FileName": self.FileName,
            "Title": self.Title,
            "Units": self.Units,
            "Frequency": self.Frequency,
            "SeasonalAdjustment": self.SeasonalAdjustment,
            "LastUpdated": self.LastUpdated
        }

