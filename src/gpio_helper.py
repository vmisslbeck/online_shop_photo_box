try:
    import RPi.GPIO as GPIO
except ImportError:
    # Fallback für Debug auf PC
    class GPIO:
        BCM = BOARD = IN = PUD_UP = FALLING = None
        def setmode(*a, **kw): pass
        def setup(*a, **kw): pass
        def add_event_detect(*a, **kw): pass
        def cleanup(): pass

class GPIOHandler:
    def __init__(self, callback=None):
        self.callback = callback

        # Beispiel: Button an GPIO17
        GPIO.setmode(GPIO.BCM)
        self.button_pin = 17
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.button_pin, GPIO.FALLING,
                              callback=self.callback, bouncetime=200)

    def cleanup(self):
        GPIO.cleanup()
