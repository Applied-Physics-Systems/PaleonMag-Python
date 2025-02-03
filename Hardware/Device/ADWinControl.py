'''
Created on Jan 28, 2025

@author: hd.nguyen
'''
import os
import time
import ADwin

class ADWinControl():
    '''
    classdocs
    '''
    adwin_digital_word = 0x00
    filePath = ''
    modConfig = None

    def __init__(self, path, modConfig=None):
        '''
        Constructor
        '''
        self.filePath = path
        self.modConfig = modConfig
        
        # Establish connection with the ADwin system
        self.adw = ADwin.ADwin(DeviceNo=1, raiseExceptions=1)
        if (self.adw.Processor_Type() != 'T9'):
            self.adw.Boot(self.filePath + 'ADwin9.btl')
            print('ADWin system boot')
        
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
        self.adwin_digital_word = dioWord | self.adwin_digital_word 
        self.adw.Set_Par(30, self.adwin_digital_word)
        
        self.adw.Load_Process(self.filePath + 'SetDigOut_Process.T91')
        self.adw.Start_Process(1)       # start Process 1
        while (self.adw.Get_Par(10) == 0):
            time.sleep(0.01)
        self.adw.Stop_Process(1)        # stops process 2

    '''
    '''
    def clearDIO(self, DIO_BIT):
        mask = ~(1 << DIO_BIT)
        self.adwin_digital_word = mask & self.adwin_digital_word 
        self.adw.Set_Par(30, self.adwin_digital_word)
        
        self.adw.Load_Process(self.filePath + 'SetDigOut_Process.T91')
        self.adw.Start_Process(1)       # start Process 1
        while (self.adw.Get_Par(10) == 0):
            time.sleep(0.01)
        self.adw.Stop_Process(1)        # stops process 2
        
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            self.setDIO(0)

        elif (taskID == 1):
            self.clearDIO(0)
                
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd() + '\\'
        devControl = ADWinControl(currentPath)
        devControl.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
        
        