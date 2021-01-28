"""Fetcher module

This script contains fetcher functions for metadata and OHLC data.

It contains following classes
    * Index: Base Index Class
    * Nifty500: Derived Index Class for Nifty 500 Index
"""

import pandas as pd
import numpy as np
from nsetools import Nse
from datetime import date
from nsepy import get_history
import time

class Index:
    """
    Base class to represent an index

    ...

    Attributes
    ----------
    fetcher : <varies>
        Fetcher object, contains methods for fetching data    
    ticker_list : list[str]
        List of constituent tickers
    
    Methods
    -------
    update_list(link=str, dest=str): void
        Updates static CSV containing tickers
    read_list(source=str): void
        Reads static CSV containing tickers into ticker_list
    fetch_metadata(dest=str, update_list=bool): void
        Fetches metadata and stores as static CSVs
    fetch_data(dest=str, start_date=datetime.date, end_date=datetime.date, update_list=bool): void
        Fetches OHLC data and stores as static CSVs
    """

    def __init__(self):
        self.fetcher = None
        self.ticker_list = []

    def update_list(self, link='', dest=''):
        """Updates static CSV containing tickers

        Parameters
        ----------
        link : str
            Link for reading ticker data
        dest : str
            Location to store ticker data (locally)
        """

        df = pd.read_csv(link)
        df.to_csv(dest)
    
    def read_list(self, source=''):
        """Reads static CSV containing tickers into ticker_list

        Parameters
        ----------
        source : str
            Source of local ticker data CSV
        """

        self.ticker_list = source
    
    def fetch_metadata(self, dest='', update_list=True):
        """Fetches metadata and stores as static CSVs

        Parameters
        ----------
        dest : str
            Location to store metadata (locally)
        update_list : bool (True)
            True if you want to update ticker list before downloading metadata
        """

        pass
    
    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), dest='', update_list=True):
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        dest : str
            Location to store OHLC data (locally)
        update_list : bool (True)
            True if you want to update ticker list before downloading data
        """

        pass


class Nifty500(Index):
    """
    Derived class to represent an Nifty 500 Index

    ...

    Attributes
    ----------
    fetcher : nsetools.nse.Nse
        Nse Fetcher object    
    ticker_list : list[str]
        List of constituent tickers
    
    Methods
    -------
    update_list(link=str, dest=str): void
        Updates static CSV containing tickers
    read_list(source=str): void
        Reads static CSV containing tickers into ticker_list
    fetch_metadata(dest=str, update_list=bool): void
        Fetches metadata and stores as static CSVs
    fetch_data(dest=str, update_list=bool): void
        Fetches OHLC data and stores as static CSVs
    """

    def __init__(self):
        super().__init__()
        self.fetcher = Nse()
        self.ticker_list = []
     
    def read_list(self, source='static_files/nifty500list.csv'):
        """Reads static CSV containing tickers into ticker_list
        By extarcting 'Symbol' column's values as python list

        Parameters
        ----------
        source : str ('static_files/nifty500list.csv')
            Source of local ticker data CSV
        """

        self.ticker_list = list(pd.read_csv(source)['Symbol'].values)
    
    def fetch_metadata(self, dest='static_files/nifty500metadata.csv', update_list=False):
        """Fetches metadata and stores as static CSVs

        Parameters
        ----------
        dest : str ('static_files/nifty500metadata.csv')
            Location to store metadata (locally)
        update_list : bool (False)
            True if you want to update ticker list before downloading metadata
        """

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
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        dest : str
            Location to store OHLC data (locally)
        update_list : bool (True)
            True if you want to update ticker list before downloading data
        """
        
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