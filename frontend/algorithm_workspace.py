import tkinter as tk
import backend.algorithm as algo
from datetime import datetime
import numpy as np
from collections import defaultdict, namedtuple


class AlgorithmWorkspace:
    """
    Workspace class which handels the workspace, makes sense to have as a seperate file and class. However unsure
    about what do with about the dependencies. I added an "open-communication" to allow for workspace to
    change graph. This might be dumb, but it'll suffice for now i guess.
    """

    def __init__(self, workspace_frame):
        self.selected_bots = []
        self.results = defaultdict(tuple)
        self.algorithm_list_frame = tk.LabelFrame(workspace_frame, text="Algorithm Workspace")
        self.algorithm_list_frame.pack(expand=True, fill=tk.BOTH)
        self.list = tk.Listbox(self.algorithm_list_frame, height=15)
        self.list.pack(expand=1, fill="both")

        self.list.bind('<BackSpace>', self.remove)
        self.list.bind('<Return>', self.select)
        self.list.bind('<Double-Button-1>', self.select)

    def open_communication_with_plotter(self, plotter):
        """
        Functions which lets the workspace modify the plot.
        :param plotter: Plotter.
        """
        self.plotter = plotter

    def update_plot(self, hold_on):
        """
        Plots selected stocks.
        :param event: Eventhandle.
        """
        plot_style = self.plotter.plot_style.get()
        if plot_style == 'Regular':
            self.plot_algorithm_results(hold_on)
        else:
            pass
            #self.plotter.percentual_change_plot(self.selected)

    def add(self, elem):
        """
        Adds an element at the end of the workspace.
        :param elem: Element to append.
        """
        stripped = [string[1:] for string in self.list.get(0, tk.END)]
        if elem[1:] not in stripped:
            self.list.insert(tk.END, elem)
            self.selected_bots.append(elem[1:])

    def remove(self, event):
        """
        Removes highlighted element from the workspace.
        """
        highlighted_idx = self.list.curselection()[0]
        highlighted_elem = self.list.get(highlighted_idx)[1:]
        self.list.delete(highlighted_idx)
        if highlighted_elem in self.selected_bots:
            self.selected_bots.remove(highlighted_elem)

    def remove_all(self, event):
        """
        Removes all elements from the workspace
        """
        self.list.delete(0, tk.END)

    def select(self, event):
        EMPTY_BOX = "\u2610"
        CHECKED_BOX = "\u2611"
        highlighted_elem = self.list.get(tk.ACTIVE)
        index = self.list.get(0, "end").index(highlighted_elem)
        # Make sure to not include the box in the ticker with [1:]
        highlighted_elem = highlighted_elem[1:]

        if highlighted_elem in self.selected_bots:
            self.selected_bots.remove(highlighted_elem)
            new_string = EMPTY_BOX + highlighted_elem

        else:
            self.selected_bots.append(highlighted_elem)
            new_string = CHECKED_BOX + highlighted_elem

        self.list.delete(index)
        self.list.insert(index, new_string)
        self.list.activate(index)
        self.list.update()

    # Kan bara hantera en algorithm åt gången atm!
    def test_algorithms(self, stocks):
        # Load all bots that are selected in the workspace
        bots = [self.load_agent(name)() for name in self.selected_bots]

        # Get dictionary of the actions that each bot made, where the bot name is the key
        actions = algo.backtest(bots, stocks)

        for bot in bots:
            x = defaultdict(list)
            y = defaultdict(list)
            positions = defaultdict(list)

            for (timestamp, ticker, price), position in actions[bot.name]:
                x[ticker].append(timestamp)
                # Append new price to y
                y[ticker].append(price)
                positions[ticker].append(position)

            result = namedtuple("Result", ["timestamp", "price", "position"])
            self.results[bot.name] = result(x, y, positions)

    def load_agent(self, name):
        """
        Loads a bot from the bots directory and validates
        its interface
        """
        mod_name = "backend.trading_algorithms." + name + ".bot"
        mod = __import__(mod_name, fromlist=['Bot'])
        klass = getattr(mod, 'Bot')
        self.has_function(klass, name, "handle_event")

        return klass

    def has_function(self, module, bot_name, function_name):
        """
        Checks if bot has the named function
        """
        op = getattr(module, function_name, None)
        if not callable(op):
            raise NotImplementedError('Bot "{}" does not implement method: "{}"'.format(
                bot_name, function_name))

    def plot_algorithm_results(self, hold_on):
        self.plotter.update_plot(self.results, type="Algorithm_results", hold_on=hold_on)
