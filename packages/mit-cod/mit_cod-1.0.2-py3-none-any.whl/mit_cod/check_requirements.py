import sys, os
import importlib.util

def check_requirements():
    print("")
    print("### MIT Course Objective Digitizer ###")

    if os.name != 'nt':
        print("Works only on Windows")
        sys.exit(-1)

    if sys.version_info[0] != 3 or sys.version_info[1] < 5:
        print("Requires Python 3.5 or later")
        sys.exit(-1)

    def is_installed(package):
        return importlib.util.find_spec(package) != None
        
    # opencv_python-3.4.1+contrib-cp35-cp35m-win32.whl
    # opencv_python-3.4.1+contrib-cp35-cp35m-win_amd64.whl
    URL = "https://www.lfd.uci.edu/~gohlke/pythonlibs/"
    A = "win_amd64" if (sys.maxsize > 2**32) else "win32"
    V = str(sys.version_info[0]) + str(sys.version_info[1])

    quit = False

    if is_installed('numpy') == False:
        print("Install numpy-$.$.$+mkl-%s-%s.whl from %s#numpy" % (V, A, URL))
        quit = True
        
    if is_installed('scipy.misc.pilutil') == False:
        print("Install scipy-$.$.$+mkl-%s-%s.whl from %s#scipy" % (V, A, URL))
        quit = True
        
    if is_installed('cv2') == False:
        print("Install opencv_python-$.$.$+contrib-%s-%s.whl from %s#opencv" % (V, A, URL))
        quit = True
        
    if is_installed('imutils') == False:
        print("Install scikit_image-$.$.$-%s-%s.whl from %s#scikit-image" % (V, A, URL))
        quit = True

    if quit == True:
        print("")
        print("To install downloaded wheels, run pip install <path_to_file>.whl")
        print("     pip install path_to_file.whl")
        print("Then try to install this package again.")
        sys.exit(-1)
        
if __name__ == "__main__":
    check_requirements()