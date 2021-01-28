import pandas as pd
from copy import copy
import backend.portfolio_management.efficient_frontier as eff


class Bot:
    def __init__(self, tickers):
        self.name = "EF"
        self.tickers = tickers
        self.prices = pd.DataFrame(columns=self.tickers)
        self.actions = []
        self.tf = 252
        self.init_invest = 1000000
        self.balance = copy(self.init_invest)
        self._needs_training = True
        self.final_value = None
        self.ef = None

    def handle_event(self, event):
        time, open_prices, close_prices = event
        if self._needs_training:
            m, n = self.prices.shape
            self.prices.loc[time] = close_prices
            if m == self.tf:
                self._needs_training = not self._needs_training
                self.ef = eff.EfficientFrontier(self.prices, rf=0.02, num_trade_days=252)
                self.allocation = self.ef.p_allocation

        else:
            self.algorithm(open_prices, close_prices)

    def algorithm(self, open_prices, close_prices):
        self.buy(open_prices)
        self.sell(close_prices)
        self.ef.update_window(close_prices, recalculate_cov=True)
        self.allocation = self.ef.p_allocation

    def buy(self, buy_prices):
        self.investments = [self.balance * alloc / buy_prices[i] for i, alloc in enumerate(self.allocation)]
        self.balance = 0

    def sell(self, sell_prices):
        self.balance = sum([invest * sell_prices[i] for i, invest in enumerate(self.investments)])
        self.investments = [0 for _ in self.allocation]
