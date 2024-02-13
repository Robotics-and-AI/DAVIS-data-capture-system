from customtkinter import *
from file_manager import FileManager
from capture_system import CaptureSystem

import customtkinter as ctk
import glob
import numpy as np
import threading
import time

class App(CTk):
    
    def __init__(self, title):

        super().__init__()

        ARDUINO_BOARD = "USB-SERIAL CH340"
        TIME_PRESS_BUTTON = 0 # Time (sec) to offset recording after pressing button. Default: 0
        self.labels = tuple()
        self.is_confirmed = False
        self._lock = threading.Lock()

        self.output_dir = os.path.join(os.path.abspath(""),"test_data")
        self.file_manager = FileManager(self.output_dir)
        self.capture_system = CaptureSystem(ARDUINO_BOARD, self.output_dir, TIME_PRESS_BUTTON) 

        self.title(title)
        self.geometry('720x480')
        self.minsize(720,480)
        set_default_color_theme("green")
        
        folder_options = []
        for file in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, file)
            if os.path.isdir(file_path):
                folder_options.append(file)

        # Recording menu setup
        record_menu = Menu(self,"Record event data", (0,1))
        record_menu.place(relx = 0.02, rely = 0.02, relwidth = 0.56, relheight = 0.71)
        # Add components to recording menu
        self.input_task_frame = InputFrame(record_menu, "Task name:", 1, 1, False)
        self.record_mode_frame = RadioFrame(record_menu, "Choose recording mode:", ["Primitive","Continuous"], 1, 0)
        self.select_primitive = ComboFrame(record_menu, "Choose primitive:", folder_options, 2, 0)
        run_button = CTkButton(record_menu, text = "Run")
        run_button.grid(row = 3, column = 0, columnspan = 2, ipadx = 5, ipady = 5)
        run_button._command = self.run_function

        # Processing menu setup
        process_menu = Menu(self, "Process event data", 0)
        process_menu.place(relx = 0.6, rely = 0.02, relwidth = 0.38, relheight = 0.71)
        # Add components to processing menu
        self.select_folder = ComboFrame(process_menu, "Choose folder:", folder_options, 2, 0)
        self.process_mode_frame = RadioFrame(process_menu, "Choose processing mode:", ["Folder", "All Files"], 1, 0)
        process_button = Button(process_menu, "Process", 3, 0)
        process_button._command = self.process_function

        # Output terminal setup
        self.output_text = CTkTextbox(self, font = ("Arial",12), state = "disabled")
        self.output_text.place(relx = 0.02, rely = 0.75, relwidth = 0.96, relheight = 0.22)
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("info", foreground="blue")
        self.output_text.tag_config("normal", foreground="black")
        self.print_message("--------- OUTPUT TERMINAL ---------\n", "normal")
        self.print_message("INSTRUCTIONS: Click on the Run button and then press the Pedal to start recording\n", "normal")
        self.print_message("----------------------------------------------\n", "normal")

        self.mainloop()

    def print_message(self, message, tag):
        
        with self._lock:
            self.output_text.configure(state = "normal")
            if tag == "error":
                self.output_text.insert(ctk.END,message,"error")
            elif tag == "info":
                self.output_text.insert(ctk.END,message,"info")
            elif tag == "normal":
                self.output_text.insert(ctk.END,message,"normal")
            self.output_text.see(ctk.END)
            self.output_text.configure(state = "disabled")

    def process_function(self):
        
        if self.process_mode_frame.radio_button1_enabled:
            
            folder = self.select_folder.get_current_value()

            list_all_files = glob.glob(os.path.join(self.output_dir,folder,"*.aedat"))
            for file in list_all_files:
                file_dir_no_ext = file[:len(file)-6] # Remove .aedat from file name
                self.file_manager.aedat_to_npy(file_dir_no_ext)

            self.print_message(f"Finished processing {len(list_all_files)} file(s) in the {folder} folder\n", "info")

        else:

            list_all_files = glob.glob(os.path.join(self.output_dir,"**","*.aedat"),recursive=True)
            
            for file in list_all_files:
                file_dir_no_ext = file[:len(file)-6] # Remove .aedat from file name
                self.file_manager.aedat_to_npy(file_dir_no_ext)

            self.print_message(f"Finished processing all {len(list_all_files)} available .aedat files\n", "info")

    def run_function(self):
        
        task_name = self.input_task_frame.get_current_value()
        paralel_thread = threading.Thread(target = self.capture_system._read_serial)

        if task_name == "":
            self.print_message(f"Insert the task name\n", "error")
            return

        try:
            self.capture_system._start_paralel_thread(paralel_thread)
        except OSError as e:
            self.print_message(f"{e}\n", "error")
            return

        self.capture_system._file_name = task_name.encode()

        if self.record_mode_frame.radio_button1_enabled: # Primitive
            with_labels = False
            primitive = self.select_primitive.get_current_value()
            list_existing_files = glob.glob(os.path.join(self.output_dir,primitive,f"{task_name}_*.aedat"))
            current_attempt = len(list_existing_files) + 1
    
        else: # Continuous
            with_labels = True
            list_existing_files = glob.glob(os.path.join(self.output_dir,f"{task_name}_*.aedat"))
            current_attempt = len(list_existing_files) + 1
            primitive = None

        while True:
            try: 
                [final_times_list,first_ts,csv_file_dir] = self.capture_system.recording_function(current_attempt, task_name, primitive, paralel_thread)
            except Exception as e:
                self.terminate_thread(paralel_thread)
                self.print_message(f"{e}\n", "error")
                return
            else:
                current_attempt += 1
                self.file_manager.write_csv_file(final_times_list, first_ts, csv_file_dir, with_labels)
                self.print_message(f"Data was saved in {csv_file_dir}\n", "info")
                self.print_message(f"Recording duration: {(self.capture_system._stop_time-self.capture_system.start_time):.2f} seconds\n", "info")
                self.print_message("----------------------------------------------\n", "info")

                try:
                    self.capture_system._wait_for_button_input("red","Press the Red Button to continue or the White Button to quit.", 200, 10, True, paralel_thread)
                except Exception as e:
                    self.print_message("Capture closed\n", "error")
                    self.print_message("----------------------------------------------\n", "normal")
                    return

    def terminate_thread(self, paralel_thread):
        self.capture_system._close_capture_system(paralel_thread)
        self.print_message(f"Stopped capturing\n", "error")

class Button(CTkButton):

    def __init__(self, menu, title, r, c):
        CTkButton.__init__(self, master = menu, text = title)
        self.grid(row = r, column = c, ipadx = 5, ipady = 5)

class ComboFrame(CTkFrame):

    def __init__(self, menu, title, primitives, r, c):
        CTkFrame.__init__(self, master = menu, corner_radius = 0)

        self.label = CTkLabel(self, text = title, font = ("Arial",13))
        self.combo_box = CTkComboBox(self, values = primitives, state = "readonly")
        self.combo_box.set("idle")
    
        self.grid(row = r, column = c, columnspan = 2, sticky="nsew", padx = 10, pady = 10)
        self.label.pack(side="top", expand = True, pady = (15,0))
        self.combo_box.pack(side="top", expand = True, pady = (0,25))
    
    def get_current_value(self):
        return self.combo_box.get()      

class InputFrame(CTkFrame):

    def __init__(self, menu, title, r, c, with_button):
        CTkFrame.__init__(self, master = menu, corner_radius = 0)

        self.label = CTkLabel(self, text = title, font = ("Arial",13))
        self.input_text = CTkEntry(self)
        
        self.grid(row = r, column = c, sticky="nsew", padx = 10, pady = 10)
        
        if with_button:
            self.button = CTkButton(self, text = "Confirm")
            self.label.pack(side="top", expand = True, pady = (5,0))
            self.input_text.pack(side="top", expand = True, pady = (0,5))
            self.button.pack(side="top", expand = True, pady = (0,10))
        else:
            self.label.pack(side="top", expand = True, pady = (20,0))
            self.input_text.pack(side="top", expand = True, pady = (0,20))
    
    def get_current_value(self):
        return self.input_text.get() 

class RadioFrame(CTkFrame):

    def __init__(self, menu, title, text_options, r, c):
        CTkFrame.__init__(self, master = menu, corner_radius = 0)
        self.menu = menu
        self.radio_button1_enabled = True

        self.label = CTkLabel(self, text = title, font = ("Arial",13))
        self.radio_button1 = CTkRadioButton(self, text = text_options[0])
        self.radio_button2 = CTkRadioButton(self, text = text_options[1])
        self.radio_button1.select()
        self.radio_button1._command = self.fcn_radio1
        self.radio_button2._command = self.fcn_radio2

        self.grid(row = r, column = c, sticky="nsew", padx = 10, pady = 10)
        self.label.pack(side="top", expand = True)
        self.radio_button1.pack(side="top", expand = True)
        self.radio_button2.pack(side="top", expand = True, pady = (0,15))
    
    def fcn_radio1(self):
        self.radio_button2.deselect()
        self.radio_button1_enabled = True

    def fcn_radio2(self):
        self.radio_button1.deselect()
        self.radio_button1_enabled = False

class Menu(CTkFrame):

    def __init__(self, parent, title, cconfig):
        
        super().__init__(parent)
        self.place(x = 0, y = 0, relwidth = 1, relheight = 1)

        self.rowconfigure((0,3), weight = 1, uniform = "a")
        self.rowconfigure((1,2), weight = 2, uniform = "a")
        self.columnconfigure(cconfig, weight = 1, uniform = "a")

        title = CTkLabel(self, text = title, font = ("Arial",18))
        title.grid(row = 0, column = 0, columnspan = 2) 

if __name__ == "__main__":
    App('DAVIS Data Capture System')
