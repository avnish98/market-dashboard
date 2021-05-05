from fetcher import Nifty500Fetcher
from cleaner import Nifty500Cleaner
from processor import IndexProcessor

nff = Nifty500Fetcher()

print("\nReading Nifty500 ticker list")
nff.read_list(update=True)

print("\nFetching Metadata")
nff.fetch_metadata()

print("\nFetching OHLC Data")
nff.fetch_data()

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