"""The serial interface is used to write data to and read data from a serial port.

For a given baudrate, the packet size and the open timeout are dongle-dependent.
For an Anker USB-C dongle, the serial packet size cannot exceed 32 bytes, and a
serial open timeout of 2 seconds is required. For an Apple USB-C dongle, the
serial packet size cannot exceed 96 bytes, and no serial open timeout is needed.
"""

import time

import serial
from absl import logging

# The maximum size in bytes of each packet to be written to the serial port.
# This value is dongle-dependent.
SERIAL_PACKET_SIZE = 32

# The timeout between consecutive packet writes.
SERIAL_PACKET_WRITE_TIMEOUT = 0.005  # seconds

# The timeout in seconds after opening the serial port.
# This value is dongle-dependent.
SERIAL_OPEN_TIMEOUT = 2  # seconds

# The timeout in seconds for a read from the serial port.
SERIAL_READ_TIMEOUT = 5  # seconds

# The timeout in seconds for a write to the serial port.
SERIAL_WRITE_TIMEOUT = 2  # seconds


class SerialInterface:
    """Interface to a serial port."""

    def __init__(self, port: str, baudrate: int, verbose: bool = False):
        # Open the serial port.
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=SERIAL_READ_TIMEOUT,
            write_timeout=SERIAL_WRITE_TIMEOUT,
        )
        time.sleep(SERIAL_OPEN_TIMEOUT)

        self.verbose = verbose

    def write(self, data: bytes) -> None:
        """Writes the data to the serial port.

        Args:
            data: Data to be written to the serial port.
        """
        if len(data) <= 0:
            return
        num_bytes_written = 0
        while num_bytes_written < len(data):
            num_bytes_to_write = min(SERIAL_PACKET_SIZE,
                                     len(data) - num_bytes_written)
            num_bytes_sent = self.serial.write(
                data[num_bytes_written:num_bytes_written + num_bytes_to_write])
            if self.verbose:
                logging.info("Wrote %d bytes to the serial port.",
                             num_bytes_sent)
            if num_bytes_sent is not None:
                num_bytes_written += num_bytes_sent
            time.sleep(SERIAL_PACKET_WRITE_TIMEOUT)

    def read(self) -> bytes:
        """Reads the data from the serial port.

        Returns:
            The data that has been read.
        """
        read_data = self.serial.read_until()
        if self.verbose:
            logging.info("Read %d bytes from the serial port.", len(read_data))
        return read_data

