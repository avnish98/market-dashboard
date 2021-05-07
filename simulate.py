from datetime import date, datetime

import pandas as pd
import numpy as np

from processor import IndexProcessor
from optimizer import Optimizer
from ds import Portfolio, Stock
from utils import find_in_json, read_json, sort_dict, slice_dict

class Environment:
    def __init__(self, data, lookback_period):
        self.data = data
        self.dates = list(data.index)[lookback_period:]
        self.current_date = 0
        self.lookback_data = np.array_split(data, 82)

    def load_next_day(self):
        dayend_prices = self.data[self.data.index == self.dates[self.current_date]]
        dayend_prices = dayend_prices.to_dict(orient='records')[0]
        self.current_date += 1
        return dayend_prices


class Agent:
    def __init__(self, optimizer=Optimizer(), portfolio_value=100000, 
                single_day_cash=0.60, **kwargs):
        self.portfolio = Portfolio(single_day_cash*portfolio_value)
        self.optimizer = optimizer
        self.total_cash = portfolio_value
        #self.optimizer.portfolio.portfolio_value = portfolio_value
        self.single_day_cash = single_day_cash
        self.orders = {}
        self.order_log = []

        try:
            self.optimizer.optimizer_type = kwargs["optimizer_type"]
        except:
            self.optimizer.optimizer_type = None

        self.optimizer.metadata_loc = kwargs["metadata_loc"] 
    
    def allocate_portfolio(self, lookback_data):
        self.optimizer.portfolio.cash_left += self.single_day_cash * self.total_cash
        self.portfolio.cash_left += self.single_day_cash * self.total_cash
        self.total_cash -= self.single_day_cash * self.total_cash
        self.optimizer.close_matrix = lookback_data.dropna(axis=1, how='all')
        self.optimizer.optimize()
        #self.initialize()
    
    # def initialize(self):
    #     if(self.portfolio.stocks == []):
    #         self.portfolio = self.optimizer.portfolio
    
    def compute_orders(self, dayend_prices=None):
        portfolio_comp = self.portfolio.discrete_composition
        optimizer_comp = self.optimizer.portfolio.discrete_composition
        #optimizer_comp = sort_dict(optimizer_comp, reverse=True)
        self.orders = {}
        if len(self.portfolio.stocks) == 0:
            self.orders = optimizer_comp
        else:
            for k, v in optimizer_comp.items():
                if k in portfolio_comp.keys():
                    if v != portfolio_comp[k]:
                        self.orders[k] = v - portfolio_comp[k]
                self.orders[k] = v
        
        # if(self.num_stocks>0):
        #     self.orders = slice_dict(self.orders, self.num_stocks)

    def execute_orders(self, dayend_prices=None):
        self.order_log = []
        #self.orders = sort_dict(self.orders, True)
        for ticker, shares in self.orders.items():
            if shares > 0:
                self.execute_buy(ticker, shares, dayend_prices[ticker])
            elif shares < 0:
                self.execute_sell(ticker, shares, dayend_prices[ticker])
    
    def execute_buy(self, ticker, quantity, price):

        if (self.portfolio.cash_left) > (quantity*price):

            if(self.portfolio.stock_in_portfolio(ticker)):
                self.portfolio.update_allocation(ticker, quantity, price)
            else:
                metadata = find_in_json(read_json(self.optimizer.metadata_loc), "Ticker", ticker)
                stock = Stock()
                stock.load(metadata)
                stock.metadata['Portfolio Allocation'] = quantity
                stock.metadata['Price'] = price
                stock.price = price
                stock.metadata['Value'] = quantity*price
                self.portfolio.stocks.append(stock)

            self.portfolio.cash_left -= quantity*price
            self.order_log.append("Bought {} shares of {} at {}".format(quantity, ticker, quantity*price))
    
    def execute_sell(self, quantity):
        metadata = find_in_json(read_json(self.optimizer.metadata_loc), "Ticker", ticker)
        stock = Stock()
        stock.load(metadata)

        if(self.portfolio.stock_in_portfolio(ticker)):
                self.portfolio.update_allocation(ticker, quantity, price)
        else:
                self.portfolio.stocks.remove(stock)
        # stock.metadata['Portfolio Allocation'] = quantity
        # stock.metadata['Value'] = quantity*price
        # self.portfolio.stocks.append(stock)
        # self.portfolio.cash_left -= quantity*price 
        self.order_log.append("Sold {} shares of {} at {}".format(-quantity, ticker, -quantity*price))
    
    def log(self):       
        pass

class Backtesting:
    def __init__(self, start_date=date(1980, 1, 1), end_date=date.today(), 
                bband_margins=True, bband_ma=20, bband_std_mul=2, 
                upper_margin=0.05, lower_margin=0.05, lookback_period=30,
                rebalance_period=30, proc_ohlc_loc=None, proc_metadata_loc=None,
                agents=[], benchmark=pd.DataFrame, benchmark_name="", 
                portfolio_value=1000000, process_metrics=False,):
                 
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

        if process_metrics:
            self.processor.process_metrics(upper_margin, lower_margin, bband_ma, 
                                        bband_std_mul)

        self.processor.process_close(start_date, end_date)

        self.agents = agents

        self.env = Environment(self.processor.close_matrix, self.lookback_period)

    def backtest(self):
        for a in self.agents:
            for i in range(5):
                a.allocate_portfolio(self.env.lookback_data[i])
                a.compute_orders()
                a.execute_orders(self.env.load_next_day())
                print()
                print(a.order_log)
        
