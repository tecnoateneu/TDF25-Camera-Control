import cv2
from picamera2 import Picamera2
import time

# Aquest programa visualitza la càmera de la Raspberry des de la Raspberry
# Instruccions:
#       - Connectar-se a la Raspberry via SSH (utilitzant VNC)
#       - Activar l'entorn virtual de Python env311. Executar des de la RBPI: source env311/bin/activate
#       - Executar aquest programa
#       - Es veu la càmera en temps real
#       - Apretant 's' es guarda la imatge en escala de grisos a la carpeta Imatges


# Activem la càmera
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

num = 0
while True:
    output = picam2.capture_array()                     # Captura la imatge 
    output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)   # Converteix la imatge a escala de grisos
    
    # Espera que l'usuari premi una tecla
    cv2.imshow('Imatge', output)
    k = cv2.waitKey(1)
    if k == ord('s'): # Si l'usuari ha premut la tecla 's', guarda la imatge
        cv2.imwrite('Imatges/' + f'cali{num}.png', output)
        num += 1
    elif k == 27:  # 27 és el codi ASCII per a la tecla 'esc'
        break
cv2.destroyAllWindows()
  