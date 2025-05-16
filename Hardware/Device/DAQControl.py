'''
Created on May 15, 2025

@author: hd.nguyen
'''
import os
import ctypes

BoardNum = 0
Range = 0

class DAQControl():
    '''
    classdocs
    '''


    def __init__(self, path, parent = None, modConfig = None):
        '''
        Constructor
        '''
        self.parent = parent
        self.modConfig = modConfig

        self.daqDLL = ctypes.CDLL(path + 'cbw64.dll')
        
        # Function definitions
        self.daqDLL.cbAIn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
        self.daqDLL.cbAIn.restypes = ctypes.c_int

        self.daqDLL.cbToEngUnits.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint8, ctypes.POINTER(ctypes.c_float)]
        self.daqDLL.cbToEngUnits.restypes = ctypes.c_int
        
    '''
    '''
    def cbAIn(self, Chan):
        outValue = ctypes.c_char(0)        
        self.daqDLL.cbAIn(BoardNum, Chan, Range, ctypes.byref(outValue))
        
        return ord(outValue.value)
        
    '''
    '''
    def cbToEngUnits(self, inValue):
        outValue = ctypes.c_float(0)
        self.daqDLL.cbToEngUnits(BoardNum, Range, inValue, ctypes.byref(outValue))
        
        return outValue.value
        
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            data = self.Get_ADC(0)
            print(data)            
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd()
        daqUtil = DAQControl(currentPath + '\\')
        
        daqUtil.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))

        