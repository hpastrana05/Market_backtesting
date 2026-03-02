from strategy_manager  import StrategyManager


class Backtesting:
    def __init__(self, strategy:dict, money:float=1000.0):
        self.money = money 
        self.strategy = StrategyManager(**strategy)
        

    def run_backtest(self):
        ended = False
        i=0
        while not ended:
            #print(i)
            ended = self.strategy.update_data()

            self.money = self.strategy.check_strategy(self.money)
            i +=1
        print(self.money)

strategy = {
    "name": "Nombre",
    "ticker_api": "AAPL",
    "ticker_data": "AAPL",
    "indicators": {
        "EMA": [10, 25]
    },
    "interval": "1D",
    "period": "max",
    "start_date": "2020-01-01",
    "end_date":"2024-01-01"
}

back = Backtesting(strategy, 1000)
back.run_backtest()