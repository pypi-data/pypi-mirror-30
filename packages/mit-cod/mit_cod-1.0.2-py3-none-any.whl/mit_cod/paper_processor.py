#!python3

import sys
from os.path import isfile, isdir
import argparse

import numpy as np
import cv2
import imutils
from imutils import contours
# from scipy.misc.pilutil import imresize

from .image_manipulation import loadImage, straightenAndCrop, getRedPenWriting, imresize
from .roi_selector import roi_selector
from .marks_model import Exam, Internal
from .marks_detection import getBoundsOfMarks
from .predictor import predictor

import clr
# clr.AddReference('System.Data')
from System import Type, Data, String

class PaperProcessor(object):
    ERROR = None
    # LOG_VERBOSE = 0
    # LOG_NONE = 1
    

    def __init__(self, file, roi, scale = 1, examType = 0, examNo = 0, showImages = True, temp = None, frmHelp = None): # logLevel = LOG_VERBOSE):
        self.__file = file
        self.__roi = roi
        self.__scale = scale
        self.__examType = examType
        self.__examNo = examNo
        self.__showImages = showImages
        self.__temp = temp
        self.__frmHelp = frmHelp
        # self.__logLevel = logLevel
        # self.__table = table
        
    
    def __getBlankDataTable(self):
        table = Data.DataTable()

        for i in range(0, 5):
            table.Columns.Add("col" + str(i), String)
        

        for i in range(0, 6):
            table.Rows.Add("", "", "", "", "")
        
        return table    
        
    def __saveMarksImage(self, img, s):
        if self.__temp != None and isdir(self.__temp):
            imres = img[s[0]:s[0]+s[2], s[1]:s[1]+s[3]]
            path = self.__temp + '\\marks.jpg'
            cv2.imwrite(path, imres)
            return path
        return ""
        
    def process(self):
        ### Exit if image file doesn't exist
        if not isfile(self.__file):
            print("Image file doesn't exist")
            return ERROR


        ### Load and resize image to fit screen
        imgOriginal = loadImage(self.__file)
        self.__showImage("Original (resized to fit screen)", imgOriginal)


        ### Correct score table perspective and crop
        if self.__roi is None:
            roi = roi_selector(imgOriginal, "Perspective Correction - (Press H for help)", self.__frmHelp).get()
        else:
            roi = np.array(self.__roi)
            
        if (roi is None):
            return None
            
        self.__log("RoI:\n%s" % str(roi))
        imgOriginalCorrected = straightenAndCrop(imgOriginal, roi)
        imgDraw = imgOriginalCorrected.copy()               # drawing canvas
        self.__showImage("Perspective Correction & Crop", imgOriginalCorrected)


        ### Grayscale
        imgGrayscale = cv2.cvtColor(imgOriginalCorrected, cv2.COLOR_BGR2GRAY)
        self.__showImage("Grayscale", imgGrayscale)


        ### HSV
        imgHsv = cv2.cvtColor(imgOriginalCorrected, cv2.COLOR_BGR2HSV)
        self.__showImage("HSV", imgHsv)


        ### Isolate red pen writing
        imgRedPen = getRedPenWriting(imgHsv)
        self.__showImage("Handwriting", imgRedPen)


        # Score table ROI width and height
        height, width = imgGrayscale.shape
        self.__log("Table RoI shape = [%d, %d]" % (height, width))


        # Predict scores
        detector = predictor()
        exam = Internal(imgGrayscale.shape)
        digitBounds = getBoundsOfMarks(imgRedPen.copy(), exam.getBoundsLimitForDetection())
     
        
        table = self.__getBlankDataTable()
        imgMarksPath = self.__saveMarksImage(imgOriginalCorrected, exam.getTableShapeForExam())
        # total = ""
        for bound in digitBounds:
            # extract the digit ROI
            (x, y, w, h) = cv2.boundingRect(bound)
            
            imgDigit = imgRedPen[y-1:y+h+2, x-1:x+w+2]
            imgDigit = imresize(imgDigit, (20, 20))
            digit = detector.predict(imgDigit)
            strDigit = str(int(digit))
            
            result = exam.getBbForPosition(y, x)
            # print("%d, %d = %s" % (y, x, box))
            if (not result == None):
                box, pos = result
                
                if (not box == None):
                    cv2.rectangle(imgDraw, (box[1], box[0]), (box[1]+box[3], box[2]+box[0]), (255, 0, 0), 1)
                    
                if (not pos == None):
                    ret, question, subquestion = pos
                    
                    if ret == Exam.BB_SUBQUESTION:
                        table.Rows[question][subquestion] +=  strDigit
                    # elif ret == Exam.BB_QUESTION_TOTAL:
                        # table.Rows[question][5] +=  strDigit
                    # elif ret == Exam.BB_EXAM_TOTAL:
                        # total += strDigit
                
            cv2.rectangle(imgDraw, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.putText(imgDraw, strDigit, (x - 2, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


        self.__showImage("OCR", imgDraw)
        # self.__waitForKey()
        
        return [imgMarksPath, table]
    
    def __showImage(self, title, image):
        # if (self.__logLevel < PaperProcessor.LOG_NONE):
        if (self.__showImages):
            cv2.imshow(title, image)
    
    
    def __log(self, msg):
        # if (self.__logLevel < PaperProcessor.LOG_NONE):
        print(msg)
            
            
    # def __waitForKey(self):
        # if (self.__logLevel < PaperProcessor.LOG_NONE):
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            
if __name__ == "__main__":
    ### Argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="Path to the input image")
    ap.add_argument("-r", "--roi", action='append', type=int, nargs='+', required=False, help="ROI for perspective transformation")
    args = vars(ap.parse_args())
    asp = PaperProcessor(temp = None, file = args["image"], roi = args["roi"], scale = 1, examType = 0, examNo = 0, showImages=True) # logLevel = PaperProcessor.LOG_VERBOSE)
    asp.process()
