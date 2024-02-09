import tkinter as tk
from tkinter import ttk

from uri_template import expand

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
        title_aedat = ttk.Label(self, text = "Record .aedat", background = "red")
        title_npy = ttk.Label(self, text = "Process .npy", background="blue")        
        button_run = ttk.Button(self, text = "Run")
        button_stop = ttk.Button(self, text = "Stop")
        button_process = ttk.Button(self, text = "Process")

        toggle_frame_record = ttk.Frame(self)
        toggle_primitive = ttk.Checkbutton(toggle_frame_record,text = "Primitive")
        toggle_continuous = ttk.Checkbutton(toggle_frame_record,text = "Continuous")
        title_task_name = ttk.Label(toggle_frame_record, text = "Task Name:")
        task_name = tk.Entry(toggle_frame_record)

        self.columnconfigure((0,1,2), weight = 1, uniform = "a")
        self.rowconfigure(0, weight = 2, uniform = "a")
        self.rowconfigure((1,2,3), weight = 4, uniform = "a")
        self.rowconfigure(4, weight = 1, uniform = "a")
        
        title_aedat.grid(row = 0, column = 0, sticky = "ew", columnspan = 2)
        title_npy.grid(row = 0, column = 2, sticky = "ew")
        button_run.grid(row = 3, column = 0, sticky = "nswe", padx = 60, pady = 20)
        button_stop.grid(row = 3, column = 1, sticky = "nswe", padx = 60, pady = 20)
        button_process.grid(row = 3, column = 2, sticky = "nswe", padx = 60, pady = 20)

        toggle_frame_record.grid(row = 1, column = 0, columnspan = 2, sticky = "nswe")
        toggle_primitive.pack(side = "top", expand = True)
        toggle_continuous.pack(side = "top", expand = True)
        title_task_name.pack(side = "top", expand = True)
        task_name.pack(side = "top", expand = True)

if __name__ == "__main__":
    App('DAVIS Data Capture System')