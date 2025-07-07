'''
Created on Jan 21, 2025

@author: hd.nguyen
'''
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice

class SQUIDControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label, modConfig):
        '''
        Constructor
        '''
        self.label = Label
        self.PortOpen = False 
                
        SerialPortDevice.__init__(self, baudRate, 'SQUIDControl', pathName, comPort, Label, modConfig)
        
    '''
    '''
    def getResponse(self):
        respStr = self.readLine()
        
        return '', respStr    
    
    '''
    '''
    def readCount(self, activeAxis):
        cmdStr = activeAxis + 'LC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'SC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def readData(self, activeAxis):
        cmdStr = activeAxis + 'LD\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'SD\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def readRange(self, activeAxis):
        cmdStr = activeAxis + 'SSR\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def resetCount(self, activeAxis):
        cmdStr = activeAxis + 'RC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
                
        return cmdStr, '' 

    '''
    '''
    def configure(self, activeAxis):
        time.sleep(0.05)
        cmdStr = activeAxis + 'CR1\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'CLC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'CSE\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'CF1\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'CLP\r'
        self.sendString(cmdStr)
        time.sleep(0.012)        
                
        return cmdStr, '' 
        
    '''
    '''
    def changeRate(self, activeAxis, rate):
        if (rate == 'F'):            
            cmdStr = activeAxis + 'CSE\r'
            self.sendString(cmdStr)
            time.sleep(0.012)
            cmdStr = activeAxis + 'CR1\r'
            self.sendString(cmdStr)
            time.sleep(0.012)

        else:            
            cmdStr = activeAxis + 'CR' + rate + '\r'
            self.sendString(cmdStr)
            time.sleep(0.012)
            
        return cmdStr, ''
    
    '''
    '''
    def setCfg(self, activeAxis, cfg):
        cmdStr = activeAxis + cfg + '\r'
        self.sendString(cmdStr)
            
        return cmdStr, ''
    
    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Public API Functions
                        
    --------------------------------------------------------------------------------------------'''                
    def Disconnect(self):
        self.PortOpen = False
        return
    
    