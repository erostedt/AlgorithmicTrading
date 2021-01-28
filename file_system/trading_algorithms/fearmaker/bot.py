import numpy as np

class Bot:
    def __init__(self):
        self.name = "fear"
        self.actions = []
        self.smooth_data = {}
        self.data = {}

    def handle_event(self, event):
        unix_time, ticker, new_price = event
        if ticker not in self.data:
            self.data[ticker] = []
            self.smooth_data[ticker] = []

        self.data[ticker].append(event)
        self.smooth_data[ticker].append(self.calc_MA(self.data[ticker],10))
        self.algorithm()
        

    def algorithm(self):
        self.actions = []
        for ticker,price in self.data.items():

            pos = None
            if len(self.smooth_data[ticker]) < 10:
                continue            

            deriv = np.convolve(self.smooth_data[ticker], [-1, 1])
            second = np.convolve(deriv, [-1, 1])
            upper = False
            for i,der in enumerate(second):
                if i >= len(deriv) - 1:
                    continue
                new_pos = pos
                if der > 0.01 and not upper and deriv[i] > 0 and not pos == "long":
                    upper = True
                    new_pos = "long"

                if der > -0.01 and deriv[i] > 0 and upper and pos == "long":
                    upper = False
                    new_pos = "short"
                
                if new_pos is not pos:
                    self.actions.append([self.data[ticker][i], new_pos])
                pos = new_pos


    @staticmethod
    def calc_MA(data,days):
        if(len(data) < days):
            return -1
        data = np.array(data)
        
        return sum(data[ -days:,2].astype(np.float))/days

