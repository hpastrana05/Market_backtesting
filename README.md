# Strategy Backtesting

This code is made for strategy backtesting.

## Idea of division
Three different classes:
- DataManager
- Simulation
- Strategy

### DataManager
This class is used to load the data, add the necessary indicators and features.
And also will be used to Save it as npy file.
Probably used with a script to load the data and save it.

### Simulation
In this class the backtesting will be done.
It will have the starting money, the fees/commisions, and the results
Will be used with a strategy class to backtest the strategy.

### Strategy
Will be used with a simulation class to backtest the strategy.
This class will have a check_entry(), check_exit(), and a update_opened_position(), methods.
Will have a Maximum max_open_trades, n_trades_opened, can_open_trade

