from pprint import *
from picamera2 import Picamera2, Preview
from libcamera import controls
from PIL import Image
import time
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={'size': (4608, 2592)})
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
while not (picam2.autofocus_cycle()):
    print('cicle')
    time.sleep(0.1)
picam2.capture_file("test.jpg")
picam2.stop()
