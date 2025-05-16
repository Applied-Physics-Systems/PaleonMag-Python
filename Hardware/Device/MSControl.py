'''
Created on Apr 22, 2025

@author: hd.nguyen
'''
import os
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice

class MSControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label, modConfig=None):
        '''
        Constructor
        '''
        self.label = Label
        self.PortOpen = False 
                
        SerialPortDevice.__init__(self, baudRate, 'MSControl', pathName, comPort, Label, modConfig)
        
    '''
    '''
    def makeMeasurement(self):
        cmdStr = 'M\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        respStr = self.readLine()
        
        return respStr 
        
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            respStr = self.makeMeasurement()
            print(respStr)
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd()
        devControl = MSControl(1200, currentPath + '\\', 'COM2', 'MS')
        devControl.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
        