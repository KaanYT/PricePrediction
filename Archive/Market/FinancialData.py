

class FinancialData:
    FD_Name = "FD"
    FD_Key = "Key"
    FD_Open = 0.0
    FD_High = 0.0
    FD_Low = 0.0
    FD_Close = 0.0
    FD_Volume = 0.0
    FD_Trade = 0
    FD_AveragePrice = 0.0

    def __init__(self, fd_name, fd_key, fd_date, fd_open, fd_high, fd_low, fd_close,
                 fd_volume=-1, fd_number_of_trades=-1, fd_average_price=-1):
        self.FD_Name = fd_name
        self.FD_Key = fd_key
        self.FD_Date = fd_date
        self.FD_Open = fd_open
        self.FD_High = fd_high
        self.FD_Low = fd_low
        self.FD_Close = fd_close
        self.FD_Volume = fd_volume
        self.FD_Trade_Count = fd_number_of_trades
        self.FD_Average_Price = fd_average_price

    def add(self, fd_high, fd_low, fd_close):
        if float(fd_high) > float(self.FD_High):
            self.FD_High = fd_high
        if float(fd_low) < float(self.FD_Low):
            self.FD_Low = fd_low
        self.FD_Close = fd_close

    def __str__(self):
        return str(self.FD_Date) + " | " + self.FD_Name + "-" + self.FD_Open + "-" + self.FD_High + "-" + self.FD_Low + "-" + self.FD_Close + " >> " + str((float(self.FD_High)+float(self.FD_Low))/2)

    def get_currency(self):  # 1 - Currency
        return {
            'Name': self.FD_Name,
            'Key': self.FD_Key,
            'Date': self.FD_Date,
            'Open': self.FD_Open,
            'High': self.FD_High,
            'Low': self.FD_Low,
            'Close': self.FD_Close
        }

    def get_product(self):  # 2 - Product
        return {
            'Name': self.FD_Name,
            'Key': self.FD_Key,
            'Date': self.FD_Date,
            'Open': self.FD_Open,
            'High': self.FD_High,
            'Low': self.FD_Low,
            'Close': self.FD_Close
        }

    def get_stock(self):  # 3 - Stock
        return {
            'Name': self.FD_Name,
            'Key': self.FD_Key,
            'Date': self.FD_Date,
            'Open': self.FD_Open,
            'High': self.FD_High,
            'Low': self.FD_Low,
            'Close': self.FD_Close,
            'Volume': self.FD_Volume,
            'TradeCount': self.FD_Trade,
            'AveragePrice': self.FD_Average_Price
        }

    def get_index(self):  # 4 - Index
        return {
            'Name': self.FD_Name,
            'Key': self.FD_Key,
            'Date': self.FD_Date,
            'Open': self.FD_Open,
            'High': self.FD_High,
            'Low': self.FD_Low,
            'Close': self.FD_Close
        }
