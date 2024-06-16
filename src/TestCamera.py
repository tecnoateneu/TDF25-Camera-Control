# Programa per fer un test de la càmera.
# S'ha d'excutar des de la Raspberry Pi amb la càmera connectada.
# Ensenya la imatge de la càmera

import cv2
from picamera2 import Picamera2
from libcamera import controls
import time  

picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={'format': 'BGR888', 'size': (4608, 2592)})
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)

num = 0
while True:
    while not (picam2.autofocus_cycle()):
        print('Càmera desenfocada')
        time.sleep(0.1)
    output = picam2.capture_array()                     # Captura la imatge 
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

    # Espera que l'usuari premi una tecla
    cv2.imshow('Imatge', output)
    k = cv2.waitKey(1)
    if k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
        break
cv2.destroyAllWindows()