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


    def __init__(self, baudRate, pathName, comPort, Label, parent=None):
        '''
        Constructor
        '''        
        self.label = Label
        self.PortOpen = False
        self.parent = parent
                
        self.VacuumMotorOn = False
        self.VacuumMotorOff = True
        self.MotorPowered = False
                
        SerialPortDevice.__init__(self, baudRate, 'VacuumControl', pathName, comPort, Label, self.parent.modConfig)
        
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
        
        self.VacuumMotorOn = True
        self.MotorPowered = True
        
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
        
        self.VacuumMotorOff = True
        self.MotorPowered = False
        
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
    def ValveConnect(self, mode):
        if not self.parent.modConfig.EnableVacuum:
            return
        
        if mode:
            self.setValveConnect()
            '''
                now the digital lines
                (July 2010 - I Hilburn) Replaces old frmMCC with frmDAQ_Comm using the Channel object variables
            '''            
            self.parent.ADwin.DoDAQIO(self.parent.modConfig.VacuumToggleA, True)
        else:
            self.clearValveConnect()
            '''
                now the digital lines
                (July 2010 - I Hilburn) Replaces old frmMCC with frmDAQ_Comm using the Channel object variables
            '''            
            self.parent.ADwin.DoDAQIO(self.parent.modConfig.VacuumToggleA, True)
            
        return
        
    '''
    '''
    def DegausserCooler(self, switch):
        # If vacuum module not enabled, exit sub
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if switch:
            self.parent.ADwin.DoDAQIO(self.modConfig.DegausserToggle, True)
        else:
            self.parent.ADwin.DoDAQIO(self.modConfig.DegausserToggle, False)
        
        return
                    
    '''--------------------------------------------------------------------------------------------
                        
                        Vacuum Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def valveConnect(self, switch):
        if not self.modConfig.EnableVacuum:
            return

        if switch:
            cmdStr, respStr = self.setValveConnect()
            self.parent.ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=True)
        else:
            cmdStr, respStr = self.clearValveConnect()
            self.parent.ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=False)
            
        return cmdStr, respStr
        
    '''
    '''
    def MotorPower(self, switch):
        if not self.modConfig.EnableVacuum:
            return
        
        if switch:
            cmdStr, respStr = self.setVacuumOn()
            self.parent.ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=True)
        else:
            cmdStr, respStr = self.setVacuumOff()
            self.parent.ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=False)
        
        return cmdStr, respStr
        
    '''
    '''
    def degausserCooler(self, mode):
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if 'On' in mode:
            self.parent.ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=True)
        else:
            self.parent.ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=False)
        
        return
   
    '''
    '''
    def init(self):
        self.reset()
        self.valveConnect(False)
        self.MotorPower(False)
        self.DegausserCooler(False)
        
        time.sleep(0.2)
        
        self.valveConnect(False)
        cmdStr, respStr = self.MotorPower(False)
        self.DegausserCooler(False)
        
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
