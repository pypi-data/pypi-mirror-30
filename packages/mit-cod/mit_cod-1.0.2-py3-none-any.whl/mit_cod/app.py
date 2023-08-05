#!python3

from .check_requirements import check_requirements
check_requirements()


import sys, os 
import cv2
import clr

from .paper_processor import PaperProcessor

from System.Reflection import Assembly
import System.Windows.Forms as WinForms
from System.Threading import Thread, ThreadStart, ApartmentState

# Load DOTNET Assembly
# PATH_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
PATH_SRC = os.path.split(__file__)[0] # os.path.dirname(os.path.realpath(__file__))
PATH_BIN = os.path.join(PATH_SRC, 'bin')
PATH_TEMP = os.path.join(os.getenv('LOCALAPPDATA'), 'MIT_CO_Digitizer')

try:
    os.makedirs(PATH_TEMP, exist_ok = True)
except:
    print("Error creating TEMP path")
    sys.exit(0)


BINARIES = [   
    'AForge.Controls.dll',
    'AForge.dll',
    'AForge.Imaging.dll',
    'AForge.Math.dll',
    'AForge.Video.DirectShow.dll',
    'AForge.Video.dll',
    'Newtonsoft.Json.dll',
    'CODGUI.dll'
]

for d in BINARIES:
    Assembly.LoadFile(os.path.join(PATH_BIN, d))

import CODGUI



class App(object):
    def __init__(self):
        self.__frmMain = None
        self.__frmCamera = None
        self.__frmEditor = None

    def __clearTempFiles(self):
        for root, dirs, files in os.walk(PATH_TEMP):
            for f in files:
                # print(os.path.join(root, f))
                os.unlink(os.path.join(root, f))
            
    def __showMain(self):            
        def OnImageChosen(examType, examNumber, showImages, path):
            self.__frmMain.ContentVisible = False
            self.__processAnswerSheet(examType = 0, examNo = 0, file = path, showImages = showImages)
        
        self.__frmMain = CODGUI.frmMain(PATH_TEMP)
        self.__frmMain.OnImageChosen += OnImageChosen
        WinForms.Application.Run(self.__frmMain)

    def __processAnswerSheet(self, examType = 0, examNo = 0, file = None, showImages = True):
        roi = None # [[86, 222], [470, 225], [467, 546], [85, 543]]
        # file = "E:\MVIP\MTech-CO-Digitizer\img\internal_filled.tif"
        asp = PaperProcessor(temp = PATH_TEMP, file = file, roi = roi, scale = 1, examType = examType, examNo = examNo, showImages = showImages, frmHelp = CODGUI.frmPerspectiveHelp()) 
        output = asp.process()
        
        if output != None:
            imgMarksPath, table = output
            self.__frmEditor = CODGUI.frmEditor(imgMarksPath, table)
            if self.__frmEditor.ShowDialog(): # == WinForms.DialogResult.OK:
                cv2.destroyAllWindows()
                self.__frmMain.ContentVisible = True
        else:
            print("Empty result")
            cv2.destroyAllWindows()
            self.__frmMain.ContentVisible = True

    def __startThread(self):
        thread = Thread(ThreadStart(self.__showMain))
        thread.SetApartmentState(ApartmentState.STA)
        thread.Start()
        thread.Join()
    
    def run(self):
        self.__clearTempFiles()
        self.__startThread()
        self.__clearTempFiles()
      
def main():
    app = App()
    app.run()
    
if __name__ == "__main__":
    main()