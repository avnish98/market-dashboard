"""Data Stucture module

This script contains data stuctures for storing stocks and portfolio data.

It contains following classes
    * Stock: Base Stock Class
    * Portfolio: Base Portfolio Class
"""

import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation

from utils import read_json, find_in_json


class Stock:
    """
    Base class to represent a Stock

    ...

    Attributes
    ----------
    ticker : str
        Stock ticker
    price : float
        Latest close price of stock
    ohlc : str
        Location of stock's OHLC data
    metadata: dict
        Dictionary containing stock's metadata
    
    Methods
    -------
    load(dict): void
        Loads stock's attributes from dictionary
    """

    def __init__(self, ticker=None, price=None, ohlc=pd.DataFrame, metadata={}):
        self.ticker = ticker
        self.price = price
        self.ohlc = ohlc
        self.metadata = metadata

    def load(self, metadata_dict):
        """Loads stock's attributes from dictionary

        Parameters
        ----------
        metadata_dict : dict
            Dictionary of stock's metadata
        """

        self.ticker = metadata_dict['Ticker']
        self.price = metadata_dict['Price']
        self.ohlc = metadata_dict['OHLC Data Location']
        self.metadata = metadata_dict


class Portfolio:
    """
    Base class to represent a Portfolio

    ...

    Attributes
    ----------
    stocks : list[Stock()]
        List of Stock objects
    composition : dict
        Dictionary containing allocation (weights) assigned to each stock
    discrete_composition : dict
        Dictionary containing allocation (stock number) assigned to each stock
    cash_left : flaot
        Cash left in portfolio
    statistics: dict
        Dictionary portfolio's statistics
    
    Methods
    -------
    construct(str, dict): void
        Constructs portfolio by: updating stock objects, calculating discrete
        allocation, and updating statistics of portfolio
    update_stocks(str, dict): void
        Updates Stock objects in stocks list using metadata and composition data
        provided by optimizer
    update_statistics(list): void
        Updates Portfolio's statistics given performance data provided by
        optimizer
    update_discrete_composition(float): void
        Calculates Portfolio's discrete composition using weights provided by
        optimizer and portfolio's value
    """

    def __init__(self, value=0):
        self.stocks = []
        self.portfolio_value = value
        self.composition = {}
        self.discrete_composition = {}
        self.cash_left = value
        self.statistics = {}
    
    def reset(self, val):
        self.portfolio_value = val
        self.cash_left = val

    def construct(self, latest_price, metadata_loc, stats):
        """Constructs portfolio by: updating stock objects, calculating discrete
        allocation, and updating statistics of portfolio

        Parameters
        ----------
        metadata_loc : str
            Location of metadata
        stats: list
            List of metrics: Expected annual returns, Volatility, Sharpe Ratio
        """

        #self.update_stocks(metadata_loc, list(self.composition.keys()))
        self.update_discrete_composition(latest_price, metadata_loc)
        self.update_statistics(stats)

    # def update_stocks(self, metadata_loc, stock_list):
    #     """Updates Stock objects in stocks list using metadata and composition data
    #     provided by optimizer

    #     Parameters
    #     ----------
    #     metadata_loc : str
    #         Location of metadata
    #     stock_list: list
    #         List of stocks provided by Optimizer
    #     """

    #     meta_json = read_json(metadata_loc)
    #     for stock_ticker in stock_list:
    #         stock_data = find_in_json(meta_json, 'Ticker', stock_ticker)
    #         #stock_data['Portfolio Allocation'] = self.composition[stock_ticker]
    #         stock = Stock()
    #         stock.load(stock_data)
    #         self.stocks.append(stock)
     
    # def update_stocks(self, close_matrix):
    #     latest_price = close_matrix.tail(1).T.reset_index()
    #     latest_price.columns = ['Stock','Price']
    #     latest_price.set_index('Stock', inplace=True)
    #     for stock_name in list(self.composition.keys()):
    #         if(stock_name in close_matrix.columns):
    #             self.stocks.append(Stock(stock_name, latest_price['Price'][stock_name]))
    
    def update_statistics(self, stats=[]):
        """Updates Portfolio's statistics given performance data provided by
        optimizer

        Parameters
        ----------
        stats : list[float]
            List of statistics provided by optimizer
        """

        temp_dict = {}
        temp_dict['Expected Annual Return'] = None if stats[0]==None else (round(stats[0], 2))*100
        temp_dict['Annual Volatility'] = None if stats[1]==None else (round(stats[1], 2))*100
        temp_dict['Sharpe Ratio'] = None if stats[2]==None else round(stats[2], 2)
        self.statistics = temp_dict
    
    def update_discrete_composition(self, latest_price, metadata_loc):
        """Calculates Portfolio's discrete composition using weights provided by
        optimizer and portfolio's value

        Parameters
        ----------
        portfolio_value : int (10000)
            Total valuation of portfolio
        """

        # price_dict = {}
        # for s in self.stocks:
        #     price_dict[s.ticker] = s.price
        # latest_price = pd.Series(price_dict)

        for k, v in dict(self.composition).items():
            if k not in latest_price.index:
                del self.composition[k]

        da = DiscreteAllocation(self.composition, latest_price, self.portfolio_value)
        self.discrete_composition, self.cash_left = da.greedy_portfolio() 

        meta_json = read_json(metadata_loc)
        for stock_ticker in list(self.discrete_composition.keys()):
            stock = Stock()
            stock_data = find_in_json(meta_json, 'Ticker', stock_ticker)
            stock_data['Portfolio Allocation'] = self.discrete_composition[stock_ticker]
            stock_data['Value'] = self.discrete_composition[stock_ticker] * stock_data['Price']
            stock.load(stock_data)
            self.stocks.append(stock)
    
    def stock_in_portfolio(self, ticker):
        flag = False
        for stock in self.stocks:
            if ticker == stock.ticker:
                flag = True
        return flag
    
    def update_allocation(self, ticker, disc_alloc, new_price):
        for stock in self.stocks:
            if ticker == stock.ticker:
                stock.metadata['Portfolio Allocation'] = stock.metadata['Portfolio Allocation'] + disc_alloc
                stock.metadata['Value'] = stock.metadata['Portfolio Allocation']*new_price

                if(stock.metadata['Portfolio Allocation']==0):
                    self.stocks.remove(stock)
                
                break
    
    def total_portfolio_value(self):
        total_val = 0
        for s in self.stocks:
            total_val += s.metadata['Value']
        return total_val