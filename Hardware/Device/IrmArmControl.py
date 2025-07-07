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


    def __init__(self, baudRate, pathName, comPort, Label, modConfig):
        '''
        Constructor
        '''
        self.label = Label
        self.PortOpen = False 
        self.IRMBackfieldMode = True
                
        SerialPortDevice.__init__(self, baudRate, 'IrmArmControl', pathName, comPort, Label, modConfig)
        
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary IRM/ARM Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def SendApsIrmCommand_AndThenWait600msec(self, cmd):
        self.sendString(cmd + '\r')
        
        # Sleep 600 milliseconds after send each command
        time.sleep(0.6)
        return
        
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
        return
            
    '''
    '''
    def SetApsIrmLevel(self, target_level):
        self.SendApsIrmCommand_AndThenWait600msec(APS_SET_LEVEL + target_level)
        return
        
    '''
    '''
    def executeApsIrmPulse(self):
        self.SendApsIrmCommand_AndThenWait600msec(APS_DO_PULSE)
        return

    '''
    '''
    def FireAPS_AtCalibratedTarget(self, target, parent, queue):
        if (target == 0):
            # Discharging IRM device
            self.SendZeroCommand_ToApsIRMDevice_AndWaitForReply()
            time.sleep(1)
            return
        
        else:
            self.SetApsIrmPolarity_FromTargetValue(target)
            level_in_positive_gauss = int(abs(target))
            self.SetApsIrmRange_FromGaussLevel(level_in_positive_gauss)
            
            # Check if level is in range
            if (level_in_positive_gauss > self.modConfig.PulseAxialMax):
                warningMessage = 'Warning: Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is above the currently set value for the Maximum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMax) + ' ' + self.modConfig.AFUnits
                queue.put(warningMessage)
                return 
            
            elif (level_in_positive_gauss < self.modConfig.PulseAxialMin):
                warningMessage = 'Warning: Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is below the currently set value for the Minimum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMax) + ' ' + self.modConfig.AFUnits
                queue.put(warningMessage)
                return
                
            target_level = str(level_in_positive_gauss)
            
            # Catch Flow Pause or Flow Halt
            if (parent.checkProgramHaltRequest()):
                return

            # Set IRM Field Level
            self.SetApsIrmLevel(target_level)

            # Catch Flow Pause or Flow Halt
            if (parent.checkProgramHaltRequest()):
                return

            # Tell APS IRM to execute pulse
            self.executeApsIrmPulse()
            
            # Wait for Done signal
            while True:
                my_local_response = self.GetApsIrmResponse(self.APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                if  self.APS_DONE_STRING in my_local_response:
                    return
                
                # Catch Flow Pause or Flow Halt
                if (self.checkProgramHaltRequest()):
                    return
                
                # Send warning message
                warningMessage = 'Warning: Over ' + str(self.APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                warningMessage += ' seconds have elapsed since the IRM Fire Command was sent '
                warningMessage += 'for an IRM Pulse at ' + target_level + ' ' + self.modConfig.AFUnits + ' and '
                warningMessage += ' no ' + self.APS_DONE_STRING + ' response has been received from the APS IRM Device.'
                queue.put(warningMessage)
                time.sleep(1)                            

    '''
        If the user has set that the IRM trim is wired such that it is
        turned on by passing a
        logic high state to the DAQ comm board IRM Trim DO channel, then
        return the TrimOn input variable as it is
        However, if the user has set that the IRM Trim is turned on by
        passing a logic low state to the IRM Trim channel, then need to
        return the logical oposite of TrimOn
    '''
    def TrimOnOff(self, TrimOn):
        status = True
        
        if self.modConfig.TrimOnTrue: 
            status = TrimOn
        
        if not self.modConfig.TrimOnTrue: 
            status = not TrimOn
        
        return status 

    '''
    '''
    def SetIRMBackFieldMode(self, enabling):
        if not self.modConfig.EnableIRMBackfield: 
            enabling = False
            
        if enabling:
            self.IRMBackfieldMode = True
        else:
            self.IRMBackfieldMode = False
        
        return

    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Public API Functions
                        
    --------------------------------------------------------------------------------------------'''                
    '''
    '''
    def init_IrmArm(self, ADwin):
        ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=0)
        
        ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=0)
        
        ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(True))
        
        ADwin.DoDAQIO(self.modConfig.IRMFire, boolValue=True)
        
        # Wait a half second
        time.sleep(0.5)
        
        ADwin.DoDAQIO(self.modConfig.ARMSet, boolValue=True)
        
        self.SetIRMBackFieldMode(False)

        return
    
    '''
    '''
    def FireIRM(self, voltage, parent, queue, CalibrationMode=False):
        if 'ASC' in self.modConfig.IRMSystem:
            print('TODO: Implement FireASC_IrmAtPulseVolts voltage, CalibrationMode')
        else:
            self.FireAPS_AtCalibratedTarget(voltage, parent, queue)

        return

    
        