import cv2
from picamera2 import Picamera2, Preview
import time

# Llegeix imatges de la càmera de la Raspberry i les guarda a la carpeta Eines/Calibracio-camera/Imatges
# Les imatges es guarden amb el nom caliX.png, on X és un número que augmenta amb cada imatge guardada
# El programa s'atura quan l'usuari prem la tecla 'esc'
# L'usuari pot guardar una imatge prement la tecla 's'
def LlegeixImatgesCalibracio():

    # Activa càmera
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
    
    # Bucle que va llegint imatges de la càmera de la Raspberry
    # Mostra la imatge llegida en una finestra
    # Si la tecla 's' és premuda, guarda la imatge amb el nom caliX.png
    # Si la tecla 'esc' és premuda, el programa s'atura
    num = 0
    while True:
        # Llegeix una imatge de la càmera
        output = picam2.capture_array()                     # Captura la imatge 
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
  
        # Mostra la imatge en una finestra
        cv2.imshow('Imatge de la càmera', output)

        # Espera que l'usuari premi una tecla
        k = cv2.waitKey(1)

        # Si l'usuari ha premut la tecla 's', guarda la imatge
        if k == ord('s'):
            cv2.imwrite('Imatges/' + f'cali{num}.png', output)
            num += 1

        # Si l'usuari ha premut la tecla 'esc', surt del bucle
        elif k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
            break

    # Allibera els recursos de la càmera i tanca les finestres d'OpenCV
    picam2.release()
    cv2.destroyAllWindows()

def main():
    LlegeixImatgesCalibracio()

if __name__ == "__main__":
    main()
   