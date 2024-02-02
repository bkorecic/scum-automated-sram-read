NUMBER_OF_CYCLES = 1000               # Number of readouts (power cycles)
YKUSHCMD_PATH = "/usr/bin/ykushcmd" # Path to ykushcmd executable
SERIAL_PORT = "/dev/ttyUSB0"        # Device name of serial port
NRF_PORT = "/dev/ttyACM3"           # Device name of the nRF

# You probably don't need to edit the following lines
BINARY_IMAGE = "sram_read.bin"  # Compiled program for SCuM to bootload
LOOK_FOR_STR = b"SRAM_DATA="    # Marker for SRAM data
