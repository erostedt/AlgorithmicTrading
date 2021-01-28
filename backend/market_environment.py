import pandas as pd
import backend.data_handler.stock_data as sd


class MarketEnvironment(object):

    def __init__(self, name, date):
        self.name = name
        self.date = date

    def get_prices(self, tickers, start, end, interval='1d', price_type='Adj close'):
        if end > self.date or start > self.date:
            raise PermissionError

        return sd.get_stock_data(tickers=tickers, start=start, end=end, interval=interval)[price_type]

    def advance(self):
        # Update time
        pass

