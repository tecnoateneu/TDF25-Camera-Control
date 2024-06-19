# Function to activate the camera
# Output: cap: VideoCapture object
def ActivaCamera():
    if LLEGEIX_CAMERA:
        cap = cv2.VideoCapture('rtsp://admin:TAV1234a@192.168.1.116:554/11')

        # Check if the camera opened successfully
        if not cap.isOpened():
            print("ActivaCamera: Could not open camera.")
            exit()
        return cap
    else:
        return None
    
# Function to read a frame from the camera
# Input: cap: VideoCapture object
# Output: frame: frame read from the camera
def LlegeixFotoCamera(cap):
    if LLEGEIX_CAMERA:
        ret, frame = cap.read()
        #GuardaImatge(frame, 'Software/Lector-posicio/Data/FotoCamp')
        
        if not ret:
            print("LlegeixFoto: Failed to capture frame.")
    else:
        frame = ObreImatge('Software/Lector-posicio/Data/FotoCamp_20240310_212033.jpg')
    
    if DEBUG:
        #Display read image
        cv2.imshow('Imatge de la camera', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
     
    return frame

# Function to correct the distortion of an image
# Input: image: image to correct
#        cameraMatrix: camera matrix
#        dist: distortion coefficients
#        newCameraMatrix: new camera matrix
#        roi: region of interest
#        w: width of the image
#        h: height of the image
# Output: dst: undistorted and cropped image
def CorregeixImatge(image, cameraMatrix, dist):
    h,  w = image.shape[:2]
    newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))
    
    # Undistort the image
    dst = cv2.undistort(image, cameraMatrix, dist, None, newCameraMatrix)
    
    # Undistort with Remapping
    #mapx, mapy = cv2.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
    #dst = cv2.remap(image, mapx, mapy, cv2.INTER_LINEAR)
    
    if DEBUG:
        # Display undistorted image
        cv2.imshow('Undistorted image', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # crop the image
    x, y, w, h = roi

    if CAMERA_USED == 'TPTEK':
        dst = dst[y + 20:y+h, x:x+w] # We remove completely text from the camera
    else:
        dst = dst[y:y+h, x:x+w]

    if DEBUG:
        # Display cropped image
        cv2.imshow('Cropped image', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return dst