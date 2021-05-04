import os

import pandas as pd

from ds import Portfolio, Stock
from utils import read_json, find_in_json, write_json, write_csv

class StockProcessor:
    def __init__(self, symbol=None, ohlc_loc=None, metadata_loc=None):
        self.stock = Stock()
        self.stock.load(find_in_json(read_json(metadata_loc), 'Ticker', symbol))
    
    def process_metrics(self, upper_margin=0.05, lower_margin=0.05, bband_ma=20,
                        bband_std=2):
        try:
            ohlc_data = pd.read_csv(self.stock.ohlc).set_index('Date')
            ohlc_data['14MA'] = ohlc_data['Close'].rolling(window=14).mean()
            ohlc_data['50MA'] = ohlc_data['Close'].rolling(window=50).mean()
            ohlc_data['200MA'] = ohlc_data['Close'].rolling(window=200).mean()
            ohlc_data['200STD'] = ohlc_data['Close'].rolling(window=200).std(ddof=0)
            ohlc_data['Daily Return'] = ohlc_data['Close'].pct_change()*100
            ohlc_data['Monthly Return'] = ohlc_data['Close'].pct_change(30)*100
            ohlc_data['Yearly Return'] = ohlc_data['Close'].pct_change(252)*100
            ohlc_data['Profit Exit'] = ohlc_data['Close'] + (ohlc_data['Close'] * (upper_margin))
            ohlc_data['Stop Loss'] = ohlc_data['Close'] - (ohlc_data['Close'] * (lower_margin))
            ohlc_data['Bollinger Band Up'] = ohlc_data['Close'].rolling(window=bband_ma).mean() +\
                                             (bband_std*ohlc_data['Close'].rolling(window=bband_ma).std(ddof=0))
            ohlc_data['Bollinger Band Down'] = ohlc_data['Close'].rolling(window=bband_ma).mean() -\
                                             (bband_std*ohlc_data['Close'].rolling(window=bband_ma).std(ddof=0))                                
            ohlc_data = ohlc_data.round(2)
            
            # latest_ohlc = ohlc_data.tail(1).to_dict(orient='records')[0]
            # self.stock.metadata['VWAP'] = latest_ohlc['VWAP']
            # self.stock.metadata['Volume'] = latest_ohlc['Volume']
            # self.stock.metadata['Previous Close'] = latest_ohlc['Prev Close']
            # self.stock.metadata['Turnover'] = latest_ohlc['Turnover']
            # self.stock.metadata['Open'] = latest_ohlc['Open']
            # self.stock.metadata['High'] = latest_ohlc['High']
            # self.stock.metadata['Low'] = latest_ohlc['Low']
            # self.stock.metadata['Profit Exit'] = self.stock.price + self.stock.price*(upper_margin)
            # self.stock.metadata['Stop Loss'] = self.stock.price - self.stock.price*(lower_margin)
            # self.stock.metadata['14MA'] = latest_ohlc['14MA']
            # self.stock.metadata['50MA'] = latest_ohlc['50MA']
            # self.stock.metadata['200MA'] = latest_ohlc['200MA']
            # self.stock.metadata['Daily Return'] = latest_ohlc['Daily Return']
            # self.stock.metadata['Monthly Return'] = latest_ohlc['Monthly Return']
            # self.stock.metadata['Yearly Return'] = latest_ohlc['Yearly Return']
            # self.stock.metadata['Volatility'] = latest_ohlc['200STD']

            self.stock.metadata['OHLC Data Available'] = True
            write_csv(ohlc_data, self.stock.ohlc)

        except FileNotFoundError as e:

            # self.stock.metadata['VWAP'] = None
            # self.stock.metadata['Volume'] = None
            # self.stock.metadata['Previous Close'] = None
            # self.stock.metadata['Turnover'] = None
            # self.stock.metadata['Open'] = None
            # self.stock.metadata['High'] = None
            # self.stock.metadata['Low'] = None
            # self.stock.metadata['Profit Exit'] = None
            # self.stock.metadata['Stop Loss'] = None
            # self.stock.metadata['14MA'] = None
            # self.stock.metadata['50MA'] = None
            # self.stock.metadata['200MA'] = None
            # self.stock.metadata['Daily Return'] = None
            # self.stock.metadata['Monthly Return'] = None
            # self.stock.metadata['Yearly Return'] = None
            # self.stock.metadata['Volatility'] = None
            
            self.stock.metadata['OHLC Data Available'] = False
            self.stock.metadata['OHLC Data Location'] = None
            print("File not present: {}".format(self.stock.ohlc))

class IndexProcessor:
    def __init__(self, ohlc_loc=None, metadata_loc=None, proc_metadata_loc=None):
        self.ohlc_location = ohlc_loc
        self.metadata_json = read_json(metadata_loc)
        self.metadata_loc = metadata_loc
        self.proc_metadata_loc = proc_metadata_loc
        self.close_matrix = pd.DataFrame
        self.returns_matrix = pd.DataFrame
        self.cov_matrix = pd.DataFrame
    
    def process_metrics(self):
        new_meta_json = []
        for entry in self.metadata_json:
            sp = StockProcessor(entry['Ticker'], 
                                entry['OHLC Data Location'], 
                                self.metadata_loc)
            sp.process_metrics()
            new_meta_json.append(sp.stock.metadata)
        write_json(new_meta_json, self.proc_metadata_loc)
        
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
    
class PortfolioProcessor:
    def __init__(self):
        self.portfolio = Portfolio()