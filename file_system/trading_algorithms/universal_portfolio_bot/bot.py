import pandas as pd
import backend.portfolio_management.universal_portfolio as unip
from copy import copy

class Bot:

    def __init__(self, tickers):
        self.name = "EF"
        self.tickers = tickers
        self.init_invest = 1000000
        self.balance = copy(self.init_invest)
        self.up = unip.UniversalPortfolio(self.tickers, version='classic', samples=1e2, memory=False, log=False)
        self.allocation = self.up.get_alloc()

    def handle_event(self, event):
        time, open_prices, close_prices = event
        self.algorithm(open_prices, close_prices)

    def algorithm(self, open_prices, close_prices):
        self.buy(open_prices)
        self.sell(close_prices)
        self.up.update(close_prices/open_prices)
        self.allocation = self.up.get_alloc()

    def buy(self, buy_prices):
        self.investments = [self.balance * alloc / buy_prices[i] for i, alloc in enumerate(self.allocation)]
        self.balance = 0

    def sell(self, sell_prices):
        self.balance = sum([invest * sell_prices[i] for i, invest in enumerate(self.investments)])
        self.investments = [0 for _ in self.allocation]
