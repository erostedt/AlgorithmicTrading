import os
import tkinter as tk
from tkfilterlist import FilterList
import backend.algorithm as algo
import file_system.file_handler as fh
import csv


class AlgorithmWindow:

    def __init__(self, root):
        self.root = root

        self.results_and_bots_frame = tk.Frame(root, height=3)
        self.results_and_bots_frame.pack(side=tk.TOP, expand=0, fill="both")

        # Create list of generated results
        self.results_frame = tk.LabelFrame(self.results_and_bots_frame, text="Results")
        self.results_frame.pack(side=tk.LEFT, fill="both")

        self.results_list = tk.Listbox(self.results_frame)
        self.results_list.pack(side=tk.TOP, fill="both", expand=1)
        self.results_list.bind('<Double-Button-1>', self.display_results)
        self.results_list.bind('<Return>', self.display_results)

        # Create bot list
        self.bot_list_frame = tk.LabelFrame(self.results_and_bots_frame, text="Bots")
        self.bot_list_frame.pack(side=tk.RIGHT, expand=1, fill="both")
        algorithms = os.listdir("file_system/trading_algorithms")
        self.list = FilterList(self.bot_list_frame,
                               source=algorithms,
                               display_rule=lambda item: item,
                               filter_rule=lambda item, text:
                               item.lower().startswith(text.lower()))

        self.list.pack(side="top", expand=1, fill="both")
        self.list.bind('<Return>', self.add_to_workspace)
        self.list.bind('<Double-Button-1>', self.add_to_workspace)
        self.list.bind('<Control-r>', self.refresh)
        self.list.focus_set()

        # Create frame for buttons
        self.button_frame = tk.Frame(self.results_frame)
        self.button_frame.pack()
        # Add entry field to enter name of result
        self.generate_frame = tk.LabelFrame(self.button_frame, text="Generate results")
        self.generate_frame.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.date_frame = tk.Frame(self.generate_frame)
        self.date_frame.pack(expand=1, fill=tk.X)
        # Add label and entry to choose start and end dates
        self.start_date_frame = tk.LabelFrame(self.date_frame, text="Starting date")
        self.start_date_frame.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.start = tk.StringVar()
        self.start.set("2019-04-20")

        self.start_date_entry = tk.Entry(self.start_date_frame, textvariable=self.start, width=10)
        self.start_date_entry.pack(expand=1, fill=tk.X)

        # Add option menu to choose the interval between data points
        self.INTERVAL_OPTIONS = [
            '1m',
            '1d',
        ]

        self.interval = tk.StringVar(self.date_frame)
        self.interval.set(self.INTERVAL_OPTIONS[1])

        self.interval_menu = tk.OptionMenu(self.date_frame, self.interval, *self.INTERVAL_OPTIONS)
        self.interval_menu.pack(side=tk.RIGHT, expand=1, fill=tk.X)

        self.end_date_frame = tk.LabelFrame(self.date_frame, text="End date")
        self.end_date_frame.pack(expand=1, fill=tk.X)
        self.end = tk.StringVar()
        self.end.set("None")

        self.end_date_entry = tk.Entry(self.end_date_frame, textvariable=self.end, width=10)
        self.end_date_entry.pack(expand=1, fill=tk.X)

        self.name_label = tk.Label(self.generate_frame, text="Name:")
        self.name_label.pack(side=tk.LEFT)
        self.name = tk.StringVar()
        self.name_entry = tk.Entry(self.generate_frame, textvariable=self.name, width=10)
        self.name_entry.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.name.set("Default")

        self.test_algorithm_button = tk.Button(self.generate_frame, text="Test Algorithm")
        self.test_algorithm_button.pack(side=tk.RIGHT, expand=1, fill=tk.X)
        self.test_algorithm_button.bind('<Button-1>', self.test_algorithms)

        self.export_button = tk.Button(self.generate_frame, text='Export data')
        self.export_button.pack(side=tk.RIGHT, expand=1, fill=tk.X)
        self.export_button.bind('<Button-1>', self.export)

        # Create statistics box
        self.statistics_frame = tk.Frame(self.root)
        self.statistics_frame.pack(fill=tk.BOTH, expand=1)
        self.algorithm_statistics_frame = tk.LabelFrame(self.statistics_frame, text="Statistics")
        self.algorithm_statistics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.statistics_box = tk.Listbox(self.algorithm_statistics_frame)
        self.statistics_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.highscore_frame = tk.LabelFrame(self.statistics_frame, text="Hall of Fame")
        self.highscore_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.highscore_box = tk.Listbox(self.highscore_frame)
        self.highscore_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.find_results()
        self.get_HOF()

    def export(self, event):
        if self.end.get() == "None":
            end = None
        else:
            end = self.end.get()

        fh.export(tickers=self.workspaces.stock_workspace.selected_tickers, name='test', start=self.start.get(), end=end, interval=self.interval.get())

    def find_results(self):
        """
        Fetches name of all the saved result files and insert them into the results listbox.
        """
        path = 'file_system/results/'
        for _file in os.listdir(path):
            file = _file.split('.')[0]
            self.results_list.insert(tk.END, file)

    def get_HOF(self):
        """
        Fetches the high score information and insert the scores into the hall of fame list.
        """
        self.highscore_box.delete(0, tk.END)
        path = 'file_system/hall_of_fame/hof.csv'
        with open(path, 'r') as csf_file:
            csv_reader = csv.reader(csf_file)
            for placing in csv_reader:
                bot, score = placing[0], placing[1]
                self.highscore_box.insert(tk.END, bot + ': ' + score)

    def add_to_HOF(self, result):
        """
        Checks if the result was good enough to get into the hall of fame. If so the result is added
        (and last one is potentianally removed).
        :param result: Dictionary of Dataframes containing the results for each bot.
        """
        path = 'file_system/hall_of_fame/hof.csv'
        for bot_name, score in result.items():
            curr_hof = []
            with open(path, 'r') as csf_file:
                csv_reader = csv.reader(csf_file)
                for placing in csv_reader:
                    bot, _score,  = placing[0], float(placing[1])
                    curr_hof.append((bot, _score))

            if len(curr_hof) < 10:
                curr_hof.append((bot_name, score))

            elif curr_hof[-1][1] < score:
                curr_hof.pop()
                curr_hof.append((bot_name, score))

            curr_hof.sort(key=lambda x: x[1], reverse=True)

            with open(path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                for placing in curr_hof:
                    csv_writer.writerow([placing[0], str(placing[1])])
        self.get_HOF()

    def test_algorithms(self, event):
        """
        Function which is called when test algorithm button is pressed. Sends info to backend to test selected bots
        on selected commodities and to write the statistics into a file. Adds to the Hall of fame if score was
        was better than (some) others in hall of fame.
        :param event: Eventhandler.
        """
        # Tell backend to test the algorithm
        tickers = self.workspaces.stock_workspace.selected_tickers
        start = self.start.get()

        if self.end.get() == "None":
            end = None
        else:
            end = self.end.get()

        interval = self.interval.get()
        bot_names = self.workspaces.algorithm_workspace.selected_bots
        # Results is a dictionary with bot.name as key, a tuple (timestamps, price, position) as value,
        # and each of those are themselves dictionaries with tickers as keys.
        name = self.name_entry.get()
        algo.test_algorithms(tickers=tickers, interval=interval, start=start, end=end, bot_names=bot_names, algorithm_name=name)

        if name in self.results_list.get(0, tk.END):
            self.results_list.delete(self.results_list.get(0, tk.END).index(name))
        self.results_list.insert(0, name)
        self.write_statistics(name)
        #self.add_to_HOF(algo.get_score('file_system/algorithm_statistics/' + name + '.csv'))
        self.results_list.selection_set(0)
        self.display_results(self.results_list.selection_get())

    def display_results(self, event):
        self.plotter.plot_result(self.results_list.selection_get())
        self.read_statistics(event=None)

    @staticmethod
    def write_statistics(name):
        algorithm_results, *unused = fh.read_result('file_system/results/' + name + '.csv')
        algorithm_statistics = algo.calc_statistics(algorithm_results)
        fh.write_statistics('file_system/algorithm_statistics/' + name + '.csv', algorithm_statistics)

    def read_statistics(self, event):
        self.statistics_box.delete(0, tk.END)
        algorithm_statistics = fh.read_statistics('file_system/algorithm_statistics/' + self.results_list.selection_get() + '.csv')
        for bot_name, bot_df in algorithm_statistics.items():
            self.statistics_box.insert(tk.END, bot_name)
            self.statistics_box.insert(tk.END, '-----------')
            for ticker, *_params in bot_df.iterrows():
                _params = _params[0]
                self.statistics_box.insert(tk.END, ticker)
                self.statistics_box.insert(tk.END, ','.join(bot_df.columns))
                params = []
                for param in _params:
                    params.append(str(param))

                self.statistics_box.insert(tk.END, ','.join(params))
            self.statistics_box.insert(tk.END, '')

    def refresh(self, event):
        self.list.destroy()
        algorithms = os.listdir("file_system/trading_algorithms")
        self.list = FilterList(self.bot_list_frame,
                               source=algorithms,
                               display_rule=lambda item: item,
                               filter_rule=lambda item, text:
                               item.lower().startswith(text.lower()))
        self.list.pack(side="top", expand=1, fill="both")
        self.list.bind('<Return>', self.add_to_workspace)
        self.list.bind('<Double-Button-1>', self.add_to_workspace)
        self.list.bind('<Control-r>', self.refresh)

    def open_communication_with_plotter(self, plotter):
        """
        Functions which lets the plot communicate the algorithm workspace.
        :param algorithm_workspace: AlgorithmWorkspace.
        """
        self.plotter = plotter

    def open_communication_with_workspaces(self, workspaces):
        """
        Functions which lets the plot communicate the workspaces.
        :param workspaces: Workspaces.
        """
        self.workspaces = workspaces

    def add_to_workspace(self, event):
        """
        Adds clicked ticker to the workspace.
        :param event: Eventhandler.
        """
        algorithm = self.list.selection()
        CHECKED_BOX = "\u2611"
        self.algorithm_workspace.add(CHECKED_BOX + algorithm)

    def open_communication_with_algorithm_workspace(self, algorithm_workspace):
        """
        Functions which lets the algorithm list modify the algorithm workspace.
        :param algorithm_workspace: Algorithm Workspace.
        """
        self.algorithm_workspace = algorithm_workspace

