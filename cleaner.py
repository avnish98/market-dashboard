import os
import json

import pandas as pd

from utils import find_in_json, write_json

class Cleaner:
    def __init__(self):
        self.ohlc_raw_data = 'data/raw/'
        self.ohlc_clean_data = 'data/cleaned/OHLC/'
        self.metadata_raw = 'data/raw'
        self.metadata_clean = 'data/cleaned/Metadata'
    
    def clean_ohlc_data(self):
        pass
    
    def clean_metadata(self):
        pass

class Nifty500Cleaner(Cleaner):
    def __init__(self):
        super().__init__()
        self.ohlc_raw_data = 'data/raw/Nifty500'
        self.ohlc_clean_data = 'data/cleaned/OHLC/Nifty500'
    
    def clean_ohlc_data(self):
        for file in os.listdir(self.ohlc_raw_data):
            try:
                temp_df = pd.read_csv("{}/{}".format(self.ohlc_raw_data,file))
                if(temp_df.shape[0] != 0):
                    temp_df.set_index('Date').dropna().to_csv('{}/{}'.format(self.ohlc_clean_data, file))
            except Exception as e:
                print("Exception {} occured for file: {}".format(e, file))
    
    def clean_metadata(self):
        metadata_json = []
        metadata1 = pd.read_csv('{}/nifty_500_list.csv'.format(self.metadata_raw)).to_dict(orient='records')
        metadata2 = pd.read_csv('{}/nifty_500_metadata.csv'.format(self.metadata_raw)).to_dict(orient='records')

        for entry in metadata1: 
            entry2 = find_in_json(metadata2, 'symbol', entry['Symbol'])

            if(entry2 is not None):
                metadata_json.append({
                    'Ticker': entry['Symbol'],
                    'Company Name': entry['Company Name'],
                    'Sector':entry['Industry'],
                    'Price':entry2['closePrice'],
                    'Book Closure End Date':entry2['bcEndDate'],
                    'Book Closure Start Date':entry2['bcStartDate'],
                    'Ex Date':entry2['exDate'],
                    'Purpose of Last Meeting':entry2['purpose'],
                    'Record Date':entry2['recordDate'],
                    'OHLC Data Location':'{}/{}.csv'.format(self.ohlc_clean_data, entry['Symbol'])
                })
        
        write_json(metadata_json, '{}/nifty500.json'.format(self.metadata_clean))