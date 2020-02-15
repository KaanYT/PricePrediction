import traceback
import ntpath
import re
import os


from Archive.Indicator.IndicatorBase import IndicatorsBase
from Archive.Indicator.Model.InfoModel import InfoModel


class IndicatorsInfo(IndicatorsBase):

    def __init__(self):
        super().__init__()
        self.country_list = ['Virgin Islands of the United States', 'United Republic of Tanzania', 'United Kingdom', 'United Arab Emirates', 'Countries with Fragile and Conflict Affected Situations', 'Developing Countries in Middle East and North Africa', 'Developing Countries in Latin America and Caribbean', 'Commonwealth of the Northern Mariana Islands', 'Developing Countries in Europe and Central Asia', 'Developing Countries in East Asia and Pacific', 'Developing Countries in Sub-Saharan Africa', 'Yugoslav Republic of Macedonia', 'Association of Southeast Asian Nations', 'Democratic Republic of Timor-Leste', 'Asian Newly Industrialized Countries', 'Democratic Republic of the Congo', "Lao People's Democratic Republic", 'Bolivarian Republic of Venezuela', 'Islamic Republic of Afghanistan', 'Plurinational State of Bolivia', 'Federated States of Micronesia', 'Occupied Palestinian Territory', 'Democratic Republic of Timor-Leste', 'OECD and Non-member Economies', 'Collectivity of Saint Martin', 'Saint Vincent and the Grenadines', "Lao People's Democratic Republic", 'Bolivarian Republic of Venezuela', 'Heavily Indebted Poor Countries', 'Low and Middle Income Countries', 'St. Vincent and the Grenadines', 'Central Europe and the Baltics', 'High Income non-OECD Countries', 'Federated States of Micronesia', "Republic of Cote d'Ivoire", 'Lower Middle Income Countries', 'Upper Middle Income Countries', 'Emerging Markets (aggregate)', 'Middle East and North Africa', 'Central African Republic', 'Islamic Republic of Iran', 'International organisations', 'International Organisations', 'Latin America and Caribbean', 'Pacific Island Small States', 'Republic of South Sudan', 'Republic of the Gambia', 'High Income OECD Countries', 'Total Reporting Countries', 'Republic of the Congo', 'Least Developed Countries', 'Industrialized Countries', 'Turks and Caicos Islands', 'Syrian Arab Republic', 'Islamic Republic of Iran', 'Central African Republic', 'Southeast Asian Nations', 'Republic of Moldova', 'Middle Income Countries', 'West Bank and Gaza', 'Africa and Middle East', 'Bosnia and Herzegovina', 'Caribbean Small States', 'Dominican Republic', 'Libyan Arab Jamahiriya', 'High Income Countries', 'Sao Tome and Principe', 'Republic of Yemen', 'Saint Kitts and Nevis', 'Syrian Arab Republic', 'Developing countries', 'Low Income Countries', 'St. Kitts and Nevis', 'Developed countries', 'OECD Total Area', 'Antigua and Barbuda', 'Channel Islands', 'Kyrgyz Republic', 'Solomon Islands', 'Trinidad and Tobago', 'Republic of Moldova', 'U.S. Virgin Islands', 'Emerging Economies', 'Advanced Economies', 'Sub-Saharan Africa', 'Group of Seven', 'European Union', 'Other Small States', 'Russian Federation', 'Dominican Republic', 'Skopje, Macedonia', 'Brunei Darussalam', 'Equatorial Guinea', 'Republic of Korea', 'Major 5 Asia', 'Emerging Markets', 'Offshore Centres', 'Asia and Pacific', 'Papua New Guinea', 'French Polynesia', 'Marshall Islands', 'OECD Europe', 'Philippines', 'Solomon Islands', 'Slovak Republic', 'Macedonia, FYR', 'Chinese Taipei','Total Area', 'Arab World', 'Kyrgyz Republic', 'European Union', 'Cayman Islands', 'Latin America', 'G20 Economies', 'All countries', 'Euro Area', 'Guinea-Bissau', 'New Caledonia', "Cote d'Ivoire", 'Faroe Islands', 'Liechtenstein', 'Sint Maarten', 'Non-OECD', 'Burkina Faso', 'OECD Members', 'Saudi Arabia', 'Sierra Leone', 'Small States', 'Turkmenistan', 'South Africa', 'Pacific Rim', 'Bahamas', 'New Zealand', 'Puerto Rico', 'El Salvador', 'Ukraine', 'Switzerland', 'Netherlands', 'Afghanistan', 'Isle of Man', 'Saint Lucia', 'Philippines', 'St. Martin', 'Azerbaijan', 'Bangladesh', 'Cape Verde', 'Costa Rica', 'Kazakhstan', 'Madagascar', 'Montenegro', 'Mozambique', 'Mauritania', 'South Asia', 'Seychelles', 'Tajikistan', 'Uzbekistan', 'Luxembourg', 'Kyrgyzstan', 'United States', 'San Marino', 'Gibraltar', 'Greenland', 'Macau SAR', 'Venezuela', 'Argentina', 'Guatemala', 'Hong Kong', 'St. Lucia', 'Sri Lanka', 'Mauritius', 'Nicaragua', 'Sudan', 'Singapore', 'Swaziland', 'Euro Area', 'Lithuania', 'Australia', 'Indonesia', 'Barbados', 'Botswana', 'Cameroon', 'Colombia', 'Djibouti', 'Ethiopia', 'Honduras', 'Cambodia', 'Kiribati', 'Maldives', 'Mongolia', 'Malaysia', 'Pakistan', 'Paraguay', 'Suriname', 'Thailand', 'Viet Nam', 'Zimbabwe', 'Bulgaria', 'Portugal', 'Dominica', 'Slovenia', 'Slovakia', 'Lao PDR', 'Bolivia', 'Moldova', 'Surinam', 'Vietnam', 'Albania', 'Armenia', 'Burundi', 'Bahrain', 'Belarus', 'Comoros', 'Curacao', 'Algeria', 'Ecuador', 'Eritrea', 'Georgia', 'Grenada', 'Jamaica', 'Lebanon', 'Liberia', 'Lesotho', 'Morocco', 'Myanmar', 'Namibia', 'Nigeria', 'Senegal', 'Somalia', 'Tunisia', 'Uruguay', 'Vanuatu', 'Austria', 'Belgium', 'Germany', 'Denmark', 'Estonia', 'Finland', 'Croatia', 'Hungary', 'Ireland', 'Iceland', 'Romania', 'Andorra', 'Bermuda', 'Bahamas', 'Ukraine', 'Europe', 'Russia', 'Angola', 'Belize', 'Bhutan', 'Guinea', 'Guyana', 'Jordan', 'Kosovo', 'Kuwait', 'Malawi', 'Panama', 'Rwanda', 'Serbia', 'Uganda', 'Zambia', 'Cyprus', 'France', 'Greece', 'Latvia', 'Norway', 'Poland', 'Canada', 'Brazil', 'Israel', 'Mexico', 'Sweden', 'Gambia', 'Monaco', 'Tuvalu', 'Turkey', 'Aruba', 'Nauru', 'Benin', 'Egypt', 'Gabon', 'Ghana', 'Haiti', 'Kenya', 'Macao', 'Niger', 'Nepal', 'Qatar', 'Tonga', 'World', 'Samoa', 'Czech', 'Spain', 'Italy', 'Malta', 'Chile', 'China', 'Japan', 'India', 'Korea', 'Congo', 'Palau', 'Sudan', 'Yemen', 'Iran', 'Libya', 'Cuba', 'Fiji', 'Guam', 'Iraq', 'Mali', 'Oman', 'Peru', 'Chad', 'Togo', 'OECD']
        self.file_list = {}

    def read_file_info(self, path=None):
        if path is None:
            path = self.config["file"]["csv_info_text"]
        with open(path, encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                array = line.split(";")
                length = len(array)
                if length > 5:
                    if length == 6:
                        info = InfoModel(array[0], array[1], array[2], array[3], array[4], array[5])
                    if length == 7:
                        info = InfoModel(array[0], array[1] + array[2], array[3], array[4], array[5], array[6])
                    if "(DISCONTINUED)" in info.Title:
                        continue
                    if "Estimate" in info.Title:
                        info.IsEstimate = True
                    res = self.string_contains_country(info.Title)
                    if res is None:
                        print(info.Title)
                    else:
                        info.set_country(res)
                    self.file_list[info.FileName] = info
                else:
                    print(array.__len__())

    def string_contains_country(self, full_string):
        for country in self.country_list:
            if re.search(country, full_string, re.IGNORECASE):
                return country
        else:
            return None

if __name__ == "__main__":
    try:
        ind = IndicatorsInfo()
        #ind.read_file_info()
        location = os.path.join(os.path.expanduser('~'), 'Downloads', 'IndicatorOut', 'Zip')
        print(location)
    except Exception as exception:
        print(exception)
        traceback.print_exc()
    exit()
