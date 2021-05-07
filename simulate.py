from datetime import date, datetime

import pandas as pd

from processor import IndexProcessor
from ds import Portfolio

class Environment:
    def __init__(self, data, lookback_period):
        self.data = data
        self.lookback_data = data.head(lookback_period)

    def load_next_day(self):
        pass

class Agent:
    def __init__(self, optimizer, portfolio_value, **kwargs):
        self.portfolio = Portfolio(portfolio_value)
        self.optimizer = optimizer
        self.optimizer.portfolio.portfolio_value = portfolio_value

        try:
            self.optimizer.optimizer_type = kwargs["optimizer_type"]
        except:
            self.optimizer.optimizer_type = None

        self.optimizer.metadata_loc = kwargs["metadata_loc"] 
    
    def initialize_portfolio(self, lookback_data):
        #lookback_data = lookback_data.dropna(axis=1, how='all')
        #lookback_data = lookback_data[lookback_data.columns[lookback_data.mean(axis=0) > 962.54]]
        self.optimizer.close_matrix = lookback_data.dropna(axis=1, how='all')
        
        #self.optimizer.close_matrix = self.optimizer.close_matrix.loc[:,self.optimizer.close_matrix.mean(axis=0) > 962.54]
        self.optimizer.optimize()
    
    def execute_buy(self, quantity):
        pass
    
    def execute_sell(self, quantity):
        pass
    
    def rebalance_portfolio(self):
        pass
    
    def log(self):       
        pass

class Backtesting:
    def __init__(self, start_date=date(1980, 1, 1), end_date=date.today(), 
                bband_margins=True, bband_ma=20, bband_std_mul=2, 
                upper_margin=0.05, lower_margin=0.05, lookback_period=30,
                rebalance_period=30, proc_ohlc_loc=None, proc_metadata_loc=None,
                agents=[], benchmark=pd.DataFrame, benchmark_name="", 
                portfolio_value=1000000):
                 
        self.start_date = start_date
        self.end_date = end_date
        self.bband_margins = bband_margins
        self.bband_ma = bband_ma,
        self.bband_std_mul = bband_std_mul
        self.upper_margin = upper_margin
        self.lower_margin = lower_margin
        self.lookback_period = lookback_period
        self.rebalance_period = rebalance_period
        self.benchmark = benchmark
        self.benchmark_name = benchmark_name

        self.processor = IndexProcessor(proc_ohlc_loc, proc_metadata_loc)
        # self.processor.process_metrics(upper_margin, lower_margin, bband_ma, 
        #                               bband_std_mul)
        self.processor.process_close(start_date, end_date)

        self.agents = agents

        self.env = Environment(self.processor.close_matrix, self.lookback_period)

    def backtest(self):
        for a in self.agents:
            a.initialize_portfolio(self.env.lookback_data)
        return a