from enum import Enum


class FDLocations(Enum):
    Currency_Open = 2
    Currency_High = 3
    Currency_Low = 4
    Currency_Close = 5
    Currency_Unknown = 6  # Unknown Data - 479.0500017

    Product_Open = 2
    Product_High = 3
    Product_Low = 4
    Product_Close = 5
    Product_Unknown = 6  # Unknown Data - 0.00905

    Stock_Open = 1
    Stock_High = 2
    Stock_Low = 3
    Stock_Close = 4
    Stock_Volume = 5
    Stock_Trade = 6
    Stock_Avg = 7

    Index_Open = 1
    Index_High = 2
    Index_Low = 3
    Index_Close = 4
    Index_Unknown = 5  # Unknown Data - 0.070100002

    IndexDateTime_Open = 2
    IndexDateTime_High = 3
    IndexDateTime_Low = 4
    IndexDateTime_Close = 5
    IndexDateTime_Unknown = 6  # Unknown Data - 0.070100002
