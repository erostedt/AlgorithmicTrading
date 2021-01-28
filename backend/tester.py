import file_system.trading_algorithms.Efficient_frontier.bot as ef_bot
import backend.portfolio_management.efficient_frontier as ef
from backend.stochastic_processes.sde import SDE, OrnsteinUhlenbeck, GBM
import backend.portfolio_management.risk as risk
import backend.data_handler.stock_data as sd
import backend.algorithm as algo
import matplotlib.pyplot as plt


#tickers = ['ERIC-B.ST',
#        'HM-B.ST',
#        'ASSA-B.ST',
#        'SHB-B.ST'
#        ]
#bots = [ef_bot.Bot(tickers)]
#algo.test_portfolios(bots, interval='1d', start='2017-07-16', end=None)


#stocks = sd.get_stock_data(tickers)
#stocks = stocks['Close']

#_ef = ef.EfficientFrontier(stocks)
#alloc = _ef.p_allocation

ou = OrnsteinUhlenbeck(start_value=45, mean=50, std=5, theta=1, interval='D')

sims = ou.simulate(20, sims=3)
t = list(range(1, 21))

fig, ax = plt.subplots()
for sim in sims.T:
        ax.plot(t, sim)

plt.show()

#print(risk.VaR(stocks, alloc, days=9))
#print(risk.VaR(stocks, alloc, investment=100000, days=9))


