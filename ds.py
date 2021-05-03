import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation

class Stock:
    def __init__(self, ticker, price, ohlc=pd.DataFrame, metadata={}):
        self.ticker = ticker
        self.price = price
        self.ohlc = ohlc
        self.metadata = metadata

class Portfolio:
    def __init__(self):
        self.stocks = []
        self.cash = None
        self.composition = {}
        self.discrete_composition = {}
        self.cash_left = None
        self.statistics = {}

    def update_stocks(self, close_matrix):
        latest_price = close_matrix.tail(1).T.reset_index()
        latest_price.columns = ['Stock','Price']
        latest_price.set_index('Stock', inplace=True)
        for stock_name in list(self.composition.keys()):
            if(stock_name in close_matrix.columns):
                self.stocks.append(Stock(stock_name, latest_price['Price'][stock_name]))
    
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