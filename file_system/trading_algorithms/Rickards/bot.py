from collections import deque, defaultdict
import numpy as np

class Bot:
    def __init__(self):
        self.name = "MeanReversion"
        self.plot_style = 'Percentual change'
        self.positions = dict()
        self.last_thirty = defaultdict(deque)
        self.mean = defaultdict(int)
        self.std = defaultdict(int)
        self.last_price = defaultdict(int)
        self.actions = []
        self.tickers = []

    def handle_event(self, event):
        timestamp, ticker, new_price = event
        if ticker not in self.tickers:
            self.add_ticker(ticker)

        self.algorithm(event)
        self.update_data(ticker, new_price)

    def algorithm(self, event):
        timestamp, ticker, new_price = event
        if len(self.last_thirty[ticker]) >= 30:
            change = 100*(new_price - self.last_price[ticker])/self.last_price[ticker]
            if abs(change) > self.mean[ticker] + 1.5*self.std[ticker]:
                if change > 0 and not self.positions[ticker] == "short":
                    self.positions[ticker] = "short"
                    self.actions.append([event, "short"])

                if change < 0 and not self.positions[ticker] == "long":
                    self.positions[ticker] = "long"
                    self.actions.append([event, "long"])

    def update_data(self, ticker, new_price):
        if len(self.last_thirty[ticker]) >= 30:
            self.last_thirty[ticker].popleft()
        self.last_thirty[ticker].append(new_price)

        perc_change_over_time = self.calc_perc_change(list(self.last_thirty[ticker]))
        self.mean[ticker] = np.mean(perc_change_over_time)
        self.std[ticker] = np.std(perc_change_over_time)
        self.last_price[ticker] = new_price

    def add_ticker(self, ticker):
        self.tickers.append(ticker)
        self.positions[ticker] = "none"

    @staticmethod
    def calc_perc_change(data):
        return [100.0 * a1 / a2 - 100 for a1, a2 in zip(data[1:], data)]
