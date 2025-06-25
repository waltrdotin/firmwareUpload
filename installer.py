#!/usr/bin/env python

from gpiozero import Button
import time
import subprocess
from led import Led
from firmware import LocalStorage, get_bin_files, get_current_path
from pathlib import Path


INSTALL_DIR = Path(__file__).resolve().parent
VENV_CONFIG_FILE = INSTALL_DIR / ".venv_path"

VENV_PYTHON = ""

try:
    if VENV_CONFIG_FILE.exists():
        VENV_PYTHON = VENV_CONFIG_FILE.read_text().strip()
        if not Path(VENV_PYTHON).exists():
            print(
                f"WARNING: Configured VENV_PYTHON path '{VENV_PYTHON}' does not exist. Using 'python3'."
            )
            VENV_PYTHON = "python3"
    else:
        print(
            f"WARNING: VENV config file '{VENV_CONFIG_FILE}' not found. Using 'python3'."
        )
        VENV_PYTHON = "python3"
except Exception as e:
    print(f"ERROR: Could not read VENV config file: {e}. Using 'python3'.")
    VENV_PYTHON = "python3"

BUTTON_PINS = [23, 24, 27, 22]

buttons = []


def read_input() -> int:
    """
    Waits for a button press and returns the index of the pressed button.
    Uses gpiozero.Button objects.
    """
    btn_down_index = -1
    while True:
        for i, button_obj in enumerate(
            buttons
        ):  # Iterate through gpiozero Button objects
            if button_obj.is_pressed:
                btn_down_index = i
                break
        if btn_down_index != -1:
            break
        time.sleep(0.1)  # Shorter sleep for quicker response
    return btn_down_index


def install_bin_file(file_path: str, the_led: Led, is_idf: bool) -> str:
    the_led.set_brightness_mode(1)
    based_path = get_current_path()
    the_led.blink(n=None, on_time=0.1, off_time=0.1, background=True)
    output = ""
    boot_loader = "WALTR.bootloader.bin"
    partitions = "WALTR.partitions.bin"
    if is_idf:
        boot_loader = "WALTR.idf.bootloader.bin"
        partitions = "WALTR.idf.partitions.bin"
    command = [
        VENV_PYTHON,
        "-m",
        "esptool",
        "-p",
        "/dev/ttyUSB0",
        "-b",
        "921600",
        "--before",
        "default_reset",
        "--after",
        "hard_reset",
        "--chip",
        "esp32",
        "write_flash",
        "--flash_mode",
        "dio",
        "--flash_size",
        "detect",
        "--flash_freq",
        "40m",
        "0x1000",
        based_path + f"/config/{boot_loader}",
        "0x8000",
        based_path + f"/config/{partitions}",
        "0x10000",
        file_path,
    ]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        output = result.stdout
        print(output)
        print("Command executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(f"Stderr: {e.stderr}")
        # Capture both stdout and stderr for error
        output = e.stdout + e.stderr
    finally:
        the_led.off()
    if "Hash of data verified." not in output:
        the_led.set_brightness_mode(3)
        the_led.on(10)
    return output


def handle_button(storage: LocalStorage, the_led: Led):
    """
    Handles button presses to trigger firmware installation based on selected device.

    Args:
        storage (LocalStorage): An instance of LocalStorage to get firmware versions.
        the_led (Led): An instance of the Led class for visual feedback.
    """
    the_led.off()
    try:
        get_bin_files(storage)
    except Exception as e:
        print(f"Error getting bin files: {e}")
    button_index = read_input()
    button_number = button_index + 1
    print(f"BUTTON: {button_number}, PIN: {BUTTON_PINS[button_index]}")
    device_version = dict()
    device_version = storage.get_version(f"button_{button_number}")
    if device_version:
        print(
            f"Installing firmware for: {device_version.get('name', 'Unknown Device')}"
        )
        install_bin_file(device_version["path"], the_led, device_version["is_idf"])
    else:
        print(f"No firmware version found for button {button_number}.")
        the_led.set_brightness_mode(3)
        the_led.blink(2, 0.2, 0.2)
    print("DONE with current operation.")
    time.sleep(0.5)
    handle_button(storage, the_led)
    return


def main():
    storage = LocalStorage()
    print("Versions and button available: ")
    for k, v in storage.get_all().items():
        print(k, v)
    global buttons
    for p in BUTTON_PINS:
        buttons.append(Button(p, pull_up=False))
    led_pin = 26
    the_led = Led(led_pin)
    the_led.set_brightness_mode(2)  # Set mode to bright
    the_led.blink(3)
    handle_button(storage, the_led)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
    except Exception as e:
        print(f"An unexpected error occurred in main: {e}")
    finally:
        # In gpiozero, individual component objects (like Button and LED)
        # automatically clean up when the script exits or they go out of scope.
        # However, it's good practice to ensure LEDs are off.
        # If Led class has a `close` or `cleanup` method for its internal PWMLED, call it.
        # Assuming the_led is accessible if main() was called
        # if 'the_led' in locals():
        #     the_led.off()
        pass  # gpiozero handles cleanup mostly automatically
