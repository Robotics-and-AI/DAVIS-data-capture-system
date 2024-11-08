from safe_io import SafeIO

import numpy as np
import os
import shutil
import struct

class FileManager:

    """ 
    Methods for reading and writing to files

    Methods
    -------
    aedat_to_npy(file_name_no_ext)
        Read .aedat file and save event data into .npy file
    decode_aedat_file(file_name_with_ext, only_first_event)
        Read .aedat file and output event data as x,y,ts,pol
    move_aedat_file(byte_string, file_name, user_number, current_attempt, primitive)
        Move .aedat file from jAER folder to recorded_data folder
    read_npy_file(file_name_no_ext)
        Read .npy file and output event data as x,y,ts,pol
    write_csv_file(final_times_list,first_ts,csv_file_dir,without_labels,mode)
        Write timestamps and labels to .csv file
    """

    def __init__(self, output_dir):
        
        self._safe_io = SafeIO()
        self._READ_MODE = ">II"
        self._N_BYTES = 8
        self._MASK = [0x003ff000,0x7fc00000,0x800,0]
        self._SHIFT = [12,22,11,31]
        self._OUTPUT_DIR = output_dir

    # ------------ AEDAT TO NPY FILE METHOD ------------

    def aedat_to_npy(self,file_name_no_ext:str) -> None:
        
        """
        Read .aedat file and save event data into .npy file
        """

        if not os.path.exists(f"{file_name_no_ext}_events.npy"):
            try:
                x,y,ts,pol = self.decode_aedat_file(f"{file_name_no_ext}.aedat",False)
            except Exception: 
                raise
            
            try:
                array_events = np.array([x,y,ts,pol],dtype = 'int32') # If timestamp values are suposed to be > int32, change to int64
            except Exception:
                raise OSError("Corrupted file: Timestamp values surpass int32 limit.")
            
            try:    
                np.save(f"{file_name_no_ext}_events.npy", array_events)
            except Exception:
                raise OSError(f"Unable to save data to {file_name_no_ext}_events.npy")

    # ------------ DECODE AEDAT FILE METHOD ------------

    def decode_aedat_file(self, file_name_with_ext: str, only_first_event: bool) -> list[list[int]]:
        
        """
        Read .aedat file and output event data as x,y,ts,pol
        """

        x = []
        y = []
        ts = []
        pol = []

        try:
            aer_file = open(file_name_with_ext, 'rb')
        except OSError:
            raise OSError("File not found.")
        
        length_file = os.stat(file_name_with_ext).st_size 
        self._safe_io.print_info(f"Processing file {file_name_with_ext}")

        bytes_pos = 0
        line = aer_file.readline()
        while line and line[0:1] == b'#': # Ignore ASCII header
            bytes_pos += len(line)
            line = aer_file.readline()            
            
        aer_file.seek(bytes_pos)
        aer_raw_data = aer_file.read(self._N_BYTES)
        bytes_pos += self._N_BYTES
        
        while bytes_pos < length_file:
            address, timestamp = struct.unpack(self._READ_MODE, aer_raw_data)
            event_type = (address >> self._SHIFT[3])

            if event_type == self._MASK[3]:
                x.append((address & self._MASK[0]) >> self._SHIFT[0])
                y.append((address & self._MASK[1]) >> self._SHIFT[1])
                ts.append(timestamp)
                pol.append((address & self._MASK[2]) >> self._SHIFT[2])

                if only_first_event:
                    break

            aer_file.seek(bytes_pos)
            aer_raw_data = aer_file.read(self._N_BYTES)
            bytes_pos += self._N_BYTES

        ts = np.subtract(ts,ts[0]) # start ts array always from 0

        try:
            print ("read %i (~ %.2fM) AE events, duration= %.2fs" % (len(ts), len(ts) / float(10 ** 6), (ts[-1] - ts[0]) * 0.000001))
            n = 5
            print ("showing first %i:" % (n))
            print ("timestamps: %s \nX-addr: %s\nY-addr: %s\npolarity: %s" % (ts[0:n], x[0:n], y[0:n], pol[0:n]))
        except:
            print ("failed to print statistics")

        return x,y,ts,pol

    # ------------ MOVE AEDAT FILE METHOD ------------

    def move_aedat_file(self, byte_string:bytes, task_name:str, current_attempt:int, primitive:str) -> str:
        
        """
        Move .aedat file from jAER folder to recorded_data folder
        """

        out_file_dir = byte_string[0].rsplit(b"file ")
        out_file_dir = out_file_dir[1].split(b"\n")
        out_file_dir = out_file_dir[0].decode()
        
        if primitive:
            aedat_file_dir = os.path.join(self._OUTPUT_DIR, primitive, f"{task_name}_{current_attempt}.aedat")
        else:
            aedat_file_dir = os.path.join(self._OUTPUT_DIR, f"{task_name}_{current_attempt}.aedat")
        
        shutil.move(out_file_dir, aedat_file_dir)

        return aedat_file_dir

    # ------------ READ FROM NPY FILE METHOD ------------
    
    def read_npy_file(self,file_name_no_ext:str) -> list[list[int]]:

        """
        Read .npy file and output event data as x,y,ts,pol
        """
            
        try:
            event_data = np.load(f"{file_name_no_ext}_events.npy")
        except Exception:
            raise OSError("File not found.")

        x = event_data[0][:]
        y = event_data[1][:]
        ts = event_data[2][:]
        pol = event_data[3][:]
        
        return x,y,ts,pol

    # ------------ WRITE CSV FILE METHOD ------------    

    def write_csv_file(self,timestamp_list:list[int],first_ts:int,csv_file_dir:str,with_labels:bool) -> None:
        
        """
        Write timestamps and labels to .csv file
        """

        if not with_labels:
            times_csv = [[timestamp_list[0]*(10**6)+first_ts, timestamp_list[-1]*(10**6)+first_ts]]
            np.savetxt(csv_file_dir, times_csv, delimiter = ", ", fmt = ["%d","%d"])
        
        else:
            times_csv = []
            n_labels = len(timestamp_list)//2
            try:
                labels = list(map(int, self._safe_io.safe_input(f"Insert the {n_labels} label(s) (int):").split(",")))
            except ValueError:
                raise ValueError("Inserted non-integer labels")
            while len(labels) != n_labels:
                self._safe_io.print_error(f"{len(labels)} label(s) and {n_labels} time(s). Please insert correct amount of label(s):")
                labels = list(map(int, input().split(",")))

            for i in range(n_labels):
                times_csv.append([labels[i],timestamp_list[2*i]*(10**6)+first_ts, timestamp_list[(2*i)+1]*(10**6)+first_ts])
            np.savetxt(csv_file_dir, times_csv, delimiter = ", ", fmt = ["%d","%d","%d"])
        
