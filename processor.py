import os

import pandas as pd

from ds import Portfolio

class PortfolioProcessor:
    def __init__(self, ohlc_loc=None, meta_data_loc=None):
        self.portfolio = Portfolio()
        self.ohlc_location = ohlc_loc
        self.meta_data_json = []
        self.meta_data_loc = meta_data_loc
        self.close_matrix = pd.DataFrame
        self.returns_matrix = pd.DataFrame
        self.cov_matrix = pd.DataFrame

    def process_close(self, time_period=250):
        files = os.listdir(self.ohlc_location)
        cpd = {}
        for f in files:
            temp_df = pd.read_csv("{}/{}".format(self.ohlc_location,f))
            temp_df.set_index('Date', inplace=True)
            temp_df = temp_df.tail(time_period)
            if (temp_df.shape[0] != 0):
                cpd[f.replace('.csv', '')] = temp_df['Close'].values
        self.close_matrix = pd.DataFrame.from_dict(cpd)
        self.close_matrix.index = temp_df.index
    
    def process_close_returns(self, time_period=250):
        self.returns_matrix = self.close_matrix.pct_change(time_period)

    def process_cov(self):
        if(self.close_matrix.shape[0] != 0):
            self.cov_matrix = self.close_matrix.cov()
    
    def process_metadata(self):
        temp_df = pd.read_csv(self.meta_data_loc).to_dict(orient='records')
        self.meta_data_json.append(temp_df)
    # def process_latest_price(self):
    #     return self.close_matrix.tail(1).T