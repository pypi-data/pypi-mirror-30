#!python3

import cv2
import imutils
import numpy as np

import clr
from System.Windows.Forms import Screen

from .perspective_correction import transform_perspective

def loadImage(path):
    img = cv2.imread(path)
    screenHeight = Screen.PrimaryScreen.Bounds.Height
    if img.shape[0] > screenHeight:
        img = imutils.resize(img, height = int(screenHeight * 0.9))
    return img
    
def fitImageInScreen(img):
    resized = False
    screenHeight = Screen.PrimaryScreen.Bounds.Height
    if img.shape[0] > screenHeight:
        img = imutils.resize(img, height = int(screenHeight * 0.9))
        resized = True
    return [resized, img]    
    
def straightenAndCrop(image, roi):
    img2 = transform_perspective(image, roi)
    img2 = cv2.GaussianBlur(img2, (1, 1), 0)
    return img2
    
def getRedPenWriting(imgHsv):
    # Mask red pen areas
    mask1 = cv2.inRange(imgHsv, np.array([0, 40, 40], dtype=np.uint8), np.array([10, 255, 255], dtype=np.uint8))
    mask2 = cv2.inRange(imgHsv, np.array([160, 40, 20], dtype=np.uint8), np.array([200, 255, 255], dtype=np.uint8))
    mask = cv2.addWeighted(mask1, 1, mask2, 1, 0)
    
    # Bitwise-AND mask and original image
    result = cv2.bitwise_and(imgHsv, imgHsv, mask= mask)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(result, 220, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
def imresize(img, size):
    return cv2.resize(img, size)
    