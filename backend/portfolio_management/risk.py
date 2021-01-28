import pandas as pd
import numpy as np
from backend.stochastic_processes.timeseries import pct_change
from backend.stochastic_processes.statistics import cov, mean
from backend.stochastic_processes.sde import GBM
import seaborn as sns
import matplotlib.pyplot as plt


def VaR(df, weights, avg_returns=None, cov_m=None, investment=None, percentile=5, days=1, method='gbm'):
    """
    Value-at-Risk
    :param df:
    :param weights:
    :param investment:
    :param percentile:
    :param days:
    :return:
    """

    # OBS! KAN VARA SKEVT ATT PASSA SUM(START_PRICE * WEIGHTS), kolla upp.
    # KOlla var hit, och var backtesting.

    if not avg_returns or not cov_m:
        returns = pct_change(df, shift=1).dropna()

    if not avg_returns:
        avg_returns = mean(returns)

    if not cov_m:
        cov_m = cov(returns)

    mu, sigma = avg_returns @ weights, np.sqrt(weights.T @ cov_m @ weights)

    sims = int(1e5)
    start_price = sum(df.iloc[-1] * weights)
    gbm = GBM(start_value=start_price, avg_returns=mu, avg_vol=sigma)
    sT = gbm.simulate(steps=days, sims=sims)

    diff = sT - start_price
    _vars = [0 for _ in range(days)]

    for i, row in enumerate(diff):
        if i == 8:
            sns.distplot(np.sort(row))
            plt.show()
        _vars[i] = -np.percentile(np.sort(row), percentile) / start_price
        if investment:
            _vars[i] *= investment
        else:
            _vars[i] *= 100

    if investment:
        _vars = pd.DataFrame(_vars, columns=['VaR (Absolute)'], index=range(days))
    else:
        _vars = pd.DataFrame(_vars, columns=['VaR (Relative %)'], index=range(days))

    return _vars
