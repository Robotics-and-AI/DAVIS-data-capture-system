from capture_system import CaptureSystem
from file_manager import FileManager
from safe_io import SafeIO

import glob
import os

# -----------------------------------------

def main() -> None:
    
    OUTPUT_DIR = os.path.join(os.path.abspath(""),"data")

    selected_option = safe_io.safe_input("Select option: 1 - Record .aedat | 2 - Create .npy ")
    
    # ------------ RECORD EVENT DATA ------------

    if selected_option == "1":
        
        recording_mode = safe_io.safe_input("Choose recording mode: 1 - Primitive | 2 - Continuous ")
        try:
            capture_system.capture(recording_mode)
        except Exception as e:
            safe_io.print_error(str(e))

    # ------------ PROCESS FILE ------------

    elif selected_option == "2":
        
        processing_mode = safe_io.safe_input("Choose processing mode: 1 - Folder | 2 - All Files ")
        
        if processing_mode == "1":
            
            folder_name = safe_io.safe_input("Input name of folder: ")
            folder_dir = os.path.join(OUTPUT_DIR,folder_name)
            for file in os.listdir(folder_dir):
                if file.endswith(".aedat"):
                    file = file[:len(file)-6] # Remove .aedat from file name
                    file_dir_no_ext = os.path.join(folder_dir,file)
                    file_manager.aedat_to_npy(file_dir_no_ext)

        elif processing_mode == "2":
            
            list_all_files = glob.glob(os.path.join(OUTPUT_DIR,"*","*.aedat"))
            for file_dir_no_ext in list_all_files:
                file_dir_no_ext = file_dir_no_ext[:len(file_dir_no_ext)-6] # Remove .aedat from file name
                file_manager.aedat_to_npy(file_dir_no_ext)


if __name__ == "__main__":

    capture_system = CaptureSystem() 
    file_manager = FileManager()
    safe_io = SafeIO()
    main()
    safe_io.print_success("Program was terminated")

    
