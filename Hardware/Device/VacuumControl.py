'''
Created on Jan 27, 2025

@author: hd.nguyen
'''
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice

class VacuumControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label, modConfig):
        '''
        Constructor
        '''        
        self.label = Label
        self.PortOpen = False 
                
        SerialPortDevice.__init__(self, baudRate, 'VacuumControl', pathName, comPort, Label, modConfig)
        
    '''
    '''
    def setVacuumOn(self):
        cmdStr = 'E\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        cmdStr = '10MFF\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        
        respStr = self.readLine()
        
        return cmdStr, respStr
        
        
    '''
    '''
    def setVacuumOff(self):
        cmdStr = 'D\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        cmdStr = '10M00\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        
        respStr = self.readLine()
        
        return cmdStr, respStr

    '''
    '''
    def setValveConnect(self):
        cmdStr = 'O\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        cmdStr = '10VFF\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        
        respStr = self.readLine()
        
        return cmdStr, respStr

    '''
    '''
    def clearValveConnect(self):
        cmdStr = 'C\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        cmdStr = '10V00\r'
        self.sendString(cmdStr)
        time.sleep(0.01)
        
        respStr = self.readLine()
        
        return cmdStr, respStr
        
    '''
    '''
    def reset(self):
        cmdStr = '10R00\r'
        self.sendString(cmdStr)
        time.sleep(0.2)
        cmdStr = '10TFF\r'
        self.sendString(cmdStr)
        time.sleep(0.2)

        respStr = self.readLine()
        
        return cmdStr, respStr

