import RPi.GPIO as GPIO
import multiprocessing
import time
import os 
import subprocess
from led import Led

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
pin = [23, 24, 27, 22]
button = 0
led_pin = 26

the_led = Led(GPIO, led_pin)

# the_led.blink(10)
# the_led.on(10_000)

GPIO.setup(led_pin, GPIO.OUT)
for i in pin: 
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Wating ")
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


def handle_button():
    the_led.brightness = 1
    button = read_input()
    active_pin = pin[button]
    button += 1
    print("BUTTON", "PIN")
    print(button + 1, active_pin)
    if button == 1:
        p = multiprocessing.Process(target=the_led.blink, args=(10_000,))
        p.start()
        # os.system("bash ~/waltr/firmwareUpload/waltr_A_cmd.sh")
        result = subprocess.run(["bash", "./waltr_A_cmd.sh"], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        print(output)
        p.terminate()
        if "Hash of data verified." not in output:
            the_led.brightness = 3
            the_led.on(10)

    print("DONE")
    time.sleep(0.5)
    handle_button()
    return



handle_button()



