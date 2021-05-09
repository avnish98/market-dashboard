"""Fetcher module

This script contains fetcher classes for metadata and OHLC data.

It contains following classes
    * IndexFetcher: Base IndexFetcher Class
    * Nifty500Fetcher: Derived IndexFetcher Class for Nifty 500 Index
"""

import time
from datetime import date, datetime
import os

import pandas as pd
import numpy as np
from nsetools import Nse
from nsepy import get_history


class IndexFetcher:
    """
    Base class to represent an Index

    ...

    Attributes
    ----------
    fetcher : <varies>
        Fetcher object, contains methods for fetching data    
    ticker_list : list[str]
        List of constituent tickers
    ohlc_dir : str
        Location of OHLC data
    metadata_dir : str
        Location of Metadata
    
    Methods
    -------
    make_dirs(): void
        Creates prerequisite directories if not present already
    read_list(): void
        Reads static CSV containing tickers into ticker_list, updates if specified
    fetch_metadata(timeout=int): void
        Fetches metadata and stores as static CSVs
    fetch_data(start_date=datetime.date, end_date=datetime.date, timeout=5): void
        Fetches OHLC data and stores as static CSVs
    ohlc_updation_check(): dict[str]=datetime.date
        Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values
    update_ohlc(timeout=int): void
        Updates OHLC data using list from ohlc_updation_check()
    """

    def __init__(self):
        self.fetcher = None
        self.ticker_list = []

        self.make_dirs()

        self.ohlc_dir = ''
        self.metadata_dir = ''
    
    def make_dirs(self):
        """Creates prerequisite directories if not present already
        """

        if not os.path.exists('data'):
            os.makedirs('data')
        
        if not os.path.exists('data/raw'):
            os.makedirs('data/raw')

        if not os.path.exists('data/cleaned'):
            os.makedirs('data/cleaned')
        
        if not os.path.exists('data/cleaned/OHLC'):
            os.makedirs('data/cleaned/OHLC')

        if not os.path.exists('data/cleaned/OHLC/Index'):
            os.makedirs('data/cleaned/OHLC/Index')

        if not os.path.exists('data/cleaned/Metadata'):
            os.makedirs('data/cleaned/Metadata')
        
        if not os.path.exists('data/processed'):
            os.makedirs('data/processed')
        
        if not os.path.exists('data/processed/OHLC'):
            os.makedirs('data/processed/OHLC')

        if not os.path.exists('data/processed/OHLC/Index'):
            os.makedirs('data/processed/OHLC/Index')

        if not os.path.exists('data/processed/Metadata'):
            os.makedirs('data/processed/Metadata')

    def read_list(self, url='', update=False):
        """Reads static CSV containing tickers
        Updates if specified

        Parameters
        ----------
        url : str
            Hyperlink of ticker data
        update: bool (False)
            Toggle to update ticker list
        """

        pass 

    def fetch_metadata(self):
        """Fetches metadata and stores as static CSVs
        """

        pass
    
    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), timeout=5):
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        timeout: int (5)
            Pause between every OHLC fetch. Keep > 0 if you don't want to be 
            blacklisted by provider
        """

        pass


    def ohlc_updation_check(self):
        """Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values
        
        Returns
        -------
        outdated: dict[str] = datetime.date
            Dictionary of outdated tickers
        """

        pass

    def update_ohlc(self, timeout=5):
        """Updates OHLC data using list from ohlc_updation_check()

        Parameters
        ----------
        timeout: int (5)
            Pause between every OHLC fetch. Keep > 0 if you don't want to be 
            blacklisted by provider
        """

        pass


class Nifty500Fetcher(IndexFetcher):
    """
    Derived class to represent an Nifty 500 Index

    ...

    Attributes
    ----------
    fetcher : nsetools.nse.Nse 
        Nse Fetcher object    
    ticker_list : list[str]
        List of constituent tickers
    ohlc_dir : str
        Location of OHLC data
    metadata_dir : str
        Location of Metadata
    
    Methods
    -------
    read_list(url=str, update=bool): void
        Reads static CSV containing tickers into ticker_list
    fetch_metadata(timeout=int): void
        Fetches metadata and stores as static CSVs
    fetch_data(start_date=datetime.date, end_date=datetime.date, timeout=int): void
        Fetches OHLC data and stores as static CSVs
    ohlc_updation_check(): dict[str]=datetime.date
        Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values
    update_ohlc(timeout=int): void
        Updates OHLC data using list from ohlc_updation_check(
    """

    def __init__(self):
        super().__init__()
        self.fetcher = Nse()
        self.ticker_list = []

        self.make_dirs()

        nifty500_ohlc_dir = 'data/raw/Nifty500'
        nifty500_metadata_dir = 'data/raw/'
        
        if not os.path.exists(nifty500_ohlc_dir):
            os.makedirs(nifty500_ohlc_dir)

        if not os.path.exists(nifty500_ohlc_dir+"/Index"):
            os.makedirs(nifty500_ohlc_dir+"/Index")

        self.metadata_dir = nifty500_metadata_dir
        self.ohlc_dir = nifty500_ohlc_dir

    def read_list(self, 
                  url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv', 
                  update=False):
        """Reads static CSV containing tickers into ticker_list
        By extarcting 'Symbol' column's values as python list

        Parameters
        ----------
        url : str
            Hyperlink of ticker data
        update: bool (False)
            Toggle to update ticker list
        """

        if(update):
            try: 
                df = pd.read_csv(url)
                df.to_csv('{}/nifty_500_list.csv'.format(self.metadata_dir))

            except Exception as e:
                print("Exception {} occured ticker list not updated".format(e))

        self.ticker_list = list(pd.read_csv("{}/nifty_500_list.csv".format(self.metadata_dir))['Symbol'].values)
    
    def fetch_metadata(self, timeout=5):
        """Fetches metadata and stores as static CSVs
        """

        self.read_list()

        num_tickers = len(self.ticker_list)
        progress = 0
        metadata = []
        exception_tickers = []

        for c in self.ticker_list:
            try:
                data = self.fetcher.get_quote(c)
                metadata.append(data)
            
            except Exception as e:
                print("Exception {} occured for ticker: {}".format(e, c))
                exception_tickers.append(c)
            
            progress +=1
            progress_perc = np.round((progress/num_tickers)*100, 2)
            print("Progress: {}% Last ticker: {}".format(progress_perc, c))
            time.sleep(timeout)

        pd.DataFrame.from_dict(metadata, orient='columns').to_csv("{}/nifty_500_metadata.csv".format(self.metadata_dir))

    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), timeout=5):
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        timeout: int (5)
            Pause between every OHLC fetch. Keep > 0 if you don't want to be 
            blacklisted by provider
        """
        
        self.read_list()

        num_tickers = len(self.ticker_list)
        progress = 0
        exception_tickers = []

        for c in self.ticker_list:
            try:
                data = get_history(symbol=c, start=start_date, end=end_date)
                data.to_csv("{}/{}.csv".format(self.ohlc_dir, c))

            except Exception as e:
                print("Exception {} occured for ticker: {}".format(e, c))
                exception_tickers.append(c)

            progress +=1
            progress_perc = np.round((progress/num_tickers)*100, 2)
            print("Progress: {}% Last ticker: {}".format(progress_perc, c))
            time.sleep(timeout)
    
    def fetch_index(self, index_name='NIFTY500', start_date=date(1980, 1, 1), end_date=date.today()):
        data = get_history(symbol=index_name, start=start_date, end=end_date)
        data.to_csv("{}/{}.csv".format(self.ohlc_dir+"/Index", index_name)
    
    def ohlc_updation_check(self):
        """Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values

        Returns
        -------
        outdated: dict[str] = datetime.date
            Dictionary of outdated tickers
        """
        
        self.read_list()

        today = date.today()

        last_bday = np.where((today - pd.tseries.offsets.BDay(0)) > today,
            (today - pd.tseries.offsets.BDay(1)),
            (today - pd.tseries.offsets.BDay(0))).item()
        last_bday = np.datetime64(last_bday)

        outdated = {}
        for ticker in self.ticker_list:
            try:
                temp_df = pd.read_csv("{}/{}.csv".format(self.ohlc_dir,ticker))
                last_date = pd.to_datetime(temp_df['Date']).values[-1]
            
                if(last_date != last_bday):
                    tdelta = (last_bday - last_date)/(1e9*3600*24)
                    tdelta = str(tdelta).split(' ')[0]
                    print("{} is outdated by {} days".format(ticker, tdelta))
                    outdated[ticker] = last_date.astype('M8[D]').astype('O')
            
            except Exception as e:
                print("Exception: {} for ticker {}".format(e, ticker))
        
        print("Total outdated tickers: {}\n".format(len(outdated)))
        
        return outdated

    def update_ohlc(self, timeout=5):
        """Updates OHLC data using dict from ohlc_updation_check()

        Parameters
        ----------
        timeout: int (5)
            Pause between every OHLC fetch. Keep > 0 if you don't want to be 
            blacklisted by provider
        """
        
        outdated_tickers = self.ohlc_updation_check()
        num_tickers = len(outdated_tickers)

        if(num_tickers>0):
            progress = 0
            exception_tickers = []

            for c in list(outdated_tickers.keys()):
                start_date = outdated_tickers[c]
                end_date = date.today()

                try:
                    data = get_history(symbol=c, start=start_date, end=end_date)
                    old_data = pd.read_csv("{}/{}.csv".format(self.ohlc_dir, c))
                    old_data.set_index('Date', inplace=True)

                    new_data = pd.concat([old_data, data]).drop_duplicates()
                    new_data.to_csv("{}/{}.csv".format(self.ohlc_dir, c))

                    last_date = new_data.index[-1]

                except Exception as e:
                    print("Exception {} occured for ticker: {}".format(e, c))
                    exception_tickers.append(c)

                progress +=1
                progress_perc = np.round((progress/num_tickers)*100, 2)
                print("Progress: {}% Ticker: {} updated till: {}".format(progress_perc, c, last_date))
                time.sleep(timeout)
        
        else:
            print("OHLC data is up-to-date")