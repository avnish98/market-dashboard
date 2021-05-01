import os

import pandas as pd

class Portfolio_Processor:
    def __init__(self, ohlc_loc):
        self.ohlc_location = ohlc_loc
        self.close_price_matrix = pd.DataFrame
        self.covariance_matrix = pd.DataFrame

    def process_close(self, time_period):
        files = os.listdir(self.ohlc_location)
        cpd = {}
        for f in files:
            temp_df = pd.read_csv("{}/{}".format(self.ohlc_location,f))
            temp_df.set_index('Date', inplace=True)
            temp_df = temp_df.tail(time_period)
            if (temp_df.shape[0] != 0):
                cpd[f.replace('.csv', '')] = temp_df['Close'].values
        self.close_price_matrix = pd.DataFrame.from_dict(cpd)
        self.close_price_matrix.index = temp_df.index
    
    def process_cov(self):
        if(self.close_price_matrix.shape[0] != 0):
            self.covariance_matrix = self.close_price_matrix.cov()