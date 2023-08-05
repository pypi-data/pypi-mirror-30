#!python3

import os 
import cv2
import numpy as np
from numpy.linalg import norm
import imutils

# PATH_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
# PATH_CLASSIFIER = os.path.join(PATH_ROOT, 'classifier', 'svm_digits.dat')
PATH_ROOT = os.path.split(__file__)[0]
PATH_CLASSIFIER = os.path.join(PATH_ROOT, "classifier", "svm_digits.dat")


# print(PATH_CLASSIFIER)

SZ = 20 # size of each digit is SZ x SZ

class predictor(object):
    def __init__(self, C = 1, gamma = 0.5):
        self.__model = cv2.ml.SVM_load(PATH_CLASSIFIER)
        self.__model.setGamma(gamma)
        self.__model.setC(C)
        self.__model.setKernel(cv2.ml.SVM_RBF)
        self.__model.setType(cv2.ml.SVM_C_SVC)
        # self.__model.load('digits_svm.dat')

    def __deskew(self, img):
        m = cv2.moments(img)
        if abs(m['mu02']) < 1e-2:
            return img.copy()
        skew = m['mu11']/m['mu02']
        M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (SZ, SZ), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
        return img
        
    def __hog(self, img):
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bin_n = 16
        bin = np.int32(bin_n*ang/(2*np.pi))
        bin_cells = bin[:10,:10], bin[10:,:10], bin[:10,10:], bin[10:,10:]
        mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)

        # transform to Hellinger kernel
        eps = 1e-7
        hist /= hist.sum() + eps
        hist = np.sqrt(hist)
        hist /= norm(hist) + eps

        return np.float32(hist)
    
    def predict(self, img):
        digit = self.__deskew(img)
        sample = self.__hog(img)
    
        digits = self.__model.predict(np.ravel(sample)[None, :])[1].ravel()
        # print(digits)
        return digits[0]