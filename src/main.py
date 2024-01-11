from algorithms import Algorithms
from capture_system import CaptureSystem
from file_manager import FileManager
from real_time import RealTime
from safe_io import SafeIO
import constants as const

#import cProfile - for testing performance
import glob
import numpy as np
import os

# -----------------------------------------

def main() -> None:
    
    selected_option = safe_io.safe_input("Select option: 1 - Record | 2 - Process File | 3 - Show Video | 4 - Real-time Viewer ")
    
    # ------------ RECORD ------------

    if selected_option == "1":
        
        #recording_mode = safe_io.safe_input("Choose recording mode: 1 - Primitive | 2 - Continuous ")
        try:
            capture_system.capture("1") # Change to "2" for Continuous
        except Exception as e:
            safe_io.print_error(str(e))

    # ------------ PROCESS FILE ------------

    elif selected_option == "2":
        
        processing_option = safe_io.safe_input("Choose processing option: 1 - Get events | 2 - Get ROI")
        processing_mode = safe_io.safe_input("Choose processing mode: 1 - Single File | 2 - Folder | 3 - All Files")

        if processing_mode == "1":

            file_name = safe_io.safe_input("Input name of file: ")

            if processing_option == "1":
                if f"{file_name}.aedat" in os.listdir(const.OUTPUT_DIR):
                    file_dir_no_ext = os.path.join(const.OUTPUT_DIR,file_name)
                    file_manager.aedat_to_npy(file_dir_no_ext)
                else:
                    safe_io.print_error("File not found.")
                
            elif processing_option == "2":
                if f"{file_name}_events.npy" in os.listdir(const.OUTPUT_DIR):
                    file_dir_no_ext = os.path.join(const.OUTPUT_DIR,file_name)
                    write_roi_csv_file(file_dir_no_ext)
                else:
                    safe_io.print_error("File not found.")
            
        elif processing_mode == "2":
            
            folder_name = safe_io.safe_input("Input name of folder: ")
            folder_dir = os.path.join(const.OUTPUT_DIR,folder_name)

            if processing_option == "1":
                for file in os.listdir(folder_dir):
                    if file.endswith(".aedat"):
                        file = file[:len(file)-6] # Remove .aedat from file name
                        file_dir_no_ext = os.path.join(folder_dir,file)
                        file_manager.aedat_to_npy(file_dir_no_ext)

            elif processing_option == "2":
                for file in os.listdir(folder_dir):
                    if file.endswith(".npy"):
                        file = file[:len(file)-11] # Remove _events.npy from file name
                        file_dir_no_ext = os.path.join(folder_dir,file)
                        write_roi_csv_file(file_dir_no_ext)

        elif processing_mode == "3":

            if processing_option == "1":
                list_all_files = glob.glob(os.path.join(const.OUTPUT_DIR,"*","*.aedat"))
                for file_dir_no_ext in list_all_files:
                    file_dir_no_ext = file_dir_no_ext[:len(file_dir_no_ext)-6] # Remove .aedat from file name
                    file_manager.aedat_to_npy(file_dir_no_ext)

            if processing_option == "2":
                list_all_files = glob.glob(os.path.join(const.OUTPUT_DIR,"*","*.npy"))
                for file_dir_no_ext in list_all_files:
                    file_dir_no_ext = file_dir_no_ext[:len(file_dir_no_ext)-11] # Remove .aedat from file name
                    write_roi_csv_file(file_dir_no_ext)

    # ------------ SHOW VIDEO ------------

    elif selected_option == "3":
        
        file_dir_no_ext = os.path.join(const.OUTPUT_DIR,"pick","dovetail_1")

        try:
            x,y,ts,pol = file_manager.read_npy_file(file_dir_no_ext)
        except Exception as e:
            safe_io.print_error(str(e))
        else:
            for i in range(0,len(x),3000):
                frame = algorithms.create_tbr_frame(x[i:i+3000],y[i:i+3000],ts[i:i+3000],pol[i:i+3000],const.N_BITS_TBR,"TTR")
                x_range, y_range = algorithms.region_of_interest(x[i:i+3000],y[i:i+3000])
                safe_io.safe_imshow(np.transpose(frame),"jet",[x_range,y_range])

    # ------------ REAL-TIME VIEWER ------------

    elif selected_option == "4":
        try:
            real_time.display_event_frames()
        except Exception as e:
            safe_io.print_error(str(e))

# -----------------------------------------
            
def write_roi_csv_file(file_name_no_ext):
        list_roi_x = []
        list_roi_y = []
        try:
            x,y,ts,pol = file_manager.read_npy_file(file_name_no_ext)
        except Exception as e:
            safe_io.print_error(str(e))
        else:
            for i in range(0,len(x),3000):
                x_range, y_range = algorithms.region_of_interest(x[i:i+3000],y[i:i+3000])
                list_roi_x.append(x_range)
                list_roi_y.append(y_range)

        file_manager.write_csv_file(list_roi_x,0,f"{file_name_no_ext}_roi_x.csv",False,"roi")
        file_manager.write_csv_file(list_roi_y,0,f"{file_name_no_ext}_roi_y.csv",False,"roi")

if __name__ == "__main__":
    
    algorithms = Algorithms()
    capture_system = CaptureSystem() 
    file_manager = FileManager()
    real_time = RealTime()
    safe_io = SafeIO()

    # cProfile.run('main()') - for testing performance
    main()
    safe_io.print_success("Program was terminated")

    
