#!/usr/bin/python
from datetime import date
from bootload import bootload
import os
import sys
import serial
import time
import subprocess
import re
import csv


def main():
    uart_port = "/dev/ttyUSB0"

    correct_key = "683d02f7e2fa18fd"

    results_path = 'results/' + date.today().isoformat()
    results_writer = csv.writer(open(results_path, 'w', newline=''))

    successes = 0
    failures = 0
    retries = 0
    while True:
        # unplug the usb cables (SRAM is totally turned off)
        subprocess.run(["/usr/bin/ykushcmd", "-d", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)
        # wait for the SRAM cells to get their default values
        time.sleep(5)
        # plug the usb cables
        subprocess.run(["/usr/bin/ykushcmd", "-u", "a"], stdin=None,
                       stdout=None, stderr=None, shell=False)
        # wait for the nRF to bootload
        time.sleep(10)

        # flash the firmware into the SCuM chip through the nRF
        # the nRF will send back a confirmation when done
        try:
            bootload()
        except:
            retries += 1
            continue

        # open the serial port with SCuM
        uart_ser = serial.Serial(
            port=uart_port,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        if uart_ser.is_open != 1:
            uart_ser.open()

        # read the output of the firmware running on SCuM
        # print('Reading the serial port.')
        while uart_ser.is_open:
            data = uart_ser.readline()
            match = re.search(b'Key: "(.+?)"', data)
            if match:
                key = match.group(1).decode('utf-8')
                if key == correct_key:
                    successes += 1
                else:
                    failures += 1
                print(
                    f"Successes: {successes}, failures: {failures}, retries: {retries}")
            # when finishing this round close the serial port with SCuM to allow
            # the nRF to use it later
            if data == b'TEST DONE\r\n':
                # print("Closing the serial port.")
                uart_ser.close()


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('Must run as root')
        sys.exit(1)
    main()
