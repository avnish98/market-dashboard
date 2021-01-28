import pandas as pd
import numpy as np
from nsetools import Nse
from datetime import date
from nsepy import get_history
import time

class Index:
    def __init__(self):
        self.fetcher = None
        self.ticker_list = []

    def update_list(self, link='', dest=''):
        df = pd.read_csv(link)
        df.to_csv(dest)
    
    def read_list(self, source=''):
        self.ticker_list = source
    
    def fetch_metadata(self, dest='', update_list=True):
        pass
    
    def fetch_data(self, dest='', update_list=True):
        pass

class Nifty500(Index):
    def __init__(self):
        super().__init__()
        self.fetcher = Nse()
        self.ticker_list = []
     
    def read_list(self, source='static_files/nifty500list.csv'):
        self.ticker_list = list(pd.read_csv(source)['Symbol'].values)
    
    def fetch_metadata(self, dest='static_files/nifty500metadata.csv', update_list=False):
        url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv'

        if(update_list):
            self.update_list(link = url, dest='static_files/nifty500list.csv')

        self.read_list()

        num_tickers = len(self.ticker_list)
        progress = 0
        meta_data = []
        exception_tickers = []

        for c in self.ticker_list:
            try:
                data = self.fetcher.get_quote(c)
                meta_data.append(data)
            
            except Exception as e:
                print("Exception {} occured for ticker: {}".format(e, c))
                exception_tickers.append(c)
            
            progress +=1
            progress_perc = np.round((progress/num_tickers)*100, 2)
            print("Progress: {}% Last ticker: {}".format(progress_perc, c))
        pd.DataFrame.from_dict(meta_data, orient='columns').to_csv(dest)

    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), dest='static_files/NSE', update_list=False):
        
        url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv'

        if(update_list):
            self.update_list(link = url, dest='static_files/nifty500list.csv')

        self.read_list()

        num_tickers = len(self.ticker_list)
        progress = 0
        exception_tickers = []

        for c in self.ticker_list:
            try:
                data = get_history(symbol=c, start=start_date, end=end_date)
                data.to_csv("{}/{}.csv".format(dest, c))

            except Exception as e:
                print("Exception {} occured for ticker: {}".format(e, c))
                exception_tickers.append(c)

            progress +=1
            progress_perc = np.round((progress/num_tickers)*100, 2)
            print("Progress: {}% Last ticker: {}".format(progress_perc, c))

            time.sleep(5)
    
    def update_ohlc(self):

        #TODO: update historical ohlc data using metadata?