import sys
import RPi.GPIO as gpio
from time import sleep
from camera import camera
from doorEmail import email, EmailError
import os

class switch(object):
    def __init__(self, gpioDict):
        #check interval
        self.filePath = ''
        self.checkInt = 3
        #warning everything 30 minutes
        minutes = 120
        self.warning = minutes * 60
        #set initial time
        self.time = 0
        self.cam = camera()
        #set position to closed
        self.shut = True
        try:
            self.email = email()
        except EmailError:
            sys.exit()
        self.messages = self.__message()
        self.gpioDict = gpioDict
        self.stateDict = dict()
        self.initializedGpio()

    def initializedGpio(self):
        gpio.setmode(gpio.BCM)
        gpios = self.gpioDict.keys()
        for g in gpios:
            gpioInt = self.gpioDict[g]
            gpio.setup(self.gpioDict[g], gpio.IN)
            self.stateDict[g] = gpio.input(gpioInt)
    
    def __message(self):
        messages = dict()
        
        subject = 'Garage door just closed'
        message = 'Hello,\nThe garage door just shut.'
        messages['closed'] = dict()
        messages['closed']['subject'] = subject
        messages['closed']['message'] = message

        subject = 'Garage door just opened!'
        message = 'Hello,\nThe garage door just opened.'
        messages['opened'] = dict()
        messages['opened']['subject'] = subject
        messages['opened']['message'] = message

        subject = 'Garage door remains open!'
        message = 'Hello,\nThe garage door remains in an open state.'
        messages['remains'] = dict()
        messages['remains']['subject'] = subject
        messages['remains']['message'] = message
        return messages
    
    def monitor(self):
        try:
            while True and 'open' in self.gpioDict:
                open = self.gpioDict['open']
                self.__checkStatus(open)
        except KeyError:
            pass
        finally:
            gpio.cleanup()

    def __getCurrentStatus(self, id):
        return gpio.input(id)
    
    def __checkStatus(self, id):
        curStat = self.__getCurrentStatus(id)
        self.__checkIfClosed(curStat)
        self.__checkIfOpened(curStat)
        self.__sendWarning(curStat)
        self.time += self.checkInt
        sleep(self.checkInt)
        return False
    
    def __sendEmail(self, state):
        self.__sendEmailAttributes(state)
        self.email.sendMessage(self.filePath)
        self.__clearEmailAttributes(state)
        self.filePath = ''

    def __sendEmailAttributes(self, state):
        self.email.subject = self.messages[state]['subject']
        self.email.message = self.messages[state]['message']
    
    def __clearEmailAttributes(self, state):
        self.email.subject = ''
        self.email.message = ''

    def __checkIfClosed(self,  status):
        if status and not self.shut:
            self.__sendEmail('closed')
            self.shut = True
            self.time = 0
    
    def __checkIfOpened(self,  status):
        if not status and self.shut:
            #probably not the way it should be, but for testing I will do this. 
            os.system("python /door/monitor/shut.py -s 17&")
            sleep(10)
            self.filePath = self.cam.capture()
            self.__sendEmail('opened')
            os.system('rm -f %s' % self.filePath)
            self.shut = False
            self.time = 0
    
    def __sendWarning(self,  status):
        if self.time >= self.warning and not self.shut:
            self.filePath = self.cam.capture()
            self.__sendEmail('remains')
            os.system('rm -f %s' % self.filePath)
            self.time = 0

