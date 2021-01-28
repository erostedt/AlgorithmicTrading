import tkinter
from tkinter import ttk
from frontend.main_window import MainWindow


class Executor:
    def __init__(self):
        self.root = tkinter.Tk()
        # Fix for OSX buttons being unaligned vertically in the notebook tabs
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':  # only for OSX
            s = ttk.Style()
            # Note: the name is specially for the text in the widgets
            s.configure('TNotebook.Tab', padding=(12, 8, 12, 0))

        self.app = MainWindow(master=self.root, reload=self.on_reload)

        # Fixes broken scrolling on some Macbooks
        while True:
            try:
                self.app.mainloop()
                break
            except UnicodeDecodeError:
                pass
        #self.app.mainloop()

    def on_reload(self, event):
        self.root.destroy()
        self.root = tkinter.Tk()
        self.app = MainWindow(master=self.root, reload=self.on_reload)
        self.app.mainloop()


if __name__ == '__main__':
    Executor()
