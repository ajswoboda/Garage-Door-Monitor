import argparse
import doorEmail
import RPi.GPIO as gpio
import open as dOpen
import time

def monitor(s):
    current = gpio.input(s)
    while not current:
        gpio.setmode(gpio.BCM)
        gpio.setup(s, gpio.IN)
        current = gpio.input(s)
        if not current and doorEmail.checkEmails():
            dOpen.main()
        print(current)
        if not current:
            time.sleep(300)


def main():
    opts = parseOptions()
    if opts.switch:
        s = opts.switch
        gpio.setmode(gpio.BCM)
        gpio.setup(s, gpio.IN)
        monitor(s)

def parseOptions():
    parser = argparse.ArgumentParser(description='Pass the switch to monitor.')
    parser.add_argument('-s', '--switch', type=int, dest='switch', help='Switch to Monitor')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
