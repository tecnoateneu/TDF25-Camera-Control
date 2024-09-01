# Programa per fer un test de la càmera.
# S'ha d'excutar des de la Raspberry Pi amb la càmera connectada.
# Ensenya la imatge de la càmera i es pot canviar el focus de la càmera

import cv2
import datetime

# Limits del camp de flors
DOWN_LEFT = (60, 2500)
DOWN_RIGHT = (4460, 2515)
UP_LEFT = (10, 160)
UP_RIGHT = (4470, 130)

#CAMERA = 'DAHUA_1_RUBEN'
#CAMERA = 'TPTEK'
CAMERA = 'WEBCAM'
TEST_VELOCITAT = True
TEST_IMATGE = False
TEST_CAMP = False

# Obrir càmera
if CAMERA == 'DAHUA_1_RUBEN':
    cap = cv2.VideoCapture('rtsp://admin:Holaquetal@192.168.1.160:554/cam/realmonitor?channel=1&subtype=0')
if CAMERA == 'TPTEK':
    cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.173:554/11')
if CAMERA == 'WEBCAM':
    cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("ActivaCamera: No s/'ha pogut obrir la càmera.")
    exit()

ret, frame = cap.read()

if TEST_VELOCITAT:
    #print HH:MM:SS:MS
    ret, frame = cap.read()
    cv2.imshow('Imatge', frame)
    while True:
        k = cv2.waitKey(1)
        if k == 27:
            break
        if k == ord('s'):
            now = datetime.datetime.now()
            formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
            print(f"Anem a llegir: {formatted_time}")
            ret, frame = cap.read()
            now = datetime.datetime.now()
            formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
            print(f"Imatge llegida: {formatted_time}")
            
            if not ret:
                print("LecturaCamera: No s'ha pogut capturar imatge.")
                
            output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

            now = datetime.datetime.now()
            formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
            font = cv2.FONT_HERSHEY_SIMPLEX
            formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
            cv2.putText(output, formatted_time, (10, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            print(f"Imatge passada a grisos: {formatted_time}")
            
            cv2.imshow('Imatge', output)
            # Guardar la imatge
            if not cv2.imwrite('src/Data/ImatgeCamera.png', output):
                print('Error al gravar la imatge.')
            else:
                print('Imatge gravada')

            

if TEST_IMATGE:
    # Llegir la imatge fins que es premi la tecla 'esc'
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("LecturaCamera: No s'ha pogut capturar imatge.")
            
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
        # Imprimeix l'hora en la foto
        now = datetime.datetime.now()
        font = cv2.FONT_HERSHEY_SIMPLEX
        formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
        cv2.putText(output, formatted_time, (10, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('Imatge', output)
        
        # Espera que l'usuari premi una tecla
        k = cv2.waitKey(1)
        if k == 27:
            break

if TEST_CAMP:
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