'''
Created on Jan 27, 2025

@author: hd.nguyen
'''
import os
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice

class VacuumControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label, modConfig=None):
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
    def DegausserCooler(self, ADwin, switch):
        # If vacuum module not enabled, exit sub
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if switch:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, True)
        else:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, False)
        
        return
                    
    '''--------------------------------------------------------------------------------------------
                        
                        Vacuum Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def valveConnect(self, ADwin, switch):
        if not self.modConfig.EnableVacuum:
            return

        if switch:
            cmdStr, respStr = self.setValveConnect()
            ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=True)
        else:
            cmdStr, respStr = self.clearValveConnect()
            ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=False)
            
        return cmdStr, respStr
        
    '''
    '''
    def motorPower(self, ADwin, switch):
        if not self.modConfig.EnableVacuum:
            return
        
        if switch:
            cmdStr, respStr = self.setVacuumOn()
            ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=True)
        else:
            cmdStr, respStr = self.setVacuumOff()
            ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=False)
        
        return cmdStr, respStr
        
    '''
    '''
    def degausserCooler(self, ADwin, mode):
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if 'On' in mode:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=True)
        else:
            ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=False)
        
        return
   
    '''
    '''
    def init(self, ADwin):
        self.reset()
        self.valveConnect(ADwin, False)
        self.motorPower(ADwin, False)
        self.DegausserCooler(ADwin, False)
        
        time.sleep(0.2)
        
        self.valveConnect(ADwin, False)
        cmdStr, respStr = self.motorPower(ADwin, False)
        self.DegausserCooler(ADwin, False)
        
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

'''
'''    
if __name__=='__main__':
    try:    
        pathName = os.getcwd() + '\\'
        vacuumControl = VacuumControl(9600, pathName, 'COM11', 'vacuum')
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
