from os import pipe
import cv2
import numpy as np

PATH_FACE_CASCADE = './src/core/viola_jones/haarcascade_frontalface_default.xml'
PATH_EYE_CASCADE = './src/core/viola_jones/haarcascade_eye.xml'

FACE_CASCADE = cv2.CascadeClassifier(PATH_FACE_CASCADE)
EYE_CASCADE = cv2.CascadeClassifier(PATH_EYE_CASCADE)

def detected(img):
    h, w = img.shape
    min_part = 0.2
    
    faces = list(FACE_CASCADE.detectMultiScale(
        img, 
        scaleFactor=1.3, 
        minNeighbors=5, # 3-6
        minSize=(int(w * min_part), int(h * min_part))
    ))
    faces = list(map(list, faces))

    eyes = []
    for (x, y, w, h) in faces:
        face_img = img[y:y+h, x:x+w]
        face_eyes = EYE_CASCADE.detectMultiScale(
            face_img, 
            scaleFactor=1.1, 
            minNeighbors=5, # 3-6
            minSize=(int(w * min_part), int(h * min_part))
        )
        face_eyes = [[x+ex, y+ey, ew, eh] for (ex, ey, ew, eh) in face_eyes]
        eyes += face_eyes
    return faces + eyes
