from picamera import PiCamera
from time import sleep, time

class camera(object):
    def __init__(self):
        self.camera = PiCamera()
        self.camera.rotation = 0
        # location for saved images
        self.path = '/captured/'
    
    def capture(self):
        self.camera.start_preview()
        ts = time()
        name = '%s.jpg' % ts
        fullPathName = '%s/%s' % (self.path, name)
        self.camera.capture(fullPathName)
        self.camera.stop_preview()
        return fullPathName

