import pandas_ta as ta

from data_manager import DataManager

class StrategyManager:

    def __init__(self, name: str, ticker_api:str, ticker_data:str, indicators:dict, interval:str, period:str, start_date, end_date):
        self.name = name
        self.ticker = ticker_api
        self.indicators = indicators
        self.dm = DataManager(ticker_data, indicators, interval, period, 30, start_date, end_date)

        self.position_open = False
        self.position_quantity = 0


    def check_entry(self):
        """
        Right now simple EMA cross 10 25
        """
        entry_check = False
        cross_sequence = list(ta.cross(self.dm.data["EMA_10"], self.dm.data["EMA_25"], above=True, equal=False))
        if cross_sequence[-2] == 1 and not self.position_open:
            entry_check = True
        
        return entry_check

    def check_exit(self):
        """
        Right now simple EMA cross 10 25
        """
        exit_check = False
        if self.position_open:
            cross_sequence = list(ta.cross(self.dm.data["EMA_10"], self.dm.data["EMA_25"], above=False, equal=False))
            if cross_sequence[-2] == 1:
                exit_check = True

        return exit_check
    
    def buy_position(self, money):
        """
        Buys in the position
        """
        quantity = money/self.dm.data["Close"].iloc[-1]
        quantity = round(quantity, 4)
        self.position_quantity = quantity
        self.position_open = True
        return 0


    def sell_position(self):
        """
        Sells in the position
        """
        self.position_open = False
        selled_quantity = self.position_quantity * self.dm.data["Close"].iloc[-1]
        self.position_quantity = 0
        print(selled_quantity)
        return selled_quantity

    
    def check_strategy(self, money):
        """
        Checks parts of the strategy.
        """
        if self.check_entry():
            #print("entry")
            return self.buy_position(money)
            

        if self.check_exit():
            #print("exit")
            return self.sell_position()

        return money
            

    def update_data(self):
        return self.dm.update_data()

"""
{
    "name": "Nombre",
    "ticker_api": "ticker",
    "ticker_data": "ticker"
    "indicators": {}
    "interval": "1m"
    "period": "1D"
    "start_date":
    "end_date":
}
"""