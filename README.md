# scum-automatic-testing

Python code for running a program multiple times on a SCuM, using a nRF for bootloading and a YKUSH board for programatically switching on and off the other boards.

## Requirements

### nRF wired bootloading

You need to setup a nRF52840DK to bootload SCuM. Check the [Bootload & Wiring Guide](https://crystalfree.atlassian.net/wiki/spaces/SCUM/pages/1901559821/Sulu+Programming+With+nRF+Setup).

### YKUSH USB Switchable Hub

In order to power cycle the whole setup, we put it behind a switchable USB hub. This project is intended to be used with the [YKUSH board](https://www.yepkit.com/products/ykush). See the setup guide for [Linux](https://www.yepkit.com/learn/setup-guide-ykush)/[Windows](https://www.yepkit.com/learn/setup-guide-ykush-windows).

By following the instructions you should get an executable file (`ykushcmd`) for controlling the USB hub. This project uses that executable file.

### Python libraries

You can see the required python libraries in `requirements.txt`. You can install them as normal with `pip install -r requirements.txt`. It is recommended to setup a [virtual environment](https://docs.python.org/3/library/venv.html) first.

## Configuration

You can find the following configuration variables in `config.py`:
* `NUMBER_OF_CYCLES`: Number of power cycles or SRAM readouts to do.
* `YKUSHCMD_PATH`: Path to the `ykushcmd` executable.
* `SERIAL_PORT`: Device name of the serial port. In Linux it should point to the device file, and in Windows it is probably `COM` followed by a number.
* `NRF_PORT`: Device name of the nRF, similarly to the serial port.

## Usage

Run the main file:

```
python3 main.py
```

To control the YKUSH board, you may need to run it as root:

```
sudo python3 main.py
```
