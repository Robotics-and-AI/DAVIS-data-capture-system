import tkinter as tk
from tkinter import ttk

from numpy import size

class App(tk.Tk):
    
    def __init__(self, title):

        super().__init__()
        
        self.title(title)
        self.geometry('720x480')
        self.minsize(720,480)

        self.menu = Menu(self)

        self.mainloop()

class Menu(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.place(x = 0, y = 0, relwidth = 1, relheight = 0.8)
        self.create_widgets()
        
    def create_widgets(self):
        title_aedat = ttk.Label(self, text = "Record .aedat")
        title_npy = ttk.Label(self, text = "Process .npy")        
        button_run = ttk.Button(self, text = "Run")
        button_stop = ttk.Button(self, text = "Stop")
        button_process = ttk.Button(self, text = "Process")

        self.columnconfigure((0,1,2), weight = 1, uniform = "a")
        self.rowconfigure(0, weight = 2, uniform = "a")
        self.rowconfigure((1,2,3), weight = 4, uniform = "a")
        self.rowconfigure(4, weight = 1, uniform = "a")
        
        title_aedat.grid(row = 0, column = 0, sticky = "ew", columnspan = 2)
        title_npy.grid(row = 0, column = 2, sticky = "ew")
        button_run.grid(row = 3, column = 0, sticky = "nswe", padx = 60, pady = 20)
        button_stop.grid(row = 3, column = 1, sticky = "nswe", padx = 60, pady = 20)
        button_process.grid(row = 3, column = 2, sticky = "nswe", padx = 60, pady = 20)

if __name__ == "__main__":
    App('DAVIS Data Capture System')