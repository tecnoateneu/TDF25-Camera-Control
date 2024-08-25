# Programa per fer un test de la càmera.
# S'ha d'excutar des de la Raspberry Pi amb la càmera connectada.
# Ensenya la imatge de la càmera i es pot canviar el focus de la càmera

import cv2
import time  

# Limits del camp de flors
DOWN_LEFT = (60, 2500)
DOWN_RIGHT = (4460, 2515)
UP_LEFT = (10, 160)
UP_RIGHT = (4470, 130)

CAMERA = 'DAHUA_1_RUBEN'
TEST_VELOCITAT = True

# Obrir càmera
if CAMERA == 'DAHUA_1_RUBEN':
    cap = cv2.VideoCapture('rtsp://admin:Holaquetal@192.168.1.160:554/cam/realmonitor?channel=1&subtype=0')

# Check if the camera opened successfully
if not cap.isOpened():
    print("ActivaCamera: No s/'ha pogut obrir la càmera.")
    exit()

ret, frame = cap.read()

if TEST_VELOCITAT:
    #print HH:MM:SS:MS
    current_time_ms = int(time.time() * 1000)
    print(f"Anem a llegir: {current_time_ms} ms")
    ret, frame = cap.read()
    current_time_ms = int(time.time() * 1000)
    print(f"Imatge llegida: {current_time_ms} ms")
    
    if not ret:
        print("LecturaCamera: No s'ha pogut capturar imatge.")
        
    output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

    print(f"Imatge passada a grisos: {current_time_ms} ms")
    
    cv2.imshow('Imatge', output)

    while True:
        k = cv2.waitKey(1)
        if k == 27:
            break

else:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("LecturaCamera: No s'ha pogut capturar imatge.")
            
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

        #Dibuixa el camp
        # cv2.line(output, DOWN_LEFT, DOWN_RIGHT, (255, 255, 255), 4)
        # cv2.line(output, DOWN_LEFT, UP_LEFT, (255, 255, 255), 4)
        # cv2.line(output, UP_LEFT, UP_RIGHT, (255, 255, 255), 4)
        # cv2.line(output, UP_RIGHT, DOWN_RIGHT, (255, 255, 255), 4)

        cv2.imshow('Imatge', output)
        
        # Espera que l'usuari premi una tecla
        k = cv2.waitKey(1)
        if k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
            break
        elif k == ord('s'):
                if not cv2.imwrite('src/Data/ImatgeCamera.png', output):
                    print('Error al gravar la imatge.')
                else:
                    print('Imatge gravada')

cv2.destroyAllWindows()
cap.release()