#!python3

import clr
from System.Windows.Forms import MessageBox as MB
from System.Windows.Forms import MessageBoxButtons as MSB
from System.Windows.Forms import MessageBoxIcon as MSI

def MsgBoxErr(msg, title = "MIT Course Outcome Digitizer"):
    return MB.Show(msg, title, MSB.OK, MSI.Hand)
    
def MsgBoxInfo(msg, title = "MIT Course Outcome Digitizer"):
    return MB.Show(msg, title, MSB.OK, MSI.Information)


if __name__ == "__main__":
    if MsgBoxErr("Test", "Title1"):
        MsgBoxInfo("Title", "Success!")