#!python3

import cv2
import imutils
import numpy as np

def getBoundsOfMarks(image, bounds):
    min_height, max_height = bounds[0]
    min_width, max_width = bounds[1]
    
    # kernel = np.ones((5,5),np.uint8)
    
    # ret, thresh = cv2.threshold(image, 127, 255, 0)   
    # thresh = cv2.erode(thresh, kernel, iterations = 1)
    # thresh = cv2.dilate(thresh, kernel, iterations = 1)
    # thresh = cv2.erode(thresh, kernel, iterations = 1)
    
    contours = cv2.findContours(image, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]
    digitContours = []

     
    # loop over the digit area candidates
    for c in contours:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
     
        # if the contour is sufficiently large, it must be a digit
        if (w >= min_width and w <= max_width) and (h >= min_height and h <= max_height):
            digitContours.append(c)
            
    return imutils.contours.sort_contours(digitContours, method="left-to-right")[0]