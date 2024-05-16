import datetime
import cv2
import math
import numpy as np
import pickle   
import time
import os
from picamera2 import Picamera2, Preview


DEBUG = True
LLEGEIX_CAMERA = True
CAMERA_USED = 'TPTEK' # Used camera. Possible values: 'TPTEK'
REDUCCIO_REFERENCIES = 10 # Pixels to reduce the field limits for avoiding the external references

MIDA_CAMP_X = 2360
MIDA_CAMP_Y = 1310

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
        print('ObreImatge: No s\'ha pogut obrir el fitxer', ruta_imatge)
        return
    
    return imatge 

# Funció per activar la càmera
# Sortida: Objecte Picamera2
def ActivaCamera():
    if LLEGEIX_CAMERA:
        try:
            picam2 = Picamera2()
            camera_config = picam2.create_still_configuration(main={"size": (4608, 2592)}, lores={"size": (640, 480)}, display="lores")
            picam2.configure(camera_config)
            picam2.start()
        except IOError:
            print("ActivaCamera: No s'ha pogut obrir o accedir a la càmera.")
        except ValueError:
            print("ActivaCamera: S'han proporcionat paràmetres no vàlids a create_still_configuration o configure.")
        except RuntimeError:
            print("ActivaCamera: S'ha cridat a start quan la càmera ja està en ús o no està configurada correctament.")
        except Exception as e:
            print(f"ActivaCamera: S'ha produït un error inesperat: {str(e)}")
        time.sleep(2)

        return picam2
    else:
        return None
    
# Funció per llegir un fotograma de la càmera
# Entrada: Objecte Picam2
# Sortida: fotograma en rgb llegit de la càmera
def LlegeixFotoCamera(camera):
    global ImatgeCounter

    if LLEGEIX_CAMERA:
        output = camera.capture_array()                     # Captura la imatge 
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
    else:
        output = ObreImatge('Imatges/ImatgeCamera999.jpg')
    
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
    marca_temps = datetime.datetime.now().strftime('_%Y%m%d_%H%M')
    if  not cv2.imwrite('Imatges/' + marca_temps + nom_fitxer + '.jpg', imatge):
        print('No s\'ha pogut guardar la imatge', nom_fitxer)
        return
    

################################################ Millora de l'imatge ################################################ 
# Funció per realitzar el threshold en una imatge
# Entrada: frame: imatge 
# Sortida: img_thresolded: imatge amb threshold
def ThresholdImatge(frame):
    # Si la imatge no està en escala de grisos, la converteix
    if len(frame.shape) > 2:
        # Converteix la imatge a escala de grisos
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Realitza el thresholding
    
    _, thresholded = cv2.threshold(frame, 250, 255, cv2.THRESH_BINARY)

    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeThresolded'
            GuardaImatge(output, NomImatge)
            ImatgeCounter += 1

    return img_thresholded 

# Funció per corregir la distorsió d'una imatge
# Entrada: imatge: imatge per corregir
#          cameraMatrix: matriu de la càmera
#          dist: coeficients de distorsió
#          newCameraMatrix: nova matriu de la càmera
#          roi: regió d'interès
#          w: amplada de la imatge
#          h: alçada de la imatge
# Sortida: dst: imatge sense distorsió i retallada
def CorregeixImatge(imatge, cameraMatrix, dist):
    h,  w = imatge.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
    
    # Desdistorsiona la imatge
    dst = cv2.undistort(imatge, cameraMatrix, dist, None, newCameraMatrix)
    
    # Desdistorsiona amb Remapping
    #mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    #dst = cv2.remap(imatge, mapx, mapy, cv2.INTER_LINEAR)
    
    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeNoDistorsio'
            GuardaImatge(output, NomImatge)
            ImatgeCounter += 1

    # retalla la imatge
    x, y, w, h = roi

    if CAMERA_USED == 'TPTEK':
        dst = dst[y + 20:y+h, x:x+w] # Eliminem completament el text de la càmera
    else:
        dst = dst[y:y+h, x:x+w]

    if DEBUG:
        if ImatgeCounter < 10:
            # Guarda imatge llegida a disk
            NomImatge = str(ImatgeCounter).zfill(3) + 'ImatgeNoRetallada'
            GuardaImatge(output, NomImatge)
            ImatgeCounter += 1

    return dst

################################################ Anàlisis inatge ################################################
# Classe que defineix el camp de les flors
class FlowerField:
    def __init__(self):
        self.left_up = (0,0) # Cantó superior esquerre del camp en píxels
        self.right_up = (0,0) # Cantó superior dret del camp en píxels
        self.left_down = (0,0) # Cantó inferior esquerre del camp en píxels
        self.right_down = (0,0) # Cantó inferior dret del camp en píxels
        self.image_size = (0,0) # Mida de la pantalla en píxels

    # Troba els límits del camp. El camp està limitat per 4 referències blanques
    # Entrada: imatge: ruta de la imatge sense distorsió
    #          imatge_umbralitzada: imatge umbralitzada
    def ObteCamp(self):
        # Carrega les dades de calibració de la càmera
        cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
        dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

        cap = ActivaCamera()  
        
        imatge = LlegeixFotoCamera(cap)   
        imatge_corregida = CorregeixImatge(imatge, cameraMatrix, dist)
        imatge_umbralitzada = ThresholdImatge(imatge_corregida)
        # Troba els contorns
        contorns, _ = cv2.findContours(imatge_umbralitzada, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) 
    
        if DEBUG:
            print('Nombre de contorns trobats:', len(contorns))
            # Imprimeix la mida de cada contorn
            contorns_trobats = list(contorns)
            # Ordena per mida
            contorns_trobats.sort(key=cv2.contourArea, reverse=True)
            print('Àrea dels contorns trobats:')
            for contorn in contorns_trobats:
                # Imprimeix la mida del contorn si és més gran que 0
                if cv2.contourArea(contorn) > 0:
                    print(cv2.contourArea(contorn))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Filtra els contorns per àrea, mantenint només els grans
        contorns = [contorn for contorn in contorns if cv2.contourArea(contorn) > 90]

        # Troba els 4 contorns que delimiten el camp
        # Troba els centres
        centres = []
        for contorn in contorns:
            M = cv2.moments(contorn)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                centres.append((cx, cy))
                cv2.circle(imatge, (cx, cy), 5, (128, 128, 128), -1)

        # Troba el centre superior esquerre 
        distancia_a_0 = [math.sqrt(x**2 + y**2) for (x, y) in centres]
        self.left_up = centres[distancia_a_0.index(min(distancia_a_0))]

        # Troba el centre superior dret
        distancia_a_x = [math.sqrt((imatge.shape[1]-x)**2 + y**2) for (x, y) in centres]
        self.right_up = centres[distancia_a_x.index(min(distancia_a_x))]

        # Troba el centre inferior esquerre
        distancia_a_y = [math.sqrt(x**2 + (imatge.shape[0]-y)**2) for (x, y) in centres]
        self.left_down = centres[distancia_a_y.index(min(distancia_a_y))]

        # Troba el centre inferior dret
        distancia_a_xy = [math.sqrt((imatge.shape[1]-x)**2 + (imatge.shape[0]-y)**2) for (x, y) in centres]
        self.right_down = centres[distancia_a_xy.index(min(distancia_a_xy))]
  
        if DEBUG:
            # Dibuixa un cercle gris en el centre de cada referència
            cv2.circle(imatge_corregida, (self.left_down), 5, (128, 128, 128), -1)
            cv2.circle(imatge_corregida, (self.right_up), 5, (128, 128, 128), -1)
            cv2.circle(imatge_corregida, (self.left_up), 5, (128, 128, 128), -1)
            cv2.circle(imatge_corregida, (self.right_down), 5, (128, 128, 128), -1)
            cv2.imshow('Imatge amb Límits del camp', imatge_corregida)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Actualitza la mida de la imatge
        self.image_size = imatge_corregida.shape
        
        return
    
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

# Funció per ajudar a ajustar els límits del camp. S'ha d'executar amb DEBUG = True i mostra contínuament la imatge del camp
# Entrada: CampFlors: objecte FlowerField
# Sortida: cap
def AjustaLimitsCamp(CampFlors):

    if not DEBUG:
        print('AjustaLimitsCamp: Només té sentit executar aquesta funció amb DEBUG = True')
        return
       
    while True:
        CampFlors.ObteCamp()
        k = cv2.waitKey(0)
        if k == 27:
            break  

# Funció per trobar la posició d'una flor a la imatge
# S'espera trobar només una flor
# Entrada: imatge: imatge per analitzar
#          CampFlors: objecte FlowerField ja calibrat (ObteCamp executat)
# Sortida: middle_point: coordenades de pantalla del punt mig entre els dos centres
#                       (0,0),0,0 si no es troba la flor
def TrobaPosicioFlor(imatge, CampFlors):
    # Redueix els límits del camp per evitar les referències externes
    xmin = max(CampFlors.left_up[0], CampFlors.left_down[0]) + REDUCCIO_REFERENCIES
    xmax = min(CampFlors.right_up[0], CampFlors.right_down[0]) - REDUCCIO_REFERENCIES
    ymin = max(CampFlors.left_up[1], CampFlors.right_up[1]) + REDUCCIO_REFERENCIES
    ymax = min(CampFlors.left_down[1], CampFlors.right_down[1]) - REDUCCIO_REFERENCIES

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
        cv2.imshow('Imatge amb Contorns trobats', imager)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Si es troben més de 2 centres, imprimeix un missatge d'error
    if len(centres) > 2 or len(centres) < 2:
        print('TrobaPosicioFlor: S\'han trobat més de 2 referències')
        # Desa la imatge 
        #GuardaImatge(imatge, 'Software/Lector-posicio/Data/ErrorReferences')
        return (0,0),0,0
    
    # Calcula la distància entre els dos centres
    distancia = math.sqrt((centres[0][0]-centres[1][0])**2 + (centres[0][1]-centres[1][1])**2)

    # Obté les coordenades del punt mig entre els dos centres
    middle_point = ((centres[0][0]+centres[1][0])//2, (centres[0][1]+centres[1][1])//2)

    if DEBUG:
        # Dibuixa un cercle gris al punt mig
        cv2.circle(imager, middle_point, 5, (128, 128, 128), -1)
        cv2.imshow('Imatge amb posicio flor', imager)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # Obté l'angle entre la línia que uneix els dos centres i l'eix y
    try:
        angle = math.atan((centres[1][0]-centres[0][0])/(centres[1][1]-centres[0][1]))
    except ZeroDivisionError:
        angle = 0
    
    # S'afegeix el que s'ha retallat al principi per eliminar les referències externes
    middle_point = (middle_point[0] + xmin, middle_point[1] + ymin)

    return middle_point, distancia, angle

# Dibuixa un cercle al punt mig i una línia a la inclinació de la flor
# Entrada: imatge: imatge per dibuixar
#          x: coordenada x de pantalla del punt mig
#          y: coordenada y de pantalla del punt mig
#          angle: inclinació de la flor
# Sortida: imatge: imatge amb el cercle i la línia dibuixats
def DibuixaPosicioFlor(imatge, x, y, angle):
    # Dibuixa un cercle al punt mig
    cv2.circle(imatge, (x, y), 100, (255, 255, 255), 2)

    # Dibuixa una línia a la inclinació de la flor
    x2 = int(x + 200 * math.sin(angle))
    y2 = int(y + 200 * math.cos(angle))
    cv2.line(imatge, (x, y), (x2, y2), (255, 255, 255), 2)
    
    if DEBUG:
        cv2.imshow('Imatge amb dibuix posicio flor', imatge)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return imatge

# Per seguir la flor
# Llegeix la càmera, corregeix la imatge, la binaritza i troba la posició de la flor
# Mostra la imatge amb un cercle al punt mig i una línia a la inclinació de la flor
# També mostra les coordenades x, y i l'angle de la flor
# Si l'usuari prem 's' guarda les imatges original, corregida, binaritzada i de posició
# Si l'usuari prem 'esc' tanca la càmera
# Entrada: Camp: objecte FlowerField ja calibrat (ObteCamp executat)
# Sortida: cap
def SegueixFlor(CampFlors):
    # Carrega les dades de calibració de la càmera
    cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
    dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

    cap = ActivaCamera()  
    
    while True:
        imatge = LlegeixFotoCamera(cap)
                
        imatgec = CorregeixImatge(imatge, cameraMatrix, dist)
        imatget = ThresholdImatge(imatgec)
        
        Posicio, Distancia, Angle = TrobaPosicioFlor(imatget, CampFlors)

        font = cv2.FONT_HERSHEY_SIMPLEX
        if (Posicio[0] == 0 and Posicio[1] == 0 and Distancia == 0 and Angle == 0):
            # No s'ha trobat la flor
            cv2.putText(imatgec, 'No s\'ha trobat flor', (50, 60), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Imatge sense posicio', imatgec)
        else:
            # Dibuixa la posició de la flor
            imager = DibuixaPosicioFlor(imatgec, Posicio[0], Posicio[1], Angle)
            PosicioReal = CampFlors.PixelXY2ReallXY(Posicio[0], Posicio[1])
            cv2.putText(imager, 'X: ' + str(int(PosicioReal[0])), (50, 80), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(imager, 'Y: ' + str(int(PosicioReal[1])), (50, 160), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            # Angle en str amb només 2 decimals
            Ang = "{:.2f}".format((Angle*360)/6.28)
            cv2.putText(imager, 'Angle: ' + Ang, (50, 240), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Imatge amb posicio', imager)
        
        if DEBUG:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        k = cv2.waitKey(5)
        if k == 27:
            break
        elif k == ord('s'):
            GuardaImatge(imatge, 'Software/Lector-posicio/Data/FotoOriginal')
            GuardaImatge(imatgec, 'Software/Lector-posicio/Data/FotoCorregida')
            GuardaImatge(imatget, 'Software/Lector-posicio/Data/FotoThreshold') 
            if not (Posicio[0] == 0 and Posicio[1] == 0 and Distancia == 0 and Angle == 0):
                GuardaImatge(imager, 'Software/Lector-posicio/Data/FotoPosicio')
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()  

# Per moure un cercle a la pantalla utilitzant el teclat i comprovar quina és la posició real calculada, per veure si coincideix amb la posició real
# Entrada: CampFlors: objecte FlowerField ja calibrat (ObteCamp executat)
# Sortida: cap (pantalla)
def ComprovaPosicio(CampFlors):
    # Carrega les dades de calibració de la càmera
    cameraMatrix = pickle.load(open('Software/Calibracio-camera/cameraMatrix.pkl', 'rb'))
    dist = pickle.load(open('Software/Calibracio-camera/dist.pkl', 'rb'))

    cap = ActivaCamera()  
    
    Posicio = (100,1000)
    Angle = 0

    while True:
        imatge = LlegeixFotoCamera(cap)
                
        imatgec = CorregeixImatge(imatge, cameraMatrix, dist)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Dibuixa la posició de la flor
        imager = DibuixaPosicioFlor(imatgec, Posicio[0], Posicio[1], Angle)
        PosicioReal = CampFlors.PixelXY2ReallXY(Posicio[0], Posicio[1])
        cv2.putText(imager, 'X: ' + str(int(PosicioReal[0])), (50, 80), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(imager, 'Y: ' + str(int(PosicioReal[1])), (50, 160), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        # Angle en str amb només 2 decimals
        Ang = "{:.2f}".format((Angle*360)/6.28)
        cv2.putText(imager, 'Angle: ' + Ang, (50, 240), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('Imatge amb posicio', imager)
        
        if DEBUG:
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        k = cv2.waitKey(5)
        # Mou la posició de la flor
        # s: dreta
        # a: esquerra
        # w: amunt
        # z: avall
        # k: 10 píxels a la dreta
        # j: 10 píxels a l'esquerra
        # i: 10 píxels a dalt
        # m: 10 píxels avall
        if k == 27:
            break
        elif k == ord('s'):
            Posicio = (Posicio[0]+1, Posicio[1])
        elif k == ord('a'):
            Posicio = (Posicio[0]-1, Posicio[1])
        elif k == ord('w'):
            Posicio = (Posicio[0], Posicio[1]-1)
        elif k == ord('z'):
            Posicio = (Posicio[0], Posicio[1]+1)
        elif k == ord('k'):
            Posicio = (Posicio[0]+10, Posicio[1])
        elif k == ord('j'):
            Posicio = (Posicio[0]-10, Posicio[1])
        elif k == ord('i'):
            Posicio = (Posicio[0], Posicio[1]-10)
        elif k == ord('m'):
            Posicio = (Posicio[0], Posicio[1]+10)
        elif k == ord('g'):
            GuardaImatge(imager, 'Software/Lector-posicio/Data/FotoPosicio')
 
                
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()  

################################################ Funció principal ################################################
def main():
    
    Camera = ActivaCamera()
    foto = LlegeixFotoCamera(Camera)
    CampFlors = FlowerField()
    AjustaLimitsCamp(CampFlors)
    CampFlors.ObteCamp()
    SegueixFlor(CampFlors)
    #ComprovaPosicio(CampFlors)
     
   
if __name__ == "__main__":
    main()
