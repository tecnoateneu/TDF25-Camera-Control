import datetime
import cv2
import math
import numpy as np
import pickle   
import time
import os
from picamera2 import Picamera2
from libcamera import controls


DEBUG = True
LLEGEIX_CAMERA = True
FOCUS = 0.0

# Limits del camp de flors en píxels
DOWN_LEFT = (60, 2500)
DOWN_RIGHT = (4460, 2515)
UP_LEFT = (10, 160)
UP_RIGHT = (4470, 130)

# Mida real del camp de flors en mm
MIDA_CAMP_X = 2000
MIDA_CAMP_Y = 1065

ImatgeCounter = 0

################################################ Lectura i gravació d'imatges ################################################

# Funció per obrir un fitxer d'imatge i realitzar un global thresholding
# Input: image_path: path al fitxer d'imatge
# Output: imatge en escala de grisos
def ObreImatge(ruta_imatge):
    # Llegeix la imatge utilitzant OpenCV
    imatge = cv2.imread(ruta_imatge, cv2.IMREAD_GRAYSCALE)

    # Comprova si s'ha llegit correctament la imatge
    if imatge is None:
        LogError('ObreImatge: No s\'ha pogut obrir el fitxer' + ruta_imatge)
        return
    
    return imatge 

# Funció per activar la càmera
# Sortida: Objecte Picamera2
def ActivaCamera():
    if LLEGEIX_CAMERA:
        try:
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(main={'format': 'BGR888', 'size': (4608, 2592)})
            picam2.set_controls({"AfMode":controls.AfModeEnum.Manual, "LensPosition":FOCUS})
            picam2.configure(camera_config)
            picam2.start()            
        except IOError:
            LogError("ActivaCamera: No s'ha pogut obrir o accedir a la càmera.")
        except ValueError:
            LogError("ActivaCamera: S'han proporcionat paràmetres no vàlids a create_still_configuration o configure.")
        except RuntimeError:
            LogError("ActivaCamera: S'ha cridat a start quan la càmera ja està en ús o no està configurada correctament.")
        except Exception as e:
            LogError(f"ActivaCamera: S'ha produït un error inesperat: {str(e)}")
        time.sleep(2)
        while not (picam2.autofocus_cycle()):              # Espera a càmera enfocada
            print('Càmera desenfocada')
            time.sleep(0.1)
        return picam2
    else:
        return None

# Funció per desactivar la càmera
# Entrada: Objecte Picam2
# Sortida: cap
def DesactivaCamera(camera):
    # Comprova si la càmera està activada
    if camera is not None:
        try:
            camera.stop()
        except Exception as e:
            LogError(f"DesactivaCamera: S'ha produït un error inesperat: {str(e)}")
    
# Funció per llegir un fotograma de la càmera
# Entrada: Objecte Picam2
# Sortida: fotograma en bgr llegit de la càmera
def LlegeixFotoCamera(camera):
    global ImatgeCounter

    if LLEGEIX_CAMERA:
        output = camera.capture_array()                     # Captura la imatge 
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
    else:
        output = ObreImatge('src/Imatges/ImatgeCamera999.jpg')
    
    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeCamera'
            GuardaImatge(output, NomImatge)
            ImatgeCounter += 1
     
    return output

# Funció per desar una imatge en un fitxer amb una marca de temps
# Entrada: imatge: imatge a desar
#          nom_fitxer: nom del fitxer
def GuardaImatge(imatge, nom_fitxer):
    # Desa la imatge en un fitxer, afegint una marca de temps al nom del fitxer
    marca_temps = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    if  not cv2.imwrite('src/Imatges/' + marca_temps + nom_fitxer + '.jpg', imatge):
        LogError('GuardaImatge: No s\'ha pogut guardar la imatge' + nom_fitxer)
        return
    

################################################ Millora de l'imatge ################################################ 
# Funció per realitzar el threshold en una imatge
# Entrada: frame: imatge 
# Sortida: img_thresolded: imatge amb threshold
def ThresholdImatge(frame):
    global ImatgeCounter

    # Si la imatge no està en escala de grisos, la converteix
    if len(frame.shape) > 2:
        # Converteix la imatge a escala de grisos
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Realitza el thresholding
    
    _, img_thresholded = cv2.threshold(frame, 250, 255, cv2.THRESH_BINARY)

    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeThresolded'
            GuardaImatge(img_thresholded, NomImatge)
            ImatgeCounter += 1

    return img_thresholded 

################################################ Anàlisis inatge ################################################
# Classe que defineix el camp de les flors
class FlowerField:
    def __init__(self):
        self.left_up = UP_LEFT # Cantó superior esquerre del camp en píxels
        self.right_up = UP_RIGHT # Cantó superior dret del camp en píxels
        self.left_down = DOWN_LEFT # Cantó inferior esquerre del camp en píxels
        self.right_down = DOWN_RIGHT # Cantó inferior dret del camp en píxels
    
    # Funció que retorna la posició real d'una flor a partir de les seves coordenades de la càmera
    # Entrada: px: coordenada x de la càmera
    #          py: coordenada y de la càmera
    # Sortida: x: coordenada x real
    #          y: coordenada y real
    def PixelXY2ReallXY(self, px, py):
        # A la càmera, el camp de flors està limitat per 4 línies, línia esquerra, línia dreta, línia superior i línia inferior
        # Cada línia està definida pels seus punts (left_up, left_down, right_up, right_down)
        # Coneixem la mida real del camp, així que la posició real és proporcional a la distància a les línies
        # Obté una equació de línia des de left_up fins a right_up
        m_up = (self.right_up[1] - self.left_up[1])/(self.right_up[0] - self.left_up[0])
        n_up = self.left_up[1] - m_up*self.left_up[0]

        # Obté una equació de línia des de left_up fins a left_down
        m_left = (self.left_down[1] - self.left_up[1])/(self.left_down[0] - self.left_up[0])
        n_left = self.left_up[1] - m_left*self.left_up[0]

        # Obté una equació de línia des de right_up fins a right_down
        m_right = (self.right_down[1] - self.right_up[1])/(self.right_down[0] - self.right_up[0])
        n_right = self.right_up[1] - m_right*self.right_up[0]

        # Obté una equació de línia des de left_down fins a right_down
        m_down = (self.right_down[1] - self.left_down[1])/(self.right_down[0] - self.left_down[0])
        n_down = self.left_down[1] - m_down*self.left_down[0]

        # Distància des de la línia esquerra al punt
        d_left = px - ((py - n_left) / m_left)
        # Distància de la línia dreta al punt
        d_right = ((py - n_right) / m_right) - px
        # Escala al món real
        x = (d_left * MIDA_CAMP_X) / (d_left + d_right)

        # Distància de la línia superior al punt
        d_up = py - ((m_up * px) + n_up)
        # Distància de la línia inferior al punt
        d_down = ((m_down * px) + n_down) - py
        # Escala al món real
        y = (d_up * MIDA_CAMP_Y) / (d_up + d_down)

        return x, y

# Funció per trobar la posició d'una flor a la imatge
# S'espera trobar només una flor
# Entrada: imatge: imatge per analitzar
#          CampFlors: objecte FlowerField 
# Sortida: middle_point: coordenades de pantalla del punt mig entre els dos centres
#                       (0,0),0,0 si no es troba la flor
def TrobaPosicioFlor(imatge, CampFlors):
    global ImatgeCounter

    # Redueix els límits del camp per ajustar-nos al camp
    xmin = max(CampFlors.left_up[0], CampFlors.left_down[0])
    xmax = min(CampFlors.right_up[0], CampFlors.right_down[0])
    ymin = max(CampFlors.left_up[1], CampFlors.right_up[1])
    ymax = min(CampFlors.left_down[1], CampFlors.right_down[1])

    # Redueix la imatge
    imager = imatge[ymin:ymax, xmin:xmax]

    # Troba els contorns
    contorns, _ = cv2.findContours(imager, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

    # Filtra els contorns per àrea, mantenint només els grans
    contorns = [contorn for contorn in contorns if cv2.contourArea(contorn) > 100]

    # Troba els centres
    centres = []
    for contorn in contorns:
        M = cv2.moments(contorn)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centres.append((cx, cy))
    
    if DEBUG:
        # Dibuixa un cercle gris en cada centre
        for centre in centres:
            cv2.circle(imager, centre, 5, (128, 128, 128), -1)
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgePosicioFlor'
            GuardaImatge(imager, NomImatge)
            ImatgeCounter += 1

    # Si es troben més de 3 centres, imprimeix un missatge d'error
    if len(centres) > 3 or len(centres) < 3:
        LogError('TrobaPosicioFlor: No s\'han trobat 3 referències')
        # Desa la imatge 
        #GuardaImatge(imatge, 'Software/Lector-posicio/Data/ErrorReferences')
        return (0,0),0,0
    
    # Troba quins són els 2 centres més propers
    min_dist = 10000
    for i in range(2):
        for j in range(i+1, 3):
            dist = math.sqrt((centres[i][0]-centres[j][0])**2 + (centres[i][1]-centres[j][1])**2)
            if dist < min_dist:
                min_dist = dist
                centres_mes_propers = [i, j]

    # Troba el punt mig entre els dos centres mes propers
    punt_mig = ((centres[centres_mes_propers[0]][0]+centres[centres_mes_propers[1]][0])//2, (centres[centres_mes_propers[0]][1]+centres[centres_mes_propers[1]][1])//2)

    # Troba el punt mig entre punt_mig i el tercer centre
    centre_flor = ((punt_mig[0]+centres[3-centres_mes_propers[0]-centres_mes_propers[1]][0])//2, (punt_mig[1]+centres[3-centres_mes_propers[0]-centres_mes_propers[1]][1])//2)

    # Troba la distància entre punt_mig i el tercer centre
    distancia = math.sqrt((centres[3-centres_mes_propers[0]-centres_mes_propers[1]][0]-punt_mig[0])**2 + (centres[3-centres_mes_propers[0]-centres_mes_propers[1]][1]-punt_mig[1])**2)

    # Troba l'angle de la línia que uneix punt_mig i el tercer centre
    try:
        angle = math.atan((centres[3-centres_mes_propers[0]-centres_mes_propers[1]][0]-punt_mig[0])/(centres[3-centres_mes_propers[0]-centres_mes_propers[1]][1]-punt_mig[1]))
    except ZeroDivisionError:
        angle = 0
    
    if DEBUG:
        # Dibuixa un cercle gris al punt mig
        cv2.circle(imager, centre_flor, 5, (128, 128, 128), -1)
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgePosicioFlor'
            GuardaImatge(imager, NomImatge)
            ImatgeCounter += 1    
    
    # S'afegeix el que s'ha retallat al principi per limitar el camp
    centre_flor = (centre_flor[0] + xmin, centre_flor[1] + ymin)
    
    return centre_flor, distancia, angle

# Dibuixa un cercle al punt mig i una línia a la inclinació de la flor
# Entrada: imatge: imatge per dibuixar
#          x: coordenada x de pantalla del punt mig
#          y: coordenada y de pantalla del punt mig
#          angle: inclinació de la flor
# Sortida: imatge: imatge amb el cercle i la línia dibuixats
def DibuixaPosicioFlor(imatge, x, y, angle):
    global ImatgeCounter

    # Dibuixa un cercle al punt mig
    cv2.circle(imatge, (x, y), 100, (255, 255, 255), 2)

    # Dibuixa una línia a la inclinació de la flor
    x2 = int(x + 200 * math.sin(angle))
    y2 = int(y + 200 * math.cos(angle))
    cv2.line(imatge, (x, y), (x2, y2), (255, 255, 255), 2)
    
    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'FlorDibuixada'
            GuardaImatge(imatge, NomImatge)
            ImatgeCounter += 1 
    
    return imatge

# Per seguir la flor
# Llegeix la càmera, corregeix la imatge, la binaritza i troba la posició de la flor
# Mostra la imatge amb un cercle al punt mig i una línia a la inclinació de la flor
# També mostra les coordenades x, y i l'angle de la flor
# Si l'usuari prem 's' guarda les imatges original, corregida, binaritzada i de posició
# Si l'usuari prem 'esc' tanca la càmera
# Entrada: Camp: objecte FlowerField 
#          camera: objecte Picamera2 activada
# Sortida: cap
def SegueixFlor(CampFlors, camera):
    global ImatgeCounter
    
    while True:
        imatge = LlegeixFotoCamera(camera)
                
        imatget = ThresholdImatge(imatge)
        
        Posicio, Distancia, Angle = TrobaPosicioFlor(imatget, CampFlors)

        font = cv2.FONT_HERSHEY_SIMPLEX
        if (Posicio[0] == 0 and Posicio[1] == 0 and Distancia == 0 and Angle == 0):
            # No s'ha trobat la flor
            cv2.putText(imatget, 'No s\'ha trobat flor', (50, 60), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeNoFlorTrobada'
            GuardaImatge(imatget, NomImatge)
            LogError('Flor no trobada')
            if not DEBUG:
                cv2.imshow('Imatge sense flor', imatget)
        else:
            # Dibuixa la posició de la flor
            imager = DibuixaPosicioFlor(imatge, Posicio[0], Posicio[1], Angle)
            PosicioReal = CampFlors.PixelXY2ReallXY(Posicio[0], Posicio[1])
            cv2.putText(imager, 'X: ' + str(int(PosicioReal[0])), (50, 80), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(imager, 'Y: ' + str(int(PosicioReal[1])), (50, 160), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            # Angle en str amb només 2 decimals
            Ang = "{:.2f}".format((Angle*360)/6.28)
            cv2.putText(imager, 'Angle: ' + Ang, (50, 240), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            if DEBUG:
                if ImatgeCounter < 10:
                    # Guarda imatge llegida a disk
                    NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeAmbPosicio'
                    GuardaImatge(imager, NomImatge)
                    ImatgeCounter += 1 
            else:
                cv2.imshow('Imatge amb posicio', imager)
        
        # Si estem en DEBUG només fem una vegada el procés
        if DEBUG:
            break
            
        k = cv2.waitKey(5)
        if k == 27:
            break
    
    cv2.destroyAllWindows()  

################################################ Utilitats ################################################
# Funció que crea un log d'errors. Afegeix l'error passat al fitxer de log posant la data i hora
# Entrada: error: missatge d'error
def LogError(error):
    data = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('src/Data/LogErrors.txt', 'a') as f:
        f.write(data + ' ' + error + '\n')

################################################ Funció principal ################################################
def main():
    # Definim el directori de treball perque sigui el mateix tant si treballem des del VSC com VNC
    os.chdir('/home/pi/Documents/TDF25-Camera-Control')
    
    Camera = ActivaCamera()
    CampFlors = FlowerField()
    SegueixFlor(CampFlors, Camera)
    DesactivaCamera(Camera)
    #ComprovaPosicio(CampFlors)
     
   
if __name__ == "__main__":
    main()
