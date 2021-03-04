from os import pipe
import cv2

PATH_CASCADE = './src/core/viola_jones/haarcascade_frontalface_default.xml'

def detected(img):
    faceCascade = cv2.CascadeClassifier(PATH_CASCADE)
    h, w = img.shape
    min_part = 0.2
    return faceCascade.detectMultiScale(
        img, 
        scaleFactor=1.1, 
        minNeighbors=5, # 3-6
        minSize=(int(w * min_part), int(h * min_part))
    )
