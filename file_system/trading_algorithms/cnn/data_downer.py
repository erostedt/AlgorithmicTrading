import numpy as np
import pandas as pd
import csv
from collections import namedtuple

import yfinance as yf
def load_ticker_name_info(exchange):
    """
    Fetches stock ticker and company name from an exchange and returns them as a list of namedtuples.
    :param exchange: Choice of stock exchange.
    :return: List of namedtuples with stock ticker and company name from stock exchange.
    """
    with open("file_system/data/Tickers/" + exchange + ".csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_file)
        company = namedtuple("company_info", ["ticker", "name"])
        stock_info = [company(stock[0], stock[1]) for stock in csv_reader]
        return stock_info


NAZIDAQ = load_ticker_name_info("NASDAQ")
prices = []
for i in range(30): 
    apple = yf.download(NAZIDAQ[i][0], period='5y', interval='1d')
    prices.append(np.array(apple["Close"].values))
prices = np.array(prices)
np.save("nasdaq30", prices)
