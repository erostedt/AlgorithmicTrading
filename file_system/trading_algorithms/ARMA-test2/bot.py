from collections import deque, defaultdict
import pandas as pd
import statsmodels.api as sm


class Bot:
    """
    Just a test if statmodels is a good resource. Turns out to be so and we should build a framework to use it
    for training time series data.
    """
    def __init__(self):
        self.name = 'Dig sick'
        self.SARIMA = defaultdict(sm.tsa.ARIMA)
        self.train_data = defaultdict(pd.DataFrame)
        self.train_dps = 20
        self.forecast_idx = dict()
        self.seen_commodities = []
        self.actions = []
        self.pos = dict()

    def handle_event(self, event):
        _time, com, price = event
        if com not in self.seen_commodities:
            self.seen_commodities.append(com)
            self.train_data[com] = pd.DataFrame(columns=['price'])
            self.forecast_idx[com] = 0
            self.pos[com] = ""

        self.train_data[com].loc[_time] = price
        num_dps = len(self.train_data[com])
        if num_dps < self.train_dps:
            pass

        elif num_dps % self.train_dps == 0:
            _new_ARIMA = sm.tsa.ARIMA(self.train_data[com], order=(5,1,0))
            _new_ARIMA.enforce_stationarity = False
            new_ARIMA = _new_ARIMA.fit()
            self.SARIMA[com] = new_ARIMA
            self.predictions = self.SARIMA[com].predict(0, self.train_dps)
            self.forecast_idx[com] = 0
        else:
            self.algorithm(price, event,com)

    def algorithm(self, price, event,com):
        if self.pos[com] != 'long':
            if price < self.predictions[self.forecast_idx[com]]:
                self.pos[com] = 'long'
                self.actions.append([event, 'long'])
        else:
            if price > self.predictions[self.forecast_idx[com]]:
                self.pos[com] = 'short'
                self.actions.append([event, 'short'])
        self.forecast_idx[com] += 1
