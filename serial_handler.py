#!/usr/bin/env python
import time
import serial


class DeviceSerial:
    def __init__(self, port: str="/dev/ttyUSB0", baudrate: int=115200):
        self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
        )
    
    def validate(self, val: str, line: int=100) -> bool:
        count = 0
        while True:
            x = self.serial.readline()
            data = x.decode("utf-8").replace("\n", "")
            count += 1
            print(count, data, val in data)
            if len(data) < 2:
                continue
            if val in data:
                break
            if count > line:
                return False
        return True



device = DeviceSerial()
print(device.validate("waltr_A"))
