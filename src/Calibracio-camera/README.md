# Calibració

En aquest directori hi ha unes rutines per calibrar una càmera.

La vaig fer servir quan utilitzava una càmera IP i la imatge que donava tenia distorsió radial (com de ull de peix). Per resoldre aquesta distorsió feia servir Captura-imatges.py per recollir vàries imatges d'un quadre d'escacs (CalibrationPattern.png). Llavors feia córrer Calibracio.py i generava un fitxer de calibració que llavors les rutines de lectura de càmera feien servir per retocar la imatge.

Amb la càmera de la Raspberry no fa falta perquè ja dóna la imatge sense distorsió.
