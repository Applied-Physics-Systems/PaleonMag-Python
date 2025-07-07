'''
Created on Jan 28, 2025

@author: hd.nguyen
'''
import ctypes
import os
import time
import configparser
import math
import numpy as np

from enum import Enum
from Process.AdwinData import AdwinAfOutputParameters
from Process.AdwinData import AdwinAfInputParameters
from Process.AdwinData import AdwinAfRampStatus

from Forms.frm908AGaussmeter import frm908AGaussmeter
from Hardware.Device.AF_2GControl import AF_2GControl
from ADwin import ADwin, ADwinError
from Process.ProcessData import ProcessData
from Process.ModConfig import ModConfig
from Process.ModConfig import WaveForm
from Modules.ModAF_DAQ import ModAF_DAQ

MsecsBetweenBootAndInit = 300/1000
MsecsBetweenInitAndRun = 300/1000
MsecsBetweenRampEndAndReadRampOutputs = 300/1000

NoiseLevel = 5

Coil_Type = Enum('Coil_Type', ['Axial', 'Transverse', 'IRMAxial', 'IRMTrans', 'Unknown'])


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
        self.filePath = path.replace('\\Hardware\\Hardware\\', '\\Hardware\\')
        self.modConfig = modConfig
        self.WaveForms = {}
        self.AF2GControl = AF_2GControl(parent = parent, modConfig = self.modConfig)
        self.modAF_DAQ = ModAF_DAQ(self.filePath, parent = parent, modConfig = self.modConfig)
        self.ramp_outputs = AdwinAfOutputParameters()
        self.ramp_inputs = AdwinAfInputParameters()
        self.ramp_status = AdwinAfRampStatus() 
        
        self.ActiveCoilSystem = None
        self.Verbose = False
        self.ramp_in_progress = False
        
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
                        
                        Relay Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def tryGetADWIN_DigOutStatusByte(self):
        status = False
        
        self.adwin_digital_word = self.Get_Digout()
        
        if ((self.adwin_digital_word >= 0) and (self.adwin_digital_word < 256)):
            status = True
            
        return status
        
    '''
    '''
    def trySetRelays_ADwin_AFsAreUpPosition(self, coilLabel, do_irm_backfield = False):
        
        if (self.modConfig.AFSystem != 'ADWIN'):
            return False
        
        if (coilLabel == 'Axial'):
            relay_byte_id = ((2 ** (self.modConfig.AFAxialRelay.chanNum)) % 256)
        elif (coilLabel == 'Transverse'):
            relay_byte_id = ((2 ** (self.modConfig.AFTransRelay.chanNum)) % 256)
        elif (coilLabel == 'IRM Axial'):
            relay_byte_id = ((2 ** (self.modConfig.IRMRelay.ChanNum)) % 256)
        
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
    def trySetRelays_ADwin_AFsAreDownPosition(self, coilLabel, do_irm_backfield = False):
        
        if (self.modConfig.AFSystem != 'ADWIN'):
            return False        
        
        all_up_byte = (2 ** 6) - 1        
        if (coilLabel == 'Axial'):
            relay_byte_id = all_up_byte - ((2 ** (self.modConfig.AFAxialRelay.ChanNum)) % 256)
        elif (coilLabel == 'Transverse'):
            relay_byte_id = all_up_byte - ((2 ** (self.modConfig.AFTransRelay.ChanNum)) % 256)
        elif (coilLabel == 'IRM Axial'):
            relay_byte_id = all_up_byte - ((2 ** (self.modConfig.IRMRelay.ChanNum)) % 256)
        
        self.tryGetADWIN_DigOutStatusByte()
        
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
    def IsCorrect_AFRelay_position(self, CoilType):
        correctFlag = True
        out_byte = self.Get_Digout()
        
        if ((out_byte >= 0) and (out_byte < 64)):        
            status_byte = out_byte % 64                
        else:    
            correctFlag = False
        
        all_up_byte = (2 ** 6) - 1
        
        if (CoilType == Coil_Type.Axial):
            if (status_byte == all_up_byte - (2 ** (self.modConfig.AFAxialRelay.ChanNum))):            
                correctFlag = True                
            else:                
                correctFlag = False
                
        elif (CoilType == Coil_Type.Transverse):
            if (status_byte == all_up_byte - (2 ** (self.modConfig.AFTransRelay.ChanNum))):            
                correctFlag = True                
            else:                
                correctFlag = False
                
        elif (CoilType == Coil_Type.IRMAxial):
            if (status_byte == (not (2 ** (self.modConfig.AFAxialRelay.ChanNum))) and
                                (2 ** (self.modConfig.AFTransRelay.ChanNum))):            
                correctFlag = True                
            else:                
                correctFlag = False
                
        elif (CoilType == Coil_Type.IRMTrans):
            if (status_byte == (not (2 ** (self.modConfig.AFTransRelay.ChanNum))) and
                                (2 ** (self.modConfig.AFAxialRelay.ChanNum))):            
                correctFlag = True                
            else:                
                correctFlag = False
                
        else:
            correctFlag = True
        
        return correctFlag

    '''
    '''
    def TrySetRelays_ADwin(self, CoilType, do_irm_backfield = False):
        if self.modConfig.AFRelays_UseUpPosition:
            status = self.trySetRelays_ADwin_AFsAreUpPosition(CoilType, do_irm_backfield)        
        else:
            status = self.trySetRelays_ADwin_AFsAreDownPosition(CoilType, do_irm_backfield)
            
        return status

    '''--------------------------------------------------------------------------------------------
                        
                        ADWin board communication Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def DoDAQIO(self, channel, numValue=-10000, boolValue=False):
        retValue = 0
        
        if (channel.ChanType == 'DO'):
            self.modAF_DAQ.DigitalOut(channel, boolValue, True)
            
        elif (channel.ChanType == 'DI'):
            print('TODO')
            
        elif (channel.ChanType == 'AO'):
            self.modAF_DAQ.AnalogOut(channel.ChanNum, channel.RangeType, numValue)

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
    def ADWIN_BootBoard(self):
        try:
            if (self.adw.Test_Version() != 0):
                # Boot the ADWIN board                
                if (self.adw.Processor_Type() != 'T9'):
                    returnValue = self.adw.Boot(self.filePath + 'ADwin9.btl')
                    if (returnValue == 8000):
                        print('ADWin system boot')
                        return True
                    else:
                        print('ADWin system boot failed')
                        return False
            
            return True
        
        except:
            return False
    
    '''
    '''
    def ClearAll_Processes(self):
        
        TempBool = True
        for i in range(1, 11):
            returnValue = 1
            while (returnValue != 0):
                # Stop the process
                self.adw.Stop_Process(i)
                
                # Check process status
                returnValue = self.adw.Process_Status(i)
                
            # Process is stopped or doesn't exist
            # Clear the process
            returnValue = self.adw.Clear_Process(i)
            
            if (returnValue == 1):
                # Error occured
                TempBool = False
                
            TempBool &= True   
            
        return TempBool
    
    '''
    '''
    def setADWinProcess(self):
        # Boot the ADWIN board if it isn't already
        if not self.ADWIN_BootBoard():            
            return False
        
        # Now clear all the process on the ADWIN board
        self.ClearAll_Processes()
        
        time.sleep(MsecsBetweenBootAndInit)
        
        # Load the 1st process, the AF Ramp output
        fileName = self.filePath + 'sineout.T91'
        try:
            self.adw.Load_Process(fileName)

        # ReturnVal of 1 = OK, ReturnVal <> 1 = Error occurred
        except:
            raise ValueError('Failed to load process ' + fileName)
        
        return True
    
    '''
    '''
    def setADWinParameters(self, MonitorWave, 
                                 UpWave, 
                                 DownWave,
                                 HangeTime, 
                                 RampMode,
                                 RampDownMode):
        # Set the Slope Up and the Slope Down for the ramp cycle
        self.adw.Set_FPar(31, UpWave.Slope)
        self.ramp_inputs.Slope_Up = UpWave.Slope
        
        self.adw.Set_FPar(32, DownWave.Slope)
        self.ramp_inputs.Slope_Down = DownWave.Slope
        
        # Set the peak monitor voltage
        self.adw.Set_FPar(33, MonitorWave.PeakVoltage)
        self.ramp_inputs.Peak_Monitor_Voltage = MonitorWave.PeakVoltage
        
        # Set the Min & sine Wave freq
        self.adw.Set_FPar(34, MonitorWave.SineFreqMin)
        self.ramp_inputs.Resonance_Freq= MonitorWave.SineFreqMin
        
        # Set the Ramp Up suggested ramp output voltage peak limit
        self.adw.Set_FPar(35, UpWave.PeakVoltage)
        self.ramp_inputs.Peak_Ramp_Voltage= UpWave.PeakVoltage
        
        # Set the Absolute Max Ramp Output voltage
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            if (self.modConfig.AfAxialRampMax == -1):
                self.adw.Set_FPar(36, 10)
                self.ramp_inputs.Max_Ramp_Voltage = 10
            else:
                self.adw.Set_FPar(36, self.modConfig.AfAxialRampMax)
                self.ramp_inputs.Max_Ramp_Voltage = self.modConfig.AfAxialRampMax
                
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            if (self.modConfig.AfTransRampMax == -1):
                self.adw.Set_FPar(36, 10)
                self.ramp_inputs.Max_Ramp_Voltage = 10
            else:
                self.adw.Set_FPar(36, self.modConfig.AfTransRampMax)
                self.ramp_inputs.Max_Ramp_Voltage = self.modConfig.AfTransRampMax

        elif (self.ActiveCoilSystem == self.modConfig.IRMAxialCoilSystem):
            if (self.modConfig.AfAxialRampMax == -1):
                self.adw.Set_FPar(36, 10)
                self.ramp_inputs.Max_Ramp_Voltage = 10
            else:
                self.adw.Set_FPar(36, self.modConfig.AfAxialRampMax)
                self.ramp_inputs.Max_Ramp_Voltage = self.modConfig.AfAxialRampMax
        
        # Set the absolute max monitor input voltage to accept
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            if (self.modConfig.AfAxialMonMax == -1):
                self.adw.Set_FPar(37, 10)
                self.ramp_inputs.Max_Monitor_Voltage = 10
            else:
                self.adw.Set_FPar(37, self.modConfig.AfAxialMonMax)
                self.ramp_inputs.Max_Monitor_Voltage = self.modConfig.AfAxialMonMax
                
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            if (self.modConfig.AfTransMonMax == -1):
                self.adw.Set_FPar(37, 10)
                self.ramp_inputs.Max_Monitor_Voltage = 10
            else:
                self.adw.Set_FPar(37, self.modConfig.AfTransMonMax)
                self.ramp_inputs.Max_Monitor_Voltage = self.modConfig.AfTransMonMax

        elif (self.ActiveCoilSystem == self.modConfig.IRMAxialCoilSystem):
            if (self.modConfig.AfAxialMonMax == -1):
                self.adw.Set_FPar(37, 10)
                self.ramp_inputs.Max_Monitor_Voltage = 10
            else:
                self.adw.Set_FPar(37, self.modConfig.AfAxialMonMax)
                self.ramp_inputs.Max_Monitor_Voltage = self.modConfig.AfAxialMonMax
        
        # Set Slope = 1 to prevent crashes
        if (MonitorWave.Slope == 0):
            MonitorWave.Slope = 1    
        if (UpWave.Slope == 0):
            UpWave.Slope = 1    
        if (DownWave.Slope == 0):
            DownWave.Slope = 1    
        if (UpWave.IORate == 0):
            UpWave.IORate = 1

        # Set the RampMode Parameter
        self.adw.Set_Par(31, RampMode)
        self.ramp_inputs.ramp_mode = RampMode
        
        # Set the AF Ramp DAC output port parameter
        self.adw.Set_Par(32, UpWave.Channel.ChanNum)
        self.ramp_inputs.Output_Port_Number = UpWave.Channel.ChanNum
        
        # Set the AF monitor ADC input port parameter
        self.adw.Set_Par(33, MonitorWave.Channel.ChanNum)
        self.ramp_inputs.Monitor_Port_Number = MonitorWave.Channel.ChanNum
        
        # Set the AF ramp rate - with conversion of Hz to ADWIN Process delay with a 25 ns processor
        # cycling time
        self.adw.Set_Par(34, math.ceil(1000000 / UpWave.IORate * 40))
        self.ramp_inputs.Process_Delay = math.ceil(1000000 / UpWave.IORate * 40)
        
        # Set the AF Noise level
        self.adw.Set_Par(35, NoiseLevel)
        self.ramp_inputs.Noise_Level = NoiseLevel
        
        # Set the number of periods to hang at peak
        self.adw.Set_Par(36, math.ceil(HangeTime * MonitorWave.SineFreqMin / 1000))
        self.ramp_inputs.Number_Periods_Hang_At_Peak = math.ceil(HangeTime * MonitorWave.SineFreqMin / 1000)
        
        # Set the number of periods to ramp down with
        self.adw.Set_Par(37, math.ceil(DownWave.PeakVoltage * MonitorWave.SineFreqMin / DownWave.Slope))
        self.ramp_inputs.Number_Periods_Ramp_Down = math.ceil(DownWave.PeakVoltage * MonitorWave.SineFreqMin / DownWave.Slope)
        
        # Set the Ramp-down mode:
        # 0 = use the Ramp down slope
        # 1 = use the Ramp down number of periods
        self.adw.Set_Par(38, RampDownMode)
        self.ramp_inputs.ramp_down_mode = RampDownMode
        
        return

    '''
    '''
    def getADWinParameters(self,
                           MonitorWave,
                           UpWave,
                           DownWave):
        
        # Get the final point of the DAC output (OUTCOUNT)
        DownWave.CurrentPoint = self.adw.Get_Par(5)
        self.ramp_outputs.Total_Output_Points = DownWave.CurrentPoint
        
        # Clip off 10 points from the end of the data set
        DownWave.CurrentPoint = DownWave.CurrentPoint - 10
    
        # Get the point # of the last ADC input point from the INCOUNT parameter
        MonitorWave.CurrentPoint = self.adw.Get_Par(6)
        self.ramp_outputs.Total_Monitor_Points = MonitorWave.CurrentPoint
    
        # Clip off 10 points from the end of the data set
        MonitorWave.CurrentPoint = MonitorWave.CurrentPoint - 10
        
        # Get the point # of the last DAC output point from the Ramp Up process
        UpWave.CurrentPoint = self.adw.Get_Par(7)
        self.ramp_outputs.Ramp_Up_Last_Point = UpWave.CurrentPoint
    
        # Get the first point # of the DAC output Ramp Down process
        DownWave.StartPoint = self.adw.Get_Par(8)
    
        # Get the max input voltage reached
        MonitorWave.CurrentVoltage = self.adw.Get_FPar(4)
        self.ramp_outputs.Measured_Peak_Monitor_Voltage = MonitorWave.CurrentVoltage
        
        # Get the max output voltage reached
        UpWave.CurrentVoltage = self.adw.Get_FPar(5)
        self.ramp_outputs.Max_Ramp_Voltage_Used = UpWave.CurrentVoltage
    
        # Get the Down slope (may now be different depending on the ramp mode)
        DownWave.Slope = self.adw.Get_FPar(32)
        self.ramp_outputs.Actual_Slope_Down_Used = DownWave.Slope
    
        # Get the Ramp process Time steps from the ADWIN board - ACOUT_TIMESTEP
        UpWave.TimeStep = self.adw.Get_FPar(6)
        MonitorWave.TimeStep = UpWave.TimeStep
        self.ramp_outputs.Time_Step_Between_Points = UpWave.TimeStep
    
        # Get the actual used points per period from the ADWIN board - NSAMPLES
        MonitorWave.PtsPerPeriod = self.adw.Get_FPar(7)
        self.ramp_outputs.Number_Points_Per_Period = MonitorWave.PtsPerPeriod
        
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            self.ramp_outputs.Coil = 'Axial'
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            self.ramp_outputs.Coil = 'Transverse'
        else:
            self.ramp_outputs.Coil = 'Unknown'
            
        zero_threshold = 4 * NoiseLevel * (MonitorWave.RangeMax - MonitorWave.RangeMin) / (2 ** 16)    
        noise_threshold = 0.005 * MonitorWave.PeakVoltage
    
        if (noise_threshold < zero_threshold):    
            noise_threshold = zero_threshold
            
        # Check for threshold
        self.ramp_status.WasSuccessful = True
        if (self.ramp_outputs.Measured_Peak_Monitor_Voltage < zero_threshold):
            self.ramp_status.WasSuccessful = False
            
        elif (((self.ramp_inputs.Peak_Monitor_Voltage - self.ramp_outputs.Measured_Peak_Monitor_Voltage) > noise_threshold) and
              (self.ramp_inputs.ramp_mode < 3)):
            self.ramp_status.WasSuccessful = False
            
        
        elif (((self.ramp_outputs.Measured_Peak_Monitor_Voltage - self.ramp_inputs.Peak_Monitor_Voltage) > noise_threshold) and 
              (self.ramp_inputs.ramp_mode < 3)):                                       
            # Overshoot monitor voltage error - only for MONITORED ramps
            self.ramp_status.WasSuccessful = False
                
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''                                        
    '''
    '''
    def setPeak_monitor(self, paramList):
        calDone = paramList[0]
        activeCoilSystem = paramList[1]
        monMax = paramList[2]
        
        # Check to see if this AF coil has been calibrated
        # and if it needs to be
        if ((not calDone) and (self.modConfig.processData.ADwin_optCalRamp == 1)):
            # Tell user they need to do a calibration
            # on the AF Axial/Transverse coil
            messageStr = 'AF Coil has not been calibrated yet. The current AF '
            messageStr += 'ramp process has been terminated.\n\n'
            messageStr += 'Would you like to calibrate the AF Coil right now?'
            raise IOError(messageStr) 
        
        # Now check to see if the user wants a calibrated, monitored ramp
        if (self.modConfig.processData.ADwin_optCalRamp == 1):
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
                respStr += ':Peak Field = ' + "{:.1f}".format(self.modConfig.processData.ADwin_peakField)
                
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
            respStr += ':OptCalRamp = 1'
            self.modConfig.processData.ADwin_optCalRamp = 1
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
            respStr += ':OptCalRamp = 0'
            self.modConfig.processData.ADwin_optCalRamp = 0
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
            RampUpDur_ms = math.ceil(RampPeakVolts / self.modConfig.AxialRampUpVoltsPerSec * 1000)    
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            # Need to multiply by 1000 to convert seconds to miliseconds
            RampUpDur_ms = math.ceil(RampPeakVolts / self.modConfig.TransRampUpVoltsPerSec * 1000)    
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
        RampDownPeriods = math.ceil(self.modConfig.RampDownNumPeriodsPerVolt * RampPeakVolts)
    
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
        guiStr += ':Up Slope = ' + "{:.6f}".format(self.modConfig.processData.rampUpSlope)
        guiStr += ':Down Slope = ' + "{:.6f}".format(self.modConfig.processData.rampDownSlope)
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
    def ValidSensorTemp(self, Temp1, Temp2):
        # Default as having no NoError
        NoErrorT1 = True
        NoErrorT2 = True
        
        # Test to see if Temp1 or Temp2 are within 20 degrees of the arithmetic
        # inverse of the their offset temperature setting
        if (math.fabs(self.modConfig.Toffset + Temp1) < 20): 
            NoErrorT1 = False
            
        if (math.fabs(self.modConfig.Toffset + Temp2) < 20): 
            NoErrorT2 = False
        
        return (NoErrorT1 and NoErrorT2)
    
    '''
    '''
    def getCoilTemperature(self):
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

        # Check Temperature to see if it is not zeroed (gone within 20 deg of -1 * Toffset)
        if not self.ValidSensorTemp(Temp1, Temp2):
            tempStr = 'ADWinAFControl:LowTemp:AF Temperature sensors reading temperature below minimum limit.'
            self.modConfig.queue.put(tempStr)

        return Temp1, Temp2
        
    
    '''
    '''
    def checkCoilTemperature(self):
        Temp1, Temp2 = self.getCoilTemperature()
                    
        if (self.modConfig.EnableT1 or self.modConfig.EnableT2):
            outRangeFlag = False
            while ((Temp1 >= self.modConfig.Thot) or (Temp2 >= self.modConfig.Thot)):
                if not outRangeFlag: 
                    tempStr = 'ADWinAFControl:HighTemp = Too hot! The AF\ndegaussing unit is\nabove ' + "{:.1f}".format(self.modConfig.Thot) 
                    self.modConfig.queue.put(tempStr)
                    outRangeFlag = True
                
                while ((Temp1 >= (self.modConfig.Thot - 5)) or (Temp2 >= (self.modConfig.Thot - 5))):
                    time.sleep(1)
                    
                    Temp1, Temp2 = self.getCoilTemperature()

            if outRangeFlag:
                tempStr = 'ADWinAFControl:Clear = '
                self.modConfig.queue.put(tempStr)
        
        return
    
    '''
    '''
    def setCoilType(self):
        if (self.ActiveCoilSystem == self.modConfig.AxialCoilSystem):
            coilType = Coil_Type.Axial
            self.ramp_inputs.Coil = 'Axial'
        elif (self.ActiveCoilSystem == self.modConfig.TransverseCoilSystem):
            coilType = Coil_Type.Transverse
            self.ramp_inputs.Coil = 'Transverse'
        elif (self.ActiveCoilSystem == self.modConfig.IRMAxialCoilSystem):
            coilType = Coil_Type.IRMAxial
            self.ramp_inputs.Coil = 'IRM Axial'
        else:
            coilType = Coil_Type.Unknown
            self.ramp_inputs.Coil = 'Unknown'
            
        return coilType
        
    '''
    '''
    def recordDCField(self, MonitorWave):
        # Set the DCFIeld Wave to a new wave object
        DCFieldWave = WaveForm()

        '''
            Initialize the DC field record
            For duration - put in the estimated duration of the ramp cycle
            plus an additional 200 miliseconds
        '''
        frm908AGaussmeter.InitializeDCFieldRecord(DCFieldWave, MonitorWave.Duration + 200)
                                       
        # Start the DC Field record and grab the
        # status of the start process
        DCFieldStatus = frm908AGaussmeter.StartDCFieldRecord(DCFieldWave)
        
        return DCFieldStatus, DCFieldWave
    
    '''
        Verify the AF Relay position
    '''
    def verifyAFRelayPosition(self, CoilType):
    
        if not self.IsCorrect_AFRelay_position(CoilType):
            if (CoilType == Coil_Type.IRMAxial):
                relayStatus = self.TrySetRelays_ADwin(CoilType.name, True)       # True = use backfield
            else:
                relayStatus = self.TrySetRelays_ADwin(CoilType.name)

            if not relayStatus:
                errorMessage = 'Unable to set AF Relays to the correct position for ADwin AF'
                raise ValueError(errorMessage)
                                    
        return
    
    '''
    '''
    def GetAdwinData(self, DataNo, startIndex, Count):
        try:
            dataCArray = self.adw.GetData_Long(DataNo, startIndex, Count)
            dataNpArray = np.ctypeslib.as_array(dataCArray)
            return dataNpArray
         
        except:
            print('Error in getting data from adwin64.dll')
            return np.array([])
            
    
    '''
    '''
    def FetchAFData_FromAdwin(self):
        
        # Pause for 1/4 the duration of the last ramp cycle for Ramp Data arrays
        # to become available
        time.sleep(self.ramp_outputs.GetTotalRampDuration() / 4)
        
        # Set N = the maximum # of data points that can be stored by
        # the ADWIN code = MAXALLOWEDDATAPTS
        self.adw.Get_Par(11)
        
        num_points = self.ramp_outputs.Total_Monitor_Points
        
        inDataArray = self.GetAdwinData(31, 1, num_points)
        if (inDataArray.size != 0): 
            np.savetxt(self.modConfig.AfRampDataPath + "InAdwinData.csv", inDataArray, delimiter=",")
        
        outDataArray = self.GetAdwinData(32, 1, num_points)
        if (outDataArray.size != 0):
            np.savetxt(self.modConfig.AfRampDataPath + "OutAdwinData.csv", outDataArray, delimiter=",")
                
        return
    
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
        self.checkCoilTemperature()
        
        self.setADWinProcess()
        
        CoilType = self.setCoilType()
        
        self.setADWinParameters(MonitorWave, 
                                UpWave, 
                                DownWave,
                                HangeTime, 
                                RampMode,
                                RampDownMode)
        
        # Calculate the Up & Down wave durations
        UpWave.Duration = UpWave.PeakVoltage / UpWave.Slope * 1000
        DownWave.Duration = DownWave.PeakVoltage / DownWave.Slope * 1000
        
        # Set Monitor Wave Duration
        MonitorWave.Duration = UpWave.Duration + DownWave.Duration + HangeTime + 200

        time.sleep(MsecsBetweenInitAndRun)
        
        # Has the user selected to record the DC field?
        DCFieldStatus = False
        if DoDCFieldRecord:
            DCFieldStatus, DCFieldWave = self.recordDCField(MonitorWave)
            
        self.verifyAFRelayPosition(CoilType)
        
        # Start the Ramp process
        self.adw.Start_Process(1)
        
        # Pause 100 ms
        time.sleep(0.1)
        
        # Loop while checking the ramp process on the ADWIN board every 200 milliseconds
        TempL = 0
        while (TempL != 7):
            # Pause 200 ms
            time.sleep(0.2)
            
            TempL = self.adw.Get_Par(4)
        
        time.sleep(MsecsBetweenRampEndAndReadRampOutputs)
        
        # Stop the DC Field record if the user has set for it to be recorded
        # and the record was started successfully
        if ((DCFieldStatus == True) and (DoDCFieldRecord == True)):
            # Stop the DC Field record
            frm908AGaussmeter.StopDCFieldRecord(DCFieldWave, True)
        
        # Pause an additional 200 ms
        time.sleep(0.2)
        
        # Now Get the basic parameters that we need to know about the AF Ramp
        # whether or not we're in debug or clipping mode
        self.getADWinParameters(MonitorWave,
                                UpWave,
                                DownWave)
        
        # Save data to file if requested
        if (RampMode > 1):
            if (self.Verbose or self.modConfig.EnableAFAnalysis):
                self.FetchAFData_FromAdwin()
        
        if (RampMode == 3):    
            # Save max monitor voltage to MonitorWave
            #Save max ramp voltage to UpWave        
            MonitorWave.CurrentVoltage = self.ramp_outputs.Measured_Peak_Monitor_Voltage
            UpWave.CurrentVoltage = self.ramp_outputs.Max_Ramp_Voltage_Used
        
        if not self.ramp_status.WasSuccessful:
            print('TODO')
        
        # Clear all processes on the ADWIN board
        self.ClearAll_Processes()
        
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

        self.Verbose = Verbose
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
        self.modConfig.waveForms['AFMONITOR'].PeakVoltage = self.modConfig.processData.ADwin_monitorTrigVolt
        
        Freq = self.computeCoilFrequency()

        self.setSlope(UpSlope, DownSlope)        
        
        # Set the IO Rate
        PeakHangTime = self.setIORate(IORate, PeakHangTime, Freq)
        
        # Set the predicted durations for the various pieces of the ramp cycle
        self.ramp_in_progress, RampMode = self.setPredictedDuration(ClipTest, PeakHangTime, Verbose)
       
        ErrorCode = self.doRampADWin(self.modConfig.waveForms['AFMONITOR'],
                                     self.modConfig.waveForms['AFRAMPUP'],
                                     self.modConfig.waveForms['AFRAMPDOWN'],
                                     self.modConfig.processData.ADwin_peakField,
                                     PeakHangTime, 
                                     RampMode,
                                     RampDownMode, 
                                     DoDCFieldRecord)
         
        if not self.TrySetAllRelaysToDefaultPosition_ADwin():
            raise ValueError('Fail to set all relays to default position')
        
        # Unlock the coils
        respStr = 'ADWinAFControl:Coil Status = False'
        self.modConfig.queue.put(respStr)
        
        self.ramp_in_progress = False
        
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

    '''
    '''
    def SwitchOff_AllRelays(self):
        self.Set_Digout(63)
        return

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
        
        