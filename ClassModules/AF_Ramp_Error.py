'''
Created on Nov 7, 2025

@author: hd.nguyen
'''
from enum import Enum

class AFErrorTypeEnum(Enum):
    NoError             = 0
    ZeroMonitorVoltage  = 1
    TargetUndershoot    = 2
    TargetOvershoot     = 4
    FatalError          = 8

'''
    --------------------------------------------------------------------------------
'''
class AF_Ramp_Error():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.ErrorType = AFErrorTypeEnum.NoError
        self.Message = ""
        self.Source = ""
        self.ErrNumber = 0
        self.StackTrace = ""
        

        