import pandas as pd

class Processor:
    def __init__(self):
        self.exchange = ''
        self.stock_name = ''
        self.ohlc_data = pd.DataFrame
        self.meta_data = []
    
    def process_metadata():
        pass
    
    def process_ohlc():
        pass


class NSEProcessor:
    def __init__(self, exchange='NSE', stock_name='3MINDIA'):
        self.exchange = exchange
        self.stock_name = stock_name
        self.ohlc_data = pd.read_csv('static_files/{}/{}.csv'.format(self.exchange, self.stock_name))
        self.meta_data = pd.merge(pd.read_csv('static_files/nifty_500_metadata.csv'),
                                pd.read_csv('static_files/nifty_500_list.csv'), how='inner', left_on='symbol', 
                                right_on='Symbol')

    def process_metadata(self):
        raw_dump = self.meta_data[self.meta_data['Symbol']==self.stock_name].to_dict(orient='records')[0]
        metadata_dump = {"Open":"", 
                 "Close":"",
                 "High":"",
                 "Low":"",
                 "Sector":"",
                 "% Change":"",
                 "Volume":""}

        metadata_dump['Open'] = raw_dump['open']
        metadata_dump['Close'] = raw_dump['closePrice']
        metadata_dump['High'] = raw_dump['dayHigh']
        metadata_dump['Low'] = raw_dump['dayLow']
        metadata_dump['Sector'] = raw_dump['Industry'].capitalize()
        metadata_dump['% Change'] = raw_dump['pChange']
        metadata_dump['Volume'] = raw_dump['totalTradedVolume']
        
        return metadata_dump

    
    def process_ohlc(self):
        return self.ohlc_data.fillna('bfill') 