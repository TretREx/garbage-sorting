import Jetson.GPIO as GPIO

class GPIOReader:
    def __init__(self, pins):
        self.pins = pins
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        self.setup_pins()

    def setup_pins(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN)

    def read_pin_states(self):
        states = {}
        for pin in self.pins:
            try:
                states[pin] = GPIO.input(pin)
            except Exception as e:
                states[pin] = None  # Could not read pin state
                print(f"Error reading pin {pin}: {e}")
        return states

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
    gpio_reader = GPIOReader([35, 36, 37, 38, 40])
    gpio_values = gpio_reader.read_pin_states()
    print(gpio_values)
    gpio_reader.cleanup()
