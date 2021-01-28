import numpy as np
from backend.utils import factorial


class UniversalPortfolio:
    """

    """
    def __init__(self, tickers, version='classic', samples=1e2, memory=False, log=False):
        """

        :param tickers:
        :param version:
        :param mesh_points:
        :param memory:
        :param log:
        :return:
        """
        self.tickers = tickers
        self.log = log
        self.memory = memory
        self.samples = int(samples)
        self.dims = len(self.tickers)
        self.sample_portfolios = self._get_samples()
        self.S = np.ones((1, self.dims))
        self.alloc = np.ones((1, self.dims)) / self.dims
        self.volume = 1/factorial(self.dims)
        self._empty = True

    def update(self, x):
        """

        :param x: close_price/open_price
        :return:
        """
        if self._empty:
            self.X = np.array(x)
            self._empty = not self._empty
        else:
            self.X = np.vstack([self.X, x])
        if self.memory:
            pass
        else:
            self.alloc = self.integrate()

    def integrate(self):
        alloc = np.zeros((1, self.dims))
        for sample in self.sample_portfolios:
            print(sample * np.prod(sample * self.X, axis=0))
            alloc += sample * np.prod(sample * self.X, axis=0)
            
        return alloc / sum(alloc)

    def get_alloc(self):
        return self.alloc if not self.memory else self.alloc[-1, :]

    def _get_samples(self):
        """
        Kraemer algorithm for tetrahedeon mesh
        :param dims:
        :param mesh_points:
        :return:
        """
        a = np.sort(np.random.random((self.samples, self.dims-1)))
        a = np.hstack([np.zeros((self.samples, 1)), a, np.ones((self.samples, 1))])
        a = np.diff(a)
        samples = np.zeros(np.shape(a))
        for i, row in enumerate(a):
            samples[i, :] = row / sum(row)
        return samples

