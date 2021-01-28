import backend.portfolio_management.efficient_frontier as ef
import backend.data_handler.stock_data as sd
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import os
from tkfilterlist import FilterList

import file_system.file_handler as fh
import csv

class Portfolio:

    def __init__(self, portfolio_window):

        # Left side:
        self.plot_rebalance_holdings_frame = tk.Frame(portfolio_window)
        self.plot_rebalance_holdings_frame.pack(side=tk.LEFT, fill="both")

        # Add plot
        self.plot_frame = tk.Frame(self.plot_rebalance_holdings_frame)
        self.plot_frame.pack()
        self.figure = plt.Figure(figsize=(2.6, 2.6))
        self.figure_frame = tk.LabelFrame(self.plot_frame, text="Plot")
        self.figure_frame.pack(side=tk.TOP, expand=0)
        self.canvas = FigureCanvasTkAgg(self.figure, self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # Add buttons and stuff below plot
        # Create frame for buttons
        self.below_plot_frame = tk.Frame(self.plot_frame)
        self.below_plot_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.X)

        self.rebalance_frame = tk.LabelFrame(self.below_plot_frame, text="Rebalance Portfolio")
        self.rebalance_frame.pack(side=tk.TOP, expand=1, fill=tk.X)
        self.option_frame = tk.Frame(self.rebalance_frame)
        self.option_frame.pack(expand=1, fill=tk.X)

        # Add label and entry to choose risk free rate and returns
        self.risk_free_rate_frame = tk.LabelFrame(self.option_frame, text="RF Rate (%)")
        self.risk_free_rate_frame.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.risk_free_rate = tk.StringVar()
        self.risk_free_rate.set("2")

        self.risk_free_rate_entry = tk.Entry(self.risk_free_rate_frame, textvariable=self.risk_free_rate, width=5)
        self.risk_free_rate_entry.pack(fill=tk.X)

        self.returns_frame = tk.LabelFrame(self.option_frame, text="Exp. Returns (%)")
        self.returns_frame.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.end = tk.StringVar()
        self.end.set("8")

        self.returns_entry = tk.Entry(self.returns_frame, textvariable=self.end, width=5)
        self.returns_entry.pack(expand=1, fill=tk.X)

        # Add buttons
        self.rebalance_save_buttons_frame = tk.LabelFrame(self.option_frame, text='')
        self.rebalance_save_buttons_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.rebalance_button = tk.Button(self.rebalance_save_buttons_frame, text="Rebalance")
        self.rebalance_button.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

        self.save_button = tk.Button(self.rebalance_save_buttons_frame, text='Save')
        self.save_button.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        # self.test_algorithm_button.bind('<Button-1>', self.rebalance_portfolio)

        # Add entry field to enter name of result
        self.name_label = tk.Label(self.rebalance_frame, text="Name:")
        self.name_label.pack(side=tk.LEFT)
        self.name = tk.StringVar()
        self.name_entry = tk.Entry(self.rebalance_frame, textvariable=self.name, width=10)
        self.name_entry.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.name.set("Default")

        self.holdings_frame = tk.LabelFrame(self.plot_rebalance_holdings_frame, text="Holdings")
        self.holdings_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.holdings_box = tk.Listbox(self.holdings_frame)
        self.holdings_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)


        # Right side:
        self.portfolios_statistics_frame = tk.Frame(portfolio_window)
        self.portfolios_statistics_frame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

        # Create portfolio list
        self.bot_list_frame = tk.LabelFrame(self.portfolios_statistics_frame, text="Portfolios", height=10)
        self.bot_list_frame.pack(side=tk.TOP, fill=tk.X)
        dir_name = "file_system/portfolios"
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        algorithms = os.listdir(dir_name)
        self.list = FilterList(self.bot_list_frame,
                               source=algorithms,
                               display_rule=lambda item: item,
                               filter_rule=lambda item, text:
                               item.lower().startswith(text.lower()))

        self.list.pack(side=tk.TOP, expand=1, fill=tk.X)
        #self.list.bind('<Return>', self.add_to_workspace)
        #self.list.bind('<Double-Button-1>', self.add_to_workspace)
        self.list.focus_set()

        # Create statistics box
        self.statistics_frame = tk.LabelFrame(self.portfolios_statistics_frame, text="Statistics")
        self.statistics_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.statistics_box = tk.Listbox(self.statistics_frame)
        self.statistics_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Remove this when the list of portfolios is finished and this functionallity added to just clicking
        # the portfolio in the portfolio list.
        #self.generate_button = tk.Button(portfolio_window, text='Generate Portfolio', command=self.generate_new)
        #self.generate_button.pack(side=tk.BOTTOM)


        self.portfolio = pd.DataFrame()
        self.ef = None
        self.stocks = None
        self.tickers = None
        self.weights = None

    def generate_new(self):
        self.stocks = sd.get_stock_data(self.stock_workspace.selected_tickers)['Close']
        self.ef = ef.EfficientFrontier(self.stocks)
        self.tickers = self.stocks.columns
        self.weights = self.ef.p_allocation
        self.portfolio = pd.DataFrame([self.weights], columns=self.tickers)
        self.plot()

    def plot(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        disp_w, disp_t = [], []
        for w, ticker in zip(self.weights, self.tickers):
            if abs(w) > 1e-4:
                disp_w.append(w)
                disp_t.append(ticker)

        pie_ax = self.ax.pie(disp_w, labels=disp_t, autopct='%1.1f%%')
        self.figure.legend(pie_ax[0], self.tickers, loc='upper right')
        self.canvas.draw()

    def open_communication_with_stock_workspace(self, stock_workspace):
        self.stock_workspace = stock_workspace