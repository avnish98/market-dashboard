from processor import IndexProcessor
from ds import Portfolio

class Environment:
    def __init__(self, data):
        self.data = data
    
    def initialize(self, lookback_period):
        pass
    
    def load_next_day(self):
        pass

class Agent:
    def __init__(self):
        self.portfolio = Portfolio()
    
    def execute_buy(self, quantity):
        pass
    
    def execute_sell(self, quantity):
        pass
    
    def rebalance_portfolio(self):
        pass
    
    def log(self):       
        pass

class Backtest:
    def __init__(self, start_date, end_date, bband_margins, bband_ma, 
                bband_std_mul, upper_margin, lower_margin, lookback_period,
                 rebalance_period, proc_ohlc_loc, proc_metadata_loc):
                 
        self.start_date = start_date
        self.end_date = end_date
        self.bband_margins = bband_margins
        self.bband_ma = bband_ma,
        self.bband_std_mul = bband_std_mul
        self.upper_margin = upper_margin
        self.lower_margin = lower_margin
        self.lookback_period = lookback_period
        self.rebalance_period = rebalance_period

        self.processor = IndexProcessor(proc_ohlc_loc, proc_metadata_loc)
        self.processor.process_metrics()
        self.processor.process_close(start_date, end_date)

        self.agent = Agent()

        self.env = Environment(self.processor.close_matrix)
        self.env.initialize(self.lookback_period)

    def backtest(self):
        pass