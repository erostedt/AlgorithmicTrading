import sys
sys.path.append("..")

import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from pandas.plotting import register_matplotlib_converters
import backend.plots as plot
register_matplotlib_converters()
from backend import utils as utils
import time
import backend.stochastic_processes.timeseries as ts


class Plotter:
    """
    ADD COMMENT HERE
    """

    def __init__(self, root):
        self.root = root
        self.plot_frame = tk.Frame(self.root)

        # Add empty figure
        self.figure = Figure(figsize=(5, 5), dpi=100)
        # Create Axes-object with add_subplot
        self.a = self.figure.add_subplot(111)
        # Reset axes to rotate tick labels, add axis-labels etc.
        self.reset_axes()

        # Add figure
        self.figure_frame = tk.LabelFrame(self.plot_frame, text="Figure")
        self.figure_frame.pack(side=tk.TOP, expand=1, fill=tk.BOTH)
        self.canvas = FigureCanvasTkAgg(self.figure, self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()#side="top")#(fill=tk.BOTH, expand=True)
        self.plot_time_frame = self.a.get_xlim()
        # Add toolbar
        self.toolbar_frame = tk.Frame(self.root) ### SHOULD BE IN PLOT FRAME, FUCK GUIS
        self.toolbar_frame.pack(side="top")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root) ### SHOULD BE IN PLOT FRAME, FUCK GUIS
        self.plot_frame.pack(side=tk.RIGHT, expand=1, fill=tk.Y)

        # Add viewing date frame
        self.timeframe_frame = tk.LabelFrame(self.plot_frame, text="Display Timeframe")
        self.timeframe_frame.pack(expand=1, fill=tk.X)

        # Add buttons to change viewing dates
        self.timeframe_buttons = []

        self.TIMEFRAME_OPTIONS = [
            'One hour',
            'Three days',
            'One month',
            'One year',
            'Three years'
        ]
        self.TIMEFRAME_TRANSFORMATIONS = [
            'one_hour',
            'three_days',
            'one_month',
            'one_year',
            'three_years'
        ]

        self.timeframe_to_func = dict(zip(self.TIMEFRAME_OPTIONS, self.TIMEFRAME_TRANSFORMATIONS))

        for i, time in enumerate(self.TIMEFRAME_OPTIONS):
            self.timeframe_buttons.append(tk.Button(self.timeframe_frame, text=time))
            self.timeframe_buttons[i].pack(side="left", expand=1, fill=tk.X)
            time = self.timeframe_to_func[time]
            self.timeframe_buttons[i].bind("<Button-1>", eval("self." + time + "_button"))

        # Add options frame
        self.option_frame = tk.Frame(self.plot_frame)
        self.option_frame.pack(side="bottom", expand=1, fill=tk.X)

        # Add "hold on"-checkbutton
        self.hold_on_button = tk.Checkbutton(self.option_frame, text="Hold on")
        self.hold_on_button.pack(side=tk.LEFT)
        self.hold_on_button.bind('<Button-1>', self.toggle_hold_on)
        self.hold_on = False
        self.param = "None"

        # Add Option Menu
        self.PLOT_OPTIONS = [
            'Regular',
            'Percentual change',
            'Moving Average',
            'Fourier Transform'
        ]
        self.PLOT_TRANSFORMATIONS = [
            'None',
            'ts.pct_change',
            'ts.moving_average',
            'ts.fourier_transform'
        ]

        self.plot_to_func = dict(zip(self.PLOT_OPTIONS, self.PLOT_TRANSFORMATIONS))

        self.plot_style = tk.StringVar(self.option_frame)
        self.plot_style.set(self.PLOT_OPTIONS[0])

        self.plot_menu = tk.OptionMenu(self.option_frame, self.plot_style, *self.PLOT_OPTIONS)
        self.plot_menu.pack(side=tk.LEFT)

        # Add Entry-field that takes user input of parameter
        self.param = tk.StringVar()
        self.param_box = tk.Entry(self.option_frame, textvariable=self.param)
        self.param.set("None")
        self.param_box.pack(side=tk.LEFT, expand=1, fill=tk.X)

    def plot_stocks(self, tickers, interval, start=None, end=None):
        # If hold-on checkbox is not checked, plot to the current figure
        if not self.hold_on:
            # Reset current Axes
            self.reset_axes()

        # Get data from backend
        stock_df = plot.get_stocks(tickers, plot_style=self.plot_to_func[
                                        self.plot_style.get()], params=self.param.get(), interval=interval, start=start, end=end)

        # Plot the retrieved stock data)
        self.a.plot(stock_df)
        self.a.legend(tickers)
        self.canvas.draw()

    def plot_result(self, result):
        # If hold-on checkbox is not checked, plot to the current figure
        if not self.hold_on:
            # Reset current Axes
            self.reset_axes()
        # Get result from backend
        structured_result, tickers, interval, start, end = plot.get_result(result)
        self.plot_stocks(tickers=tickers, interval=interval, start=start, end=end)
        for bot_name, bot_results in structured_result.items():
            for ticker, (long, short) in bot_results.items():
                x_long = [utils.convert_timestamp_to_datetime(l) for l in long.index]
                x_short = [utils.convert_timestamp_to_datetime(s) for s in short.index]
                if self.plot_style.get() == 'Regular':
                    self.a.scatter(x_long, list(long.values), marker='o')
                    self.a.scatter(x_short, list(short.values), marker='x')
                else:
                    self.a.plot((x_long, x_long), self.a.get_ylim(), 'g--')
                    self.a.plot((x_short, x_short), self.a.get_ylim(), 'r--')

        # Change timeframe on plot to only display the frame where the results are

        if end is None:
            end = time.time()/(60*60*24)
        else:
            end = utils.convert_timestamp_to_datetime(end).timestamp()/(60*60*24)
        start = utils.convert_timestamp_to_datetime(start).timestamp()/(60*60*24)
        days_diff = end - start
        start_matplotlib_time = self.a.get_xlim()[1] - days_diff
        end_matplotlib_time = self.a.get_xlim()[1]
        self.a.set_xlim(start_matplotlib_time, end_matplotlib_time)

        self.canvas.draw()

    def reset_axes(self):
        self.a.cla()
        self.a.set_ylabel('$')
        self.a.set_xlabel('Date')
        self.a.tick_params(axis='x', labelrotation=45, labelsize=8)
        self.a.tick_params(axis='y', labelsize=8)
        self.a.margins(x=0.0)

    # Hur slår vi ihop alla dessa till en funktion?!
    def one_hour_button(self, event):
        if self.stock_workspace.interval.get() == "1d":
            self.stock_workspace.interval.set("1m")
            self.stock_workspace.plot_stocks(event="None")
        _, curr_x_max = self.a.get_xlim()
        self.a.set_xlim((curr_x_max - 1/24, curr_x_max))
        self.canvas.draw()

    def three_days_button(self, event):
        if self.stock_workspace.interval.get() == "1d":
            self.stock_workspace.interval.set("1m")
            self.stock_workspace.plot_stocks(event="None")
        _, curr_x_max = self.a.get_xlim()
        self.a.set_xlim((curr_x_max - 3, curr_x_max))
        self.canvas.draw()

    def one_month_button(self, event):
        if self.stock_workspace.interval.get() == "1m":
            self.stock_workspace.interval.set("1d")
            self.stock_workspace.plot_stocks(event="None")
        _, curr_x_max = self.a.get_xlim()
        self.a.set_xlim((curr_x_max - 30, curr_x_max))
        self.canvas.draw()

    def one_year_button(self, event):
        if self.stock_workspace.interval.get() == "1m":
            self.stock_workspace.interval.set("1d")
            self.stock_workspace.plot_stocks(event="None")
        _, curr_x_max = self.a.get_xlim()
        self.a.set_xlim((curr_x_max - 365, curr_x_max))
        self.canvas.draw()

    def three_years_button(self, event):
        if self.stock_workspace.interval.get() == "1m":
            self.stock_workspace.interval.set("1d")
            self.stock_workspace.plot_stocks(event="None")
        _, curr_x_max = self.a.get_xlim()
        self.a.set_xlim((curr_x_max - 365*3, curr_x_max))
        self.canvas.draw()

    def toggle_hold_on(self, event):
        self.hold_on = not self.hold_on

    def open_communication_with_stock_workspace(self, stock_workspace):
        """
        Gives plotter possibility to modify workspace.
        :param stock_workspace: StockWorkspace
        """
        self.stock_workspace = stock_workspace
