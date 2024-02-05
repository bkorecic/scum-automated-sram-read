#!/usr/bin/python
from bootload import bootload
from config import Config
import pathlib
import datetime
import os
import sys
import serial
import time
import subprocess


def main():
    # Make results directory if it doesn't exist
    base_dir = pathlib.Path(__file__).parent
    pathlib.Path(base_dir / 'results').mkdir(exist_ok=True)
    # Use timestamp for results file
    basename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    results_path = base_dir / 'results' / (basename + '.csv')
    results_file = open(results_path, 'w')
    err_log_path = base_dir / 'results' / (basename + '-errors.txt')
    err_log_file = open(err_log_path, 'w')

    # Success: the SRAM data was sent and read without problems
    successes = 0
    # Timeout: for some reason SCuM was not able to print the SRAM data
    timeouts = 0
    # Failure: the received SRAM data was corrupted
    failures = 0
    # Retry: the bootload failed (nRF was not detected or similar problems)
    retries = 0
    for attempt in range(Config.NUMBER_OF_CYCLES):
        start_time = time.time()
        print('Starting power cycle. Switching off the USB hub.', end='')
        # unplug the usb cables (SRAM is totally turned off)
        subprocess.run([Config.YKUSHCMD_PATH, "-d", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)

        # wait for the SRAM cells to get their default values
        time.sleep(5)

        print('\33[2K\rSwitching on the USB hub.', end='')
        # plug the usb cables
        subprocess.run([Config.YKUSHCMD_PATH, "-u", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)

        print('\33[2K\rWaiting for nRF to start.', end='')
        # wait for the nRF to bootload
        time.sleep(10)

        print('\33[2K\rFlashing the SCuM firmware.', end='')
        # flash the firmware into the SCuM chip through the nRF
        # the nRF will send back a confirmation when done
        try:
            bootload(Config.NRF_PORT, Config.BINARY_IMAGE)
        except Exception as e:
            err_log_file.write(e)
            err_log_file.write('\n')
            print()  # need to end tests with a newline
            retries += 1
            continue

        start_timestamp = time.time()

        print('\33[2K\rOpening the serial port and waiting for the SRAM data.',
              end='')
        # open the serial port with SCuM
        uart_ser = serial.Serial(
            timeout=Config.SERIAL_TIMEOUT,
            port=Config.SERIAL_PORT,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        if uart_ser.is_open != 1:
            uart_ser.open()

        # read the output of the firmware running on SCuM
        while uart_ser.is_open:
            data = uart_ser.readline()
            if not data.endswith('\n'):
                # if newline is missing, it returned on timeout
                timeouts += 1
                uart_ser.close()
            if data.startswith(Config.LOOK_FOR_STR):
                try:
                    results_file.write(','.join(
                        [str(start_timestamp),
                         str(time.time()),
                         data.lstrip(Config.LOOK_FOR_STR)  # Strip marker
                             .decode('utf-8')  # Convert to string
                             .rstrip()])  # Strip newline characters
                        + '\n')
                    successes += 1
                except Exception as e:
                    err_log_file.write(e)
                    err_log_file.write('\n')
                    failures += 1
                uart_ser.close()
        time_elapsed = time.time() - start_time
        print(
            f'\33[2K\rTotal attempts: {attempt+1} | '
            f'Succeeded: {successes} | '
            f'Timeouts: {timeouts} | '
            f'Failed: {failures} | '
            f'Retried: {retries} | '
            f'Cycle time: {time_elapsed:5.2f}s')


if __name__ == '__main__':
    if os.name == 'posix' and os.geteuid() != 0:
        print('Must run as root')
        sys.exit(1)
    if not pathlib.Path(Config.YKUSHCMD_PATH).is_file():
        print('Executable ykushcmd not found,'
              ' check config.py or file permissions')
        sys.exit(1)
    main()
