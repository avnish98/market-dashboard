import os

import pandas as pd

from ds import Portfolio, Stock
from utils import read_json, find_in_json, write_json, write_csv

class Processor:
    def __init__(self, ohlc_loc=None, metadata_loc=None):
        self.ohlc_location = ohlc_loc
        self.metadata_loc = metadata_loc

    def process_metrics(self):
        pass
        
class StockProcessor(Processor):
    def __init__(self, symbol=None, ohlc_loc=None, metadata_loc=None):
        super().__init__()
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
            self.stock.metadata['OHLC Data Available'] = True
            self.stock.metadata['OHLC Data Location'] = self.stock.metadata['OHLC Data Location'].replace('cleaned', 'processed')
            write_csv(ohlc_data, self.stock.ohlc.replace('cleaned', 'processed'))

        except FileNotFoundError as e:            
            self.stock.metadata['OHLC Data Available'] = False
            self.stock.metadata['OHLC Data Location'] = None
            print("File not present: {}".format(self.stock.ohlc))

class IndexProcessor(Processor):
    def __init__(self, ohlc_loc=None, metadata_loc=None):
        super().__init__()
        self.ohlc_location = ohlc_loc
        self.metadata_json = read_json(metadata_loc)
        self.metadata_loc = metadata_loc
        self.proc_metadata_loc = metadata_loc.replace('cleaned', 'processed')
        self.close_matrix = pd.DataFrame
        self.returns_matrix = pd.DataFrame
        self.cov_matrix = pd.DataFrame
        
        if not os.path.exists(self.ohlc_location.replace('cleaned', 'processed')):
                os.makedirs(self.ohlc_location.replace('cleaned', 'processed'))

    
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
    
class PortfolioProcessor(Processor):
    def __init__(self):
        super().__init__()
        pass