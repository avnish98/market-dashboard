from datetime import date, datetime

import pandas as pd
import numpy as np

from processor import IndexProcessor
from optimizer import Optimizer
from ds import Portfolio, Stock
from utils import find_in_json, read_json, sort_dict, slice_dict, return_latest_data

class Environment:
    def __init__(self, data, metadata, lookback_period):
        self.data = data
        self.metadata = metadata
        self.dates = list(data.index)#[lookback_period:]
        self.current_date =(-1)
        self.lookback_period = lookback_period

    def load_next_day(self, agent):
        dayend_prices = self.data[self.data.index == self.dates[self.current_date]]
        dayend_prices = dayend_prices.to_dict(orient='records')[0]

        agent.orders = {}
        agent.order_log = []

        for s in agent.portfolio.stocks:
         
            s.price = dayend_prices[s.ticker]
            s.metadata['Price'] = dayend_prices[s.ticker]

            try:
                ohlc_data = pd.read_csv(s.metadata['OHLC Data Location'])
                ohlc_data['Date'] = pd.to_datetime(ohlc_data['Date']).dt.date
                ohlc_data = ohlc_data[ohlc_data['Date'] == self.dates[self.current_date]]
                ohlc_data = ohlc_data.to_dict(orient='records')[0]

                if((s.price <= ohlc_data['Bollinger Band Down']) or (s.price >= ohlc_data['Bollinger Band Up'])):
                    agent.execute_sell(s.ticker, -s.metadata['Portfolio Allocation'], s.price)   
            except Exception as e:
                print("Exception {} for ticker {} for date {}".format(e, s.ticker, self.dates[self.current_date]))
            
        self.current_date += 1
        return dayend_prices
    
    def load_lookback_data(self):
        start_cond = (self.data.index > self.dates[self.current_date - self.lookback_period])
        end_cond = (self.data.index <= self.dates[self.current_date])
        allocation_data = self.data.loc[start_cond & end_cond]
        return allocation_data

    def is_reallocation_day(self):
        flag = False
        if(self.current_date !=0):
            if(self.current_date % self.lookback_period==0):
                flag=True
        return flag


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

    # def update_stocks(self, dayend_prices):
    #     df = pd.read_json(self.optimizer.metadata_loc)
    #     for s in self.portfolio.stocks:
    #         s.price = dayend_prices[s.ticker]
    #         s.metadata['Price'] = dayend_prices[s.ticker]
    #         s.metadata['Price'] = dayend_prices[s.ticker]
    #         s.metadata['Price'] = dayend_prices[s.ticker]
    
    # def compute_daily_orders(self, dayend_prices=None):
    #     portfolio_comp = self.portfolio.discrete_composition
    #     self.orders = {}

    #     for stock in self.portfolio.stocks:
    #         if(stock.price <= stock.metadata['Bollinger Band Down']):
    #             self.orders[stock.ticker]= -stock.metadata['Portfolio Allocation']
    #         elif(stock.price >= stock.metadata['Bollinger Band Up']):
    #             self.orders[stock.ticker]= -stock.metadata['Portfolio Allocation']

    def compute_allocation_orders(self):
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
        #self.orders = []
    
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
            #print("Bought {} shares of {} at {}".format(quantity, ticker, quantity*price))
    
    def execute_sell(self, ticker, quantity, price):

        if(self.portfolio.stock_in_portfolio(ticker)):
            self.portfolio.update_allocation(ticker, quantity, price)
            
        # metadata = find_in_json(read_json(self.optimizer.metadata_loc), "Ticker", ticker)
        # stock = Stock()
        # stock.load(metadata)

        # if(self.portfolio.stock_in_portfolio(ticker)):
        #         self.portfolio.update_allocation(ticker, -quantity, price)
        # else:
        #         self.portfolio.stocks.remove(stock)
        self.portfolio.cash_left += (-quantity)*price

        self.order_log.append("Sold {} shares of {} at {}".format(-quantity, ticker, -quantity*price))
        #print("Sold {} shares of {} at {}".format(-quantity, ticker, -quantity*price))
    
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

        self.env = Environment(self.processor.close_matrix, pd.DataFrame(read_json(proc_metadata_loc)),
                                self.lookback_period)

    def backtest(self):
        for a in self.agents:
            for i in range(len(self.env.dates)):
                # a.allocate_portfolio(self.env.lookback_data[i])
                # a.compute_orders()
                #try:
                    dayend_prices = self.env.load_next_day(a)
                    #a.update_stocks(dayend_prices,)
                    #a.compute_daily_orders(dayend_prices)
                    #a.execute_orders(dayend_prices)

                    if(self.env.is_reallocation_day()):
                        print("Reallocation day")
                        print(self.env.current_date)
                        #print(self.env.current_date)
                        # start_cond = (self.env.data.index > self.env.dates[i-self.lookback_period])
                        # end_cond = (self.env.data.index <= self.env.dates[i])
                        # allocation_data = self.env.data.loc[start_cond & end_cond]

                        allocation_data = self.env.load_lookback_data()
                        # print("This is allocation data")
                        # print("Date: {}".format(self.env.dates[i]))
                        # print(allocation_data.head())
                        # print(allocation_data.info())

                        a.allocate_portfolio(allocation_data)
                        a.compute_allocation_orders()
                        a.execute_orders(dayend_prices)
                        
                    #print()
                    #print(self.env.dates[i])
                    print(self.env.dates[i])
                    print(a.order_log)
                    print()
                    print(dict(zip([s.ticker for s in a.portfolio.stocks], [s.metadata['Portfolio Allocation'] for s in a.portfolio.stocks])))
                    # for s in a.portfolio.stocks:
                    #     s.ticker
                    #     s.metadata['Portfolio Allocation']
                    print()
                # except Exception as e:
                #     print(e)
        
