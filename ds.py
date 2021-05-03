import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation

from utils import read_json

class Stock:
    def __init__(self, ticker=None, price=None, ohlc=pd.DataFrame, metadata={}):
        self.ticker = ticker
        self.price = price
        self.ohlc = ohlc
        self.metadata = metadata

    def load(self, metadata_dict):
        self.ticker = metadata_dict['Ticker']
        self.price = metadata_dict['Price']
        self.ohlc = metadata_dict['OHLC Data Location']
        self.metadata = metadata_dict


class Portfolio:
    def __init__(self):
        self.stocks = []
        self.cash = None
        self.composition = {}
        self.discrete_composition = {}
        self.cash_left = None
        self.statistics = {}

    def construct(self, metadata_loc):
        self.update_discrete_composition()
        self.update_stocks(meta_data_loc, list(self.composition.keys()))
        self.update_statistics()

    def update_stocks(self, meta_data_loc, stock_list):
        meta_json = read_json(meta_data_loc)
        for stock_ticker in stock_list:
            stock_data = find_in_json(meta_json, 'Ticker', stock_ticker)
            stock = Stock()
            self.stocks.append(stock.load(stock_data))
     
    # def update_stocks(self, close_matrix):
    #     latest_price = close_matrix.tail(1).T.reset_index()
    #     latest_price.columns = ['Stock','Price']
    #     latest_price.set_index('Stock', inplace=True)
    #     for stock_name in list(self.composition.keys()):
    #         if(stock_name in close_matrix.columns):
    #             self.stocks.append(Stock(stock_name, latest_price['Price'][stock_name]))
    
    def update_statistics(self, stats=[]):
        temp_dict = {}
        temp_dict['Expected Annual Return'] = (round(stats[0], 2))*100
        temp_dict['Annual Volatility'] = (round(stats[1], 2))*100
        temp_dict['Sharpe Ratio'] = round(stats[2], 2)
        self.statistics = temp_dict
    
    def update_discrete_composition(self, portfolio_value=10000):
        price_dict = {}
        for s in self.stocks:
            price_dict[s.ticker] = s.price
        latest_price = pd.Series(price_dict)

        da = DiscreteAllocation(self.composition, latest_price, portfolio_value)
        self.discrete_composition, self.cash_left = da.greedy_portfolio() #Clean by including cash in composition