import csv
import tkinter as tk
from collections import namedtuple
from tkfilterlist import FilterList
import backend.data_handler.stock_data as sd
import os


class StockWindow:
    """
    Class for the entire stock tab.
    Currently contains its tab, a stockplot and the list of stocks in an exchange.
    """

    def __init__(self, stock_tab):
        self.stock_tab = stock_tab
        self.lists_frame = tk.Frame(self.stock_tab)
        self.lists_frame.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        self.stock_list = StockList(self.lists_frame)

        self.info_frame = tk.LabelFrame(self.stock_tab, text="Information")
        self.info_frame.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)
        self.info_list = Info(self.info_frame)


class StockList:
    """
    Class for the filterable stocklist.
    Contains its rootframe and the stock plot which shall be updated.
    """

    def __init__(self, lists_frame):

        self.stock_list_frame = tk.LabelFrame(lists_frame, text='Stocks')
        self.stock_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.stock_names = self.load_ticker_name_info("NASDAQ")
        self.stock_filter_list = FilterList(self.stock_list_frame,
                                            height=1,
                                            source=self.stock_names,
                                            display_rule=lambda item: item[0] + ": " + item[1],
                                            filter_rule=lambda item, text:
                                            item[0].lower().startswith(text.lower()) or item[1].lower().startswith(
                                                text.lower()))

        self.stock_filter_list.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        self.stock_filter_list.bind('<Return>', self.add_to_workspace)
        self.stock_filter_list.bind('<Double-Button-1>', self.add_to_workspace)
        self.stock_filter_list.bind('<Double-Button-3>', self.get_stock_info)
        self.stock_filter_list.bind('<Control-i>', self.get_stock_info)
        self.EXCHANGES = [os.path.splitext(name)[0] for name in os.listdir("./file_system/data/tickers")]

        self.exchange = tk.StringVar(self.stock_list_frame)
        self.exchange.set(self.EXCHANGES[0])
        self.exchange.trace('w', self.change_exchange)

        self.exchange_menu = tk.OptionMenu(self.stock_list_frame, self.exchange, *self.EXCHANGES)
        self.exchange_menu.pack(side=tk.RIGHT)
        self.text_box = tk.Text(self.stock_list_frame, height=1, width=20)
        self.text_box.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        self.text_box.insert(tk.END, 'Choose exchange: ')

    def change_exchange(self, *args):
        self.stock_names = self.load_ticker_name_info(self.exchange.get())
        self.stock_filter_list._source = self.stock_names
        self.stock_filter_list.clear()

    def add_to_workspace(self, event):
        """
        Adds clicked ticker to the workspace.
        :param event: Eventhandler.
        """
        ticker = self.stock_filter_list.selection()[0]
        CHECKED_BOX = "\u2611"
        self.stock_workspace.add(CHECKED_BOX + ticker)

    def get_stock_info(self, event):
        self.info_list.display_stock_info(self.stock_filter_list.selection()[0])

    @staticmethod
    def load_ticker_name_info(exchange):
        """
        Fetches stock ticker and company name from an exchange and returns them as a list of namedtuples.
        :param exchange: Choice of stock exchange.
        :return: List of namedtuples with stock ticker and company name from stock exchange.
        """
        with open("file_system/data/tickers/" + exchange + ".csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_file)
            company = namedtuple("company_info", ["ticker", "name"])
            stock_info = [company(stock[0], stock[1]) for stock in csv_reader]
            return stock_info

    def open_communication_with_stock_workspace(self, stock_workspace):
        """
        Gives stock list possibility to modify workspace. Perhaps silly solution, but will have to do for now.
        :param stock_workspace: StockWorkspace
        """
        self.stock_workspace = stock_workspace

    def open_communication_with_info_list(self, info_list):
        """
        Gives stock list possibility to modify workspace. Perhaps silly solution, but will have to do for now.
        :param stock_workspace: StockWorkspace
        """
        self.info_list = info_list


class Info:

    def __init__(self, frame):
        self.frame = frame
        self.info_list = tk.Listbox(self.frame, height=5)

        self.info_list.pack(expand=1, fill=tk.BOTH)

    def display_stock_info(self, ticker):
        self.info_list.delete(0, tk.END)
        stock_info = sd.get_stock_info(ticker)
        for cat, measure in stock_info.items():
            self.info_list.insert(tk.END, cat + ': ' + str(measure))
