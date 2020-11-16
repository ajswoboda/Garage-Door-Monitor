import RPi.GPIO as gpio
from time import sleep

gpio.setmode(gpio.BCM)

class relay(object):
    def __init__(self, id):
        self.id = id
        gpio.setup(self.id, gpio.OUT)
    
    def output(self, high=False):
        if high:
            output = 1
        else:
            output = 0

        gpio.output(self.id, output)
        sleep(0.5)
    
    def cleanup(self):
        gpio.cleanup()


