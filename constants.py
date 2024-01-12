import os

# - Generics -
BOARD_TYPE = "Genuino Uno"                                          # Arduino board type
TIME_PRESS_BUTTON = 0                                               # Time (sec) to press button
BUFSIZE_RT = 10000                                                  # UDP buffer size (receive UDP)
PRIMITIVES = ["idle","pick","place","screw"]                        # List of available primitives

# - Region of interest -
EDGE_SIZE = 5                                                       # Number of successive values that define the edge
EDGE_SUM = 6                                                        # Maximum value that dictates borders of ROI

# - TBR/TTR method -
N_BITS_TBR = 8                                                      # Number of bits to use in TBR and TTR methods


# --------------------------------------------------
# ------- DO NOT CHANGE THE FOLLOWING VALUES -------
# --------------------------------------------------


# ---------- GENERICS ----------

DAVIS_RESOLUTION = [240,180]                                        # DAVIS event camera resolution
OUTPUT_DIR = os.path.join(os.path.abspath(""),"recorded_data")      # Directory for files

# ------- CAPTURE SYSTEM -------

UDP_IP = "localhost"                                                # IP jAER Viewer (send commands)
UDP_PORT = 8997                                                     # UDP jAER Viewer (send commands)
BUFSIZE = 3000                                                      # UDP buffer size (send commands)
UDP_RT_IP = "localhost"                                             # IP jAER Viewer (receive UDP)
UDP_RT_PORT = 8991                                                  # UDP jAER Viewer (receive UDP)

# ------- FILE MANAGER -------

READ_MODE = ">II"                                                   # 2x ulong, 4B+4B
N_BYTES = 8                                                         # Number of bytes per AE
MASK = [0x003ff000,0x7fc00000,0x800,0]                              # Masks for X, Y, Polarity and Event Type, respectively
SHIFT = [12,22,11,31]                                               # Bit shifts for X, Y, Polarity and Event Type, respectively