import tkinter as tk


class Console:
    def __init__(self, console_tab):
        self.txt = tk.StringVar()
        self.txt.set("Enter command here!")
        self.entry = tk.Entry(console_tab, textvariable=self.txt, width=35)
        self.entry.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.entry.bind("<Return>", self.enter_command)
        self.console_frame = tk.Text(console_tab, width=45, height=30)
        self.console_frame.pack(fill=tk.BOTH, expand=1)

    def enter_command(self, event):
        command = tk.Text(self.console_frame, height=1, width=45)
        command.pack(side=tk.TOP, fill=tk.X)
        t = self.txt.get()
        self.txt.set("")
        command.insert(tk.END, t + ": \n")
        executed_command = tk.Text(self.console_frame, height=1, width=45)
        executed_command.pack(side=tk.TOP, fill=tk.X)
        try:
            executed_command.insert(tk.END, str(eval(t)) + "\n")
        except:
            executed_command.insert(tk.END, "Command not found! \n")

        self.console_frame.see(tk.END)

    def open_communication_with_stock_workspace(self, stock_workspace):
        """
        Gives stock list possibility to modify workspace. Perhaps silly solution, but will have to do for now.
        :param stock_workspace: StockWorkspace
        """
        self.stock_workspace = stock_workspace

