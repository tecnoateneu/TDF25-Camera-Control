# Programa per fer un test de la càmera.
# S'ha d'excutar des de la Raspberry Pi amb la càmera connectada.
# Ensenya la imatge de la càmera i es pot canviar el focus de la càmera

import cv2
from picamera2 import Picamera2
from libcamera import controls
import time  

# Limits del camp de flors
DOWN_LEFT = (100, 2500)
DOWN_RIGHT = (4500, 2500)
UP_LEFT = (100, 100)
UP_RIGHT = (4500, 100)

picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={'format': 'BGR888', 'size': (4608, 2592)})
#picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})         # Autofocus
picam2.set_controls({"AfMode":controls.AfModeEnum.Manual,"LensPosition":0.0})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)

focus = float(0)

while True:
#   while not (picam2.autofocus_cycle()):              # Espera a càmera enfocada quan autofocus
#        print('Càmera desenfocada')
#        time.sleep(0.1)
    output = picam2.capture_array()                     # Captura la imatge 
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

    #Visualitza valor de focus
    cv2.putText(output, 'Focus: ' + str(focus), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 0), 2, cv2.LINE_AA)

    #Dibuixa el camp
    cv2.line(output, DOWN_LEFT, DOWN_RIGHT, (255, 255, 255), 4)
    cv2.line(output, DOWN_LEFT, UP_LEFT, (255, 255, 255), 4)
    cv2.line(output, UP_LEFT, UP_RIGHT, (255, 255, 255), 4)
    cv2.line(output, UP_RIGHT, DOWN_RIGHT, (255, 255, 255), 4)

    cv2.imshow('Imatge', output)
    picam2.set_controls({"AfMode":controls.AfModeEnum.Manual,"LensPosition":focus})

    # Espera que l'usuari premi una tecla
    k = cv2.waitKey(1)
    if k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
        break
    elif k == ord('q'):
        focus = focus + 0.1
        cv2.imshow('Imatge', 0)
    elif k == ord('a'):
        focus = focus - 0.1
    elif k == ord('w'):
        focus = focus + 0.01
    elif k == ord('s'):
        focus = focus - 0.01
    # Arrodoneix a 2 decimals
    focus = round(focus, 2)

cv2.destroyAllWindows()