import csv
from collections import defaultdict
#sys.path.append('..')
import os.path
import os
import backend.data_handler.stock_data as sd
import pickle
from backend.stochastic_processes.statistics import *


def export(tickers, name, start=None, end=None, interval="1d"):
    stocks_df = sd.get_stock_data(tickers=tickers, start=start, end=end, interval=interval)
    path = 'file_system/exports/'
    if not os.path.exists(path):
        os.mkdir(path)
    _info = {}
    for ticker in tickers:
        _info[ticker] = sd.get_stock_info(ticker)

    core_info = {"price": stocks_df, "info": _info}

    pickle.dump(core_info, open(path + name, 'wb'))


def read_result(file):
    """
    Reads file and construct a dictionary with (bot name, bot dataframe) as key-value pair.
    :param file: File to be read.
    :return: Result dictionary.
    """
    bots = defaultdict(pd.DataFrame)
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        tickers = next(csv_reader)
        [interval, start, end] = next(csv_reader)
        if end == "None":
            end = None
        num_bots = int(next(csv_reader)[0])
        bot_idx = 0
        while bot_idx < num_bots:
            bot_info = next(csv_reader)
            bot_name = bot_info[0]
            num_actions = int(bot_info[1])
            cols = next(csv_reader)[1:]
            df = pd.DataFrame(columns=cols)
            for action_idx in range(num_actions):
                timestamp, price, position, ticker = next(csv_reader)
                df = df.append(pd.DataFrame([[float(price), position, ticker]], columns=cols, index=[timestamp]))
            bots[bot_name] = df
            bot_idx += 1
    return bots, tickers, interval, start, end


def write_result(file, results, tickers, interval, start, end):
    """
    Writes results to a file. Results assumed to be a dictionary with (bot name, bot dataframe) as key-value pair.

    DATA STORAGE INFO: First row contains number of bots. Thereafter the following rows have the following structure:
    bot name, Number of actions.
    Dataframe columns: '', Price, Position, Ticker.
    action
    action
    ...
    action
    bot name, number of actions
    etc.

    :param file: filepath.
    :param results: Results to be written to file.
    :param tickers: Tickers of commodities tested upon.
    :param interval: Time interval, 1d -> One new data point per day.
    :param start: Start time.
    :param end: End time.
    """

    # Doesnt work on all computers for some reason
    #dir_name = os.path.dirname(file)
    #if not os.path.exists(dir_name):
    #    os.mkdir(dir_name)

    if not end:
        end = 'None'
    with open(file, 'w', newline='') as f:
        f.write(",".join(tickers) + "\n")
        f.write(",".join([interval, start, end]) + "\n")

        f.write(str(len(results)) + '\n')

    for bot_name, df in results.items():
        with open(file, 'a', newline='') as f:
            f.write(bot_name + ',' + str(len(df.index)) + '\n')
            df.to_csv(f, index=True)


def read_statistics(file):
    """
    Reads file and construct a dictionary with (bot name, bot dataframe) as key-value pair.
    :param file: File to be read.
    :return: Statistics dictionary.
    """
    bots = defaultdict(pd.DataFrame)
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        num_bots = int(next(csv_reader)[0])
        bot_idx = 0
        while bot_idx < num_bots:
            bot_info = next(csv_reader)
            bot_name = bot_info[0]
            num_tickers = int(bot_info[1])
            cols = next(csv_reader)[1:]
            df = pd.DataFrame(columns=cols)
            for ticker_idx in range(num_tickers):
                ticker, *_params = next(csv_reader)
                params = []
                for param in _params:
                    if '.' in param:
                        params.append(f'{float(param):.2f}')
                    else:
                        params.append(int(param))
                df = df.append(pd.DataFrame([params], columns=cols, index=[ticker]))
            bots[bot_name] = df
            bot_idx += 1
    return bots


def write_statistics(file, statistics):
    """
    Writes statistics to a file. Results assumed to be a dictionary with (bot name, bot dataframe) as key-value pair.

    DATA STORAGE INFO: First row contains number of bots. Thereafter the following rows have the following structure:
    bot name, number of tickers
    Dataframe columns: '', params
    ticker, params
    ticker, params
    ...
    ticker, params
    bot name, number of tickers
    etc.

    :param file: filepath.
    :param statistics: statistics to be written to file.
    """

    dir_name = os.path.dirname(file)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    with open(file, 'w', newline='') as f:
        f.write(str(len(statistics)) + '\n')

    for bot_name, df in statistics.items():
        with open(file, 'a', newline='') as f:
            f.write(bot_name + ',' + str(len(df.index)) + '\n')
            df.to_csv(f, index=True)
