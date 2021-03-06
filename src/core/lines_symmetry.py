import cv2
import math
import numpy as np
from numpy.linalg import norm

from src.core.viola_jones import detected

''' ============ SEARCH METHODS ============ '''

def _search_line_window(img):
    '''Search line symmetry by window method'''
    w = 40 # size of window

    x_min = None
    d_min = np.iinfo(np.int32).max

    _, w_img = img.shape
    for x in range(w,w_img,w):
        if w_img - x < w: break
        img_L = img[:, x-w:x]
        img_R = np.flip(img[:, x:x+w], axis=1)
        d = np.sum(np.abs(img_L - img_R))
        if d < d_min: x_min = x ; d_min = d

    return x_min

def _search_line_express(img):
    '''Search line symmetry by express method'''
    diff = img - np.flip(img, axis=1)

    x_max = None
    d_max = np.iinfo(np.int64).min

    _, w_img = img.shape
    for x in range(1, w_img - 1):
        d = np.sum(np.abs(diff[:, x-1:x].astype(np.int32) - diff[:, x:x+1].astype(np.int32)))
        if d > d_max: x_max = x ; d_max = d
    
    return x_max


''' ============ SUPPORT METHODS ============ '''

def _center_rect(rect):
    '''Count center of rectangle'''
    x, y, w, h = rect
    return np.array([x + w // 2, y + h // 2])

def _angle_vec(v1, v2):
    '''Count angle(degrees) between vectors'''
    cos_val = np.dot(v1, v2) / norm(v1) / norm(v2)
    rad = np.arccos(np.clip(cos_val, -1, 1))
    return np.rad2deg(rad)

def _rotate_vec(p1, p2, angle):
    '''Rotate vector around your center on specified angle'''
    c = (p1 + p2) / 2
    v = p2 - c

    rad = angle * (math.pi / 180)

    x, y = v
    rot_v = np.array([x*math.cos(rad)+y*math.sin(rad), y*math.cos(rad)-x*math.sin(rad)])

    return tuple(map(int, c - rot_v)), tuple(map(int, c + rot_v))

def _rotate_image(image, angle):
    '''Rotate image around your center on specified angle'''
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def search_lines(img, method='express'):
    # Detections areas of face and eyes by Viola Jones
    detections = detected(img)
    if len(detections) != 3: return None
    face, eye1, eye2 = detections

    # Count centers of areas eyes
    c_loc1 = _center_rect(eye1)
    c_loc2 = _center_rect(eye2)
    
    # Count the angle at which the face is rotated in XY space 
    vec = c_loc2 - c_loc1
    angle = _angle_vec(vec, np.array([1, 0]))
    if angle > 90: angle -= 180
    if vec[1] < 0: angle = -angle

    # Rotate area of face on img
    x_f, y_f, w_f, h_f = face
    face_img = img[y_f:y_f+h_f, x_f:x_f+w_f].copy()
    rot_face_img = _rotate_image(face_img, angle)

    # Search central line of symmentry and rotate it
    if method == 'express': x_central = _search_line_express(rot_face_img)
    if method == 'window': x_central = _search_line_window(rot_face_img)
    p1_central, p2_central = _rotate_vec(np.array([x_central, 0]), np.array([x_central, h_f]), -angle)
    p1_central = (x_f + p1_central[0], y_f + p1_central[1])
    p2_central = (x_f + p2_central[0], y_f + p2_central[1])
    line_central = (p1_central, p2_central)

    # Count local line of symmentry and rotate their
    l = 10
    p1_loc1, p2_loc1 = _rotate_vec(c_loc1 - np.array([0, l]), c_loc1 + np.array([0, l]), -angle)
    p1_loc2, p2_loc2 = _rotate_vec(c_loc2 - np.array([0, l]), c_loc2 + np.array([0, l]), -angle)
    line_loc1 = (p1_loc1, p2_loc1) ; line_loc2 = (p1_loc2, p2_loc2)

    return line_central, line_loc1, line_loc2, (c_loc1, c_loc2)
