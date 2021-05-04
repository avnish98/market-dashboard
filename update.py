from fetcher import Nifty500Fetcher
from cleaner import Nifty500Cleaner
from processor import IndexProcessor

nft = Nifty500Fetcher()

print("\nFetching Metadata")
nft.fetch_metadata()

print("\nRunning Updation Check")
nft.update_ohlc()

nfc = Nifty500Cleaner()

print("\nCleaning Metadata")
nfc.clean_metadata()

print("\nCleaning OHLC Data")
nfc.clean_ohlc_data()

pp = IndexProcessor("data/cleaned/OHLC/Nifty500", 
                    "data/cleaned/Metadata/nifty500.json", 
                    "data/cleaned/Metadata/proc_nifty500.json")

print("\nProcessing Metrics")
pp.process_metrics()

print("\nFinished")