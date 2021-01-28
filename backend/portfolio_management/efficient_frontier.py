from copy import copy
import numpy as np
import pandas as pd
from backend.stochastic_processes.statistics import mean, cov
import scipy.optimize as opt


class EfficientFrontier:
    """
    A class which finds the optimal stock allocation from a dataframe of stocks with history of prices.
    Used for risk management. Not relevent for algorithmic trading but suitable for riskmanagement (hedgeing).
    """
    def __init__(self, df, rf=0.02, num_trade_days=252, allow_neg_weights=False):
        """

        :param df:
        :param rf:
        :param log:
        :param num_trade_days:
        """
        # Prep
        self.rf = rf
        self.num_trade_days = num_trade_days
        self.allow_neg_weights = allow_neg_weights

        self.prev_prices = np.log(df.tail(1).iloc[0])
        self.stocks = [stock for stock in df.columns]
        self.num_stocks = len(self.stocks)

        self.returns = (np.log(df) - np.log(df.shift(1))).dropna()
        self.expected_returns = mean(self.returns) * self.num_trade_days
        self.expected_cov_m = cov(self.returns) * self.num_trade_days

        if not allow_neg_weights:
            self.constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            self.bounds = tuple((0, 1) for _ in self.stocks)

        self.solve()

    def get_stats(self, weights):
        p_ret = np.sum(self.expected_returns * weights)
        p_vol = np.sqrt(weights.T @ self.expected_cov_m @ weights)
        return np.array([p_ret, p_vol, p_ret / p_vol])

    def get_neg_sharpe(self, weights):
        return -self.get_stats(weights)[2]

    def solve(self):
        if self.allow_neg_weights:
            _allocation = np.linalg.solve(self.expected_cov_m, self.expected_returns)
            self.p_allocation = _allocation / sum(_allocation)

        else:
            _opt = opt.minimize(self.get_neg_sharpe, np.ones(self.num_stocks) / self.num_stocks, method='SLSQP',
                                bounds=self.bounds, constraints=self.constraints)

            self.p_allocation = _opt['x']

        self.p_return, self.p_std, self.p_sharpe = self.get_stats(self.p_allocation)

    def return_allocation(self, target_return):
        wp = (target_return - self.rf)/(self.p_return - self.rf)
        _opt_alloc = wp*self.p_allocation
        cols = copy(self.stocks)
        cols.append('rf')
        _opt_alloc = np.append(_opt_alloc, 1-wp)
        return pd.DataFrame([_opt_alloc], columns=cols, index=[f'W for return={target_return}'])

    def risk_allocation(self, target_risk):
        wp = (target_risk/self.p_std)
        _opt_alloc = wp*self.p_allocation
        cols = copy(self.stocks)
        cols.append('rf')
        _opt_alloc = np.append(_opt_alloc, 1-wp)
        return pd.DataFrame([_opt_alloc], columns=cols, index=[f'W for vol={target_risk}'])

    def update_window(self, row_to_add, recalculate_cov=False):
        # Fix log later
        row_to_add = np.log(row_to_add)
        _return = row_to_add - self.prev_prices
        e_return = _return * self.num_trade_days


        self.expected_returns = (1/self.num_trade_days) * ((self.num_trade_days - 1) * self.expected_returns + e_return)

        self.returns.loc[row_to_add.name] = e_return
        self.returns.drop(self.returns.index[0], inplace=True)

        if recalculate_cov:
            self.expected_cov_m = cov(self.returns) * self.num_trade_days

        else:
            # ej klar
            pass

        self.prev_prices = row_to_add
        self.solve()
