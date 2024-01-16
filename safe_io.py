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

            