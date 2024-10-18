#!/usr/bin/env python

import RPi.GPIO as GPIO
import multiprocessing
import time
import subprocess
import os
from led import Led
from firmware import LocalStorage, get_bin_files, get_current_path

pin = [23, 24, 27, 22]

def read_input() -> int:
    btn_down = -1
    while True:
        for i, p in enumerate(pin):
            state = GPIO.input(p)
            if state == GPIO.HIGH:
                btn_down = i
                break
        if btn_down != -1:
            break
        time.sleep(0.5)
    return btn_down

def install_bin_file(file_path: str, the_led: Led) -> str:
    the_led.brightness = 1
    based_path = get_current_path()
    p = multiprocessing.Process(target=the_led.blink, args=(10_000,))
    p.start()
    output = ""
    command = [
        "python3", "-m", "esptool", 
        "-p", "/dev/ttyUSB0", 
        "-b", "460800", 
        "--before", "default_reset", 
        "--after", "hard_reset", 
        "--chip", "esp32", 
        "write_flash", 
        "--flash_mode", "dio", 
        "--flash_size", "detect", 
        "--flash_freq", "40m", 
        "0x1000",  based_path + "/config/WALTR.bootloader.bin", 
        "0x8000", based_path + "/config/WALTR.partitions.bin", 
        "0x10000", file_path
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        output = result.stdout
        print("Command executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
    p.terminate()
    if "Hash of data verified." not in output:
        the_led.brightness = 3
        the_led.on(10)
    return output


def handle_button(storage: LocalStorage, the_led: Led):
    button = 0
    the_led.off()
    try:
        get_bin_files(storage)
    except:
        pass
    button = read_input()
    active_pin = pin[button]
    button += 1
    print("BUTTON", "PIN")
    print(button, active_pin)
    device_version = dict()
    if button == 1:
        device_version = storage.get_version("waltr_A")
    if button == 2:
        device_version = storage.get_version("waltr_B")
    if button == 3:
        device_version = storage.get_version("waltr_C")
    if button == 4:
        device_version = storage.get_version("waltr_V")
    if device_version != dict():
        install_bin_file(device_version['path'], the_led)
    print("DONE")
    time.sleep(0.5)
    handle_button(storage, the_led)
    return


def main():
    storage = LocalStorage()
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    led_pin = 26
    the_led = Led(GPIO, led_pin)
    GPIO.setup(led_pin, GPIO.OUT)
    for i in pin: 
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    the_led.brightness = 2
    the_led.blink(3)
    handle_button(storage, the_led)


if __name__=="__main__":
    main()



