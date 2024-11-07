'''
Created on Nov 6, 2024

@author: hd.nguyen
'''
import time
from Hardware.Device.SerialPortDevice import SerialPortDevice

APS_GET_STATUS = "PSS"
APS_DO_PULSE = "PET"
APS_SET_LEVEL = "PCA "
APS_SET_RANGE_HIGH = "PCRH"
APS_SET_RANGE_LOW = "PCRL"
APS_SET_POLARITY_NEGATIVE = "PCRN"
APS_SET_POLARITY_POSITIVE = "PCRP"
APS_DO_ZERO_DISCHARGE = "ZERO"

APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS = 121
APS_ZERO_DISCHARGE_COMMAND_REPLY_FROM_DEVICE = "Discharged."
APS_DONE_STRING = "Done."

class IrmArmControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label):
        '''
        Constructor
        '''
        self.label = Label
        self.PortOpen = False 
                
        SerialPortDevice.__init__(self, baudRate, 'IrmArmControl', pathName, comPort, Label)
        
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary IRM/ARM Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def SendApsIrmCommand_AndThenWait600msec(self, cmd):
        self.sendString(cmd + '\r')
        
        # Sleep 600 milliseconds after send each command
        time.sleep(0.6)
        
    '''
    '''
    def GetApsIrmResponse(self, timeout_secs=1):
        respStr = ''
        startTime = time.time()
        
        loopFlag = True        
        while loopFlag:
            currentTime = time.time()        
            if ((currentTime - startTime) > timeout_secs):
                errorMessage = 'No response received via Serial Comm from IRM device! '
                errorMessage += 'Comm has timed out after: ' + str(timeout_secs)
                raise ValueError(errorMessage)
            
            respStr = self.readLine() 
            if '\r' in respStr:
                loopFlag = False
                
        return respStr 

    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Control Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def SendZeroCommand_ToApsIRMDevice_AndWaitForReply(self):
        status = False
        
        self.SendApsIrmCommand_AndThenWait600msec(APS_DO_ZERO_DISCHARGE)
        
        my_local_response = self.GetApsIrmResponse(APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
    
        if APS_ZERO_DISCHARGE_COMMAND_REPLY_FROM_DEVICE in my_local_response:
            status = True
        
        return status
    
    '''
    '''
    def SetApsIrmPolarity_FromTargetValue(self, target_value):
        if (target_value < 0):
            self.SendApsIrmCommand_AndThenWait600msec(APS_SET_POLARITY_NEGATIVE)
        else:
            self.SendApsIrmCommand_AndThenWait600msec(APS_SET_POLARITY_POSITIVE)
            
        return
         
    '''
    '''
    def SetApsIrmRange_FromGaussLevel(self, level_in_positive_gaus):
        if (self.ApsIrm_DoRangeChange and 
            (level_in_positive_gaus > self.ApsIrm_RangeChangeLevel)):
            self.SendApsIrmCommand_AndThenWait600msec(APS_SET_RANGE_HIGH)
        else:
            self.SendApsIrmCommand_AndThenWait600msec(APS_SET_RANGE_LOW)
            
    '''
    '''
    def SetApsIrmLevel(self, target_level):
        self.SendApsIrmCommand_AndThenWait600msec(APS_SET_LEVEL + target_level)
        
    '''
    '''
    def executeApsIrmPulse(self):
        self.SendApsIrmCommand_AndThenWait600msec(APS_DO_PULSE)
        
    
        