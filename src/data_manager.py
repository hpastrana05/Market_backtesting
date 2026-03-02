import yfinance as yf
import datetime as dt
import pandas as pd
import pandas_ta as ta

class DataManager:
    def __init__(self, ticker, indicators, interval="1m", period="max", data_window=30, start_date=None, end_date=None):
        self.ticker = ticker
        self.indicators = indicators
        self.interval = interval
        self.period = period
        self.data_window = data_window

        self.now = dt.datetime.now()
        self.filename = f"{ticker}_{period}_{interval}.csv"
        self.total_data = self.open_data()
        self.update_indicators()

        if start_date and end_date:
            self.total_data.set_index('Date', inplace=True)
            self.total_backtest_data = self.total_data.loc[start_date:end_date].copy()
            self.total_data = self.total_data.reset_index()
        else:
            self.total_backtest_data=self.total_data
        self.current_index = self.data_window
        # Inicializamos self.data con el primer bloque de datos
        self.data = self.total_backtest_data.iloc[:self.current_index].copy()

        

    def open_data(self):
        """
        This function will try to open the data of the ticker.
        """
        try:
            data = pd.read_csv(f"src/data/{self.filename}")
            #print("opened")
        except:
            #print("downloaded")
            data = self.download_data()
            
        data.set_index('Date', inplace=True)
        data.sort_index()
        data = data.reset_index()

        return data
        

    def download_data(self):
        """
        This function will download and save the data taking into account this:
        1m	                   ->   7 days
        2m, 5m, 15m, 30m, 90m  ->   60 days
        1h	                   ->   2 years
        1d, 1wk, 1mo           ->   MAX
        """
        ticker = self.ticker
        period = self.period
        interval = self.interval

        data = yf.download(ticker, period=period, interval=interval, progress=False)

        if interval == "1m":
            period = "7D"
        elif interval in ["2m", "5m", "15m", "30m", "90m"]:
            period = "60D"
        elif interval == "1h":
            period = "2y"
        else: period = "max"

        if not data.empty:
            self.filename = f"{ticker}_{period}_{interval}.csv"

            data.columns = data.columns.get_level_values(0)
            data = data.reset_index()

            data.to_csv(f'src/data/{self.filename}', index=False)

        return data

    def fetch_data(self, ticker, interval, period):
        data = yf.download(ticker, interval=interval, period=period, progress=False)
        # Only one entry not two
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return pd.DataFrame(data)

    def update_data(self):
        """Will update the data and remove old data rows to maintain a fixed window size."""
        #print(self.current_index)
        #print(len(self.total_backtest_data))
        if self.current_index < len(self.total_backtest_data):
            # 1. Obtener la siguiente fila
            next_row = self.total_backtest_data.iloc[[self.current_index]]
            
            # 2. Concatenar a self.data
            self.data = pd.concat([self.data, next_row], ignore_index=True)
            
            # 3. Mantener el tamaño de la ventana (data_window)
            if len(self.data) > self.data_window:
                self.data = self.data.iloc[-self.data_window:].copy()
            
            # 4. Incrementar puntero para la próxima llamada
            self.current_index += 1
            
            # print(f"Dato actualizado. Nueva fecha: {self.data.iloc[-1]['Date']}")
            return False
        else:
            return True
        
    
    def update_indicators(self):
        """Add technical indicators to the data."""
        if self.indicators is None: return

        for name, values in self.indicators.items():
            for value in values:
                if name == "EMA":               
                    self.total_data[f"EMA_{value}"] = ta.ema(self.total_data["Close"], length=value)
                elif name == "RSI":
                    self.total_data[f"RSI_{value}"] = ta.rsi(self.total_data["Close"], length=value)
                elif name == "SMA":
                    self.total_data[f"SMA_{value}"] = ta.sma(self.total_data["Close"], length=value)
                elif name == "WMA":
                    self.total_data[f"WMA_{value}"] = ta.wma(self.total_data["Close"], length=value)
                elif name == "BBands":
                    bbands = ta.bbands(self.total_data["Close"], length=value[0], std=value[1])
                    self.total_data[f'BBands_{value}'] = bbands
                elif name == "EMA_CROSS":
                    self.total_data[f"EMA_CROSS_{value}"] = ta.cross(self.data[f"EMA_{value[0]}"], self.total_data[f"EMA_{value[1]}"],above=True, equal=False)
'''
indicators = {
    "EMA": [10, 20],
    "RSI": [14],
    "SMA": [50],
    "WMA": [30],
    "BBands": [(20, 2)]
}
dm = DataManager("AAPL", indicators, "1m", "1D")

print(dm.data.columns)
print(dm.data.tail())

'''
'''
indicators = {
    "EMA": [10, 20],
}

dm = DataManager('AAPL', indicators, "1D", "max",30,"2020-01-01","2024-01-01")
#print(dm.data.tail())

'''