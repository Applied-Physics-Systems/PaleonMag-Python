'''
Created on Jan 28, 2025

@author: hd.nguyen
'''
import ctypes
import os
import time
from ADwin import ADwin, ADwinError

class ADWinControl():
    '''
    classdocs
    '''    
    __err = ctypes.c_int32(0)
    __errPointer = ctypes.pointer(__err)
    
    adwin_digital_word = 0x00
    filePath = ''
    modConfig = None

    def __init__(self, path, modConfig=None):
        '''
        Constructor
        '''
        self.filePath = path
        self.modConfig = modConfig
        
        try:
            # Establish connection with the ADwin system        
            self.adw = ADwin(DeviceNo=1, raiseExceptions=1)
            if (self.adw.Processor_Type() != 'T9'):
                self.adw.Boot(self.filePath + 'ADwin9.btl')
                print('ADWin system boot')            

        except ADwinError as e:
            self.adw.Boot(self.filePath + 'ADwin9.btl')
            print('ADWin system boot')            

    '''--------------------------------------------------------------------------------------------
                        
                        DLL Functions
                        
    --------------------------------------------------------------------------------------------'''        
    def __checkError(self, functionName):
        if self.__err.value != 0:
            if self.raiseExceptions != 0:
                raise ADwinError(functionName, self.adw.Get_Error_Text(self.__err.value), self.__err.value)

    '''    
    '''
    def Get_Digout(self):
        ret = self.adw.dll.Get_Digout(self.adw.DeviceNo)
        self.__checkError('Get_Digout')
                
        return ret

    '''    
    '''
    def Set_Digout(self, digWord):
        ret = self.adw.dll.Set_Digout(digWord, self.adw.DeviceNo)
        self.__checkError('Set_Digout')
                
        return ret

    '''    
    '''
    def Get_Digin(self):
        ret = self.adw.dll.Get_Digin(self.adw.DeviceNo)
        self.__checkError('Get_Digin')
                
        return ret

    '''    
    '''
    def Set_Digin(self, digWord):
        ret = self.adw.dll.Set_Digin(digWord, self.adw.DeviceNo)
        self.__checkError('Set_Digin')
                
        return ret

    '''    
    '''
    def Get_ADC(self, channel):
        ret = self.adw.dll.Get_ADC(channel, self.adw.DeviceNo)
        self.__checkError('Get_ADC')
                
        return ret

    '''    
    '''
    def Set_DAC(self, channel, value):
        ret = self.adw.dll.Set_DAC(channel, value, self.adw.DeviceNo)
        self.__checkError('Set_DAC')
                
        return ret

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def DoDAQIO(self, channel, numValue=-10000, boolValue=False):
        
        if (channel.ChanType == 'DO'):
            if boolValue:
                self.setDIO(channel.ChanNum)
            else:
                self.clearDIO(channel.ChanNum)
            self.modConfig.processData.ADwinDO = self.adwin_digital_word
            
        elif (channel.ChanType == 'DI'):
            print('TODO')
            
        elif (channel.ChanType == 'AO'):
            print('TODO')

        elif (channel.ChanType == 'AI'):
            print('TODO')
            
        return
        
    '''
    '''
    def setDIO(self, DIO_BIT):
        dioWord = 0x01 << DIO_BIT
        self.adwin_digital_word = self.Get_Digout()
        self.adwin_digital_word = dioWord | self.adwin_digital_word 
        self.Set_Digout(self.adwin_digital_word)
        return
        
    '''
    '''
    def clearDIO(self, DIO_BIT):
        mask = ~(1 << DIO_BIT)
        self.adwin_digital_word = self.Get_Digout()
        self.adwin_digital_word = mask & self.adwin_digital_word 
        self.Set_Digout(self.adwin_digital_word)
                
    '''
    '''
    def setDigOut(self, digOut):
        self.adw.Set_Par(30, digOut)
        
        self.adw.Load_Process(self.filePath + 'SetDigOut_Process.T91')
        self.adw.Start_Process(1)       # start Process 1
        while (self.adw.Get_Par(10) == 0):
            time.sleep(0.01)
        self.adw.Stop_Process(1)        # stops process 2
        
    '''
    '''
    def tryGetADWIN_DigOutStatusByte(self):
        return self.adwin_digital_word
        
    '''
    '''
    def trySetRelays_ADwin_AFsAreUpPosition(self, coilLabel):
        
        if (coilLabel == 'Axial'):
            relay_byte_id = ((2 ^ (self.modConfig.AFAxialRelay.chanNum)) % 256)
        elif (coilLabel == 'Transverse'):
            relay_byte_id = ((2 ^ (self.modConfig.AFTransRelay.chanNum)) % 256)
        elif (coilLabel == 'IRM Axial'):
            relay_byte_id = ((2 ^ (self.modConfig.IRMRelay.ChanNum)) % 256)
        
        status_byte = self.tryGetADWIN_DigOutStatusByte()
        
        # Intermediate State - Prior State + desired Relay set low
        if ((coilLabel == 'Axial') or (coilLabel == 'Transverse')):
            if ((status_byte and relay_byte_id) == relay_byte_id):                
                intermediate_byte = status_byte - relay_byte_id                
            else:            
                intermediate_byte = status_byte
                
            # Final State - Only Desired Relay set high
            final_byte = relay_byte_id
            
        elif ((coilLabel == 'IRM Axial') or (coilLabel == 'IRM Transverse')):
            # intermediate - drop all relays
            intermediate_byte = 0
            
            # Final state - set to desired byte
            final_byte = relay_byte_id
        
        # Set the intermediate relay position
        if (intermediate_byte != final_byte):
            self.setDigOut(intermediate_byte)
            # Wait two seconds, do not allow events
            time.sleep(2)
    
        # Set the final relay position
        self.setDigOut(final_byte)        
        time.sleep(1)
        
        return True
        
    '''
    '''
    def trySetRelays_ADwin_AFsAreDownPosition(self, coilLabel):
        
        all_up_byte = (2 ^ 6) - 1        
        if (coilLabel == 'Axial'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.AFAxialRelay.chanNum)) % 256)
        elif (coilLabel == 'Transverse'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.AFTransRelay.chanNum)) % 256)
        elif (coilLabel == 'IRM Axial'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.IRMRelay.chanNum)) % 256)
        
        # Intermediate State - Prior State + desired Relay set high
        intermediate_byte = all_up_byte
            
        # Final State - Only Desired Relay set high
        final_byte = relay_byte_id
        
        # Set the intermediate relay position
        if (intermediate_byte != final_byte):
            self.setDigOut(intermediate_byte)
    
            # Wait two seconds, do not allow events
            time.sleep(2)
    
        # Set the final relay position
        self.setDigOut(final_byte)
        
        time.sleep(2)
        
        return True 
        
    '''--------------------------------------------------------------------------------------------
                        
                        public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    def trySetRelays_ADwin(self, coilLabel):
        if self.modConfig.AFRelays_UseUpPosition:
            status = self.trySetRelays_ADwin_AFsAreUpPosition(coilLabel)
        else:
            status = self.trySetRelays_ADwin_AFsAreDownPosition(coilLabel)
            
        return status 

    '''--------------------------------------------------------------------------------------------
                        
                        Unit Test Functions
                        
    --------------------------------------------------------------------------------------------'''                  
    '''
    '''
    def runTask(self, taskID):
        # Test set/reset Digital outpur
        if (taskID == 0):
            pin = 2
            self.setDIO(pin)
            time.sleep(2)
            self.clearDIO(pin)

        # Test ADC/DAC
        elif (taskID == 1):
            pin = 1
            value = 50000
            self.Set_DAC(pin, value)
            time.sleep(1)
            value = self.Get_ADC(pin)
            print(value)
                            
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd() + '\\'
        devControl = ADWinControl(currentPath)
        devControl.runTask(1)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
        
        