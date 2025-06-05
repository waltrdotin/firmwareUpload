import time
from gpiozero import PWMLED, LED as GZ_LED # Import specific classes from gpiozero

class Led:
    """
    Controls an LED connected to a Raspberry Pi GPIO pin using gpiozero.
    Supports dimming, brightening, solid on/off, and blinking.
    """
    def __init__(self, pin: int):
        """
        Initializes the Led object.

        Args:
            pin (int): The GPIO pin number to which the LED is connected.
                       This should be a BCM pin number (e.g., 17, 27).
        """
        self.led = PWMLED(pin)
        self.brightness_mode = 0 # 0 for off, 1 for dim, 2 for bright, 3 for full on

    def ledDim(self):
        """
        Simulates a dimming effect by rapidly pulsing the LED with a low duty cycle.
        This uses PWMLED's value property for control.
        """
        self.led.value = 0.01 # 1% brightness
        time.sleep(0.2) # Keep it at this brightness for a short period

    def ledBright(self):
        """
        Simulates a brightening effect by rapidly pulsing the LED with a higher duty cycle.
        """
        self.led.value = 0.1 # 10% brightness
        time.sleep(0.2)

    def on(self, durationSeconds: float):
        """
        Turns the LED on for a specified duration, with different brightness modes.

        Args:
            durationSeconds (float): The duration in seconds to keep the LED on.
        """
        start_time = time.time()
        while (time.time() - start_time) < durationSeconds:
            if self.brightness_mode == 1:
                self.ledDim()
            elif self.brightness_mode == 2:
                self.ledBright()
            elif self.brightness_mode == 3:
                self.led.on()
                time.sleep(0.01)
            else:
                self.led.off()
                time.sleep(0.01)

        self.led.off()
        return

    def off(self):
        """
        Turns the LED completely off.
        """
        self.led.off()
        self.brightness_mode = 0

    def set_brightness_mode(self, mode: int):
        """
        Sets the brightness mode for the LED.

        Args:
            mode (int): 0 for off, 1 for dim, 2 for bright, 3 for full on.
        """
        if mode in [0, 1, 2, 3]:
            self.brightness_mode = mode
        else:
            print("Invalid brightness mode. Use 0 (off), 1 (dim), 2 (bright), or 3 (full on).")

    def blink(self, n: int, on_time: float = 0.2, off_time: float = 0.2):
        """
        Makes the LED blink n times.

        Args:
            n (int): The number of times to blink.
            on_time (float): The duration the LED stays on during each blink cycle.
            off_time (float): The duration the LED stays off during each blink cycle.
        """
        self.led.blink(on_time=on_time, off_time=off_time, n=n, background=False)
        self.led.off() # Ensure LED is off after blinking

if __name__ == '__main__':
    try:
        my_led = Led(pin=26)

        print("Testing dim mode...")
        my_led.set_brightness_mode(1)
        my_led.on(2) # Run dim mode for 2 seconds
        time.sleep(1)

        print("Testing bright mode...")
        my_led.set_brightness_mode(2)
        my_led.on(2) # Run bright mode for 2 seconds
        time.sleep(1)

        print("Testing full on mode...")
        my_led.set_brightness_mode(3)
        my_led.on(1) # Full on for 1 second
        time.sleep(1)

        print("Testing blink...")
        my_led.blink(5) # Blink 5 times
        time.sleep(1)

        print("Turning off LED.")
        my_led.off()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'my_led' in locals() and my_led.led.is_lit: # Check if led object exists and is lit
            my_led.led.off() # Ensure it's off before closing
        print("GPIO cleanup complete.")
