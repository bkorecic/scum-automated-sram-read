from serial_interface import SerialInterface

import random

def bootload(nRF_port, binary_image):
    # Serial connections
    nRF_ser = None

    #boot_mode = '3wb'
    pad_random_payload = False

    # Open COM port to nRF
    nRF_ser = SerialInterface(
        port=nRF_port,
        baudrate=250000)

    # Open binary file from Keil
    with open(binary_image, 'rb') as f:
        bindata = bytearray(f.read())

    # Need to know how long the binary payload to pad to 64kB
    code_length = len(bindata) - 1
    pad_length = 65536 - code_length - 1

    # print(code_length)

    # Optional: pad out payload with random data if desired
    # Otherwise pad out with zeros - uC must receive full 64kB
    if (pad_random_payload):
        for _ in range(pad_length):
            bindata.append(random.randint(0, 255))
        code_length = len(bindata) - 1 - 8
    else:
        for _ in range(pad_length):
            bindata.append(0)


    # Transfer payload to nRF
    # nRF_ser.write(b'transfersram\n')
    # print(nRF_ser.read_until())
    # Send the binary data over uart
    nRF_ser.write(bindata)
    # and wait for response that writing is complete
    # print(nRF_ser.read())
    nRF_ser.read()
    nRF_ser.read()

    # Execute 3-wire bus bootloader on nRF
    # nRF_ser.write(b'boot3wb\n')

    # Display 3WB confirmation message from nRF
    #print(nRF_ser.read())
