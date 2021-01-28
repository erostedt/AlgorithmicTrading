import backend.utils as utils
import backend.data_handler.stock_data as sd
from collections import defaultdict
from file_system.file_handler import write_result, read_statistics
import pandas as pd
from importlib import reload


def get_event_list(tickers, interval, start, end):
    """
    Constructs eventlist for the specified parameters. E.g. AAPL and TSLA are tickers, interval is 1 day,
    start is 2019-05-30 and end is 2020-05-30, then the eventlist with the following form:
    [(2019-05-30-00:00:00, AAPL, AAPL_price0), (2019-05-30-00:00:00, TSLA, TSLA_price0),
    (2020-05-31-00:00:00, AAPL, AAPL_price1), (2020-05-31-00:00:00, TSLA, TSLA_price1), ...,
    (2020-05-30-00:00:00, AAPL, AAPL_price364), (2020-05-30-00:00:00, TSLA, TSLA_price364)
    ]
    :param tickers: Stock tickers to be tested on.
    :param interval: Time interval between measurements.
    :param start: Start date/time
    :param end: End date/time
    :return: Sorted (in time) eventlist with all prescribed tickers.
    """
    event_list = []
    for ticker in tickers:
        stock_data = sd.get_stock_data(tickers=ticker, start=start, end=end, interval=interval)
        for timestamp, new_price in stock_data["Close"].iteritems():
            _datetime = utils.convert_timestamp_to_datetime(timestamp)
            event_list.append([_datetime, ticker, new_price])
    event_list.sort(key=lambda x: x[0])
    for i, (datetime, _, _) in enumerate(event_list):
        event_list[i][0] = utils.convert_datetime_to_timestamp(datetime)
    return event_list


def backtest(bots, tickers, interval, start, end):
    """
    Tests the bots on granted stocks/tickers over prescibed time with granted time interval.
    E.g. bots x and y shall be tested on the stocks AAPL (apple) and TSLA (Tesla) from
    start 2019-05-30 to end 2020-05-30 with one day interval. Returns actions done by all bots.
    :param bots: Iterable of bots.
    :param tickers: Tickers to be tested on.
    :param interval: Time interval e.g. 1 day -> one new data point every day (probably closed value).
    :param start: Start time.
    :param end: End time.
    :return: Dictionary of (bot, actions taken by the bot) key value pairs.
    """
    # Get price changes of all stocks sorted by time
    event_list = get_event_list(tickers=tickers, start=start, end=end, interval=interval)
    # Loop over each event and let each bot handle it
    for event in event_list:
        for bot in bots:
            bot.handle_event(event)
    # Save all the different bot.actions in a dictionary
    actions = dict()
    for bot in bots:
        actions[bot.name] = bot.actions
    return actions


def test_portfolios(bots, interval, start, end):
    tickers = bots[0].tickers
    df = sd.get_stock_data(tickers=tickers, interval=interval, start=start, end=end)
    open_df = df['Open']
    close_df = df['Close']

    print('___________________________________________________________________________________________________')

    for time, (_, open_prices), (_, close_prices) in zip(open_df.index, open_df.iterrows(), close_df.iterrows()):
        for bot in bots:
            bot.handle_event((time, open_prices, close_prices))

    result = {}
    for bot in bots:
        result[bot.name + 'Absolute profit/loss'] = bot.balance - bot.init_invest
        result[bot.name + 'Relative profit/loss'] = bot.balance/bot.init_invest

        print('Initial investment:', bot.init_invest)
        print('___________________________________________________________')
        print('Optimal portfolio: ')
        print('final weights:', bot.allocation)
        print('')
        print('Final value:', bot.balance)
        print('Profit:', bot.balance - bot.init_invest)
        print('Relative profit (%):', 100 * (bot.balance/bot.init_invest - 1))
        eq_dist = 1/len(tickers)
        start_prices = close_df.head(1)
        end_prices = close_df.tail(1)

        portfolio = [bot.init_invest * eq_dist / start_prices[ticker][0] for ticker in tickers]
        end_value = sum([end_prices[ticker][0] * num_stock for ticker, num_stock in zip(tickers, portfolio)])
        print('____________________________________________________________')
        print('Equally distributed portfolio: ')
        print('')
        print('Final value:', end_value)
        print('Profit: ', end_value - bot.init_invest)
        print('Relative profit (%):', 100 * (end_value / bot.init_invest - 1))
    return result


def test_algorithms(tickers, interval, start, end, bot_names, algorithm_name):
    """
    Tests the prescribed algorithms and writes all actions to a file as pandas dataframes.
    :param tickers: Tickers be be tested on.
    :param interval: Interval period. E.g. 1d -> One new data point per day.
    :param start: Start date/time
    :param end: End date/time
    :param bot_names: Name of all bots to be tested.
    :param algorithm_name: Name of the algorithm (this name will be the name of the saved file).
    """
    # Load all bots that are selected in the workspace
    bots = [load_agent(name)() for name in bot_names]
    # Get dictionary of the actions that each bot made, where the bot name is the key
    actions = backtest(bots=bots, tickers=tickers, interval=interval, start=start, end=end)

    results = defaultdict(pd.DataFrame)

    for bot in bots:
        all_bot_actions = pd.DataFrame(columns=['Price', 'Position', 'Ticker'])
        for (timestamp, ticker, price), position in actions[bot.name]:
            _df = pd.DataFrame([[price, position, ticker]], columns=['Price', 'Position', 'Ticker'], index=[timestamp])
            all_bot_actions = all_bot_actions.append(_df)
        results[bot.name] = all_bot_actions
    write_result('file_system/results/' + algorithm_name + '.csv', results, tickers, interval, start, end)


def get_score(file):
    statistics = read_statistics(file)
    scores = defaultdict(float)
    for bot_name, statistic in statistics.items():
        correct = statistic['Correct'].sum()
        incorrect = statistic['Incorrect'].sum()
        scores[bot_name] = float(f'{correct/(correct+incorrect):.2f}')
    return scores


def calc_statistics(results):
    statistics = defaultdict(pd.DataFrame)

    perc_profits = _calc_componentwise_percentual_profit(results)
    correct_pos = _calc_correct_positions(results)

    dicts_to_morph = [perc_profits, correct_pos]
    for _dict in dicts_to_morph:
        for bot_name, bot_df in _dict.items():
            statistics[bot_name] = pd.DataFrame(pd.concat([statistics[bot_name], bot_df], axis=1))
    return statistics


def _calc_componentwise_percentual_profit(results):
    """
    Calculates the individual profit multipliers for every prescribed stock for every prescribed bot.
    :param results: Dictionary with (bot name, bot dataframe) as key-value paris.
    :return: Dict of (bot name, profit multiplier dataframe) as key value pair.
    """
    profit_multipliers = defaultdict(pd.DataFrame)
    for bot_name, bot_df in results.items():
        df = pd.DataFrame(columns=['Multiplier'])
        for ticker in bot_df.Ticker.unique():
            ticker_df = bot_df.loc[bot_df['Ticker'] == ticker]
            prices = ticker_df['Price']
            multiplier = 1
            for shift, (price, position) in enumerate(zip(prices[:-1], ticker_df['Position']), start=1):
                multiplier *= prices[shift]/price if position == 'long' else 2 - prices[shift]/price
            df.loc[ticker] = multiplier
        profit_multipliers[bot_name] = df

    return profit_multipliers


def _calc_correct_positions(results):
    guessed_positions = defaultdict(pd.DataFrame)
    for bot_name, bot_df in results.items():
        df = pd.DataFrame(columns=['Correct', 'Incorrect'])
        for ticker in bot_df.Ticker.unique():
            ticker_df = bot_df.loc[bot_df['Ticker'] == ticker]
            prices = ticker_df['Price']
            total_guesses = len(prices) - 1
            corrects = 0
            for shift, (price, position) in enumerate(zip(prices[:-1], ticker_df['Position']), start=1):
                if (position == 'long' and prices[shift] > price) or (position == 'short' and price > prices[shift]):
                    corrects += 1
            df.loc[ticker] = [corrects, total_guesses - corrects]
        guessed_positions[bot_name] = df

    return guessed_positions


def load_agent(name):
    """
    Loads a bot from the bots directory and validates
    its interface
    :param name: Name of bot.
    :return klass: bot class.
    """
    mod_name = "file_system.trading_algorithms." + name + ".bot"
    mod = __import__(mod_name, fromlist=['Bot'])
    reload(mod)
    klass = getattr(mod, 'Bot')
    has_function(klass, name, "handle_event")
    return klass


def has_function(module, bot_name, function_name):
    """
    Checks if bot has the named function.
    """
    op = getattr(module, function_name, None)
    if not callable(op):
        raise NotImplementedError('Bot "{}" does not implement method: "{}"'.format(
            bot_name, function_name))