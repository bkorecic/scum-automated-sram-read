#!/usr/bin/python
from bootload import bootload
from config import config
import pathlib
import datetime
import os
import sys
import serial
import time
import subprocess
import csv


def main():
    # Make results directory if it doesn't exist
    base_dir = pathlib.Path(__file__).parent
    pathlib.Path(base_dir / 'results').mkdir(exist_ok=True)
    # Use timestamp for results file
    results_path = base_dir / 'results' / \
        (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv')
    results_writer = csv.writer(open(results_path, 'w', newline=''))

    successes = 0
    failures = 0
    retries = 0
    for attempt in range(config.NUMBER_OF_CYCLES):
        print('Starting power cycle. Switching off the USB hub.')
        # unplug the usb cables (SRAM is totally turned off)
        subprocess.run([config.YKUSHCMD_PATH, "-d", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)

        # wait for the SRAM cells to get their default values
        time.sleep(5)

        print('Switching on the USB hub.')
        # plug the usb cables
        subprocess.run([config.YKUSHCMD_PATH, "-u", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)

        print('Waiting for nRF to start.')
        # wait for the nRF to bootload
        time.sleep(5)

        print('Flashing the SCuM firmware.')
        # flash the firmware into the SCuM chip through the nRF
        # the nRF will send back a confirmation when done
        try:
            bootload(config.NRF_PORT, config.BINARY_IMAGE)
        except Exception as e:
            print(e)
            retries += 1
            continue

        start_timestamp = time.time()

        print('Opening the serial port and waiting for the SRAM data.')
        # open the serial port with SCuM
        uart_ser = serial.Serial(
            timeout=70,
            port=config.SERIAL_PORT,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        if uart_ser.is_open != 1:
            uart_ser.open()

        failures += 1

        # read the output of the firmware running on SCuM
        # print('Reading the serial port.')
        while uart_ser.is_open:
            data = uart_ser.readline()
            if data.startswith(config.LOOK_FOR_STR):
                results_writer.writerow(
                    [start_timestamp,
                     time.time(),
                     data.lstrip(config.LOOK_FOR_STR).decode('utf-8')])
                successes += 1
                failures -= 1
            # when finishing this round close the serial port
            # with SCuM to allow the nRF to use it later
            elif data.startswith(b'TEST DONE'):
                uart_ser.close()
        print(
            f'Total attempts: {attempt+1}\t'
            f'Succeeded: {successes}\t'
            f'Failed: {failures}\tRetried: {retries}')


if __name__ == '__main__':
    if os.name == 'posix' and os.geteuid() != 0:
        print('Must run as root')
        sys.exit(1)
    if not pathlib.Path(config.YKUSHCMD_PATH).is_file():
        print('Executable ykushcmd not found,'
              ' check config.py or file permissions')
        sys.exit(1)
    main()
