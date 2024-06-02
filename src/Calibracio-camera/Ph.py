import cv2
from picamera2 import Picamera2
from libcamera import controls
import time
help(controls)
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={'format': 'BGR888', 'size': (4608, 2592)})
picam2.configure(camera_config)
picam2.start()
picam2.controls = set_controls({"AfMode": controls.AfModeEnum.Manual,"LensPosition":0.55})
time.sleep(2)

num = 0
while True:
    output = picam2.capture_array()                     # Captura la imatge 
    
    # Espera que l'usuari premi una tecla
    cv2.imshow('Imatge', output)
    k = cv2.waitKey(1)
    if k == ord('s'): # Si l'usuari ha premut la tecla 's', guarda la imatge
        cv2.imwrite('Imatges/' + f'cali{num}.png', output)
        num += 1
    elif k == ord('p'):
        print(picam2.capture_metadata())
    elif k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
        break
cv2.destroyAllWindows()