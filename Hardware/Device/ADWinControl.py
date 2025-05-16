'''
Created on Jan 28, 2025

@author: hd.nguyen
'''
import ctypes
import os
import time
import configparser

from Hardware.Device.AF_2GControl import AF_2GControl
from ADwin import ADwin, ADwinError
from Process.ProcessData import ProcessData
from Process.ModConfig import ModConfig
from Modules.ModAF_DAQ import ModAF_DAQ

class ADWinControl():
    '''
    classdocs
    '''    
    __err = ctypes.c_int32(0)
    __errPointer = ctypes.pointer(__err)
    
    adwin_digital_word = 0x00
    filePath = ''
    modConfig = None

    def __init__(self, path, parent=None, modConfig=None):
        '''
        Constructor
        '''
        self.filePath = path
        self.modConfig = modConfig
        self.WaveForms = {}
        self.AF2GControl = AF_2GControl(parent = parent, modConfig = self.modConfig)
        self.modAF_DAQ = ModAF_DAQ(path.replace('\\Hardware\\Hardware\\', '\\Hardware\\') , parent = parent, modConfig = self.modConfig)
        
        self.ActiveCoilSystem = None
        
        try:
            # Establish connection with the ADwin system        
            self.adw = ADwin(DeviceNo=1, raiseExceptions=1)
            if (self.adw.Processor_Type() != 'T9'):
                self.adw.Boot(self.filePath + 'ADwin9.btl')
                print('ADWin system boot')
                
            if (self.modConfig != None):
                self.WaveForms = self.modConfig.waveForms             

        except ADwinError:
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
        retValue = 0
        
        if (channel.ChanType == 'DO'):
            if boolValue:
                self.modAF_DAQ.setDIO(channel.ChanNum)
            else:
                self.modAF_DAQ.clearDIO(channel.ChanNum)
            self.modConfig.processData.ADwinDO = self.adwin_digital_word
            
        elif (channel.ChanType == 'DI'):
            print('TODO')
            
        elif (channel.ChanType == 'AO'):
            print('TODO')

        elif (channel.ChanType == 'AI'):
            retValue = self.modAF_DAQ.AnalogIn(channel.ChanNum)
            
        return retValue
        
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
    def tryGetADWIN_DigOutStatusByte(self):
        return self.adwin_digital_word
        
    '''
    '''
    def trySetRelays_ADwin_AFsAreUpPosition(self, coilLabel):
        
        if (self.modConfig.AFSystem != 'ADWIN'):
            return False
        
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
            self.Set_Digout(intermediate_byte)
            # Wait two seconds, do not allow events
            time.sleep(2)
    
        # Set the final relay position
        self.Set_Digout(final_byte)        
        time.sleep(1)
        
        return True
        
    '''
    '''
    def trySetRelays_ADwin_AFsAreDownPosition(self, coilLabel):
        
        if (self.modConfig.AFSystem != 'ADWIN'):
            return False        
        
        all_up_byte = (2 ^ 6) - 1        
        if (coilLabel == 'Axial'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.AFAxialRelay.ChanNum)) % 256)
        elif (coilLabel == 'Transverse'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.AFTransRelay.ChanNum)) % 256)
        elif (coilLabel == 'IRM Axial'):
            relay_byte_id = all_up_byte - ((2 ^ (self.modConfig.IRMRelay.ChanNum)) % 256)
        
        # Intermediate State - Prior State + desired Relay set high
        intermediate_byte = all_up_byte
            
        # Final State - Only Desired Relay set high
        final_byte = relay_byte_id
        
        # Set the intermediate relay position
        if (intermediate_byte != final_byte):
            self.Set_Digout(intermediate_byte)
    
            # Wait two seconds, do not allow events
            time.sleep(2)
    
        # Set the final relay position
        self.Set_Digout(final_byte)
        
        time.sleep(2)
        
        return True 
        
    '''
    '''
    def setPeak_monitor(self, paramList):
        calDone = paramList[0]
        activeCoilSystem = paramList[1]
        monMax = paramList[2]
        
        # Check to see if this AF coil has been calibrated
        # and if it needs to be
        if ((not calDone) and (self.modConfig.processData.ADwin_optCalRamp == 0)):
            # Tell user they need to do a calibration
            # on the AF Axial/Transverse coil
            messageStr = 'AF Coil has not been calibrated yet. The current AF '
            messageStr += 'ramp process has been terminated.\n\n'
            messageStr += 'Would you like to calibrate the AF Coil right now?'
            raise IOError(messageStr) 
        
        # Now check to see if the user wants a calibrated, monitored ramp
        if (self.modConfig.processData.ADwin_optCalRamp == 0):
            # We know the coil system is calibrated, we can get the Monitor voltage
            # matching the Peak Field set by the user
            self.modConfig.processData.ADwin_monitorTrigVolt = self.AF2GControl.FindXCalibValue(self.modConfig.processData.ADwin_peakField, 
                                                                                                activeCoilSystem)
            # Check to make sure the monitor voltage is below the max monitor voltage for
            # the Axial/Transverse coil system
            if (self.modConfig.processData.ADwin_monitorTrigVolt > monMax):
                self.modConfig.processData.ADwin_monitorTrigVolt = monMax
            respStr = "{:.1f}".format(self.modConfig.processData.ADwin_monitorTrigVolt)
            self.modConfig.queue.put('ADWinAFControl:Peak Monitor Voltage = ' + respStr)
            
        else:
            # Check to make sure the monitor voltage is below the max monitor voltage for
            # the Axial/Transverse coil system
            respStr = ''
            if (self.modConfig.processData.ADwin_monitorTrigVolt > monMax):
                self.modConfig.processData.ADwin_monitorTrigVolt = monMax
                respStr = "{:.1f}".format(self.modConfig.processData.ADwin_monitorTrigVolt)
                respStr = 'ADWinAFControl:Peak Monitor Voltage = ' + respStr
                
            if (calDone):
                self.modConfig.processData.ADwin_peakField = self.modAF_DAQ.FindFieldFromVolts(self.modConfig.processData.ADwin_monitorTrigVolt,
                                                                                               activeCoilSystem)
                if (respStr == ''):
                    respStr = 'ADWinAFControl'
                respStr += ':Peak Field = ' + "{:.1f}".format(self.modConfig.processData.peakField)
                
            if (respStr != ''):
                self.modConfig.queue.put(respStr)
        return
    
    '''
    '''
    def SetPeakValues(self, chkClippingTest):
        # Now, depending on the coil system used, need to translate the active field
        # setting (Peak Field or Monitor Voltage) into the other two fields (Ramp voltage needs
        # to be set as well).
        # Check if the Ramp is unmonitored
        if not chkClippingTest:
            # This is a monitored ramp, the peak ramp value needs
            # to be determined from the Peak Monitor Voltage
        
            # If this is a calibrated ramp
            # Need to get the needed Monitor peak voltage
            # from the Peak Field value
            
            # Check to see if the Axial coil is active
            if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
                paramList = [self.modConfig.AFAxialCalDone,
                             self.modConfig.AxialCoilSystem,
                             self.modConfig.AfAxialMonMax]
                self.setPeak_monitor(paramList)
                
            elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
                paramList = [self.modConfig.AfTransCalDone,
                             self.modConfig.TransverseCoilSystem,
                             self.modConfig.AfTransMonMax]
                self.setPeak_monitor(paramList)
                        
                                        
            '''
                Update the Ramp Peak Voltage
                Depends on how high the monitor voltage relative to the maximum monitor voltage
            '''
            if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
                self.modConfig.processData.ADwin_rampPeakVoltage = self.modConfig.processData.ADwin_monitorTrigVolt / self.modConfig.AfAxialMonMax * self.modConfig.AfAxialRampMax    
                
            elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
                self.modConfig.processData.ADwin_rampPeakVoltage = self.modConfig.processData.ADwin_monitorTrigVolt / self.modConfig.AfTransMonMax * self.modConfig.AfTransRampMax / 2.2
               
            '''
                Make sure the peak ramp voltage is within bounds
            '''
            if ((self.ActiveCoilSystem == self.modConfig.AxialCoilSystem) and (self.modConfig.processData.ADwin_rampPeakVoltage > self.modConfig.AfAxialRampMax)):
                self.modConfig.processData.ADwin_rampPeakVoltage = self.modConfig.AfAxialRampMax
                
            elif ((self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem) and (self.modConfig.processData.ADwin_rampPeakVoltage > self.modConfig.AfTransRampMax)):
                self.modConfig.processData.ADwin_rampPeakVoltage = self.modConfig.AfTransRampMax
            
            respStr = 'ADWinAFControl:Peak Ramp Voltage = ' + "{:.1f}".format(self.modConfig.processData.ADwin_rampPeakVoltage)
            self.modConfig.queue.put(respStr)
            
        return
        
    '''
    '''
    def setActiveCoil(self):
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            if not self.trySetRelays_ADwin('Axial'):
                return 'Coil Status = False' 
            
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            if not self.trySetRelays_ADwin('Transverse'):
                return 'Coil Status = False' 
            
        else:
            return 'Coil Status = False' 
        
        # Check to see if the AF wave-forms were successfully loaded from the .INI settings file
        if not self.WaveForms:
            errorMessage = 'Error: Bad AF Ramp Settings! Please check the .INI file for formatting errors.'
            raise ValueError(errorMessage)
         
        return 'Coil Status = True'  
    
    '''
        Check to see if this is a calibrated ramp
    '''
    def checkCalibratedRamp(self, respStr, CalRamp, PeakValue, ClipTest):
        RampDownMode = 0 
        if CalRamp:
            # Set the clip-text (unmonitored ramp) check-box to unchecked
            respStr += ':Unmonitored Ramp = False'
            chkClippingTest = False
            # Inputed value will be treated as though it is a Peak Field value
            self.modConfig.processData.ADwin_peakField = PeakValue
            respStr += ':Peak Field = ' + str(PeakValue)
            # Select the calibrated ramp radio button
            # and deselect the uncalibrated ramp radio button
            respStr += ':OptCalRamp = 0'
            self.modConfig.processData.ADwin_optCalRamp = 0
            # Set Ramp Down mode = 1 (use # periods instead of voltage / sec slope)
            RampDownMode = 1
            
        elif ((not CalRamp) and (not ClipTest)):
            # Set the clip-text (unmonitored ramp) check-box to unchecked
            respStr += ':Unmonitored Ramp = False'
            chkClippingTest = False
            # This is an uncalibrated, monitored ramp,
            # Peak value is a Monitor Peak Voltage
            self.modConfig.processData.ADwin_peakField = PeakValue
            respStr += ':Peak Monitor Voltage = ' + str(PeakValue)
            # Select the calibrated ramp radio button
            # and deselect the uncalibrated ramp radio button
            respStr += ':OptCalRamp = 1'
            self.modConfig.processData.ADwin_optCalRamp = 1
            # Set Ramp Down mode = 1 (use # periods instead of voltage / sec slope)
            RampDownMode = 1

        elif ((not CalRamp) and (ClipTest)):
            # Set the clip-text (unmonitored ramp) check-box to checked
            respStr += ':Unmonitored Ramp = True'
            chkClippingTest = True
            # This is an uncalibrated, unmonitored clip-test ramp
            # Peak value is a Ramp Peak Voltage
            self.modConfig.processData.ADwin_peakField = PeakValue
            respStr += ':Peak Ramp Voltage = ' + str(PeakValue)
            # Set Ramp Down mode = 0 (use slope instead of # periods)
            RampDownMode = 0
        self.modConfig.queue.put('ADWinAFControl:' + respStr)
        
        return RampDownMode, chkClippingTest 
    
    '''
    '''
    def computeCoilFrequency(self):
        '''
            Figure out which of the two coil resonance freq's are larger
            New to use to rescale the slope up & down for the lower freq coil
            to make sure that the same number of periods are used for the ramp
            up and ramp down
        '''
        if (self.modConfig.AfAxialResFreq > self.modConfig.AfTransResFreq):    
            BiggerFreq = self.modConfig.AfAxialResFreq
            SmallerFreq = self.modConfig.AfTransResFreq        
        else:
            BiggerFreq = self.modConfig.AfTransResFreq
            SmallerFreq = self.modConfig.AfAxialResFreq
        
        # Set the frequency to use now
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            Freq = self.modConfig.AfAxialResFreq            
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            Freq = self.modConfig.AfTransResFreq
            
        # Update the wave objects
        self.modConfig.waveForms['AFRAMPUP'].SineFreqMin = Freq
        self.modConfig.waveForms['AFRAMPDOWN'].SineFreqMin = Freq
        self.modConfig.waveForms['AFMONITOR'].SineFreqMin = Freq
        
        # Update the ADWIN AF form
        self.modConfig.queue.put('ADWinAFControl:Frequency = ' + "{:.1f}".format(Freq))
        
        return Freq
    
    '''
        This function is the brains behind how fast an ADWIN AF ramp up
        is allowed to happen.
    '''
    def GetUpSlope(self, RampPeakVolts):
        # If no coil is selected, default to a 1 second ramp
        getUpSlope = RampPeakVolts
        # Compare the RampPeakVolts to the Ramp Voltage corresponding to the
        # peak field (if the calibration is done), if not, then relative to the
        # Max ramp voltage set in the AF Auto tune form
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            #Need to multiply by 1000 to convert seconds to miliseconds
            RampUpDur_ms = RampPeakVolts / self.modConfig.AxialRampUpVoltsPerSec * 1000    
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            # Need to multiply by 1000 to convert seconds to miliseconds
            RampUpDur_ms = RampPeakVolts / self.modConfig.TransRampUpVoltsPerSec * 1000    
        else:        
            return getUpSlope 
            
        #Check to make sure RampUpDur_ms is not smaller than the minimum allowed ramp duration
        if (RampUpDur_ms < self.modConfig.MinRampUpTime_ms):    
            RampUpDur_ms = self.modConfig.MinRampUpTime_ms
    
        if (RampUpDur_ms > self.modConfig.MaxRampUpTime_ms):
            RampUpDur_ms = self.modConfig.MaxRampUpTime_ms
            
        # Now can use the ramp up duration to calculate the Ramp Up slope
        # Note: RampUpDur_ms is in miliseconds
        getUpSlope = RampPeakVolts / (RampUpDur_ms / 1000)
        
        return getUpSlope

    '''
    '''
    def GetDownSlope(self, RampPeakVolts):
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            RampPeriod = 1 / self.modConfig.AfAxialResFreq
            
        if (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem): 
            RampPeriod = 1 / self.modConfig.AfTransResFreq

        # Get the initial calculated ramp-Down duration
        # based Downon the Max Ramp-Down time setting
        RampDownPeriods = self.modConfig.RampDownNumPeriodsPerVolt * RampPeakVolts
    
        if (RampDownPeriods < self.modConfig.MinRampDown_NumPeriods):    
            RampDownPeriods = self.modConfig.MinRampDown_NumPeriods
            
        if (RampDownPeriods > self.modConfig.MaxRampDown_NumPeriods):
            RampDownPeriods = self.modConfig.MaxRampDown_NumPeriods
        
        # Now calculate the RampDuration from this (ramp duration is in SECONDS)
        RampDuration = RampDownPeriods * RampPeriod
        getDownSlope = RampPeakVolts / RampDuration
        
        return getDownSlope

    '''
    '''
    def RoundSlopeToPeriod(self, Slope, PeakVoltage, SineFreq):
        # If a zero slope is put in, output a zero slope
        if (Slope == 0):
            return 0
            
        # Slope is non-zero, calculate the number of whole periods closest
        # to that slope
        NumPeriods = PeakVoltage / Slope * SineFreq
    
        # Recalculate the slope from NumPeriods
        roundSlopeToPeriod = PeakVoltage * SineFreq / NumPeriods
    
        return roundSlopeToPeriod

    '''
    '''
    def setSlope(self, UpSlope, DownSlope):
        # Determine what the Up & Down slopes should be
        if (UpSlope == -1):
            # No ramp-up slope inputed.
            # Set ramp-up slope depending on the Ramp Peak voltage
            UpSlope = self.GetUpSlope(self.modConfig.waveForms['AFRAMPUP'].PeakVoltage)
        
        # Set the Slope Up
        self.modConfig.waveForms['AFRAMPUP'].Slope = UpSlope
    
        # Update the ADWIN AF form
        self.modConfig.processData.rampUpSlope = self.modConfig.waveForms['AFRAMPUP'].Slope
        
        if (DownSlope == -1):    
            # No ramp-down slope inputed.
            # Set ramp-down slope depending on the Ramp Peak voltage
            DownSlope = self.GetDownSlope(self.modConfig.waveForms['AFRAMPDOWN'].PeakVoltage)
                
        # Round down slope to the nearest period value
        DownSlope = self.RoundSlopeToPeriod(DownSlope, 
                                       self.modConfig.waveForms['AFRAMPDOWN'].PeakVoltage, 
                                       self.modConfig.waveForms['AFRAMPDOWN'].SineFreqMin)
        
        # Set the Slope Down
        self.modConfig.waveForms['AFRAMPDOWN'].Slope = DownSlope
        
        # Update the ADWIN AF form
        self.modConfig.processData.rampDownSlope = self.modConfig.waveForms['AFRAMPDOWN'].Slope
    
        # Update Up and Down slope on the GUI
        guiStr = 'ADWinAFControl'
        guiStr += ':Up Slope = ' + "{:.1f}".format(self.modConfig.processData.rampUpSlope)
        guiStr += ':Down Slope = ' + "{:.1f}".format(self.modConfig.processData.rampDownSlope)
        self.modConfig.queue.put(guiStr)
                
        return
    
    '''
    '''
    def setIORate(self, IORate, PeakHangTime, Freq):
        if (IORate == -1):    
            # No IORate given, use the default wave object's IORates
            IORate = self.modConfig.waveForms['AFRAMPUP'].IORate
            
            # Propagate this IOrate to the two other ADWIN AF wave objects
            self.modConfig.waveForms['AFRAMPDOWN'].IORate = IORate
            self.modConfig.waveForms['AFMONITOR'].IORate = IORate
                        
        else:        
            # Update all the ADWIN AF wave objects' IORates
            self.modConfig.waveForms['AFRAMPUP'].IORate = IORate
            self.modConfig.waveForms['AFRAMPDOWN'].IORate = IORate
            self.modConfig.waveForms['AFMONITOR'].IORate = IORate
        
        

        # Update the form with this IORate
        respStr = 'ADWinAFControl:Ramp Rate = ' + "{:.1f}".format(IORate)
        
        # Update the TimeSteps of all three ADWIN AF wave objects
        self.modConfig.waveForms['AFRAMPUP'].TimeStep = 1 / IORate
        self.modConfig.waveForms['AFRAMPDOWN'].TimeStep = 1 / IORate
        self.modConfig.waveForms['AFMONITOR'].TimeStep = 1 / IORate
            
        # Check to see if a PeakHangTime was inputed
        if (PeakHangTime == -1):    
            # Calculate 100 periods worth of peak hang time in miliseconds
            PeakHangTime = self.modConfig.HoldAtPeakField_NumPeriods * 1 / Freq * 1000
        
        # Need to prevent to small of a peak hang time (time needs to be > 100 ms)
        if (PeakHangTime < 100):
            PeakHangTime = 100        
                
        # Update the form
        respStr += ':Ramp Peak Duration = ' + "{:.1f}".format(PeakHangTime)         
        self.modConfig.queue.put(respStr)
        
        return PeakHangTime
    
    '''
    '''
    def setPredictedDuration(self, ClipTest, PeakHangTime, Verbose):        
    
        if (self.modConfig.waveForms['AFRAMPUP'].PeakVoltage == 0):        
            return False
                    
        self.modConfig.waveForms['AFRAMPUP'].Duration = self.modConfig.waveForms['AFRAMPUP'].PeakVoltage / self.modConfig.waveForms['AFRAMPUP'].Slope * 1000
        
        
                           
        self.modConfig.waveForms['AFRAMPDOWN'].Duration = self.modConfig.waveForms['AFRAMPDOWN'].PeakVoltage / self.modConfig.waveForms['AFRAMPDOWN'].Slope * 1000
                
    
        # Set the AF Ramp cycle total duration + 200 ms for kicks & giggles    
        self.modConfig.waveForms['AFMONITOR'].Duration = self.modConfig.waveForms['AFRAMPUP'].Duration + self.modConfig.waveForms['AFRAMPDOWN'].Duration + PeakHangTime + 200                                              
                       
        # Determine the Ramp mode
        if (ClipTest == True):
            RampMode = 3        
        elif ((Verbose == True) or (self.modConfig.EnableAFAnalysis == True)): 
            RampMode = 2        
        else:
            RampMode = 1
    
        # Display this duration on the form
        respStr = 'ADWinAFControl:Ramp Up Duration = ' + "{:.1f}".format(self.modConfig.waveForms['AFRAMPUP'].Duration)
        respStr += ':Ramp Down Duration = ' + "{:.1f}".format(self.modConfig.waveForms['AFRAMPDOWN'].Duration)
        respStr += ':Total Ramp Duration = ' + "{:.1f}".format(self.modConfig.waveForms['AFMONITOR'].Duration)
        self.modConfig.queue.put(respStr)
    
        return True, RampMode
    
    '''
    '''
    def DoRampADWIN_WithParameterLogging(self,
                                         MonitorWave,
                                         UpWave,
                                         DownWave,
                                         PeakField,
                                         HangeTime = 0,
                                         RampMode = 1,
                                         RampDownMode = 0,
                                         DoDCFieldRecord = False,
                                         RetryNumber = 0):
        
        # Do a double check real quick of the max ramp & monitor voltages
        if (((self.ActiveCoilSystem == self.modConfig.AxialCoilSystem) and
             (self.modConfig.AfAxialRampMax == -1) or
             (self.modConfig.AfAxialMonMax == -1) and
             (RampMode != 3)) or
            ((self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem) and
             (self.modConfig.AfTransRampMax == -1) or
             (self.modConfig.AfTransMonMax == -1) and
             (RampMode != 3)) or
            ((self.ActiveCoilSystem == self.modConfig.IRMAxialCoilSystem) and
             (self.modConfig.AfAxialRampMax == -1) or
             (self.modConfig.AfAxialMonMax == -1) and
             (RampMode != 3))):
            errorStr = 'The Maximum Ramp voltages allowed for the ADWIN AF system '
            errorStr += 'have not been set yet.  Please perform an AF Clipping-Test now.'
            raise ValueError(errorStr)
        
        # Before doing anything with the ADWIN board, get the AF coil temperatures
        if self.modConfig.EnableT1:    
            Temp1 = self.DoDAQIO(self.modConfig.AnalogT1)
            Temp1 = Temp1 * self.modConfig.TSlope - self.modConfig.Toffset
                
        
        if self.modConfig.EnableT2:
            Temp2 = self.DoDAQIO(self.modConfig.AnalogT2)        
            Temp2 = Temp2 * self.modConfig.TSlope - self.modConfig.Toffset
    
        tempStr = 'ADWinAFControl'
        tempStr += ':T1 = ' + "{:.2f}".format(Temp1)
        tempStr += ':T2 = ' + "{:.2f}".format(Temp2)
        self.modConfig.queue.put(tempStr)
        
        return True
    
    '''    
    '''
    def doRampADWin(self,
                    MonitorWave,
                    UpWave,
                    DownWave,
                    PeakField,
                    HangeTime = 0,
                    RampMode = 1,
                    RampDownMode = 0,
                    DoDCFieldRecord = False):
        
        status = self.DoRampADWIN_WithParameterLogging(MonitorWave,
                                                       UpWave,
                                                       DownWave,
                                                       PeakField,
                                                       HangeTime,
                                                       RampMode,
                                                       RampDownMode,
                                                       DoDCFieldRecord)
        
        return status
    
    '''
    '''
    def executeRamp(self, AFCoilSystem,
                          PeakValue,
                          UpSlope = -1.0,
                          DownSlope = -1.0,
                          IORate = -1,
                          PeakHangTime = -1.0,
                          CalRamp = True,
                          ClipTest = False,
                          Verbose = False,
                          DoDCFieldRecord = False):

        if not self.modConfig.EnableAF:
            messageStr = 'Warning: AF Module is currently disabled.  AF Ramp will now abort.'
            return messageStr
    
        '''
            Based on AFCoilSystem, set the active coil system
            and set optCoil radio button on frmADWIN_AF
            The optCoil Click routine will set the frequency to use
        '''
        self.ActiveCoilSystem = AFCoilSystem
        
        respStr = self.setActiveCoil()
                    
        # Check to see if this is a calibrated ramp
        RampDownMode, chkClippingTest = self.checkCalibratedRamp(respStr, CalRamp, PeakValue, ClipTest)

        # Set the peak values now
        self.SetPeakValues(chkClippingTest)
        
        # Save the peak values to wave objects
        self.modConfig.waveForms['AFRAMPUP'].PeakVoltage = self.modConfig.processData.ADwin_rampPeakVoltage  
        self.modConfig.waveForms['AFRAMPDOWN'].PeakVoltage = self.modConfig.processData.ADwin_rampPeakVoltage
        self.modConfig.waveForms['AFMONITOR'].PeakVoltage = self.modConfig.processData.ADwin_rampPeakVoltage
        
        Freq = self.computeCoilFrequency()

        self.setSlope(UpSlope, DownSlope)        
        
        # Set the IO Rate
        PeakHangTime = self.setIORate(IORate, PeakHangTime, Freq)
        
        # Set the predicted durations for the various pieces of the ramp cycle
        ramp_in_progress, RampMode = self.setPredictedDuration(ClipTest, PeakHangTime, Verbose)
       
        ErrorCode = self.doRampADWin(self.modConfig.waveForms['AFMONITOR'],
                                     self.modConfig.waveForms['AFRAMPUP'],
                                     self.modConfig.waveForms['AFRAMPDOWN'],
                                     self.modConfig.processData.ADwin_peakField,
                                     PeakHangTime, 
                                     RampMode,
                                     RampDownMode, 
                                     DoDCFieldRecord) 
        
        # Unlock the coils
        respStr = 'ADWinAFControl:Coil Status = False'
        self.modConfig.queue.put(respStr)
        
        ramp_in_progress = False
        
        return 
        
    '''--------------------------------------------------------------------------------------------
                        
                        public API Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def refreshTs(self):
        temp1Str = "T1="
        temp2Str = "T2="
        
        if self.modConfig.EnableT1:
            temp1 = self.DoDAQIO(self.modConfig.AnalogT1)
            temp1 = temp1 * self.modConfig.TSlope - self.modConfig.Toffset
            temp1Str += "{:.2f}".format(temp1)

        if self.modConfig.EnableT2:
            temp2 = self.DoDAQIO(self.modConfig.AnalogT2)
            temp2 = temp1 * self.modConfig.TSlope - self.modConfig.Toffset
            temp2Str += "{:.2f}".format(temp2)
        
        return temp1Str, temp2Str
    
    '''
    '''
    def trySetRelays_ADwin(self, coilLabel):
        if self.modConfig.AFRelays_UseUpPosition:
            status = self.trySetRelays_ADwin_AFsAreUpPosition(coilLabel)
        else:
            status = self.trySetRelays_ADwin_AFsAreDownPosition(coilLabel)
            
        return status     

    '''
    '''
    def TrySetAllRelaysDown_ADwin(self):
        self.Set_Digout(0)
        return True

    '''
    '''
    def TrySetAllRelaysUp_ADwin(self):
        self.Set_Digout(63)
        return True

    '''
    '''
    def TrySetAllRelaysToDefaultPosition_ADwin(self):
        # Default position is opposite the AF Relay position
        # (If AF's are Relay Up, then Defaults are Relay down and vice versa)
        if self.modConfig.AFRelays_UseUpPosition:    
            status = self.TrySetAllRelaysDown_ADwin()
        
        else:    
            status = self.TrySetAllRelaysUp_ADwin()
        
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
            
        # Test RefreshTs
        elif (taskID == 2):
            temp1Str, temp2Str = self.refreshTs()
            print(temp1Str + '; ' + temp2Str)
            
        # Test RefreshTs
        elif (taskID == 3):
            respStr = self.cleanCoils(True)
            print(respStr)
            
                            
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        config = configparser.ConfigParser()
        config.read('C:\\Temp\\PaleonMag\\Settings\\Paleomag_v3_Hung.INI')
        processData = ProcessData()
        processData.config = config 
        modConfig = ModConfig(process=processData)
        
        currentPath = os.getcwd() + '\\'            
        devControl = ADWinControl(currentPath, modConfig=modConfig)
        devControl.runTask(3)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
        
        