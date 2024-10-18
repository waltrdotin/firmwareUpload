import time

class Led:
    def __init__(self, GPIO, pin: int):
        self.io = GPIO
        self.pin = pin
        self.io.setup(self.pin, self.io.OUT)
        self.brightness = 1

    def ledDim(self):
        for _ in range(20):
            self.io.output(self.pin, self.io.HIGH)
            time.sleep(.0001)
            self.io.output(self.pin, self.io.LOW)
            time.sleep(.0099)

    def ledBright(self):
        for _ in range(20):
            self.io.output(self.pin, self.io.HIGH)
            time.sleep(.001)
            self.io.output(self.pin, self.io.LOW)
            time.sleep(.009)

    def on(self,  durationSeconds: float):
        time_count: float = 0
        while True:
            if self.brightness <= 1:
                self.ledDim()
            elif self.brightness == 2:
                self.ledBright()
            else:
                self.io.output(self.pin, self.io.HIGH)
                time.sleep(.2)
            time_count += 0.2
            if time_count >= durationSeconds: 
                break
        self.io.output(self.pin, self.io.LOW)

    def blink(self, n: int):
        for _ in range(n):
            self.on(0.2)
            time.sleep(.2)
        self.io.output(self.pin, self.io.LOW)





