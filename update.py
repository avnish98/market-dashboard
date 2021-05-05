from fetcher import Nifty500Fetcher
from cleaner import Nifty500Cleaner
from processor import IndexProcessor

nft = Nifty500Fetcher()

flag = 0

while(flag==0):
    option = input("Want to update Metadata? [Y/N]: ")
    if(option == "Y"):
        print("\nFetching Metadata")
        nft.fetch_metadata()
        flag=1
    elif(option=="N"):
        flag=1

print("\nRunning Updation Check")
nft.update_ohlc()

nfc = Nifty500Cleaner()

print("\nCleaning Metadata")
nfc.clean_metadata()

print("\nCleaning OHLC Data")
nfc.clean_ohlc_data()

pp = IndexProcessor("data/cleaned/OHLC/Nifty500", 
                    "data/cleaned/Metadata/nifty500.json")

print("\nProcessing Metrics")
pp.process_metrics()

print("\nFinished")