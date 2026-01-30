'''
Created on Sep 9, 2025

@author: hd.nguyen
'''
import time
from builtins import property

from ClassModules.AF_Error_Response import AFErrorActionEnum
from ClassModules.AF_Ramp_Error import AFErrorTypeEnum

from Modules.modAF_DAQ import coil_type
from Modules.modAF_DAQ import modStatusCode

DEMAGLEN = 6

RockmagStepAFmax = "AFmax"
RockmagStepAFz = "AFz"
RockmagStepAF = "AF"
RockmagStepUAFX1 = "UAFX1"
RockmagStepUAFX2 = "UAFX2"
RockmagStepUAFZ1 = "UAFZ1"
RockmagStepaTAFX = "aTAFX" 
RockmagStepaTAFY = "aTAFY"
RockmagStepaTAFZ = "aTAFZ"
RockmagStepARM = "ARM"
RockmagStepVRM = "VRM"
RockmagStepPulseIRMAxial = "IRMz"
RockmagStepPulseIRMTrans = "IRMx"
RockmagStepRRM = "RRM"
RockmagStepRRMz = "RRMz"

class RockmagStep():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.BiasField = 0
        self.SpinSpeed = 0
        self.HoldTime = 0
        
        self.StepType = ''
        self.key = ''
        self.Remarks = ''
                
        self.Measure = False
        self.MeasureSusceptibility = False
        
        self.rockmagsteptype = ''
                
        self._Level = 0
        self._DemagStepLabel = ''
        self._DemagStepLabelLong = ''

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def DemagStepLabel(self):
        return self._DemagStepLabel
    
    @DemagStepLabel.getter
    def DemagStepLabel(self):
        self._DemagStepLabel = self.StepType
        
        if (len(self._DemagStepLabel) > DEMAGLEN):
            self._DemagStepLabel = self._DemagStepLabel[0:DEMAGLEN]
            
        numLength = DEMAGLEN - len(self._DemagStepLabel)
        if (self.StepType == RockmagStepARM): 
            setLevel = self.BiasField 
        else: 
            setLevel = self.Level
        
        if (setLevel != 0):
            self._DemagStepLabel = self._DemagStepLabel + str(setLevel).rjust(numLength)
        
        if (len(self._DemagStepLabel) < DEMAGLEN):
            for _ in range(len(self._DemagStepLabel), DEMAGLEN+1):
                self._DemagStepLabel += " "
        
        
        return self._DemagStepLabel

    @property
    def DemagStepLabelLong(self):
        return self._DemagStepLabelLong
    
    @DemagStepLabelLong.getter
    def DemagStepLabelLong(self):
        self._DemagStepLabelLong = self.StepType
        
        if (self.StepType == RockmagStepARM): 
            setLevel = self.BiasField 
        else: 
            setLevel = self.Level
            
        self._DemagStepLabelLong += " " + str(setLevel)
        if (self.StepType == RockmagStepRRM):
            self._DemagStepLabelLong = self._DemagStepLabelLong + "/" + self.SpinSpeed & " rps"
        
        return self._DemagStepLabelLong
    
    @property
    def Level(self):
        return self._Level
    
    @Level.setter
    def Level(self, value):
        self._Level = value
        return
    
    @Level.getter
    def Level(self):
        mvarLevel = self._Level
        
        if (self.StepType == RockmagStepAF):
            if (self.parent.modConfig.AfAxialMax > self.parent.modConfig.AfTransMax):
                maxAcceptableLevel = self.parent.modConfig.AfTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            if (self.parent.modConfig.AfAxialMin < self.parent.modConfig.AfTransMin):
                minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            else: 
                minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepAFmax):
            if (self.parent.modConfig.AfAxialMax > self.parent.modConfig.AfTransMax):
                maxAcceptableLevel = self.parent.modConfig.AfTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            if (self.parent.modConfig.AfAxialMin < self.parent.modConfig.AfTransMin):
                minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            else: 
                minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
                
        elif (self.StepType == RockmagStepAFz):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFX1):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFX2):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFZ1):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
                
        elif (self.StepType == RockmagStepaTAFX):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepaTAFY):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepaTAFZ):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepARM):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableARM:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepPulseIRMAxial):
            if (self.parent.modConfig.PulseTransMax > self.parent.modConfig.PulseAxialMax):
                maxAcceptableLevel = self.parent.modConfig.PulseTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.PulseAxialMax
            if self.parent.modConfig.EnableIRMBackfield:
                minAcceptableLevel = -1*self.parent.modConfig.PulseAxialMax 
            else: 
                minAcceptableLevel = self.parent.modConfig.PulseAxialMin
            
            if not self.parent.modConfig.EnableAxialIRM:
                maxAcceptableLevel = 0
                minAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepRRM):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        else:
            maxAcceptableLevel = 999999
            minAcceptableLevel = -999999
    
        if (self.StepType == RockmagStepAFmax):
            mvarLevel = maxAcceptableLevel
            
        elif (self._Level == 0):
            mvarLevel = 0
            
        elif (self._Level > maxAcceptableLevel):
            mvarLevel = maxAcceptableLevel
            
        elif (self._Level < minAcceptableLevel):
            mvarLevel = minAcceptableLevel
            
        else:
            mvarLevel = self._Level
        
        return mvarLevel

    '''--------------------------------------------------------------------------------------------
                        
                        Iternal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def setRockmagStepAF(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):             
            # Override defaults for error table for Axial Ramp
            self.parent.modAF_DAQ.AF_Error_Response_Table.Add(AFErrorTypeEnum.ZeroMonitorVoltage, coil_type.Axial, modStatusCode.CodeRed, AFErrorActionEnum.SuppressError)
            self.parent.modAF_DAQ.AF_Error_Response_Table.Add(AFErrorTypeEnum.TargetUndershoot, coil_type.Axial, modStatusCode.CodeRed, AFErrorActionEnum.SuppressError)
             
            # Axial AF Ramp
            if (self.parent.modConfig.AFSystem == "2G"):                
                # (August 2007 L Carporzen) Allow to wait between each ramp
                if (self.parent.ADwin.AF2GControl.txtWaitingTime != 0): 
                    time.sleep(self.parent.ADwin.AF2GControl.txtWaitingTime)                
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.AxialCoilSystem, self.Level, self.parent.modConfig.AFRampRate)            
                self.parent.ADwin.AF2GControl.Disconnect()
            
            elif (self.parent.modConfig.AFSystem == "ADWIN"):                                                
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.AxialCoilSystem,
                                              self.Level,
                                              CalRamp = True, 
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
                                                                    
            three_seconds = 3            
            self.parent.modAF_DAQ.PauseBetweenUseCoils_InSeconds(three_seconds)
            
            # Transverse AF Ramp - X direction
            if (self.parent.modConfig.AFSystem == "2G"):                
                self.parent.ADwin.AF2GControl.Connect()
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.TransverseCoilSystem, self.Level, self.parent.modConfig.AFRampRate)
                
            elif (self.parent.modConfig.AFSystem == "ADWIN"):            
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.TransverseCoilSystem,
                                              self.Level,
                                              CalRamp = True,
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
                                                    
            self.parent.motors.TurningMotorRotate(90)
                            
            # Transverse AF Ramp - Y direction
            if (self.parent.modConfig.AFSystem == "2G"):            
                # (August 2007 L Carporzen) Allow to wait between each ramp
                if (self.parent.ADwin.AF2GControl.txtWaitingTime != 0):
                    time.sleep(self.parent.ADwin.AF2GControl.txtWaitingTime)                
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.TransverseCoilSystem, self.Level, self.parent.modConfig.AFRampRate)
                                    
            elif (self.parent.modConfig.AFSystem == "ADWIN"):            
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.TransverseCoilSystem,
                                              self.Level,
                                              CalRamp = True, 
                                              ClipTest = False, 
                                              Verbose=self.parent.ADwin.Verbose)
            
            self.parent.motors.TurningMotorRotate(360)
            
            # Check for Axial Error, error types are safe for bit-wise combination
            if ((self.parent.modConfig.AFSystem == "ADWIN") and \
               (((self.parent.modAF_DAQ.AF_Axial_Error_Status.ErrorType == AFErrorTypeEnum.TargetUndershoot) or
               (self.parent.modAF_DAQ.AF_Axial_Error_Status.ErrorType == AFErrorTypeEnum.ZeroMonitorVoltage)))):            
                # Need to enable expression of code-red error for axial AF failure
                self.parent.modAF_DAQ.AF_Error_Response_Table.Add(AFErrorTypeEnum.ZeroMonitorVoltage, coil_type.Axial, modStatusCode.CodeRed, AFErrorActionEnum.ExpressError)
                self.parent.modAF_DAQ.AF_Error_Response_Table.Add(AFErrorTypeEnum.TargetUndershoot, coil_type.Axial, modStatusCode.CodeRed, AFErrorActionEnum.ExpressError)
                
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.AxialCoilSystem, 
                                              self.Level, 
                                              CalRamp = True,
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
            
            # Restore Default AF error handling / error responses
            self.parent.modAF_DAQ.InitDefault_AFErrorResponseTable()
                                    
            self.parent.gaussMeter.cmdResetPeak_Click()
            
        return
    
    '''
    '''
    def setRockmagStepAFmax(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            # Suppress CodeYellow and CodeRed Target Undershoot errors
            self.parent.modAF_DAQ.AF_Error_Response_Table.SetItem(AFErrorTypeEnum.TargetUndershoot, coil_type.Axial, modStatusCode.CodeYellow, AFErrorActionEnum.SuppressError) 
            self.parent.modAF_DAQ.AF_Error_Response_Table.SetItem(AFErrorTypeEnum.TargetUndershoot, coil_type.Transverse, modStatusCode.CodeYellow, AFErrorActionEnum.SuppressError)
            self.parent.modAF_DAQ.AF_Error_Response_Table.SetItem(AFErrorTypeEnum.TargetUndershoot, coil_type.Axial, modStatusCode.CodeRed, AFErrorActionEnum.SuppressError)
            self.parent.modAF_DAQ.AF_Error_Response_Table.SetItem(AFErrorTypeEnum.TargetUndershoot, coil_type.Transverse, modStatusCode.CodeRed, AFErrorActionEnum.SuppressError)
            
            if (self.parent.modConfig.AFSystem == "2G"):                
                self.parent.ADwin.AF2GControl.Connect
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.TransverseCoilSystem, self.parent.modConfig.AfTransMax, self.parent.modConfig.AFRampRate)
                
            elif (self.parent.modConfig.AFSystem == "ADWIN"):                                                    
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.TransverseCoilSystem,
                                              self.parent.modConfig.AfTransMax,
                                              CalRamp = True,
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
            
            self.parent.motors.TurningMotorRotate(90)
            
            if (self.parent.modConfig.AFSystem == "2G"):                
                # (August 2007 L Carporzen) Allow to wait between each ramp
                if (self.parent.ADwin.AF2GControl.txtWaitingTime != 0):
                    time.sleep(self.parent.ADwin.AF2GControl.txtWaitingTime)            
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.TransverseCoilSystem, self.parent.modConfig.AfTransMax, self.parent.modConfig.AFRampRate)
                
            elif (self.parent.modConfig.AFSystem == "ADWIN"):            
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.TransverseCoilSystem, 
                                              self.parent.modConfig.AfTransMax,
                                              CalRamp = True,
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
            
            self.parent.motors.TurningMotorRotate(360)
            
            if (self.parent.modConfig.AFSystem == "2G"):                
                # (August 2007 L Carporzen) Allow to wait between each ramp
                if (self.parent.ADwin.AF2GControl.txtWaitingTime != 0):
                    time.sleep(self.parent.ADwin.AF2GControl.txtWaitingTime)                        
                self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, self.parent.modConfig.AxialCoilSystem, self.parent.modConfig.AfAxialMax, self.parent.modConfig.AFRampRate)                
                self.parent.ADwin.AF2GControl.Disconnect()
                
            elif (self.parent.modConfig.AFSystem == "ADWIN"):            
                self.parent.ADwin.ExecuteRamp(self.parent.modConfig.AxialCoilSystem, 
                                              self.parent.modConfig.AfAxialMax,
                                              CalRamp = True,
                                              ClipTest = False,
                                              Verbose=self.parent.ADwin.Verbose)
                                        
            # Set Error responses back to default
            self.parent.modAF_DAQ.InitDefault_AFErrorResponseTable()

        return
    
    '''
    '''
    def setRockmagStep(self, coilSystem):
        if (self.parent.modConfig.AFSystem == "2G"):                
            self.parent.ADwin.AF2GControl.Connect()                
            self.parent.ADwin.AF2GControl.CycleWithHold(self.HoldTime, 
                                                        coilSystem, 
                                                        self.Level, 
                                                        self.parent.modConfig.AFRampRate)                
            self.parent.ADwin.AF2GControl.Disconnect()
            
        elif (self.parent.modConfig.AFSystem == "ADWIN"):            
            self.parent.ADwin.ExecuteRamp(coilSystem, 
                                          self.Level,
                                          CalRamp = True,
                                          ClipTest = False,
                                          Verbose=self.parent.ADwin.Verbose)
        return
   
    '''
    '''
    def setRockmagStepAFz(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)        
        return
   
    '''
    '''
    def setRockmagStepUAFX1(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.TransverseCoilSystem)
        return
   
    '''
    '''
    def setRockmagStepUAFX2(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.parent.motors.TurningMotorRotate(90)
            self.setRockmagStep(self.parent.modConfig.TransverseCoilSystem)                        
            self.parent.motors.TurningMotorRotate(360)
            
        return
    
    '''
    '''
    def setRockmagStepUAFZ1(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)
        return
    
    '''
    '''
    def setRockmagStepaTAFX(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)
        return
   
    '''
    '''
    def setRockmagStepaTAFY(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)
        return
   
    '''
    '''
    def setRockmagStepaTAFZ(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableAF):            
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)
        return
   
    '''
    '''
    def setRockmagStepARM(self):
        if ((self.Level > 0) and self.parent.modConfig.EnableARM):
            self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)
            
        else:        
            time.sleep(self.HoldTime)
            
        return
   
    '''
    '''
    def setRockmagStepVRM(self):
        self.parent.displayStatusBar('VRM Decay: ' + '{:.1f}'.format(self.HoldTime) + ' secs')
        remaining_time_seconds = self.HoldTime
        while (remaining_time_seconds >= 0):
            time.sleep(1)
            remaining_time_seconds -= 1
            self.parent.displayStatusBar('VRM Decay: ' + '{:.1f}'.format(remaining_time_seconds) + ' secs')
        return
    
    '''
    '''
    def setRockmagStepPulseIRMAxial(self, SampleHeight):
        if self.parent.modConfig.EnableAxialIRM:            
            SampleCenterRMPosition = int(self.parent.apsIRM.IRMCenteringPos(self.Level) + SampleHeight / 2)
            
            if ((SampleCenterRMPosition / abs(SampleCenterRMPosition)) != (self.parent.modConfig.AFPos / abs(self.parent.modConfig.AFPos))):                
                # crap... our sample is too large to put in the AF coil!
                return
                         
            # discharge with sample in load position            
            self.parent.motors.UpDownMove(0, 1)            
            if (self.parent.modConfig.IRMSystem != "APS"):
            
                self.parent.apsIRM.update_frmIRMARM('Coil Type = Axial')
                self.parent.apsIRM.FireIRM(0)                 # ??? 5/12/17
                
                time.sleep(1)
                
                self.parent.apsIRM.update_frmIRMARM('Coil Type = Axial')
                self.parent.apsIRM.FireIRM(0)
            
            self.parent.motors.UpDownMove(SampleCenterRMPosition, 1)
            
            if (abs(self.Level) > 0):
                self.parent.apsIRM.update_frmIRMARM('Coil Type = Axial')
                self.parent.apsIRM.FireIRMAtField(self.Level)
        
        return
    
    '''
    '''
    def setRockmagStepRRM(self):
        if self.parent.modConfig.EnableAF:            
            self.parent.motors.TurningMotorSpin(self.SpinSpeed, 300 + self.HoldTime)            
            if (self.Level > 0):
                self.setRockmagStep(self.parent.modConfig.TransverseCoilSystem)            
            self.parent.motors.TurningMotorSpin(0)
        
        return
    
    '''
    '''
    def setRockmagStepRRMz(self):
        if self.parent.modConfig.EnableAF:            
            self.parent.motors.TurningMotorSpin(self.SpinSpeed, 300 + self.HoldTime)
            if (self.Level > 0):
                self.setRockmagStep(self.parent.modConfig.AxialCoilSystem)            
            self.parent.motors.TurningMotorSpin(0)
            
        return
   
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '   August 11, 2010
    '   Mod to Public Sub PerformStep
    '
    '   Isaac Hilburn
    '
    '   Summary:    Added If ... then ... elseif ... then statments to select the correct AFsystem to do
    '               the treatment for the rock mag step.
    '               Also, cleaned up the code appearance so that it's easier to read / understand.  Also
    '               added more code documentation
    '''
    def PerformStep(self, specimen):        
        if self.parent.checkProgramHaltRequest():
            return
        
        if (self.parent.modConfig.ARMMax > 0):
            self.parent.apsIRM.SetBiasField(0)
        
        if not ((self.StepType == RockmagStepAF) or \
                (self.StepType == RockmagStepARM) or \
                (self.StepType == RockmagStepPulseIRMAxial) or \
                (self.StepType == RockmagStepPulseIRMTrans) or \
                (self.StepType == RockmagStepRRM) or \
                (self.StepType == RockmagStepVRM) or \
                (self.StepType == RockmagStepUAFX1) or \
                (self.StepType == RockmagStepUAFX2) or \
                (self.StepType == RockmagStepUAFZ1) or \
                (self.StepType == RockmagStepaTAFX) or \
                (self.StepType == RockmagStepaTAFY) or \
                (self.StepType == RockmagStepaTAFZ) or \
                (self.StepType == RockmagStepAFmax) or \
                (self.StepType == RockmagStepAFz)):
            return

        '''        
            (August 2010 - I Hilburn)
            Added in logical conditions to check to see that the necessary module
            for a rockmag step is enabled
        
            Check AF module
        '''
        if (((self.StepType == RockmagStepAF) or \
            (self.StepType == RockmagStepAFz) or \
            (self.StepType == RockmagStepUAFX1) or \
            (self.StepType == RockmagStepUAFX2) or \
            (self.StepType == RockmagStepUAFZ1) or \
            (self.StepType == RockmagStepaTAFX) or \
            (self.StepType == RockmagStepaTAFY) or \
            (self.StepType == RockmagStepaTAFZ) or \
            (self.StepType == RockmagStepAFmax) or \
            (self.StepType == RockmagStepARM)) and \
            (not self.parent.modConfig.EnableAF)):
            # Wha-oh, user is trying to do an AF step without the AF module switched on
            MsgBox = "AF Module is currently disabled. AF demag cannot be performed."
            self.parent.displayMessageBox(caption="Whoops!", message=MsgBox, pause=True)
            return
            
        
        # Check IRM Axial module
        if ((self.StepType == RockmagStepPulseIRMAxial) and \
           (not self.parent.modConfig.EnableAxialIRM)):
            # Wha-oh, user is trying to do an IRM axial step without the module switched on
            MsgBox = "Axial IRM Module is currently disabled. IRM Axial pulse cannot be performed."
            self.parent.displayMessageBox(caption="Whoops!", message=MsgBox, pause=True)
            return
        
        # Check IRM Transverse module
        if ((self.StepType == RockmagStepPulseIRMTrans) and \
           (not self.parent.modConfig.EnableTransIRM)):
            # Wha-oh, user is trying to do an IRM transverse step without the module switched on
            MsgBox = "Transverse IRM Module is currently disabled. " 
            MsgBox += "IRM Transverse pulse cannot be performed."
            self.parent.displayMessageBox(caption="Whoops!", message=MsgBox, pause=True)
            return
        
        # Check ARM
        if ((self.rockmagsteptype == RockmagStepARM) and \
           (not self.parent.modConfig.EnableARM)):
            # MsgBox the user - ARM module is disabled
            MsgBox = "ARM Module is currently disabled. " 
            MsgBox += "ARM Bias Voltage cannot be used right now, " 
            MsgBox += "though the AF module is enabled."
            self.parent.displayMessageBox(caption="Whoops!", message=MsgBox, pause=True)
            return
        
        if (specimen.parent.doBoth and (not specimen.parent.doUp)):
            return
        
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
        if ((self.StepType == RockmagStepaTAFX) or \
           (self.StepType == RockmagStepaTAFY) or \
           (self.StepType == RockmagStepaTAFZ)):
            if (self.parent.measurements.frmMeasure_lblDemag != specimen.parent.measurementSteps.CurrentStep.DemagStepLabelLong):            
                # We assume that we have the same height than before                
                self.parent.motors.HomeToTop()
                
                message = "Doing " + self.StepType
                message += " axial demagnetization.\n"
                message += "What is the height (in cm) of the sample?\n \n"
                message += "Orientation conventions:\n"
                message += "aTAFX vertical quartz disk with arrow toward the top and "
                message += "sample on the clean lab side of the disk.\n"
                message += "aTAFY vertical quartz disk with arrow toward the oven and "
                message += "sample on the clean lab side of the disk."
                title = "Important!"  
                inputValue = specimen.SampleHeight / self.parent.modConfig.UpDownMotor1cm                
                valX = self.parent.displayInputForm(message=message, title=title, inputValue=inputValue)
                specimen.SampleHeight = self.parent.modConfig.UpDownMotor1cm * valX
                    
            
        # Position the center of the sample in the center of the
        # rock-mag coils
        SampleCenterRMPosition = int(self.parent.modConfig.AFPos + specimen.SampleHeight / 2)
            
        if ((SampleCenterRMPosition / abs(SampleCenterRMPosition)) != (self.parent.modConfig.AFPos / abs(self.parent.modConfig.AFPos))):            
            # crap... our sample is too large to put in the AF coil!
            return
        
        if (self.StepType == RockmagStepPulseIRMAxial):            
            self.parent.motors.UpDownMove(0, 1)            
        else:            
            #  Move somewhat slowly into AF region
            self.parent.motors.UpDownMove(SampleCenterRMPosition, 1)
        
        
        self.parent.motors.TurningMotorRotate(0)
        
        # Set the ARM Bias field if this rock-mag step requires it
        if (self.parent.modConfig.EnableARM and (self.BiasField > 0) and \
           ((self.StepType == RockmagStepARM) or \
            (self.StepType == RockmagStepRRM) or \
            (self.StepType == RockmagStepRRMz))):
            self.parent.apsIRM.SetBiasField(self.BiasField)
                
        self.parent.modAF_DAQ.ClearAFErrorStatus()
        self.parent.modAF_DAQ.InitDefault_AFErrorResponseTable()
        
        #Select Case mvarStepType            
        if (self.StepType == RockmagStepAF):
            self.setRockmagStepAF()
                                                
        elif (self.StepType == RockmagStepAFmax):
            self.setRockmagStepAFmax()
                                                
        elif (self.StepType == RockmagStepAFz):
            self.setRockmagStepAFz()
                            
        elif (self.StepType == RockmagStepUAFX1):
            self.setRockmagStepUAFX1()
                            
        elif (self.StepType == RockmagStepUAFX2):
            self.setRockmagStepUAFX2()
                            
        elif (self.StepType == RockmagStepUAFZ1):
            self.setRockmagStepUAFZ1()                
            
        elif (self.StepType == RockmagStepaTAFX):
            self.setRockmagStepaTAFX()
                            
        elif (self.StepType == RockmagStepaTAFY):
            self.setRockmagStepaTAFY()                    
            
        elif (self.StepType == RockmagStepaTAFZ):
            self.setRockmagStepaTAFZ()
                                
        elif (self.StepType == RockmagStepARM):
            self.setRockmagStepARM()
                        
        elif (self.StepType == RockmagStepVRM):
            self.setRockmagStepVRM()
                    
        elif (self.StepType == RockmagStepPulseIRMAxial):
            self.setRockmagStepPulseIRMAxial(specimen.SampleHeight)
                                    
        elif (self.StepType == RockmagStepRRM):
            self.setRockmagStepRRM()
                                    
        elif (self.StepType == RockmagStepRRMz):
            self.setRockmagStepRRMz()
                                
        if (self.BiasField > 0):        
            self.parent.apsIRM.SetBiasField(0)
            
        return
        
'''
    -----------------------------------------------------------------------------------------------
'''        
class RockmagSteps():
    '''
    classdocs
    '''


    def __init__(self, parent=None, mainForm=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.mainForm = mainForm
        
        self.CurrentStepIndex = 0
        self.nextStepID = 1
        self.Item = []
        
        self._Count = 0
        self._CurrentStep = RockmagStep(mainForm)

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def Count(self):    
        return self._Count
    
    @Count.getter
    def Count(self):
        self._Count = len(self.Item)
        return self._Count
    
    @property
    def CurrentStep(self):
        return self._CurrentStep
    
    @CurrentStep.getter
    def CurrentStep(self):
        self._CurrentStep = RockmagStep(self.mainForm)
        self._CurrentStep.StepType = ''
        
        if (len(self.Item) > self.CurrentStepIndex):
            self._CurrentStep = self.Item[self.CurrentStepIndex]
        
        return self._CurrentStep
    
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    
   
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def AdvanceStep(self):
        self.CurrentStepIndex = (self.CurrentStepIndex + 1)
        if (self.CurrentStepIndex >= self.Count):
            self.CurrentStepIndex = -1            
        return
    
    '''
    '''
    def Remove(self, index):
        del self.Item[index]
        return
    
    '''
    '''
    def Add(self, StepType, 
                  Level= 0.0, 
                  BiasField = 0, 
                  SpinSpeed = 0, 
                  HoldTime = 0, 
                  Measure = True, 
                  MeasureSusceptibility = False, 
                  Remarks = '', 
                  BeforeStep = 0, 
                  AfterStep = 0):
        
        objNewMember = RockmagStep(self.mainForm)
        
        # set the properties passed into the method
        objNewMember.StepType = StepType
        objNewMember.Level = Level
        objNewMember.BiasField = BiasField
        objNewMember.SpinSpeed = SpinSpeed
        objNewMember.HoldTime = HoldTime
        objNewMember.Measure = Measure
        objNewMember.MeasureSusceptibility = MeasureSusceptibility
        objNewMember.Remarks = Remarks 
        objNewMember.key = "S" + str(self.nextStepID)
        
        self.Item.append(objNewMember)
        
        self.nextStepID = self.nextStepID + 1
        
        return objNewMember
    