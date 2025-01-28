'''
Created on Jan 27, 2025

@author: hd.nguyen
'''

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
        