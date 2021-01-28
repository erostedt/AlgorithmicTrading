import backend.data_handler.stock_data as sd
from collections import defaultdict
from file_system.file_handler import read_result
import pandas as pd
import backend.stochastic_processes.timeseries as ts


def get_stocks(tickers, plot_style, params=None, start=None, end=None, interval="1d", price_type="Close"):
    """
    Gets the stock data for prescribed tickers, start time, end time, time interval, price type.
    Applies (optionally) data transformations and returns list of timestamps and a dataframe of the prices.
    :param tickers: Tickers to be fetched.
    :param plot_style: Data transformations (e.g. moving average).
    :param params: Parameters for data transformation.
    :param start: Start time.
    :param end: End time.
    :param interval: Time interval. E.g. 1d -> one new data point per day.
    :param price_type: Which price to be fetched. E.g. Daily highest price, Closing price etc.
    :return: list of timestamps and a dataframe of the prices.
    """
    stock_data = sd.get_stock_data(tickers, interval=interval, start=start, end=end)
    stock_data = stock_data[price_type]

    # If we do not want to apply any transformation, return the regular stock data
    if plot_style == 'None' or not plot_style:
        return stock_data

    if not params or params == 'None':
        params = ''
    else:
        params = ', ' + params
    prices = dict()
    if len(tickers) == 1:
        prices[tickers[0]] = eval(plot_style + '(stock_data' + params + ')')

    else:
        for ticker, _prices in stock_data.items():

            prices[ticker] = eval(plot_style + '(_prices' + params + ')')

    new_df = pd.DataFrame()
    for df in prices.values():
        new_df = pd.concat([new_df, df], axis=1)

    return new_df


def get_result(result_name):
    """
    Fetches the prescribed file name and structure the result so that the plotter can easily read and plot the result.
    :param result_name: Name of the file.
    :return: Structured result dictionary.
    """
    result, tickers, interval, start, end = read_result('file_system/results/' + result_name + '.csv')
    structure_results = defaultdict(defaultdict)
    for bot_name, df in result.items():
        # Loop over all stocks that the algorithm was tested on
        bot_results = defaultdict(tuple)
        for ticker in df.Ticker.unique():
            actions = df.loc[df['Ticker'] == ticker]
            # Separate long and short positions and scatter with different markers
            x_long, x_short, y_long, y_short = [], [], [], []
            for timestamp, price, position in zip(actions.index, actions['Price'], actions['Position']):
                if position == 'long':
                    x_long.append(timestamp)
                    y_long.append(price)
                else:
                    x_short.append(timestamp)
                    y_short.append(price)

            long = pd.Series(y_long, index=x_long)
            short = pd.Series(y_short, index=x_short)
            bot_results[ticker] = (long, short)
        structure_results[bot_name] = bot_results
    return structure_results, tickers, interval, start, end

