import pandas as pd

class Stock:
    def __init__(self):
        self.ticker = ""
        self.name = ""
        self.ohlc = pd.DataFrame
        self.metadata = {}

class Portfolio:
    def __init__(self):
        self.stocks = []
        self.composition = {}
        self.statistics = {}