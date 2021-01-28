
class Bot:
    def __init__(self):
        self.name = "BuyHighSellLow"
        self.positions = dict()
        self.last_ten_days = dict([])
        self.last_twenty_days = dict([])
        self.ten_day_MA = dict()
        self.twenty_day_MA = dict()
        self.actions = []
        self.tickers = []

    def handle_event(self, event):
        timestamp, ticker, new_price = event
        if ticker not in self.tickers:
            self.add_ticker(ticker)

        self.update_MAs(ticker, new_price)
        self.algorithm(ticker, event)

    def algorithm(self, ticker, event):
        if self.ten_day_MA[ticker] > 0 and self.twenty_day_MA[ticker] > 0:
            if self.ten_day_MA[ticker] > self.twenty_day_MA[ticker] and not self.positions[ticker] == "short":
                self.positions[ticker] = "short"
                self.actions.append([event, "short"])

            if self.ten_day_MA[ticker] < self.twenty_day_MA[ticker] and not self.positions[ticker] == "long":
                self.positions[ticker] = "long"
                self.actions.append([event, "long"])

    def update_MAs(self, ticker, new_price):
        if len(self.last_ten_days[ticker]) >= 10:
            self.last_ten_days[ticker].pop(0)
        self.last_ten_days[ticker].append(new_price)

        if len(self.last_twenty_days[ticker]) >= 20:
            self.last_twenty_days[ticker].pop(0)
        self.last_twenty_days[ticker].append(new_price)

        self.ten_day_MA[ticker] = self.calc_MA(self.last_ten_days[ticker], 10)
        self.twenty_day_MA[ticker] = self.calc_MA(self.last_twenty_days[ticker], 20)

    def add_ticker(self, ticker):
        self.tickers.append(ticker)
        self.last_ten_days[ticker] = []
        self.last_twenty_days[ticker] = []
        self.ten_day_MA[ticker] = -1
        self.twenty_day_MA[ticker] = -1
        self.positions[ticker] = "none"

    @staticmethod
    def calc_MA(data, days):
        if len(data) == days:
            return sum(data)/days
        else:
            return -1

