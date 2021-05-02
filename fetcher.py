"""Fetcher module

This script contains fetcher functions for metadata and OHLC data.

It contains following classes
    * Index: Base Index Class
    * Nifty500: Derived Index Class for Nifty 500 Index
"""

import time
from datetime import date, datetime
import os

import pandas as pd
import numpy as np
from nsetools import Nse
from nsepy import get_history

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
    ohlc_dir : str
        Location of OHLC data
    metadata_dir : str
        Location of Metadata
    
    Methods
    -------
    read_list(): void
        Reads static CSV containing tickers into ticker_list, updates if specified
    fetch_metadata(hiccup=int): void
        Fetches metadata and stores as static CSVs
    fetch_data(start_date=datetime.date, end_date=datetime.date, hiccup=5): void
        Fetches OHLC data and stores as static CSVs
    ohlc_updation_check(): dict[str]=datetime.date
        Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values
    update_ohlc(hiccup=int): void
        Updates OHLC data using list from ohlc_updation_check()
    """

    def __init__(self):
        self.fetcher = None
        self.ticker_list = []
        self.ohlc_dir = ''
        self.metadata_dir = ''

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
    
    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), hiccup=5):
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        hiccup: int (5)
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

    def update_ohlc(self, hiccup=5):
        """Updates OHLC data using list from ohlc_updation_check()

        Parameters
        ----------
        hiccup: int (5)
            Pause between every OHLC fetch. Keep > 0 if you don't want to be 
            blacklisted by provider
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
    ohlc_dir : str
        Location of OHLC data
    metadata_dir : str
        Location of Metadata
    
    Methods
    -------
    read_list(url=str, update=bool): void
        Reads static CSV containing tickers into ticker_list
    fetch_metadata(hiccup=int): void
        Fetches metadata and stores as static CSVs
    fetch_data(start_date=datetime.date, end_date=datetime.date, hiccup=int): void
        Fetches OHLC data and stores as static CSVs
    ohlc_updation_check(): dict[str]=datetime.date
        Checks if static CSVs are outdated and returns a dictionary
        of outdated tickers with last date as values
    update_ohlc(hiccup=int): void
        Updates OHLC data using list from ohlc_updation_check(
    """

    def __init__(self):
        super().__init__()
        self.fetcher = Nse()
        self.ticker_list = []

        if not os.path.exists('data'):
            os.makedirs('data')
        self.metadata_dir = 'data'

        if not os.path.exists('data/NSE'):
            os.makedirs('data/NSE')
        self.ohlc_dir = 'data/NSE'

     
    def read_list(self, url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv', update=False):
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
    
    def fetch_metadata(self, hiccup=5):
        """Fetches metadata and stores as static CSVs
        """

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
            time.sleep(hiccup)

        pd.DataFrame.from_dict(meta_data, orient='columns').to_csv("{}/nifty_500_metadata.csv".format(self.metadata_dir))

    def fetch_data(self, start_date=date(1980, 1, 1), end_date=date.today(), hiccup=5):
        """Fetches OHLC data and stores as static CSVs

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of OHLC data
        end_date: datetime.date (Today)
            Ending date of OHLC data
        hiccup: int (5)
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
            time.sleep(hiccup)
    
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
        
        print("Total outdated tickers: {}".format(len(outdated)))
        
        return outdated

    def update_ohlc(self, hiccup=5):
        """Updates OHLC data using dict from ohlc_updation_check()

        Parameters
        ----------
        hiccup: int (5)
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
                time.sleep(hiccup)
        
        else:
            print("OHLC data is up-to-date")