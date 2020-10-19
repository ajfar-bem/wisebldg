import sys
import traceback
import cgitb
from bemoss_lib.utils.catcherror import getErrorInfo

def handleException(excType, excValue, trace):
    print 'error'
    cgitb.Hook(format="text")(excType, excValue, trace)

sys.excepthook = handleException

def test_func():
    h = 1
    J = [34]
    S = J.append(h)
    M = J[1] - h
    T = h / M

try:
    test_func()
except:

    print getErrorInfo()

