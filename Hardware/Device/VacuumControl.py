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
    def DegausserCooler(self, switch, ADwin):
        # If vacuum module not enabled, exit sub
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if switch:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, True)
        else:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, False)
        
        return
        
    '''
    '''
    def MotorPower(self, switch, ADwin):
        # If vacuum module not enabled, exit sub
        if not self.modConfig.EnableVacuum:
            return
            
        if switch:
            cmdStr = "E\r"
            self.sendString(cmdStr)
            cmdStr = "10MFF\r"
            self.sendString(cmdStr)
            
            respStr = self.readLine()
            
            ADwin.DoDAQIO(self.modConfig.MotorToggle, True)
            
        else:
            cmdStr = "D\r"
            self.sendString(cmdStr)
            cmdStr = "10M00\r"
            self.sendString(cmdStr)
            
            respStr = self.readLine()
            
            ADwin.DoDAQIO(self.modConfig.MotorToggle, False)
            
        return cmdStr, respStr
    
    '''
    '''
    def valveConnect(self, switch, ADwin):
        # Check for whether the vacuum module is enabled
        if not self.modConfig.EnableVacuum:
            return
        
        if switch:
            cmdStr = "O\r"
            self.sendString(cmdStr)
            cmdStr = "10VFF\r"
            self.sendString(cmdStr)
            
            respStr = self.readLine()
            
            ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=True)
            
        else:
            cmdStr = "C\r"
            self.sendString(cmdStr)
            cmdStr = "10V00\r"
            self.sendString(cmdStr)
            
            respStr = self.readLine()
            
            ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=False)
        
        return cmdStr, respStr
        
    '''--------------------------------------------------------------------------------------------
                        
                        Vacuum Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def init(self, ADwin):
        self.reset()
        self.valveConnect(False, ADwin)
        self.MotorPower(False, ADwin)
        self.DegausserCooler(False, ADwin)
        
        time.sleep(0.2)
        
        self.valveConnect(False, ADwin)
        cmdStr, respStr = self.MotorPower(False, ADwin)
        self.DegausserCooler(False, ADwin)
        
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

    '''
    '''
    def Disconnect(self):
        if self.PortOpen:
            self.PortOpen = False
        return
