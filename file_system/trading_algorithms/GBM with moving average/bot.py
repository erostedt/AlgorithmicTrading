from collections import defaultdict
import backend.stochastic_processes.sde as sde
import statistics as stat
import numpy as np


class Bot:
    """
    Just a test for using SDEs.
    """

    def __init__(self):
        self.name = 'GBM'
        self.avgs = defaultdict(list)
        self.inits = defaultdict(int)

        self.prediction_idxs = defaultdict(int)
        self.predictions = defaultdict(list)

        self.seen_commodities = []
        self.actions = []
        self.pos = ''
        self.bm_steps = 10
        self.sims = 100

    def handle_event(self, event):
        """
        For each stock: Saves 11 prices and calculates average returns -> 10 dps. Then makes a 10 day prediction
        of the stock price. resets the price list and compares the predictions and the price. And repeat.
        """
        _, self.com, self.price = event
        if self.com not in self.seen_commodities:
            self.seen_commodities.append(self.com)
            self.inits[self.com] = 0
            self.prediction_idxs[self.com] = 0

        curr_avg = self.avgs[self.com]
        curr_avg.append(self.price)

        if self.inits[self.com] < self.bm_steps-1:
            self.inits[self.com] += 1
            return

        num_in_avg = len(curr_avg)

        if num_in_avg == self.bm_steps:
            self.returns = [(_next - curr)/curr for _next, curr in zip(curr_avg[1:], curr_avg[:-1])]
            self.predictions[self.com] = self.predict()
            curr_avg.clear()
            self.prediction_idxs[self.com] = 0

        self.algorithm(event)

    def predict(self):
        """
        Runs 100 prediction simulations. Finds 80 percentile for each prediction if long position is hold,
        Price has to go up a lot if we are going to change our thought that the stock is undervalued.
        reverse if short is held.
        """
        pred_matrix = np.zeros((self.bm_steps, self.sims))
        for sim in range(self.sims):
            pred_matrix[:, sim] = sde.gbm(self.price, stat.mean(self.returns), stat.stdev(self.returns), self.bm_steps)

        pred_list = []
        if self.pos == 'long':
            for preds in pred_matrix:
                pred_list.append(np.percentile(preds, 80))
        else:
            for preds in pred_matrix:
                pred_list.append(np.percentile(preds, 20))

        return pred_list

    def algorithm(self, event):
        """
        Compares the price with the 80/20 percentile estimates to see if the stock is over or under-valed.
        """
        pred_idx = self.prediction_idxs[self.com]

        if self.pos != 'long':
            if self.price < self.predictions[self.com][pred_idx]:
                self.pos = 'long'
                self.actions.append([event, 'long'])
                self.predictions[self.com] = self.predict()
        else:
            if self.price > self.predictions[self.com][pred_idx]:
                self.pos = 'short'
                self.actions.append([event, 'short'])
                self.predictions[self.com] = self.predict()

        pred_idx += 1
