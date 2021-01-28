import numpy as np
import pandas as pd
from abc import abstractmethod, ABC

"""
File that shall be filled with functions related to Stochastic Differential Equations.

Could be relevant:
https://github.com/mattja/sdeint/tree/master/sdeint
"""


class SDE(ABC):

    def __init__(self):
        pass

    @staticmethod
    def brownian_motion(length, dt=1., num_bms=1):
        """
        Calculates a brownian motion.
        :param length: Length of brownian motion.
        :param num_bms: How many brownian motions to be simulated.
        :return: Matrix of brownian motion processes.
        """
        b = np.random.normal(0, np.sqrt(dt), (length, num_bms))
        W = np.cumsum(b, axis=0)
        return W

    @abstractmethod
    def integrate(self, *args):
        pass

    @abstractmethod
    def simulate(self, *args):
        pass


class GBM(SDE):

    def __init__(self, start_value, avg_returns, avg_vol, interval='D'):
        super(GBM, self).__init__()
        self.avg_returns = avg_returns
        self.avg_vols = avg_vol
        self.interval = interval

        self.start_time = 0
        self.start_price = start_value

    def integrate(self, steps, bm=None):
        t = np.arange(steps)
        expected_returns, expected_vols = self.avg_returns * steps, self.avg_vols * np.sqrt(steps)

        if bm is None:
            bm = self.brownian_motion(steps)

        drift = (expected_returns - 0.5 * np.power(expected_vols, 2)) * t
        diffusion = expected_vols * bm
        stock_prices = self.start_price * np.exp(drift + diffusion)

        return stock_prices

    def simulate(self, steps, sims=1e5):
        simulations = np.zeros((steps, sims))
        sims = int(sims)
        bms = self.brownian_motion(steps, num_bms=sims).T
        for i, bm in enumerate(bms):
            simulations[:, i] = self.integrate(steps, bm=bm)

        return simulations


class OrnsteinUhlenbeck(SDE):
    """
    Solver to the SDE:

    dS_t = theta * (mu - S_t) * dt + sigma * dB_t

    method: Euler-Maruyama -> S_t = S_{t-1} + a(S_{t-1}) dt + b(S_{t-1}) dB_{t-1}

    :param start_price: Initial stock price.
    :param avg_return: Expected average return
    :param vol: Expected (average) volatility
    :param steps: Length of process.
    :param theta: Optional scaling term for the drift (optional).
    :return: Estimated future returns based on the Ornstein-Uhlenbeck SDE.
    """

    def __init__(self, start_value, mean, std, theta=0, interval='D'):
        super(OrnsteinUhlenbeck, self).__init__()
        self.theta = theta
        self.mean = mean
        self.std = std
        self.interval = interval

        self.start_time = 0
        self.start_price = start_value

    def integrate(self, steps, bm=None, dt=1.):
        t = np.arange(steps)

        stock_prices = np.zeros(steps)
        stock_prices[0] = self.start_price

        if bm is None:
            bm = self.brownian_motion(steps)

        dB = bm[1:] - bm[:-1]

        for step in range(1, steps):
            stock_prices[step] = stock_prices[step - 1] + self.theta * (
                        self.mean - stock_prices[step - 1]) * dt + self.std * dB[step - 1]

        return stock_prices

    def simulate(self, steps, sims=1e5):
        simulations = np.zeros((steps, sims))
        sims = int(sims)
        bms = self.brownian_motion(steps, num_bms=sims).T
        for i, bm in enumerate(bms):
            simulations[:, i] = self.integrate(steps, bm=bm, dt=1.)

        return simulations


def runge_kutta():
    """
    Might be added later.
    """
    pass
