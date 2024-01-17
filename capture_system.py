from file_manager import FileManager
from safe_io import SafeIO

import glob
import os
import serial
import serial.tools.list_ports
import socket
import threading
import time

class CaptureSystem:

    """ 
    Methods for recording event data using jAER

    Methods
    -------
    capture(recording_mode)
        Record and save event data as .aedat and timestamps in .csv
    """
    
    def __init__(self):
        
        self._lock = threading.Lock()
        self._safe_io = SafeIO()
        self._file_manager = FileManager()

        # jAER variables
        self._is_recording = False
        self._keep_recording = False
        self._exit_cue = False
        self._jaer_is_ready = False
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._data = b""
        self._file_name = b"a"

        # Arduino variables
        self._BOARD_TYPE = "Genuino Uno"
        self._is_reading_serial = False
        self._serial_thread = threading.Thread(target = self._read_serial)
        
        # Other variables
        self._stop_time = 0.0
        self._times_list = []
        self._TIME_PRESS_BUTTON = 0 # Time (sec) wait after pressing button. Default: 0
        self._OUTPUT_DIR = os.path.join(os.path.abspath(""),"data")

    # ------------ MAIN RECORDING METHOD ------------

    def capture(self,recording_mode: int) -> None:
        
        """
        Record and save event data as .aedat and timestamps in .csv
        """

        self._start_serial_thread()

        task_name = self._safe_io.safe_input("Insert name of task:")
        self._file_name = task_name.encode()

        if recording_mode == "1":
            
            PRIMITIVES = []
            for file in os.listdir(self._OUTPUT_DIR):
                file_path = os.path.join(self._OUTPUT_DIR, file)
                if os.path.isdir(file_path):
                    PRIMITIVES.append(file)

            self._safe_io.print_info("Available primitives: ")
            for element in PRIMITIVES:
                self._safe_io.print_info(f"{element}")
            primitive = self._safe_io.safe_input("Insert name of primitive:")
            while primitive not in PRIMITIVES:
                self._safe_io.print_error("Please choose one of the available primitives.")
                for element in PRIMITIVES:
                    self._safe_io.print_info(f"{element}")
                primitive = self._safe_io.safe_input("Insert name of primitive:")

            list_existing_files = glob.glob(os.path.join(self._OUTPUT_DIR,primitive,f"{task_name}_*.aedat"))
            current_attempt = len(list_existing_files) + 1
        
        else:
            list_existing_files = glob.glob(os.path.join(self._OUTPUT_DIR,f"{task_name}_*.aedat"))
            current_attempt = len(list_existing_files) + 1

        while True:
            
            self._set_keep_recording(False)
            self._set_start_time(self._TIME_PRESS_BUTTON)
            self._empty_times_list()

            # Record data using jAER
            self._set_jaer_is_ready(True)
            self._record_with_jaer()
            self._set_jaer_is_ready(False)

            aedat_file_dir = self._file_manager.move_aedat_file(self._data, task_name, current_attempt, primitive)

            # Get first timestamp of .aedat file
            first_ts_us = self._file_manager.decode_aedat_file(aedat_file_dir,True)[2]
            try:
                first_ts = first_ts_us[0] # in us
            except IndexError:
                self._close_capture_system()
                raise IndexError("The .aedat file is empty")

            csv_file_dir = aedat_file_dir.replace(".aedat","_labels.csv")
            final_times_list = self._get_times_list()

            if recording_mode == "1":
                self._file_manager.write_csv_file(final_times_list,first_ts,csv_file_dir,False) # Without labels
                
            elif recording_mode == "2":
                self._file_manager.write_csv_file(final_times_list,first_ts,csv_file_dir,True) # With labels
                
            self._safe_io.print_info(f"Recording duration: {(self._stop_time-self.start_time):.2f} seconds")
            current_attempt += 1
            
            self._wait_for_button_input("red","Press the Red Button to continue or the White Button to quit.", 200, 10, True)

    
    # ------------ RECORD WITH JAER METHOD ------------
            
    def _record_with_jaer(self) -> None:
        
        """
        Send commands to jAER to start and stop recording
        """

        try: 
            self._wait_for_button_input("pedal","Press the Pedal to start recording...", 500, 10, True)
        except RuntimeError:
            self._close_capture_system()
            raise

        # Start logging        
        self._add_to_times_list(self._get_start_time()) 
        self._set_start_time(time.time()+self._TIME_PRESS_BUTTON)
        try: 
            self._send_command_to_jaer((b"startlogging " + self._file_name)) 
        except OSError:
            self._close_capture_system()
            raise     

        try:
            self._wait_for_button_input("pedal","Press the Pedal to stop recording...", 3000, 10, False)
        except RuntimeError:
            self._close_capture_system()
            raise

        # Stop logging
        self._set_stop_time(time.time())
        self._add_to_times_list(self._get_stop_time()-self._get_start_time())
        try:
            self._send_command_to_jaer(b"stoplogging")
        except OSError:
            self._close_capture_system()
            raise 

    # ------------ START SERIAL THREAD METHOD ------------
        
    def _start_serial_thread(self) -> None:

        """
        Connect to arduino and start serial thread
        """

        all_ports = serial.tools.list_ports.comports()
        com_port = None
        for port, desc, _ in all_ports:
            if self._BOARD_TYPE in desc: 
                com_port = port 
                self._safe_io.print_success(f"{self._BOARD_TYPE} board was found at {com_port}")
        if com_port is None:
            raise OSError(f"Board {self._BOARD_TYPE} was not found")

        # Connect to Arduino
        try:
            self.arduino = serial.Serial(port = com_port, baudrate = 9600, timeout = .1)
        except Exception:
            self._close_capture_system()
            raise OSError(f"Unable to connect to {self._BOARD_TYPE}")
        
        # Start serial thread
        self._set_is_reading_serial(True)
        self._serial_thread.start()

    # ------------ READ SERIAL (THREAD) METHOD ------------
        
    def _read_serial(self) -> None:
        
        """
        Get and process button inputs detected by the Arduino
        """
        
        while self._get_is_reading_serial():
            time.sleep(0.01)
            value = self.arduino.readline()

            if value == b'pedal_high\r\n' and self._get_jaer_is_ready():
                # If pressed, start or stop recording
                if not self._get_is_recording():
                    self._set_is_recording(True)
                    self._safe_io.print_info("Started recording")
                else:
                    self._set_is_recording(False)
                    self._set_exit_cue(False)
                    self._safe_io.print_info("Stopped recording")

            elif value == b'white\r\n':
                # If pressed, register time to times_list
                if self._get_is_recording() is True:
                    current_time = time.time()        
                    self._add_to_times_list(current_time - self._get_start_time())
                    self._add_to_times_list(current_time - self._get_start_time() + 2*self._TIME_PRESS_BUTTON)
                    self._safe_io.print_info("Time was registered")
                else:
                    self._set_exit_cue(True)

            elif value == b'red\r\n':
                #If pressed, keep recording
                if not self._get_is_recording():
                    self._set_keep_recording(True)
                    self._safe_io.print_success("Ready for next recording.")

    # ------------ WAIT FOR BUTTON INPUT METHOD ------------
                    
    def _wait_for_button_input(self, button:str, text: str, n_cycles: int, max_wait: int, condition: bool) -> None:   
        
        """
        Wait for specific button input until max_wait
        """
        
        counter = 0
        counter_wait = 0

        if button == "pedal":
            while self._get_is_recording() is not condition:
                
                time.sleep(0.01) # n_cycles = 100 -> approx. 1 second
                if counter > n_cycles:
                    counter = 0
                    self._safe_io.print_warning(text) # Warn that capture() is waiting for button prompt
                    counter_wait += 1
                elif counter_wait == max_wait: # Timeout condition
                    self._close_capture_system()
                    raise RuntimeError(f"No input detected. Function timed out.")
                else:
                    counter += 1

        elif button == "red":
            while self._get_keep_recording() is not condition:
                
                if self._get_exit_cue():
                    self._close_capture_system()
                    raise OSError(f"Exit program.")
                
                time.sleep(0.01) # n_cycles = 100 -> approx. 1 second
                if counter > n_cycles:
                    counter = 0
                    self._safe_io.print_warning(text) # Warn that capture() is waiting for button prompt
                    counter_wait += 1
                elif counter_wait == max_wait: # Timeout condition
                    self._close_capture_system()
                    raise RuntimeError(f"No input detected. Function timed out.")
                else:
                    counter += 1

    # ------------ SEND COMMAND TO JAER METHOD ------------
        
    def _send_command_to_jaer(self,command: bytes) -> None:
        
        """
        Send given command to jAER
        """
        
        self._s.sendto(command, ("localhost", 8997)) 
        try:
            self._data = self._s.recvfrom(3000)
        except Exception:
            self._close_capture_system()
            raise OSError(f"Unable to connect to jAER") 

    # ------------ CLOSE CAPTURE SYSTEM METHOD ------------
    
    def _close_capture_system(self) -> None:
    
        """
        Terminate thread and serial connection
        """
    
        self._set_is_reading_serial(False)
        self._serial_thread.join()
        self.arduino.close()

    # ------------ SETTER AND GETTER METHODS ------------

    # - Set and get for variable is_recording -
    def _set_is_recording(self, val: bool) -> None:
        with self._lock:
            self._is_recording = val

    def _get_is_recording(self) -> bool:
        with self._lock:
            return self._is_recording is True
    
    # - Set and get for variable exit_cue -
    def _set_exit_cue(self, val: bool) -> None:
        with self._lock:
            self._exit_cue = val

    def _get_exit_cue(self) -> bool:
        with self._lock:
            return self._exit_cue is True

    # - Set and get for variable exit_cue -
    def _set_jaer_is_ready(self, val: bool) -> None:
        with self._lock:
            self._jaer_is_ready = val

    def _get_jaer_is_ready(self) -> bool:
        with self._lock:
            return self._jaer_is_ready is True

    # - Set and get for variable keep_recording -
    def _set_keep_recording(self, val: bool) -> None:
        with self._lock:
            self._keep_recording = val

    def _get_keep_recording(self) -> bool:
        with self._lock:
            return self._keep_recording is True

    # - Set and get for variable is_reading_serial -
    def _set_is_reading_serial(self, val: bool) -> None:
        with self._lock:
            self._is_reading_serial = val

    def _get_is_reading_serial(self) -> bool:
        with self._lock:
            return self._is_reading_serial is True

    # - Set and get for variable start_time -
    def _set_start_time(self, val: float) -> None:
        with self._lock:
            self.start_time = val

    def _get_start_time(self) -> float:
        with self._lock:
            return self.start_time

    # - Set and get for variable stop_time -
    def _set_stop_time(self, val: float) -> None:
        with self._lock:
            self._stop_time = val

    def _get_stop_time(self) -> float:
        with self._lock:
            return self._stop_time

    # - Methods for variable times_list -
    
    def _empty_times_list(self) -> None:
        with self._lock:
            self._times_list = []
    
    def _add_to_times_list(self, val: float) -> None:
        with self._lock:
            self._times_list.append(val)

    def _get_times_list(self) -> list:
        with self._lock:
            return self._times_list