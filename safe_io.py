import constants as const

import cv2 as cv
import numpy as np
import threading

class SafeIO():

    """ 
    Methods for thread-safe input and output

    Methods
    -------
    safe_print(text):
        Print text with white color
    safe_input(text):
        Print text with yellow color and returns input
    safe_imshow(frame,image_type,roi)
        Show frame in given image_type (jet or gray) and with roi overlayed

    print_sucess(text):
        Print text with green color
    print_info(text):
        Print text with blue color
    print_warning(text):
        Print text with yellow color
    print_error(text):
        Print text with red color
    """

    def __init__(self):
        
        self._lock = threading.Lock()
        self._RESOLUTION = const.DAVIS_RESOLUTION

    # ------------ SAFE PRINTING METHOD ------------

    def safe_print(self, text:str) -> None:
        
        """
        Print text with white color
        """

        with self._lock:
            print(text)

    # ------------ SAFE INPUT METHOD ------------

    def safe_input(self,text:str) -> None:

        """
        Print text with yellow color and returns input
        """

        with self._lock:
            return input("\033[93m {}\033[00m" .format(text))

    # ------------ SAFE IMSHOW METHOD ------------

    def safe_imshow(self, frame:np.ndarray, image_type:str, roi:list[int]) -> None:
        
        """
        Show frame in given image_type (jet or gray) and with roi overlayed
        """

        frame = np.multiply(frame,(255/frame.max()))

        if image_type == "jet":
            
            frame = cv.flip(frame,-1)
            frame8 = frame.astype(np.uint8)
            frame8 = cv.applyColorMap(frame8, cv.COLORMAP_JET)

        elif image_type == "gray":
            
            frame = cv.flip(frame,-1)
            frame8 = frame.astype(np.uint8)
            if roi: 
                frame8 = cv.cvtColor(frame8,cv.COLOR_GRAY2BGR)

        if roi:
            color = (0,0,255) # Red color in BGR
            start_point = (self._RESOLUTION[0]-roi[0][0],self._RESOLUTION[1]-roi[1][1])
            end_point = (self._RESOLUTION[0]-roi[0][1],self._RESOLUTION[1]-roi[1][0])
            frame8 = cv.rectangle(frame8, start_point, end_point, color, 2)

        with self._lock: 
            cv.imshow("frame",frame8)
            cv.waitKey(1)

    # ------------ COLORED TERMINAL TEXT ------------

    def print_success(self, text:str) -> None: 

        """
        Print text with green color
        """

        self.safe_print("\033[92m {}\033[00m".format(text)) 


    def print_info(self, text:str) -> None: 

        """
        Print text with blue color
        """

        self.safe_print("\033[96m {}\033[00m" .format(text))


    def print_warning(self, text:str) -> None: # Yellow
        
        """
        Print text with yellow color
        """

        self.safe_print("\033[93m {}\033[00m" .format(text))


    def print_error(self, text:str) -> None: # Red

        """
        Print text with red color
        """
        
        self.safe_print("\033[91m {}\033[00m" .format(text))

            