import yfinance as yf
import time
from datetime import timedelta
from collections import namedtuple
from backend.utils import *


def get_stock_data(tickers, start=None, end=None, period="5y", interval="1d", group_by='column', auto_adjust=False, prepost=False, threads=True,proxy=None):
	"""
	Fetches the stock data (can be multiple at once) with prescribed options like start time etc.
	:return: Stock data.
	"""
	if interval[-1] == "m" and start == None:
		# Might be able to get about one more days worth of data somehow
		start = time.time() - 60*60*24*6
		start = datetime.utcfromtimestamp(start).strftime("%Y-%m-%d")

	return yf.download(tickers=tickers, start=start, end=end, period=period, interval=interval, group_by=group_by, auto_adjust=auto_adjust, prepost=prepost, threads=threads, proxy=proxy)


def get_categories():
	return ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']


def get_cats_in_df(df):
	if isinstance(df.columns[0], tuple):
		cats = []
		for col in df:
			if col[0] not in cats:
				cats.append(col[0])
		return cats


def get_stock_info(ticker):
	"""
	could be somewhat interesting.

	# show dividends
	print(msft.dividends)

	# show splits
	print(msft.splits)

	# show sustainability
	print(msft.sustainability)

	# show options expirations
	print(msft.option)

	# get option chain for specific expiration
	print(msft.option_chain('2020-06-12'))

	popup with more info?
	Infos:
	fullTimeEmployees, sector, country, previousClose, averageDailyVolume10Day, dividend rate, beta, trailingPE, marketCap,
	priceToSalesTrailing12Months, forwardPE, profitMargins, enterpriseToEbitda, forwardEps, bookValue, priceToBook, shortRatio,
	earningsQuarterlyGrowth, pegRatio
	"""
	stock = yf.Ticker(ticker)
	try:
		_stock_info = stock.info
		info_categories = _info_categories()
		stock_info = {cat: info for cat, info in _stock_info.items() if cat in info_categories}

	except:
		return {'Data could not be fetched': ''}
	"""
	try:
		stock_info['recommendations (7d)'] = _recommendations(stock.recommendations['To Grade'], time_frame=7)

	except:
		stock_info['recommendations (7d)'] = 'None'
	"""

	return stock_info


def _info_categories():
	"""
	Returns a list of information categories.
	:return: List of info categories.
	"""
	#'longBusinessSummary'
	return ['fullTimeEmployees', 'sector', 'country', 'previousClose', 'averageDailyVolume10Day',
			'dividendRate', 'beta', 'trailingPE', 'marketCap', 'priceToSalesTrailing12Months', 'forwardPE',
			'profitMargins', 'enterpriseToEbitda', 'forwardEps', 'bookValue', 'priceToBook', 'shortRatio',
			'earningsQuarterlyGrowth', 'pegRatio']


def _recommendations(_ratings, time_frame=30):
	"""
	Returns a tuple of (Positive, Neutral, Negative) recommendations for a stock.
	:param _ratings: Dataframe of ratings.
	:param time_frame (optional): Time frame of the recommendations, default is 30 days.
	:return: Ratings tuple
	"""
	now = datetime.now()
	prior = now - timedelta(days=time_frame)
	_ratings = _ratings[prior:]
	pos, neutral, neg = 0, 0, 0
	pos_ratings = ['Outperform', 'Buy', 'Overweight']
	for rating in _ratings:
		if rating in pos_ratings:
			pos += 1
		elif rating == 'Neutral':
			neutral += 1
		else:
			neg += 1
	rating_tuple = namedtuple('Ratings', ['Positive', 'Neutral', 'Negative'])
	return rating_tuple(Positive=pos, Neutral=neutral, Negative=neg)
