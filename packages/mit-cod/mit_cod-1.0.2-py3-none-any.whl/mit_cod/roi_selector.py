#!python3

import numpy as np
import cv2
import imutils

from .image_manipulation import fitImageInScreen

# ============================================================================

ENTER = 13
SPACE = 32
ESC = 27

ALPHA = 0.5
MASK_COLOR = (0, 255, 0)

# ============================================================================

class roi_selector(object):
    def __init__(self, image, window_name = "Select RoI (Press H for Help)", frmHelp = None):
        self.__window_name = window_name      # Name for our window
        self.__done = False                   # Flag signalling we're done
        self.__current = (0, 0)               # Current position, so we can draw the line-in-progress
        self.__points = []                    # List of points defining our polygon
                     
        
        # No image provided
        if np.array(image).size == 0:
            print("Image is blank")
            return self.__blank()
            
        self.__image = self.__rgba(image)       # add alpha        
        self.__frmHelp = frmHelp    
        
    # add transparency layer    
    def __rgba(self, image):
        b, g, r = cv2.split(image)
        a = np.ones(b.shape, dtype=b.dtype) * 50        # create a dummy alpha channel image.
        return cv2.merge((b, g, r, a))


    # Mouse event callback
    def __on_mouse(self, event, x, y, buttons, user_param):
        if self.__done:       # got 4 point roi
            return

        if event == cv2.EVENT_MOUSEMOVE:
            # Update current mouse position 
            self.__current = (x, y)
            
        elif event == cv2.EVENT_LBUTTONDOWN:
            # Add a point at current position to the list of points
            # print("Adding point #%d with position(%d,%d)" % (len(self.__points), x, y))
            self.__points.append((x, y))
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # restart roi
            self.__reset()

    # empty result
    def __blank(self):
        # return np.array([])
        cv2.destroyWindow(self.__window_name)
        return None
        
        
    def __getTransparentPolygon(self, image, canvas):
        image2 = image.copy()
        cv2.addWeighted(canvas, ALPHA, image2, 1 - ALPHA, 0, image2)
        return image2
        
        
    def __reset(self):
        self.__points = []
        self.__done = False
        
        
    def __cloneImage(self):
        return self.__image.copy()
        
        
    def __addHelpMsg(self, canvas):
        if self.__frmHelp is None:
            return
        cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 50), (0, 0, 255), -1)
        cv2.putText(canvas, 'Press H for help', (int(canvas.shape[1]/4), 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 128), 2, cv2.LINE_AA)
        
         
    def get(self):
        resized, imgResized = fitImageInScreen(self.__image)
        if resized:
            self.__originalImage = self.__cloneImage()
            self.__image = imgResized
    
        # Create named window and show image
        cv2.namedWindow(self.__window_name)
        cv2.imshow(self.__window_name, self.__image)
        cv2.waitKey(1)
        cv2.setMouseCallback(self.__window_name, self.__on_mouse)
        
        # yet to get 4 points
        while(not self.__done):
            # continuosly update image in window
            
            canvas = self.__cloneImage()      # create working image
            #self.__addHelpMsg(canvas)
            
            if (len(self.__points) == 4):
                # 4 points complete
                # print("Completing polygon with %d points." % len(self.__points))
                self.__done = True
                
            elif (len(self.__points) > 0):
                # yet to finish
                if (len(self.__points) > 2):
                    cv2.fillPoly(canvas, np.array([self.__points]), MASK_COLOR)
                    canvas = self.__getTransparentPolygon(self.__cloneImage(), canvas)
                else:
                    # Draw all the current polygon segments
                    cv2.polylines(canvas, np.array([self.__points]), False, MASK_COLOR, 1)
                    
                # Line to curent mouse position
                cv2.line(canvas, self.__points[-1], self.__current, MASK_COLOR)
                
            cv2.imshow(self.__window_name, canvas)    # show working image

            key = cv2.waitKey(50)   # wait 50ms
            # if key != -1:
                # print(key)
            
            if key == ENTER or key == SPACE:    # restart when incomplete
                self.__reset()
                cv2.imshow(self.__window_name, self.__cloneImage())
                
            if key == ESC:    # exit
                return self.__blank()

            if self.__frmHelp != None and (key == 72 or key == 104):    # exit
                if self.__frmHelp.ShowDialog():
                    continue
                
        # got roi
        canvas = self.__cloneImage()      # Final image
        #self.__addHelpMsg(canvas)
        
        if (len(self.__points) == 4):
            # 4 points done
            cv2.fillPoly(canvas, np.array([self.__points]), MASK_COLOR)
            canvas = self.__getTransparentPolygon(self.__cloneImage(), canvas)
            
        cv2.imshow(self.__window_name, canvas)
        # Waiting for the user to press any key
        key = cv2.waitKey()

        if key == SPACE:        # restart
            self.__reset()
            return self.get()
        
        if key == ESC:    # exit
            return self.__blank()
                
        cv2.destroyWindow(self.__window_name)
        
        if resized:
            points = []
            for point in self.__points:
                x = int(point[0]/self.__image.shape[1] * self.__originalImage.shape[1])
                y = int(point[1]/self.__image.shape[0] * self.__originalImage.shape[0])
                points.append((x, y))
        else:
            points = self.__points
            
        return np.array(points)

# ============================================================================

if __name__ == "__main__":
    image = cv2.imread("img/internal_filled.tif")
    image = imutils.resize(image, width = 500)
    r = roi_selector(image)
    print(r.get())