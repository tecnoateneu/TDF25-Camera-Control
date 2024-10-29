# Programa per fer un test de la càmera.
# S'ha d'excutar des de la Raspberry Pi amb la càmera connectada.
# Ensenya la imatge de la càmera i es pot canviar el focus de la càmera

import cv2
import datetime
import queue
import threading

# Limits del camp de flors
DOWN_LEFT = (60, 2500)
DOWN_RIGHT = (4460, 2515)
UP_LEFT = (10, 160)
UP_RIGHT = (4470, 130)

#CAMERA = 'DAHUA_1_RUBEN'
#CAMERA = 'TPTEK'
CAMERA = 'WEBCAM'
#CAMERA = 'REOLINK_RUBEN'
TEST_VELOCITAT = True
TEST_IMATGE = False
TEST_CAMP = False

# Obrir càmera
if CAMERA == 'DAHUA_1_RUBEN':
    cap = cv2.VideoCapture('rtsp://admin:Holaquetal@192.168.1.125:554/cam/realmonitor?channel=1&subtype=0')
if CAMERA == 'TPTEK':
    cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.173:554/11')
if CAMERA == 'WEBCAM':
    cap = cv2.VideoCapture(0)
if CAMERA == 'REOLINK_RUBEN':
    cap = cv2.VideoCapture('rtsp://admin:adminTAV@192.168.1.110:554')

# Set internal buffer to 1
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Check if the camera opened successfully
if not cap.isOpened():
    print("ActivaCamera: No s/'ha pogut obrir la càmera.")
    exit()

ret, frame = cap.read()
           
if TEST_VELOCITAT:
    # Quan s'apreta la tecla 's' es captura una imatge i es guarda
    # Agafem 5 imatges i les ensenyem per escalfar la càmera
    for i in range(5):
        ret, frame = cap.read()
        cv2.imshow('Imatge', frame)
    
    while True:
        k = cv2.waitKey(1)
        if k == 27:
            break
        if k == ord('s'):
            Hora_inici = datetime.datetime.now()
            ret, frame = cap.read()
            Hora_Lectura = datetime.datetime.now()
            
            if not ret:
                print("LecturaCamera: No s'ha pogut capturar imatge.")
                
            output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos

            Hora_Grisos = datetime.datetime.now()
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            formatted_time = "Hora inici: " + Hora_inici.strftime("%H:%M:%S:%f")[:-3]
            cv2.putText(output, formatted_time, (10, 200), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            formatted_time = "Hora lectura: " + Hora_Lectura.strftime("%H:%M:%S:%f")[:-3]
            cv2.putText(output, formatted_time, (10, 230), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
            formatted_time = "Hora grisos: " + Hora_Grisos.strftime("%H:%M:%S:%f")[:-3]
            cv2.putText(output, formatted_time, (10, 260), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Imatge', output)
            # Guardar la imatge
            if not cv2.imwrite('src/Data/ImatgeCamera.png', output):
                print('Error al gravar la imatge.')
            else:
                print('Imatge gravada')

            

if TEST_IMATGE:
    # Llegir la imatge i visualitzar-la fins que es premi la tecla 'esc'
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("LecturaCamera: No s'ha pogut capturar imatge.")
            
        output = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
        # Imprimeix l'hora en la foto
        now = datetime.datetime.now()
        font = cv2.FONT_HERSHEY_SIMPLEX
        formatted_time = now.strftime("%H:%M:%S:%f")[:-3]
        cv2.putText(output, formatted_time, (10, 200), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
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