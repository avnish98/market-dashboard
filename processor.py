"""Processor module

This script contains processor classes for metadata and OHLC data.

It contains following classes
    * Processor: Base Processor Class
    * StockProcessor: Derived Cleaner Class for processing data of 
                     individual stocks
    * IndexProcessor: Derived Cleaner Class for processing data of 
                     all stocks present in index
"""

import os
from datetime import date, datetime

import pandas as pd

from ds import Portfolio, Stock
from utils import read_json, find_in_json, write_json, write_csv, get_close_df


class Processor:
    """
    Base class to represent a Processor

    ...

    Attributes
    ----------
    ohlc_location : str
        Location of OHLC Cleaned data
    metadata_loc : str
        Location of Cleaned Metadata
    
    Methods
    -------
    process_metrics(): void
        Calculates required metrics and stores them in CSV format
    """

    def __init__(self, ohlc_loc=None, metadata_loc=None):
        self.ohlc_location = ohlc_loc
        self.metadata_loc = metadata_loc

    def process_metrics(self):
        """Calculates required metrics and stores them in CSV format
        """

        pass


class StockProcessor(Processor):
    """
    Derived class to represent a Stock Processor

    ...

    Attributes
    ----------
    ohlc_location : str
        Location of OHLC Cleaned data
    metadata_loc : str
        Location of Cleaned Metadata
    stock: Stock()
        Stock Object
    
    Methods
    -------
    process_metrics(): void
        Calculates required metrics and stores them in CSV format for OHLC data
        Updates location and availability data for OHLC in metadata
    """

    def __init__(self, symbol=None, ohlc_loc=None, metadata_loc=None):
        super().__init__()
        self.stock = Stock()
        self.stock.load(find_in_json(read_json(metadata_loc), 'Ticker', symbol))
    
    def process_metrics(self, upper_margin=0.05, lower_margin=0.05, bband_ma=20,
                        bband_std=2):
        """Calculates required metrics and stores them in CSV format for OHLC data 
        Updates location and availability data for OHLC in metadata

        Parameters
        ----------
        upper_margin: float (0.05)
            Profit Exit in Percentage
        lower_margin: float (0.05)
            Stop Loss in Percentage
        bband_ma: int (20)
            Number of days for Moving Average for Bollinger Bands
        bband_std: int (2)
            Multiplier for Standard Deviation for Bollinger Bands
        """

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

            ohlc_data_latest = ohlc_data.tail(1).to_dict(orient='records')[0]

            self.stock.metadata['OHLC Data Available'] = True
            self.stock.metadata['Profit Exit'] = ohlc_data_latest['Profit Exit']
            self.stock.metadata['Stop Loss'] = ohlc_data_latest['Stop Loss']
            self.stock.metadata['Bollinger Band Up'] = ohlc_data_latest['Bollinger Band Up']
            self.stock.metadata['Bollinger Band Down'] = ohlc_data_latest['Bollinger Band Down']

            mp = self.stock.metadata['OHLC Data Location'].replace('cleaned', 'processed')
            self.stock.metadata['OHLC Data Location'] = mp

            write_csv(ohlc_data, self.stock.ohlc.replace('cleaned', 'processed'))

        except FileNotFoundError as e:            
            self.stock.metadata['Profit Exit'] = None
            self.stock.metadata['Stop Loss'] = None
            self.stock.metadata['Bollinger Band Up'] = None
            self.stock.metadata['Bollinger Band Down'] = None
            self.stock.metadata['OHLC Data Available'] = False
            self.stock.metadata['OHLC Data Location'] = None
            print("File not present: {}".format(self.stock.ohlc))


class IndexProcessor(Processor):
    """
    Derived class to represent a Index Processor

    ...

    Attributes
    ----------
    ohlc_location : str
        Location of OHLC Cleaned data
    metadata_loc : str
        Location of Cleaned Metadata
    metadata_json: list[dict]
        JSON containing metadata of all the stocks
    proc_metadata_loc: str
        Location of Processed metadata to be stored
    close_matrix: pd.DataFrame
        Matrix containing close price of all the stocks in index, over time
            
    Methods
    -------
    process_metrics(): void
        Processes metrics for each stock individually
    process_close(start_date=datetime.date, end_date=datetime.date): void
        Processes close price matrix out of OHLC data
    """

    def __init__(self, ohlc_loc=None, metadata_loc=None):
        super().__init__()
        self.ohlc_location = ohlc_loc
        self.metadata_json = read_json(metadata_loc)
        self.metadata_loc = metadata_loc
        self.proc_metadata_loc = metadata_loc.replace('cleaned', 'processed')
        self.close_matrix = pd.DataFrame
        
        if not os.path.exists(self.ohlc_location.replace('cleaned', 'processed')):
                os.makedirs(self.ohlc_location.replace('cleaned', 'processed'))

    
    def process_metrics(self, upper_margin=0.05, lower_margin=0.05, bband_ma=20,
                        bband_std=2):
        """Processes metrics for each stock individually

        Parameters
        ----------
        upper_margin: float (0.05)
            Profit Exit in Percentage
        lower_margin: float (0.05)
            Stop Loss in Percentage
        bband_ma: int (20)
            Number of days for Moving Average for Bollinger Bands
        bband_std: int (2)
            Multiplier for Standard Deviation for Bollinger Bands
        """

        new_meta_json = []
        for entry in self.metadata_json:
            sp = StockProcessor(entry['Ticker'], 
                                entry['OHLC Data Location'], 
                                self.metadata_loc)
            sp.process_metrics(upper_margin, lower_margin, bband_ma,
                        bband_std)
            new_meta_json.append(sp.stock.metadata)
        write_json(new_meta_json, self.proc_metadata_loc)
        
    def process_close(self, start_date=date(1980, 1, 1), end_date=date.today()):
        """Processes close price matrix out of OHLC data

        Parameters
        ----------
        start_date: datetime.date (1/1/1980)
            Starting date of data
        end_date: datetime.date (Today)
            Ending date of data
        """

        proc_loc = self.ohlc_location.replace('cleaned', 'processed')
        files = os.listdir(proc_loc)
        file_sizes = [os.path.getsize("{}/{}".format(proc_loc, f)) for f in files]

        file_data = dict(zip(files, file_sizes))
        file_data = {k: v for k, v in sorted(file_data.items(), key=lambda item: item[1], reverse=True)}
        df_list = []

        for f in list(file_data.keys()):
            df_list.append(get_close_df(proc_loc, f, start_date, end_date))

        self.close_matrix = pd.concat(df_list, axis=1, join='outer')


class PortfolioProcessor(Processor):
    """
    Derived class to represent a Portfolio Processor

    ...

    Attributes
    ----------
    ohlc_location : str
        Location of OHLC Cleaned data
    metadata_loc : str
        Location of Cleaned Metadata
            
    Methods
    -------
    """

    def __init__(self):
        super().__init__()
        pass