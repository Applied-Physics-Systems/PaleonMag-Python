'''
Created on Nov 6, 2024

@author: hd.nguyen
'''
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice
from Process.IRMData import IRMData

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
        self.CurrentBiasField = 0   
        self.CoilsLocked = False     
        self.coilLabel = 'Axial'
        self.parent = None
        self.queue = None
        self.IRMInterrupt = False
                
        SerialPortDevice.__init__(self, baudRate, 'IrmArmControl', pathName, comPort, Label, modConfig)

    '''--------------------------------------------------------------------------------------------
                        
                        Calibration Mode Display Functions
                        
    --------------------------------------------------------------------------------------------'''
    def CalMode_setDirection(self):
        print('TODO: frmIRM_VoltageCalibration.setDirection')
        # Set the directions label in the picture box
        #TODO    frmIRM_VoltageCalibration.lblDirections.Caption = "Waiting for IRM capacitor to charge"
        
        # Hide the text-box and highlighting
        #TODO    frmIRM_VoltageCalibration.txtCapacitorVoltage.Visible = False
        #TODO    frmIRM_VoltageCalibration.picHighlight.Visible = False
        
        # Hide the accept and redo buttons
        #TODO    frmIRM_VoltageCalibration.cmdAccept.Visible = False
        #TODO    frmIRM_VoltageCalibration.cmdRedo.Visible = False
        
        # Show the picture box
        #TODO    frmIRM_VoltageCalibration.picGetCapacitorVoltage.Visible = True
        
        return
    
    '''
    '''
    def CalMode_setCalibrationTable(self):
        print('TODO: frmIRM_VoltageCalibration.setCalibrationTable')
        #TODO    With frmIRM_VoltageCalibration.gridVoltageCal
        
            #TODO    .row = frmIRM_VoltageCalibration.CurrentRow
            
            # Store the Output DAQ Voltage to the IRM capacitor box
            #TODO    .Col = 2
            #TODO    .text = Format(pulse_volts, "#0.0#####")
                        
            # Store the Return Voltage from the IRM capacitor box
            #TODO    .Col = 3
            #TODO    .text = Format(readVoltage * modConfig.PulseReturnMCCVoltConversion, "#0.0#####")
    
            # Resize the 2nd and 3rd columns of the grid
            #TODO    ResizeGrid frmIRM_VoltageCalibration.gridVoltageCal, _
            #TODO      frmIRM_VoltageCalibration, , , _
            #TODO    2, _
            #TODO    3
                           
        #TODO    End With
    
        # Update picture box and tell user to write in the Calibration display voltage
        #TODO    frmIRM_VoltageCalibration.lblDirections = "Write in the highest reached IRM capacitor box voltage."
        #TODO    frmIRM_VoltageCalibration.txtCapacitorVoltage.Visible = True
        #TODO    frmIRM_VoltageCalibration.picHighlight.BackColor = QBColor(4)
        #TODO    frmIRM_VoltageCalibration.picHighlight.Visible = True
        
        return
    
    '''
    '''
    def CalMode_updateDirectionDisplay(self):
        print('TODO: frmIRM_VoltageCalibration.updateDirectionDisplay')
        # Format the time remaining
        # TODO    TimeRemaining = Trim(str(CLng((ChargeTime - ElapsedTime) / 1000)))

        # TODO    TimeRemaining = PadLeft(TimeRemaining, 3)

        # Update the picture box
        # TODO    frmIRM_VoltageCalibration.lblDirections.Caption = _
            # TODO     "Waiting for IRM Capacitor to charge." & vbNewLine & _
            # TODO     "Prepare to read IRM Box pulse_volts display in: " & _
            # TODO     TimeRemaining & " sec."

        # TODO    If CLng(ChargeTime - ElapsedTime) < 3000 Then

            # Show the text-box with a pink highlight
            # TODO    frmIRM_VoltageCalibration.txtCapacitorVoltage.Visible = True

            # TODO    frmIRM_VoltageCalibration.picHighlight.BackColor = QBColor(13)
            # TODO    frmIRM_VoltageCalibration.picHighlight.Visible = True
        
        return
            
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary IRM/ARM Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def closeDevice(self):
        self.frmIRM_VoltageCalibration = None        
        SerialPortDevice.closeDevice(self)        
        return
    
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

    '''
        Specific function for interpolating the Volts vs Field value table for the
        IRM low-field pulse to convert field values to pulse voltage values
    '''
    def ConvertGaussToPulseAxialVolts(self, field):
        # If the field is less than zero, than invert it's sign
        if (field < 0):
            field = -1 * field
        
        # Coerce the field value in range with the max and min field values
        if (field < self.modConfig.PulseAxialMin): 
            field = self.modConfig.PulseAxialMin
        if (field > self.modConfig.PulseAxialMax):
            field = self.modConfig.PulseAxialMax
        
        # Set the function return = -1
        outVolts = -1
        
        # Get the Number of elements in the field calibration table
        if (self.modConfig.PulseAxial.size == 0):
            return outVolts
        
        N = self.modConfig.PulseAxial.shape[0]
        
        # Loop through the table, ignoring the field (zero) entry
        # and find the pulse voltage that matches the inputed field value
        for i in range(1, N):            
            if (self.modConfig.PulseAxial[i, 1] == field):            
                outVolts = self.modConfig.PulseAxial[i, 0]
                return outVolts 
                
            elif ((self.modConfig.PulseAxial[i - 1, 1] < field) and (self.modConfig.PulseAxial[i, 1] > field)):            
                # Calculate the local slope (Voltage / Field)
                Slope = (self.modConfig.PulseAxial[i, 0] - self.modConfig.PulseAxial[i - 1, 0]) / \
                        (self.modConfig.PulseAxial[i, 1] - self.modConfig.PulseAxial[i - 1, 1])
                
                # Use X = Y(0) + Slope * Y to calculate the matching voltage value
                outVolts = self.modConfig.PulseAxial[i - 1, 0] + Slope * (field - self.modConfig.PulseAxial[i - 1, 1])
                break                
                
            elif (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 1] < field):            
                # Need to extrapolate out slope
                # Calculate the local slope (Voltage / Field)
                Slope = (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 0] - \
                         self.modConfig.PulseAxial[self.modConfig.PulseAxialCount - 1, 0]) / \
                        (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 1] - \
                         self.modConfig.PulseAxial[self.modConfig.PulseAxialCount - 1, 1])
                
                outVolts = self.modConfig.PulseAxial(self.modConfig.PulseAxialCount, 0) + \
                            Slope * (field - self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 1])
                break
                                    
        return outVolts

    '''
    '''
    def ConvertGaussToPulseTransVolts(self, field):
        # If the field is less than zero, than invert it's sign
        if (field < 0):
            field = -1 * field
        
        # Coerce the field value in range with the max and min field values
        if (field < self.modConfig.PulseTransMin):
            field = self.modConfig.PulseTransMin
        if (field > self.modConfig.PulseTransMax):
            field = self.modConfig.PulseTransMax
        
        # Set the function return = -1
        outVolts = -1
        
        # Get the Number of elements in the field calibration table
        if (self.modConfig.PulseTrans.size == 0):
            return outVolts
        
        N = self.modConfig.PulseTrans.shape(0)
        
        # Loop through the table, ignoring the field (zero) entry
        # and find the pulse voltage that matches the inputed field value
        for i in range(2, N):            
            if (self.modConfig.PulseTrans[i, 1] == field):            
                outVolts = self.modConfig.PulseTrans[i, 0]
                break 
                
            elif ((self.modConfig.PulseTrans[i - 1, 1] < field) and (self.modConfig.PulseTrans[i, 1] > field)):            
                # Calculate the local slope (Voltage / Field)
                Slope = (self.modConfig.PulseTrans[i, 0] - self.modConfig.PulseTrans[i - 1, 0]) / \
                        (self.modConfig.PulseTrans[i, 1] - self.modConfig.PulseTrans[i - 1, 1])
                
                # Use X = Y(0) + Slope * Y to calculate the matching voltage value
                outVolts = self.modConfig.PulseTrans[i - 1, 0] + Slope * (field - self.modConfig.PulseTrans[i - 1, 1])
                break
                
            elif (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 1] < field):            
                # Need to extrapolate out slope
                # Calculate the local slope (Voltage / Field)
                Slope = (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 0] - \
                         self.modConfig.PulseTrans[self.modConfig.PulseTransCount - 1, 0]) / \
                        (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 1] - \
                         self.modConfig.PulseTrans[self.modConfig.PulseTransCount - 1, 1])
                
                outVolts = self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 0] + \
                           Slope * (field - self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 1])
                break
                                
        return outVolts

    '''
        Convert a field value in gauss to a low or high field IRM Pulse
        using the IRM field calibration table
    '''
    def ConvertGaussToPulseVolts(self, field):
        # If the field is negative, flip the sign on it
        if (field < 0):
            field = -1 * field
    
        if (self.coilLabel == 'Axial'):        
            outVolts = self.ConvertGaussToPulseAxialVolts(field)            
        else:
            outVolts = self.ConvertGaussToPulseTransVolts(field)                    
            
        return outVolts

    '''
    '''
    def ConvertPulseVoltsToMCCVolts(self, Volts):
        outVolts = Volts * self.modConfig.PulseMCCVoltConversion
        
        return outVolts
    
    '''
        Specific function for interpolating the Volts vs Field value table for the
        IRM low-field pulse to convert pulse volts to field values
    '''
    def ConvertPulseAxialVoltsToGauss(self, Volts):
        # ConvertPulseAxialVoltsToGauss = PulseAxialY + PulseAxialSlope * VOLTS
        outGauss = 0
        
        if (Volts < 0):
            Volts = -1 * Volts
        
        if (Volts == 0):        
            return outGauss
                        
        # Get the number of calibration values in the IRM low-field pulse
        # calibration table
        N = self.modConfig.PulseAxial.shape[0]
        
        # Loop through the values in the IRM Low-field pulse calibration table
        # and interpolate matching field value for inputed pulse voltage
        for i in range(1, N):        
            if (self.modConfig.PulseAxial[i, 0] == Volts):            
                outGauss = self.modConfig.PulseAxial[i, 1]
                return outGauss 
                
            elif ((self.modConfig.PulseAxial[i - 1, 0] < Volts) and (self.modConfig.PulseAxial[i, 0] > Volts)):            
                # Calculate local slope of the IRM low-field calibration table
                # (Field / Voltage)
                Slope = (self.modConfig.PulseAxial[i, 1] - self.modConfig.PulseAxial[i - 1, 1]) / \
                        (self.modConfig.PulseAxial[i, 0] - self.modConfig.PulseAxial[i - 1, 0])
                
                # Use Y = X(0) + Slope * X to get the field value
                # Where Y = field value, and X = pulse value
                outGauss = self.modConfig.PulseAxial[i - 1, 1] + Slope * (Volts - self.modConfig.PulseAxial[i - 1, 0])
                break
                
            elif (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 0] < Volts):            
                # Calculate local slope of the IRM low-field calibration table
                # (Field / Voltage)
                Slope = (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 1] - \
                         self.modConfig.PulseAxial[self.modConfig.PulseAxialCount - 1, 1]) / \
                        (self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 0] - \
                         self.modConfig.PulseAxial[self.modConfig.PulseAxialCount - 1, 0])
                
                # Extrapolate past voltage in (i,0)
                outGauss = self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 1] + \
                           Slope * (Volts - self.modConfig.PulseAxial[self.modConfig.PulseAxialCount, 0])
                break
                        
        return outGauss
    
    '''
    '''
    def ConvertPulseTransVoltsToGauss(self, Volts):
        # ConvertPulseTransVoltsToGauss = PulseTransY + PulseTransSlope * VOLTS
        outGauss = 0
        
        if (Volts < 0):
            Volts = -1 * Volts
        
        # Get the number of calibration values in the IRM high-field pulse
        # calibration table
        N = self.modConfig.PulseTrans.shape(0)
        
        # Loop through the values in the IRM high-field pulse calibration table
        # and interpolate matching field value for inputed pulse voltage
        for i in range(1, N):        
            if (self.modConfig.PulseTrans[i, 0] == Volts):            
                outGauss = self.modConfig.PulseTrans[i, 1]
                return outGauss
                
            elif ((self.modConfig.PulseTrans[i - 1, 0] < Volts) and (self.modConfig.PulseTrans[i, 0] > Volts)):            
                # Calculate local slope of the IRM low-field calibration table
                # (Field / Voltage)
                Slope = (self.modConfig.PulseTrans[i, 1] - self.modConfig.PulseTrans[i - 1, 1]) / \
                        (self.modConfig.PulseTrans[i, 0] - self.modConfig.PulseTrans[i - 1, 0])
                
                # Use Y = X(0) + Slope * X to get the field value
                # Where Y = field value, and X = pulse value
                outGauss = self.modConfig.PulseTrans[i - 1, 0] + Slope * (Volts - self.modConfig.PulseTrans[i - 1, 0])
                break
                
            elif (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 0] < Volts):            
                # Calculate local slope of the IRM low-field calibration table
                # (Field / Voltage)
                Slope = (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 1] - \
                         self.modConfig.PulseTrans[self.modConfig.PulseTransCount - 1, 1]) / \
                        (self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 0] - \
                         self.modConfig.PulseTrans[self.modConfig.PulseTransCount - 1, 0])
                
                # Extrapolate past voltage in (i,0)
                outGauss = self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 1] + \
                           Slope * (Volts - self.modConfig.PulseTrans[self.modConfig.PulseTransCount, 0])
                break
            
        return outGauss
    
    '''
        Convert a IRM axial or transverse pulse voltage to a field value in gauss
        using the IRM field calibration table
    '''
    def ConvertPulseVoltsToGauss(self, Volts):
        if (self.coilLabel == 'Axial'):
            outGauss = self.ConvertPulseAxialVoltsToGauss(Volts)
        else:
            outGauss = self.ConvertPulseTransVoltsToGauss(Volts)
            
        return outGauss
    
    '''
    '''
    def GetCoilTemperatures(self):
        
        txtTemp = ''
        Temp1 = 0.0
        Temp2 = 0.0
        
        if self.modConfig.EnableT1:             
            Temp1 = self.parent.ADwin.DoDAQIO(self.modConfig.AnalogT1)                 
            Temp1 = Temp1 * self.modConfig.TSlope - self.modConfig.Toffset
            txtTemp = ':Temp1 = ' + "{:.2f}".format(Temp1)
             
        if self.modConfig.EnableT2:             
            Temp2 = self.parent.ADwin.DoDAQIO(self.modConfig.AnalogT2)                 
            Temp2 = Temp2 * self.modConfig.TSlope - self.modConfig.Toffset
            txtTemp = ':Temp2 = ' + "{:.2f}".format(Temp2)
            
        if (txtTemp != ''):
            self.queue.put('IRMControl' + txtTemp)
         
        # Check Temperature to see if it is not zeroed (gone within 20 deg of -1 * Toffset)
        if not self.parent.ADwin.ValidSensorTemp(Temp1, Temp2):             
            # Start code to tell user that the temp sensor values are bad
            self.NotifySensorError(Temp1, Temp2)
        
        return Temp1, Temp2

    '''
        Function changes the AF/IRM relays depending on the IRM system
        that the user inputs and returns a success status
        True = new coil set successfully
        False = failure to set new coil or NoIRMCoilSystem passed
        in as the IRM system set value    
    '''
    def SetRelaysForIRM(self):
        status = False
        
        # Check to see what AF System is in place
        if "2G" in self.modConfig.AFSystem:
            print('TODO: SetRelaysForIRM for 2G')
                    
        elif "ADWIN" in self.modConfig.AFSystem:        
            # Need to figure out which Relays need to be set
            # First, see if this is a backfield or normal IRM            
            if (self.modConfig.EnableIRMBackfield and self.IRMBackfieldMode):                
                self.CoilsLocked = False
                status = self.parent.ADwin.TrySetRelays_ADwin('IRM Axial', self.IRMBackfieldMode)
                self.CoilsLocked = True
                
            elif ((not self.IRMBackfieldMode) and self.modConfig.EnableAxialIRM):                                
                self.CoilsLocked = False
                status = self.parent.ADwin.TrySetRelays_ADwin('IRM Axial', self.IRMBackfieldMode)
                self.CoilsLocked = True
                
            else:            
                status = False
                            
        else:        
            status = False
            
        
        return status
    
    '''
    '''
    def IRMCapacitorVoltage(self):
        outVoltage = 1.0 * self.parent.ADwin.DoDAQIO(self.modConfig.IRMCapacitorVoltageIn)
        
        if (outVoltage < 0):
            outVoltage = 0.0
                        
        return outVoltage

    '''
    '''
    def IRMAverageVoltageIn(self, Times=5):
        Sum = 0
        for _ in range(0, Times):
            working = self.IRMCapacitorVoltage()
            Sum += working
        
        outVoltage = Sum / Times / self.modConfig.PulseReturnMCCVoltConversion        
        self.queue.put('IRMControl:Read Voltage = ' + "{:.1f}".format(outVoltage))
        
        return outVoltage
    
    '''
    '''
    def CalculateAscBoostMultiplier(self, target_capacitor_voltage):
        outMult = 1
        
        if (self.modConfig.IRMAxialVoltMax <= 0):
            return outMult
        
        ratio_to_max = target_capacitor_voltage / self.modConfig.IRMAxialVoltMax
        
        if (self.modConfig.AscSetVoltageMaxBoostMultiplier <= \
            self.modConfig.AscSetVoltageMinBoostMultiplier):           
            outMult = round(self.modConfig.AscSetVoltageMinBoostMultiplier - \
                      (ratio_to_max) * (self.modConfig.AscSetVoltageMinBoostMultiplier - \
                      self.modConfig.AscSetVoltageMaxBoostMultiplier), 2)
                                                          
        else:        
            outMult = round(self.modConfig.AscSetVoltageMinBoostMultiplier + \
                      (ratio_to_max) * (self.modConfig.AscSetVoltageMaxBoostMultiplier - \
                      self.modConfig.AscSetVoltageMinBoostMultiplier), 2)
    
        return outMult
    
    '''
    '''
    def ConvertMCCVoltsToPulseVolts(self, Volts):
        return (Volts/self.modConfig.PulseReturnMCCVoltConversion)

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
        if (self.modConfig.ApsIrm_DoRangeChange and \
            (level_in_positive_gaus > self.modConfig.ApsIrm_RangeChangeLevel)):
            
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
    def FireAPS_AtCalibratedTarget(self, target):
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
                warningMessage = 'Warning:Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is above the currently set value for the Maximum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMax) + ' ' + self.modConfig.AFUnits + ')'
                self.queue.put(warningMessage)
                return 
            
            elif (level_in_positive_gauss < self.modConfig.PulseAxialMin):
                warningMessage = 'Warning:Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is below the currently set value for the Minimum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMin) + ' ' + self.modConfig.AFUnits + ')'
                self.queue.put(warningMessage)
                return
                
            target_level = str(level_in_positive_gauss)
            
            # Catch Flow Pause or Flow Halt
            self.parent.checkProgramHaltRequest()

            # Set IRM Field Level
            self.SetApsIrmLevel(target_level)

            # Catch Flow Pause or Flow Halt
            self.parent.checkProgramHaltRequest()

            # Tell APS IRM to execute pulse
            self.executeApsIrmPulse()
            
            # Wait for Done signal
            while True:
                my_local_response = self.GetApsIrmResponse(APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                if  APS_DONE_STRING in my_local_response:
                    return
                
                # Catch Flow Pause or Flow Halt
                self.parent.checkProgramHaltRequest()
                
                # Send warning message
                warningMessage = 'Warning: Over ' + str(APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                warningMessage += ' seconds have elapsed since the IRM Fire Command was sent '
                warningMessage += 'for an IRM Pulse at ' + target_level + ' ' + self.modConfig.AFUnits + ' and '
                warningMessage += ' no ' + APS_DONE_STRING + ' response has been received from the APS IRM Device.'
                self.queue.put(warningMessage)
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
            self.queue.put('IRMControl:Back Field Mode = True')
        else:
            self.IRMBackfieldMode = False
            self.queue.put('IRMControl:Back Field Mode = False')
        
        return
    
    '''
    '''
    def NotifySensorError(self, Temp1, Temp2):
                
        # Create Error message
        ErrorMessage = "Warning:AF Temperature sensors reading temperature below minimum limit.\n"
        ErrorMessage += "Sensor #1 Temp = " + "{:.2f}".format(Temp1) + " " + self.modConfig.Tunits + "\n"
        ErrorMessage += "Sensor #2 Temp = " + "{:.2f}".format(Temp2) + " " + self.modConfig.Tunits + "\n"
        ErrorMessage += "Execution has been paused. Please come in and check the temperature\n" 
        ErrorMessage += "sensor box.  The two 9V batteries may need to be replaced, or the switch may need to be turned on."
        
        self.queue.put(ErrorMessage)
        
        return
    
    '''
    '''
    def AtEndOfTrimCycle(self, irm_pulse_data):
        status = False
            
        # Compare the average change over the past window to the average change over the entire ramp.
        if ((irm_pulse_data.average_change_over_window != 0) and \
           (irm_pulse_data.average_change_entire_charging_cycle != 0)):           
            change_ratio = abs(irm_pulse_data.average_change_over_window / irm_pulse_data.average_change_entire_charging_cycle)      
            
            # Stop on trim rate slowing     
            if ((change_ratio * 100) < self.stop_trimming_change_threshold_in_percent):           
                status = True
                           
            # Stop on no trim happening at all
            if ((abs(1 - change_ratio) * 100) < self.stop_trimming_change_threshold_in_percent):
                status = True
                   
        return status

    '''
    '''
    def chargeIRM(self, StartTime, TargetVoltage, DaqControlVoltage, CalibrationMode):
        # Turn off trim / voltage bleed
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(False))        
        self.queue.put("IRMControl:IRM Status = Charging")            
        # Update Program status Bar
        self.queue.put("Program Status:Charging...   0%")
                
        # Wait only 0.1 seconds
        time.sleep(0.1)
                                        
        still_charging = True                
        irm_pulse_data = IRMData()
        while still_charging:                    
            # Get the current IRM charge set pulse_volts
            readVoltage = self.IRMAverageVoltageIn()
              
            if (readVoltage >= TargetVoltage):
                controlVoltage = DaqControlVoltage * \
                                (self.modConfig.PulseReturnMCCVoltConversion / \
                                 self.modConfig.PulseMCCVoltConversion)
                self.parent.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=controlVoltage)
                break
                                  
            # Store pulse_volts and time
            irm_pulse_data.Add((time.time() - StartTime), readVoltage)
              
            if self.AtEndOfChargeCycle(irm_pulse_data):
                break
            
            PercentDone = "{:.1f}".format(100 * readVoltage / TargetVoltage)
            PercentDone += " %"
                        
            # Update the status display on the IRM form
            lblIRMStatus = "Charging... " + "{:.2f}".format(PercentDone)
            
            # Update Program form
            self.queue.put("Program Status:" + lblIRMStatus)
                                                            
            # Read in the poweramp pulse_volts
            txtMCCIRMPowerAmpVoltageIn = ":Read Voltage = {:.2f}".format(readVoltage)
            self.queue.put("IRMControl:IRM Status = " + lblIRMStatus + txtMCCIRMPowerAmpVoltageIn)

            # If this IRM pulse is being run in calibration mode,
            # need to update the directions caption on frmIRM_VoltageCalibration
            if CalibrationMode:
                self.CalMode_updateDirectionDisplay()
            
            # Same for either system
            self.IRMInterrupt = self.parent.checkInterruptRequest()
            if self.IRMInterrupt:                
                self.IRMInterrupt = False
                
                # Update program status bar
                self.queue.put("Program Status:Charging... Interrupted!")
                self.queue.put("IRMControl:IRM Status = Charge Interrupted")
                
                # Pause 2 seconds
                time.sleep(2)
                
                # Wipe the status bars clean
                self.queue.put("Program Status:")
                
                    
        # Update program status bar
        self.queue.put("Program Status:Charging... Done!")
        return True
    
    '''
    '''
    def dischargeIRM(self, StartTime):
        still_trimming = True
        
        # Turn on trim / voltage bleed
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(True))
        self.queue.put("IRMControl:IRM Trim = On")
    
        # Loop until capacitor voltage is less than 3 V
        irm_pulse_data = IRMData()
        while still_trimming:            
            readVoltage = self.IRMAverageVoltageIn()
            
            if (self.modConfig.AscIrmMaxFireAtZeroGaussReadVoltage <= 0):
                self.modConfig.AscIrmMaxFireAtZeroGaussReadVoltage = 3
                
            if (readVoltage <= self.modConfig.AscIrmMaxFireAtZeroGaussReadVoltage):
                break
            
            # Store pulse_volts and time
            irm_pulse_data.Add((time.time() - StartTime), readVoltage)
              
            if self.AtEndOfTrimCycle(irm_pulse_data):
                break
            
            if (readVoltage == 0):
                PercentDone = "100.00"
            else:
                PercentDone = "{:.1f}".format(100 * abs(readVoltage - self.modConfig.AscIrmMaxFireAtZeroGaussReadVoltage) / readVoltage)
            PercentDone += " %"
            # Update the status display on the IRM form
            lblIRMStatus = "Trimming... " + PercentDone
            
            # Update Program form
            self.queue.put("Program Status:" + lblIRMStatus)
                                                            
            # Read in the poweramp pulse_volts
            txtMCCIRMPowerAmpVoltageIn = ":Read Voltage = {:.2f}".format(readVoltage)
            self.queue.put("IRMControl:IRM Status = " + lblIRMStatus + txtMCCIRMPowerAmpVoltageIn)
            
            # Same for either system
            self.IRMInterrupt = self.parent.checkInterruptRequest()
            if self.IRMInterrupt:                
                self.IRMInterrupt = False
                                                                               
                # Update program status bar
                self.queue.put("Program Status:Trimming... Interrupted!")
                self.queue.put("IRMControl:IRM Status = Trim Interrupted")
                
                # Pause 2 seconds
                time.sleep(2)
                
                # Wipe the status bars clean
                self.queue.put("Program Status:")
                        
            # Pause 50 ms
            time.sleep(0.05)
                                
        # We're ready to fire the IRM coils at charge voltage = 0
        # Turn off trim / voltage bleed
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(False))
        self.queue.put("IRMControl:IRM Trim = Off")
        
        return True

    '''
    '''
    def FireASC_IrmAtPulseVolts(self, pulse_volts, CalibrationMode):
        
        if (pulse_volts > 0):                 
            # Before doing anything with the ADWIN board, get the AF coil temperatures
            Temp1, Temp2 = self.GetCoilTemperatures()
                              
            if (self.modConfig.EnableT1 or self.modConfig.EnableT2):
                 
                while ((Temp1 >= self.modConfig.Thot) or (Temp2 >= self.modConfig.Thot)):                     
                    self.queue.put('IRMControl:Temp Hot')
                     
                    # Loop until the temperature which was above Thot decreases at least 5 degrees before restarting
                    while ((Temp1 >= (self.modConfig.Thot - 5)) or (Temp2 >= (self.modConfig.Thot - 5))):                         
                        time.sleep(1)
                        Temp1, Temp2 = self.GetCoilTemperatures()
             
            self.queue.put('IRMControl:Temp Normal')
            
        self.parent.checkProgramHaltRequest()            
                    
        # First, lock the Coil selection
        self.CoilsLocked = True
        self.queue.put('IRMControl:Coil locked = True')
        
        if ((not self.modConfig.EnableAxialIRM) and (not self.modConfig.EnableTransIRM)):
            return
        
        self.IRMInterrupt = False
                
        # Default IRM backfield mode to false
        self.SetIRMBackFieldMode(False)
        
        # If pulse_volts is negative, set the backfield mode to true, else
        # set it to false
        if ((pulse_volts < 0) and self.modConfig.EnableIRMBackfield):        
            # Set the Backfield IRM mode = True
            self.SetIRMBackFieldMode(True)            
            pulse_volts = -1 * pulse_volts
            
        elif (pulse_volts < 1):        
            pulse_volts = 0
            self.SetIRMBackFieldMode(False)
                
        elif (not self.modConfig.EnableIRMBackfield):        
            self.SetIRMBackFieldMode(False)
                    
        TargetVoltage = pulse_volts
                
        # Convert capacitor pulse_volts into a DAQ Control pulse_volts
        DaqControlVoltage = self.ConvertPulseVoltsToMCCVolts(TargetVoltage)
        
        if (DaqControlVoltage > self.modConfig.PulseVoltMax):
            DaqControlVoltage = self.modConfig.PulseVoltMax
            
        # Convert back to Capacitor Volts for the displays on frmIRMARM
        TargetVoltage = self.ConvertMCCVoltsToPulseVolts(DaqControlVoltage)
        txtOut = 'IRMControl:Volts Out = ' + "{:.1f}".format(TargetVoltage)
        txtOut += ':Peak Field = ' + "{:.1f}".format(self.ConvertPulseVoltsToGauss(TargetVoltage))
        self.queue.put(txtOut)
        
        DaqControlVoltage = DaqControlVoltage * self.CalculateAscBoostMultiplier(TargetVoltage)
        
        if (DaqControlVoltage > self.modConfig.PulseVoltMax):
            DaqControlVoltage = self.modConfig.PulseVoltMax
           
        # Call function to set the relays into the correct configuration
        # If settings are not correct / relays were unable to set, Abort the IRM pulse fire process
        if not self.SetRelaysForIRM():        
            ErrorMessage = "IRM system settings need to be changed.  Current IRM pulse has been aborted.\n"
            ErrorMessage += "IRM Backfield Enabled = " + str(self.modConfig.EnableIRMBackfield) + "\n"
            ErrorMessage += "Axial IRM Enabled = " + str(self.modConfig.EnableAxialIRM) + "\n"
            ErrorMessage += "Transverse IRM Enabled = " + str(self.modConfig.EnableTransIRM)
            self.queue.put('IRMControl:Error:' + ErrorMessage)
            
            self.parent.Flow_Pause()
                                   
        # Clear pulse_volts
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=0)
        self.queue.put("IRMControl:Read Voltage = 0" + txtOut)
        
        # Wait for pulse_volts clear command to process through
        time.sleep(0.05)
                  
        # If we're in calibrate mode, pop-up picture-box in frmIRM_VoltageCalibration
        if CalibrationMode:
            self.CalMode_setDirection()
        
        # Get the start time of the IRM charge process
        StartTime = time.time()
        
        # Set Voltage to new IRM output pulse_volts target
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=DaqControlVoltage)
        self.queue.put("IRMControl:Read Voltage = " + "{:.2f}".format(pulse_volts))
                
        # Wait again for pulse_volts set command to process
        time.sleep(0.1)
        
        # Update Status Panel
        self.queue.put("Program Status:IRM @ " + "{:.2f}".format(TargetVoltage) + " Volts")
        
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(False))
        self.queue.put("IRMControl:IRM Trim = Off")
                
        self.stop_charging_change_threshold_in_percent = 0.1
        self.stop_trimming_change_threshold_in_percent = 0.5
        
        # Update the IRM Charging status on the main form
        if (TargetVoltage > 0):
            if not self.chargeIRM(StartTime, TargetVoltage, DaqControlVoltage, CalibrationMode):
                return        
                
        elif (TargetVoltage == 0):
            if not self.dischargeIRM(StartTime):
                return
                                
        # Now, if this is a calibration run,
        # Write the Return voltage to frmIRM_VoltageCalibration grid
        if CalibrationMode:
            self.CalMode_setCalibrationTable()
        
        # IRM box is all charged up, can fire the IRM now
        # fire IRM
            
        # Read in the current peak voltage (fewer read in's to lessen amount of time hanging here)
        readVoltage = self.IRMAverageVoltageIn(10)
        
        # Save readVoltage to peak voltage
        self.IRMPeakVoltage = readVoltage
        
        # Update program status bar and frmIRMARM display
        self.queue.put("Program Status:Firing!")
        self.queue.put("IRMControl:IRM Status = Firing")
                    
        # Close the TTL switch to connect the IRM circuit
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMFire, boolValue=False)
        self.queue.put('IRMControl:IRM Fire = On')
        
        # Pause while the IRM pulse
        # goes through the AF Coil
        # Check to see which coil is active to see if we
        # need to pause three times longer for the transverse coil IRM pulse
        amplitude_dependent_wait_factor = 0.0
                    
        if (self.parent.ADwin.ActiveCoilSystem == self.modConfig.AxialCoilSystem):        
            # Pause for a second
            time.sleep(1 + round(amplitude_dependent_wait_factor, 2))
                        
        elif (self.parent.ADwin.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):        
            # Pause for 3 seconds
            time.sleep(3 + round(amplitude_dependent_wait_factor, 2))
            
        else:        
            # Delay for 1 second
            time.sleep(1)
            
        # Reset IRM fire status
        # Open the TTL switch to break the IRM circuit
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMFire, boolValue=True)
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=0)            
        
        #Update program status bar - IRM Pulse done
        self.queue.put("Program Status:")
                
        # Last, unlock the coil selection
        self.CoilsLocked = False
        self.queue.put('IRMControl:IRM Fire = Off:Read Voltage = 0:IRM Status = :Coil locked = False')
    
        return

    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Public API Functions
                        
    --------------------------------------------------------------------------------------------'''                
    '''
    '''
    def init_IrmArm(self):
        self.parent.ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=0)
        
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=0)
        
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMTrim, boolValue=self.TrimOnOff(True))
        
        self.parent.ADwin.DoDAQIO(self.modConfig.IRMFire, boolValue=True)
        
        # Wait a half second
        time.sleep(0.5)
        
        self.parent.ADwin.DoDAQIO(self.modConfig.ARMSet, boolValue=True)
        
        self.SetIRMBackFieldMode(False)

        return
    
    '''
    '''
    def FireIRM(self, voltage, CalibrationMode=False):
        if 'ASC' in self.modConfig.IRMSystem:
            self.FireASC_IrmAtPulseVolts(voltage, CalibrationMode)
            
        elif 'APS' in self.modConfig.IRMSystem:
            self.FireAPS_AtCalibratedTarget(voltage)

        return
        
    '''
    '''
    def FireIRMAtField(self, Gauss):
        # First, lock the Coil selection
        self.CoilsLocked = True
        self.queue.put('IRMControl:Coil locked = True')
        
        outField = 0
        txtPulseVolts = 'IRMControl'
        if (self.modConfig.IRMSystem == "APS"):                        
            # APS IRM System is pre-calibrated.          
            self.parent.ADwin.TrySetRelays_ADwin('IRM Axial', True)    
            time.sleep(0.2)          
            self.FireIRM(Gauss)
          
        else:
            if ((Gauss < 0) and (self.modConfig.EnableIRMBackfield)):
                self.SetIRMBackFieldMode(True)
                Gauss = -Gauss                
                PulseVoltsOut = self.ConvertGaussToPulseVolts(Gauss)
                MCCVoltsOut = self.ConvertPulseVoltsToMCCVolts(PulseVoltsOut)
                PulseVoltsOut = -1 * PulseVoltsOut
                
            else:            
                self.SetIRMBackFieldMode(False)
                PulseVoltsOut = self.ConvertGaussToPulseVolts(Gauss)
                MCCVoltsOut = self.ConvertPulseVoltsToMCCVolts(PulseVoltsOut)
        
            txtPulseVolts += ':Volts Out = ' + "{:.2f}".format(PulseVoltsOut)            
            if (MCCVoltsOut < 0):
                MCCVoltsOut = 0
            elif (MCCVoltsOut > 10):
                MCCVoltsOut = 10            
            self.FireIRM(PulseVoltsOut)                
            outField = self.ConvertMCCVoltsToPulseVolts(MCCVoltsOut)
                
        # Last, unlock the coil selection
        self.CoilsLocked = False
        self.queue.put(txtPulseVolts + ':Coil locked = False')
        
        return outField

    '''
    '''
    def SetBiasField(self, Gauss):        
        # If ARM is not enabled in the Modules settings, then don't
        # let the code set an ARM Bias voltage!
        if not self.modConfig.EnableARM:
            return
        
        # Get the current bias field level
        self.CurrentBiasField = Gauss
        
        # Convert that field value to voltage using the ARM calibration value
        voltage = self.modConfig.ARMVoltGauss * Gauss
        
        # No negative voltages allowed
        if (voltage < 0): 
            voltage = 0
        
        # Coerce voltage to be less than the ARM max voltage
        if (voltage > self.modConfig.ARMVoltMax):
            voltage = self.modConfig.ARMVoltMax
        
        # Display the new bias voltage
        txtBiasField = 'IRMControl:Bias Field = '
        txtBiasField += "{:.2f}".format(voltage/self.modConfig.ARMVoltGauss)
        self.queue.put(txtBiasField)
        
        # Zero the ARM Bias voltage on the ARM Box
        self.parent.ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=0)
        
        # Wait 0.5 seconds
        time.sleep(0.5)
        
        if (Gauss > 0):        
            # Close the TTL switch to connect the ARM box
            # to the ARM Coils
            self.parent.ADwin.DoDAQIO(self.modConfig.ARMSet, boolValue=False)
            txtMCCARMSet = "ARM Set = On"
                    
            # Wait another half second
            time.sleep(0.5)
            
            # Set the ARM bias voltage to the desired target voltage
            self.parent.ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=voltage)
            txtMCCARMVout = txtMCCARMSet + ':ARM V = '
            txtMCCARMVout += "{:.2f}".format(voltage)
            self.queue.put('IRMControl:' + txtMCCARMVout)
            
            # Wait 1 second to allow the ARM charge to settle
            time.sleep(1)
            
        else:            
            # Re-zero the ARM Bias voltage
            self.parent.ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=0)
            txtMCCARMVout = "ARM V = 0.0"
            
            # Wait 0.5 seconds
            time.sleep(0.5)
            
            # Open the TTL switch to disconnect the ARM Box
            # fromt the ARM coils
            self.parent.ADwin.DoDAQIO(self.modConfig.ARMSet, boolValue=True)
            txtMCCARMSet = txtMCCARMVout + ":ARM Set = Off"
            self.queue.put('IRMControl:' + txtMCCARMSet)
        
        return
    
    '''
    '''
    def RefreshTemp(self):
        
        txtTemp = ''
        if self.modConfig.EnableT1:        
            Temp1 = self.parent.ADwin.DoDAQIO(self.modConfig.AnalogT1)            
            Temp1 = Temp1 * self.modConfig.TSlope - self.modConfig.Toffset                        
            txtTemp = ':Temp1 = ' + "{:.2f}".format(Temp1)
        
        if self.modConfig.EnableT2:        
            Temp2 = self.parent.ADwin.DoDAQIO(self.modConfig.AnalogT2)            
            Temp2 = Temp2 * self.modConfig.TSlope - self.modConfig.Toffset
            txtTemp += ':Temp2 = ' + "{:.2f}".format(Temp2)
        
        if (txtTemp != ''):
            self.queue.put('IRMControl' + txtTemp)
        
        return
    
    '''
    '''
    def outVoltage(self, channelConfig, outVoltage):
        self.parent.ADwin.DoDAQIO(channelConfig, numValue=outVoltage)
        return

    '''
    '''
    def inVoltage(self, channelConfig):
        inVoltage = self.parent.ADwin.DoDAQIO(channelConfig)
        return inVoltage
    
    '''
    '''
    def toggleTTLRelays(self, channelConfig, mode):
        self.parent.ADwin.DoDAQIO(channelConfig, boolValue=mode)
        return
    
    