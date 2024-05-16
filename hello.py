from picamera2 import Picamera2, Preview
import time
import cv2
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (4608, 2592)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test.jpg")

image = cv2.imread('test.jpg')

# Get the dimensions of the image
dimensions = image.shape

# Print the dimensions
print('Dimensions:', dimensions)

# Height, width, number of channels in image
height = image.shape[0]
width = image.shape[1]
channels = image.shape[2]

print('Image Dimension    : ',dimensions)
print('Image Height       : ',height)
print('Image Width        : ',width)
print('Number of Channels : ',channels)