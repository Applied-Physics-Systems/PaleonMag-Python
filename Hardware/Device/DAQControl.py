'''
Created on May 15, 2025

@author: hd.nguyen
'''
import os
import ctypes

BoardNum = 0
Range = 0
DIGITALOUT = 1

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
                
    '''
    '''
    def cbAIn(self, Chan):
        # Function definitions
        self.daqDLL.cbAIn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
        self.daqDLL.cbAIn.restypes = ctypes.c_int
        
        outValue = ctypes.c_char(0)        
        self.daqDLL.cbAIn(BoardNum, Chan, Range, ctypes.byref(outValue))
        
        return ord(outValue.value)
        
    '''
    '''
    def cbAOut(self, Chan, Gain, DataValue):
        self.daqDLL.cbAOut.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint8]
        self.daqDLL.cbAOut.restypes = ctypes.c_int
        
        status = self.daqDLL.cbAOut(BoardNum, Chan, Gain, DataValue)
        
        return status
   
    '''
    '''
    def cbToEngUnits(self, inValue):
        self.daqDLL.cbToEngUnits.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint8, ctypes.POINTER(ctypes.c_float)]
        self.daqDLL.cbToEngUnits.restypes = ctypes.c_int
        
        outValue = ctypes.c_float(0)
        self.daqDLL.cbToEngUnits(BoardNum, Range, inValue, ctypes.byref(outValue))
        
        return outValue.value
    
    '''
    '''
    def cbFromEngUnits(self, EngUnits):
        self.daqDLL.cbFromEngUnits.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_float, ctypes.POINTER(ctypes.c_uint8)] 
        self.daqDLL.cbFromEngUnits.restypes = ctypes.c_int
        
        outValue = ctypes.c_uint8(0)
        self.daqDLL.cbFromEngUnits(BoardNum, Range, EngUnits, ctypes.byref(outValue))
        
        return outValue.value
        
    '''
    '''
    def  cbDConfigBit(self, OutChannel):
        self.daqDLL.cbDConfigBit.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int] 
        self.daqDLL.cbDConfigBit.restypes = ctypes.c_int
        
        status = self.daqDLL.cbDConfigBit(BoardNum, OutChannel.PortType, OutChannel.ChanNum, DIGITALOUT)
        
        return status
    
    '''
    '''
    def cbDBitOut(self, OutChannel, BitValue):
        self.daqDLL.cbDBitOut.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint8] 
        self.daqDLL.cbDBitOut.restypes = ctypes.c_int
        
        status = self.daqDLL.cbDBitOut(BoardNum, OutChannel.PortType, OutChannel.ChanNum, BitValue)
    
        return status
        
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

        