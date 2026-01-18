import pandas as pd


class DataManager:
    def __init__(self, data_path: str, name):
        self.name = name
        self.data = None
        self.path = f"./data/{self.name}.parquet"
        if data_path:
            self.load_data(data_path)



    def load_data(self, file_path: str):
        """Loads data from CSV (or other formats) into a pandas DataFrame."""
        try:
            # Load with timestamp parsing
            self.data = pd.read_csv(file_path)
            
            # Standardize column names (example mapping, expand as needed)
            # Assuming input has specific names, or we map them dynamically
            # For now, let's assume standard names or simple lowercase matching
            self.data.columns = [c.capitalize() for c in self.data.columns]
            
            if 'Timestamp' in self.data.columns:
                 self.data['Timestamp'] = pd.to_datetime(self.data['Timestamp'], unit='s')
                 self.data.set_index('Timestamp', inplace=True)
            elif 'Date' in self.data.columns:
                 self.data['Date'] = pd.to_datetime(self.data['Date'])
                 self.data.set_index('Date', inplace=True)

            # Ensure required columns exist
            required = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in self.data.columns for col in required):
                print(f"Warning: Missing one of {required} columns.")

            # Data Cleaning
            self.data.sort_index(inplace=True)
            self.data = self.data[~self.data.index.duplicated(keep='first')]
            self.data.fillna(method='ffill', inplace=True)
            
            print(f"Data loaded successfully from {file_path}")
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error loading data: {e}")
        
        return self.data
    


    def save_data(self):
        """Saves data to parquet."""
        try:
            self.data.to_parquet(self.path) # Index is preserved by default in Parquet
            print(f"Data saved successfully to {self.path}")
        except Exception as e:
            print(f"Error saving data: {e}")
        
        return self


    def get_data(self):
        if self.data is not None:
            return self.data
            
        try:
            self.data = pd.read_parquet(self.path)
            return self.data
        except FileNotFoundError:
             print(f"No existing data found at {self.path}")
             return None
    

    def add_indicators(self, indicators: list = None):
        """
        Adds technical indicators to the DataFrame.

        Args:
            indicators (list): List of dicts specifying indicators to add.
                               Example: [
                                   {'kind': 'sma', 'length': 20, 'col': 'Close'},
                                   {'kind': 'rsi', 'length': 14, 'col': 'Close'}
                               ]
        """
        if self.data is None:
            self.get_data()

        if indicators is None:
            return self

        for ind in indicators:
            kind = ind.get('kind', '').lower()
            col = ind.get('col', 'Close')
            length = ind.get('length', 14)
            name = ind.get('name', f"{kind}_{length}")

            if kind == 'sma':
                self.data[name] = self.data[col].rolling(window=length).mean()

            elif kind == 'ema':
                self.data[name] = self.data[col].ewm(span=length, adjust=False).mean()

            elif kind == 'rsi':
                delta = self.data[col].diff()
                gain = (delta.where(delta > 0, 0)).ewm(alpha=1/length, adjust=False).mean()
                loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/length, adjust=False).mean()
                rs = gain / loss
                self.data[name] = 100 - (100 / (1 + rs))

            elif kind == 'bb':
                std_dev = ind.get('std_dev', 2)
                self.data[f'{name}_mid'] = self.data[col].rolling(window=length).mean()
                std = self.data[col].rolling(window=length).std()
                self.data[f'{name}_upper'] = self.data[f'{name}_mid'] + (std_dev * std)
                self.data[f'{name}_lower'] = self.data[f'{name}_mid'] - (std_dev * std)

            elif kind == 'atr':
                high = ind.get('high', 'High')
                low = ind.get('low', 'Low')
                close = ind.get('close', 'Close')
                tr1 = self.data[high] - self.data[low]
                tr2 = abs(self.data[high] - self.data[close].shift())
                tr3 = abs(self.data[low] - self.data[close].shift())
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                self.data[name] = tr.ewm(alpha=1/length, adjust=False).mean()

            else:
                print(f"Warning: Indicator '{kind}' not recognized.")
        
        return self
