'''
Created on Feb 3, 2025

@author: hd.nguyen
'''
import wx

from Forms.frmSettings import frmSettings
from Forms.frmFileSave import frmFileSave
from Forms.frmAFTuner import frmAFTuner
from Forms.frmCalibrateCoils import frmCalibrateCoils
from Forms.frm908AGaussmeter import frm908AGaussmeter

class frmADWIN_AF(wx.Frame):
    '''
    classdocs
    '''
    ramp_in_progress = False

    def __init__(self, parent):
        '''
        Constructor
        '''        
        self.parent = parent
        if (parent != None):
            super(frmADWIN_AF, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmADWIN_AF, self).__init__(parent, wx.NewIdRef())
        
        self.IORate = 50000   
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        XOri = 10
        YOri = 10        
        # First Column, First box
        box1Length = 150
        box1Height = 130
        wx.StaticBox(panel, -1, 'Active Coil', pos=(XOri, YOri), size=(box1Length, box1Height))
        self.GUI_ActiveCoil(panel, XOri, YOri)
        
        # First Column, Second box
        box2Height = 165
        YOri = YOri + box1Height + 20
        wx.StaticBox(panel, -1, 'AF Ramp Mode', pos=(XOri, YOri), size=(box1Length, box2Height))
        self.GUI_AFRampMode(panel, XOri, YOri)
                
        # First Column, Third box
        box3Height = 215
        YOri = YOri + box2Height + 20
        wx.StaticBox(panel, -1, 'Shiny Buttons', pos=(XOri, YOri), size=(box1Length, box3Height))
        self.GUI_ShinyButtons(panel, XOri, YOri)
                
        # Second Column, First box
        YOri = 10
        XOri = XOri + box1Length + 10
        box2Length = 2*box1Length
        box4Height = 110 
        wx.StaticBox(panel, -1, 'AF Coil Temperature', pos=(XOri, YOri), size=(box2Length, box4Height))
        self.GUI_AFCoilTemperature(panel, XOri, YOri)
        
        # Second Column, Second box                
        XOri = box1Length + 20
        YOri += box4Height + 20
        box5Height = 500
        wx.StaticBox(panel, -1, 'AF Ramp Setup', pos=(XOri, YOri), size=(box2Length, box5Height))
        self.GUI_AFRampSetup(panel, XOri, YOri)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)

        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
                                
        self.SetSize((500, 690))
        self.SetTitle('ADWIN AF Ramp')
        self.Centre()
        self.Show(True)
    
    '''
    '''
    def GUI_AFRampSetup(self, panel, XOri, YOri):
        XOri += 10
        btnLength = 130
        btnHeight = 30
        txtOffset = 5
        txtBoxHeight = 25
        
        YOffset = 35
        txtBoxXOffset = 160
        smallTxtBoxLength = 70
                
        wx.StaticText(panel, label='Sine Freq. (Hz)', pos=(XOri, YOri + YOffset + txtOffset))
        self.sineFreqTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        self.sineFreqTBox.Bind(wx.EVT_TEXT, self.onFreqChanged)
        wx.StaticText(panel, label='Time at Peak (ms)', pos=(XOri, YOri + 2*YOffset + txtOffset))
        self.timePeakTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 2*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        self.timePeakTBox.Bind(wx.EVT_TEXT, self.onRampPeakVoltage)
        wx.StaticText(panel, label='Ramp IO Rate (Hz)', pos=(XOri, YOri + 3*YOffset + txtOffset))
        self.rampRateTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 3*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Peak Field', pos=(XOri, YOri + 4*YOffset + txtOffset))
        self.peakFieldTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 4*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Units', pos=(XOri + txtBoxXOffset + smallTxtBoxLength  + 10, YOri + 4*YOffset - 15))
        self.peakUnitCBox = wx.ComboBox(panel, value='G', pos=(XOri + txtBoxXOffset + smallTxtBoxLength + 10, YOri + 4*YOffset), size=(40,22), choices=['G'])        
        wx.StaticText(panel, label='Peak Monitor Voltage', pos=(XOri, YOri + 5*YOffset + txtOffset))
        self.peakMonitorTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 5*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Peak Ramp Voltage', pos=(XOri, YOri + 6*YOffset + txtOffset))
        self.peakRampTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 6*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        self.peakRampTBox.Bind(wx.EVT_TEXT, self.onRampPeakVoltageChange)
        lblList = ['Uncalibrated Ramp (use Peak Monitor Voltage)', 
                   'Calibrated Ramp (use Peak Field value)']     
        self.calibrateRBox = wx.RadioBox(panel, label = '', pos = (XOri, YOri + 7*YOffset), choices = lblList ,
                                majorDimension = 1, style = wx.RA_SPECIFY_COLS)
        self.calibrateRBox.SetSelection(1)        
        self.calSlopeChkBox = wx.CheckBox(panel, label='Calculate Ramp Slopes Automatically', pos=(XOri, YOri + 9*YOffset))
        self.calSlopeChkBox.Bind(wx.EVT_CHECKBOX, self.onAutoSlope)
        wx.StaticText(panel, label='Duration\n    (ms)', pos=(XOri + txtBoxXOffset + smallTxtBoxLength, YOri + 9*YOffset + txtOffset))
        
        wx.StaticText(panel, label='Ramp Up Slope (volts/sec)', pos=(XOri, YOri + 10*YOffset + txtOffset))
        self.rampUpSlopeTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 10*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        self.rampUpSlopeTBox.Bind(wx.EVT_TEXT, self.onRampUpSlope)
        self.rampUpLabel = wx.StaticText(panel, label='', pos=(XOri + txtBoxXOffset + smallTxtBoxLength + 10, YOri + 10*YOffset + txtOffset))
        
        wx.StaticText(panel, label='Ramp Down Slope (volts/sec)', pos=(XOri, YOri + 11*YOffset + txtOffset))
        self.rampDownSlopeTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 11*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        self.rampDownSlopeTBox.Bind(wx.EVT_TEXT, self.onRampDownSlope)
        self.rampDownLabel = wx.StaticText(panel, label='', pos=(XOri + txtBoxXOffset + smallTxtBoxLength + 10, YOri + 11*YOffset + txtOffset))
        
        wx.StaticText(panel, label='Total Ramp Time (ms)', pos=(XOri, YOri + 12*YOffset + txtOffset))        
        self.rampTimeLabel = wx.StaticText(panel, label='', pos=(XOri + txtBoxXOffset, YOri + 12*YOffset + txtOffset))
        startRampBtn = wx.Button(panel, label='Start Ramp', pos=(XOri + 10, YOri + 13*YOffset), size=(btnLength*2, btnHeight))
        startRampBtn.Bind(wx.EVT_BUTTON, self.onStartRamp)
        return
    
    '''
    '''
    def GUI_AFCoilTemperature(self, panel, XOri, YOri):
        XOri += 10
        YOri += 10
        XOffset = 10
        YOffset = 20
        txtOffset = 5        
        txtBoxXOffset = 70
        smallTxtBoxLength = 60
        txtBoxHeight = 25
        
        wx.StaticText(panel, label='Axial Coil', pos=(XOri, YOri + YOffset + txtOffset))
        self.axialTempTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        degreeTxt = chr(176) + 'C'
        wx.StaticText(panel, label=degreeTxt, pos=(XOri + txtBoxXOffset + smallTxtBoxLength + txtOffset, YOri + YOffset + txtOffset))        
        wx.StaticText(panel, label='Transver Coil', pos=(XOri, YOri + 3*YOffset + txtOffset))
        self.transTempTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 3*YOffset), size=(smallTxtBoxLength, txtBoxHeight))
        degreeTxt = chr(176) + 'C'
        wx.StaticText(panel, label=degreeTxt, pos=(XOri + txtBoxXOffset + smallTxtBoxLength + txtOffset, YOri + 3*YOffset + txtOffset))
        XOri = XOri + txtBoxXOffset + smallTxtBoxLength + txtOffset + 4*XOffset
        labelTxt = ''        
        self.warningText = wx.StaticText(panel, label=labelTxt, pos=(XOri, YOri + 20))
        btnLength = 100
        btnHeight = 30
        refreshTBtn = wx.Button(panel, label='Refresh T', pos=(XOri, YOri + 3*YOffset), size=(btnLength, btnHeight))
        refreshTBtn.Bind(wx.EVT_BUTTON, self.onRefreshT)
        return
    
    '''
    '''
    def GUI_ShinyButtons(self, panel, XOri, YOri):
        XOffset = 10
        btnLength = 130
        btnHeight = 30
        YOffset = 20
        YOri = YOri+YOffset
        
        afSettingsBtn = wx.Button(panel, label='Open AF Settings', pos=(XOri + XOffset, YOri), size=(btnLength, btnHeight))
        afSettingsBtn.Bind(wx.EVT_BUTTON, self.onAFOpenSettings)
        YOffset = 35
        afFileBtn = wx.Button(panel, label='Open AF File Settings', pos=(XOri + XOffset, YOri+YOffset), size=(btnLength, btnHeight))
        afFileBtn.Bind(wx.EVT_BUTTON, self.onFileSave)
        tuneAfBtn = wx.Button(panel, label='Tune AF Coils', pos=(XOri + XOffset, YOri+2*YOffset), size=(btnLength, btnHeight))
        tuneAfBtn.Bind(wx.EVT_BUTTON, self.onAFTuner)
        calibrateAfBtn = wx.Button(panel, label='Calibrate AF Coils', pos=(XOri + XOffset, YOri+3*YOffset), size=(btnLength, btnHeight))
        calibrateAfBtn.Bind(wx.EVT_BUTTON, self.onCoilCalibration)
        btnHeight = 40
        gaussmeterBtn = wx.Button(panel, label='908A Gaussmeter\nControl', pos=(XOri + XOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))
        gaussmeterBtn.Bind(wx.EVT_BUTTON, self.onGaussmeterControl)
        closeBtn = wx.Button(panel, label='Close', pos=(XOri + XOffset, YOri + 6*YOffset + 5), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
        return    
    
    '''
    '''
    def GUI_AFRampMode(self, panel, XOri, YOri):
        XOffset = 10
        YOffset = 30
        btnLength = 130
        btnHeight = 30        
        
        self.rampChkBox = wx.CheckBox(panel, label='Unmonitored Ramp', pos=(XOri + XOffset, YOri+YOffset))
        self.rampChkBox.Bind(wx.EVT_CHECKBOX, self.onUnmonitoredRamp)
        self.debugChkBox = wx.CheckBox(panel, label='Debug Mode?', pos=(XOri + XOffset, YOri+2*YOffset))
        self.recordChkBox = wx.CheckBox(panel, label='Record DC Field', pos=(XOri + XOffset, YOri+3*YOffset))
        cleanCoilBtn = wx.Button(panel, label='Clean Coils', pos=(XOri + XOffset, YOri+4*YOffset), size=(btnLength, btnHeight))
        cleanCoilBtn.Bind(wx.EVT_BUTTON, self.onCleanCoil)
        return
        
    '''
    '''
    def GUI_ActiveCoil(self, panel, XOri, YOri):
        XOffset = 10
        YOffset = 20
        smallBtnLength = 50
        btnHeight = 20
        
        self.ActiveCoilSystem = 'Axial'
        self.axialRBtn = wx.RadioButton(panel, 11, label = self.ActiveCoilSystem, pos = (XOri + XOffset, YOri+YOffset), style = wx.RB_GROUP) 
        self.transRBtn = wx.RadioButton(panel, 22, label = 'Transverse',pos = (XOri + XOffset, YOri+2*YOffset)) 
        self.irmRBtn = wx.RadioButton(panel, 33, label = 'IRM Axial',pos = (XOri + XOffset,YOri+3*YOffset))        
        self.Bind(wx.EVT_RADIOBUTTON, self.onCoilRGroup)
        
        switchBtn = wx.Button(panel, label='Switch', pos=(XOri + 90, YOri+2*YOffset-2), size=(smallBtnLength, btnHeight))
        switchBtn.Bind(wx.EVT_BUTTON, self.onSwitch)
        self.lockCoilChkBox = wx.CheckBox(panel, label='Lock Coil Selection', pos=(XOri + XOffset, YOri+5*YOffset))
        self.lockCoilChkBox.Bind(wx.EVT_CHECKBOX, self.onLockCoil)
        
        return

    '''--------------------------------------------------------------------------------------------
                        
                        internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def computePeakHangTime(self):
        try:
            freq = float(self.sineFreqTBox.GetValue())            
            return (1/freq)*100000
        
        except:
            return 0

    '''
    '''
    def getCoilRBtnSelection(self):
        selected = ''
        
        if (self.axialRBtn.GetValue()):
            selected = self.axialRBtn.GetLabel()
        elif (self.transRBtn.GetValue()):
            selected = self.transRBtn.GetLabel()
        elif (self.irmRBtn.GetValue()):
            selected = self.irmRBtn.GetLabel()
        
        return selected
    
    '''
    '''
    def getFloatValue(self, valueStr):
        try:
            value = float(valueStr)
        except:
            value = 0.0
            
        return value 

    '''
    '''
    def rampUpSlopeChange(self):
        TempD = self.getFloatValue(self.rampUpSlopeTBox.GetValue())
        if ((TempD > -0.0001) and (TempD < 0.0001)):
            return 
        
        peakVoltage = self.getFloatValue(self.peakRampTBox.GetValue())
        TempS = (peakVoltage/TempD) * 1000  
        self.rampUpLabel.SetLabel("{:.2f}".format(TempS))  
        
        '''Need to adjust the total duration label
           Add the ramp up and ramp down durations + time at peak
           and the extra 200 ms the code adds to make sure the process
           has indeed finished'''
        TempD = TempS + self.getFloatValue(self.rampDownLabel.GetLabel()) + self.getFloatValue(self.timePeakTBox.GetValue()) + 200  
        self.rampTimeLabel.SetLabel("{:.2f}".format(TempD))
        return

    '''
    '''
    def rampDownSlopeChange(self):
        TempD = self.getFloatValue(self.rampDownSlopeTBox.GetValue())
        if ((TempD > -0.0001) and (TempD < 0.0001)):
            return 
        
        peakVoltage = self.getFloatValue(self.peakRampTBox.GetValue())
        TempS = (peakVoltage/TempD) * 1000  
        self.rampDownLabel.SetLabel("{:.2f}".format(TempS))  
        
        '''Need to adjust the total duration label
           Add the ramp up and ramp down durations + time at peak
           and the extra 200 ms the code adds to make sure the process
           has indeed finished'''
        TempD = TempS + self.getFloatValue(self.rampUpLabel.GetLabel()) + self.getFloatValue(self.timePeakTBox.GetValue()) + 200  
        self.rampTimeLabel.SetLabel("{:.2f}".format(TempD))
        
        return

    '''
    '''
    def getUpSlope(self):
        '''Compare the RampPeakVolts to the Ramp Voltage corresponding to the
           peak field (if the calibration is done), if not, then relative to the
           Max ramp voltage set in the AF Auto tune form'''
        RampPeakVolts = self.getFloatValue(self.peakRampTBox.GetValue()) 
        
        activeCoil = self.getCoilRBtnSelection()
        if (activeCoil == 'Axial'):
            # Need to multiply by 1000 to convert seconds to miliseconds
            RampUpDur_ms = (RampPeakVolts / self.parent.modConfig.AxialRampUpVoltsPerSec) * 1000 
        elif (activeCoil == 'Transverse'):
            RampUpDur_ms = (RampPeakVolts / self.parent.modConfig.TransRampUpVoltsPerSec) * 1000
        else:
            upSlope = RampPeakVolts
            return upSlope
        
        # Check to make sure RampUpDur_ms is not smaller than the minimum allowed ramp duration
        if (RampUpDur_ms < self.parent.modConfig.MinRampUpTime_ms):
            RampUpDur_ms = self.parent.modConfig.MinRampUpTime_ms            
        if (RampUpDur_ms > self.parent.modConfig.MaxRampUpTime_ms):
            RampUpDur_ms = self.parent.modConfig.MaxRampUpTime_ms
                      
        # Now can use the ramp up duration to calculate the Ramp Up slope
        # Note: RampUpDur_ms is in miliseconds
        upSlope = RampPeakVolts / (RampUpDur_ms / 1000)
                       
        return upSlope

    '''
    '''
    def getDownSlope(self):
        RampPeakVolts = self.getFloatValue(self.peakRampTBox.GetValue()) 

        activeCoil = self.getCoilRBtnSelection()
        if (activeCoil == 'Axial'):
            RampPeriod = 1 / self.parent.modConfig.AfAxialResFreq
        elif (activeCoil == 'Transverse'):
            RampPeriod = 1 / self.parent.modConfig.AfTransResFreq
        else:
            RampPeriod = 1 / self.parent.modConfig.AfAxialResFreq
        
        '''Get the initial calculated ramp-Down duration
           based Downon the Max Ramp-Down time setting '''
        RampDownPeriods = self.parent.modConfig.RampDownNumPeriodsPerVolt * RampPeakVolts
        if (RampDownPeriods < self.parent.modConfig.MinRampDown_NumPeriods):
            RampDownPeriods = self.parent.modConfig.MinRampDown_NumPeriods
        if (RampDownPeriods > self.parent.modConfig.MaxRampDown_NumPeriods):
            RampDownPeriods = self.parent.modConfig.MaxRampDown_NumPeriods 
        
        # Now calculate the RampDuration from this (ramp duration is in SECONDS)
        RampDuration = RampDownPeriods * RampPeriod
        downSlope = RampPeakVolts / RampDuration
        
        return downSlope

    '''
    '''
    def setCheckBox(self, paramStr, checkBox):
        if 'True' in paramStr:
            checkBox.SetValue(True)
        else:
            checkBox.SetValue(False)
        return

    '''
    '''
    def getADWinValues(self):
        self.parent.modConfig.processData.ADwin_optCalRamp = self.calibrateRBox.GetSelection()
        try:
            peakField = float(self.peakFieldTBox.GetValue())
        except:
            peakField = 0.0
        self.parent.modConfig.processData.ADwin_peakField = peakField
        try:
            monitorTrigVolt = float(self.peakMonitorTBox.GetValue())
        except:
            monitorTrigVolt = 0.0
        self.parent.modConfig.processData.ADwin_monitorTrigVolt = monitorTrigVolt
        
        return
        
    '''
    '''
    def setActiveCoil(self, activeCoil):
        self.ActiveCoilSystem = activeCoil
        if 'Axial' in activeCoil:
            self.axialRBtn.SetValue(True)
            
        elif 'Transverse' in activeCoil:
            self.transRBtn.SetValue(True)

        elif 'IRM Axial' in activeCoil:
            self.irmRBtn.SetValue(True)
            
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageList):
        for eachEntry in messageList:
            if 'T1 = ' in eachEntry:
                self.axialTempTBox.SetValue(eachEntry.strip().replace('T1 = ', ''))                
            elif 'T2 = ' in eachEntry:
                self.transTempTBox.SetValue(eachEntry.strip().replace('T2 = ', ''))
            elif 'Coil Status = ' in eachEntry:
                self.setCheckBox(eachEntry, self.lockCoilChkBox)
            elif 'Unmonitored Ramp = ' in eachEntry:
                self.setCheckBox(eachEntry, self.rampChkBox)
            elif 'Peak Field = ' in eachEntry:
                self.peakFieldTBox.SetValue(eachEntry.strip().replace('Peak Field = ', ''))
            elif 'Peak Monitor Voltage = ' in eachEntry:
                self.peakMonitorTBox.SetValue(eachEntry.strip().replace('Peak Monitor Voltage = ', ''))
            elif 'Peak Ramp Voltage = ' in eachEntry:
                self.peakRampTBox.SetValue(eachEntry.strip().replace('Peak Ramp Voltage = ', ''))
            elif 'OptCalRamp = ' in eachEntry:
                index = int(eachEntry.strip().replace('OptCalRamp = ', ''))
                self.calibrateRBox.SetSelection(index)
            elif 'Frequency = ' in eachEntry:
                self.sineFreqTBox.SetValue(eachEntry.strip().replace('Frequency = ', ''))
            elif 'Up Slope = ' in eachEntry:
                self.rampUpSlopeTBox.SetValue(eachEntry.strip().replace('Up Slope = ', ''))
            elif 'Down Slope = ' in eachEntry:
                self.rampDownSlopeTBox.SetValue(eachEntry.strip().replace('Down Slope = ', ''))
            elif 'Ramp Rate = ' in eachEntry:
                self.rampRateTBox.SetValue(eachEntry.strip().replace('Ramp Rate = ', ''))
            elif 'Ramp Peak Duration = ' in eachEntry:
                self.timePeakTBox.SetValue(eachEntry.strip().replace('Ramp Peak Duration = ', ''))
            elif 'Ramp Up Duration = ' in eachEntry:
                self.rampUpLabel.SetValue(eachEntry.strip().replace('Ramp Up Duration = ', ''))
            elif 'Ramp Down Duration = ' in eachEntry:
                self.rampDownLabel.SetValue(eachEntry.strip().replace('Ramp Down Duration = ', ''))
            elif 'Total Ramp Duration = ' in eachEntry:
                self.rampTimeLabel.SetValue(eachEntry.strip().replace('Total Ramp Duration = ', ''))
            elif 'HighTemp = ' in eachEntry:                
                self.axialTempTBox.SetBackgroundColour((255, 165, 0))
                self.transTempTBox.SetBackgroundColour((255, 165, 0))
                self.warningText.SetLabel(eachEntry.strip().replace('HighTemp = ', ''))
            elif 'Clear = ' in eachEntry:    
                self.axialTempTBox.SetBackgroundColour((255, 255, 255))
                self.transTempTBox.SetBackgroundColour((255, 255, 255))
                self.warningText.SetLabel(' ')
            elif 'Active Coil = ' in eachEntry:
                self.setActiveCoil(eachEntry.strip().replace('Active Coil = ', ''))
                            
                
        return
                    
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        self.ramp_in_progress = False
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onRampPeakVoltageChange(self, event):
        upSlope = self.getUpSlope()
        self.rampUpSlopeTBox.SetValue("{:.2f}".format(upSlope))
        self.rampUpSlopeChange()

        downSlope = self.getDownSlope()
        self.rampDownSlopeTBox.SetValue("{:.2f}".format(downSlope))
        self.rampDownSlopeChange()
        
        return
        
    '''
    '''
    def onRampPeakVoltage(self, event):
        self.rampUpSlopeChange()
        self.rampDownSlopeChange()
        return
        
    '''
    '''
    def onRampUpSlope(self, event):
        self.rampUpSlopeChange()
        return
        
    '''
    '''
    def onRampDownSlope(self, event):
        self.rampDownSlopeChange()
        return                
        
    '''
    '''
    def onCoilRGroup(self, event):
        selected = event.EventObject.GetLabel()
        
        self.ActiveCoilSystem = selected  
        if (selected == 'Axial'):
            freq = str(self.parent.modConfig.AfAxialResFreq)
            self.sineFreqTBox.SetValue(freq)
        elif (selected == 'Transverse'):
            freq = str(self.parent.modConfig.AfTransResFreq)
            self.sineFreqTBox.SetValue(freq)
        else:
            freq = str(self.parent.modConfig.AfAxialResFreq)
            self.sineFreqTBox.SetValue(freq)
            
        return
    
    '''
    '''
    def onAutoSlope(self, event):
        if (event.EventObject.GetValue()):
            self.rampUpSlopeTBox.Disable()
            self.rampDownSlopeTBox.Disable()
        else:
            self.rampUpSlopeTBox.Enable()
            self.rampDownSlopeTBox.Enable()
        
        return
    
    '''
    '''
    def onLockCoil(self, event):
        if (event.EventObject.GetValue()):
            self.axialRBtn.Disable()
            self.transRBtn.Disable()
        else:
            self.axialRBtn.Enable()
            self.transRBtn.Enable()
            
        return
    
    '''
    '''
    def onUnmonitoredRamp(self, event):
        if (event.EventObject.GetValue()):
            self.calibrateRBox.Disable()
            self.peakFieldTBox.Disable()
            self.peakMonitorTBox.Disable()
        else:
            self.calibrateRBox.Enable()
            self.peakFieldTBox.Enable()
            self.peakMonitorTBox.Enable()
        return
            
    '''
    '''
    def onGaussmeterControl(self, event):
        frm908AGaussmeter(self.parent)
        return
        
    '''
    '''
    def onCoilCalibration(self, event):
        frmCalibrateCoils(self.parent)
        return
        
    '''
    '''
    def onAFTuner(self, event):
        frmAFTuner(self.parent)
        return
    
    '''
    '''
    def onFileSave(self, event):
        frmFileSave(self.parent)
        return
    
    '''
    '''
    def onAFOpenSettings(self, event):
        tabPanel = frmSettings(self.parent)
        tabPanel.tabs.notebook.SetSelection(3)
        tabPanel.Show()
        return
    '''
    '''
    def onStartRamp(self, event):
        paramList = [self.ActiveCoilSystem]
        if self.rampChkBox.GetValue():
            if self.calSlopeChkBox.GetValue():
                # Don't put in up and down slopes
                paramList.append(self.peakRampTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())                
                paramList.append(self.timePeakTBox.GetValue())
                paramList.append(False)
                paramList.append(True)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())
            else:
                # Need to put in the Ramp Up & Down slopes
                paramList.append(self.peakRampTBox.GetValue())
                paramList.append(self.rampUpSlopeTBox.GetValue())
                paramList.append(self.rampDownSlopeTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())
                paramList.append(self.timePeakTBox.GetValue())
                paramList.append(False)
                paramList.append(True)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())
            
        elif (self.calibrateRBox.GetSelection() == 0):
            if self.calSlopeChkBox.GetValue():
                # Don't put in up and down slopes
                paramList.append(self.peakMonitorTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())
                paramList.append(self.timePeakTBox.GetValue())   
                paramList.append(False)
                paramList.append(False)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())                
            else:
                # Need to put in the Ramp Up & Down slopes
                paramList.append(self.peakMonitorTBox.GetValue())
                paramList.append(self.rampUpSlopeTBox.GetValue())
                paramList.append(self.rampDownSlopeTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())
                paramList.append(self.timePeakTBox.GetValue())
                paramList.append(False)
                paramList.append(False)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())                
            
        elif (self.calibrateRBox.GetSelection() == 1):
            if self.calSlopeChkBox.GetValue():
                # Don't put in up and down slopes
                paramList.append(self.peakFieldTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())
                paramList.append(self.timePeakTBox.GetValue())   
                paramList.append(True)
                paramList.append(False)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())                
            else:
                # Need to put in the Ramp Up & Down slopes
                paramList.append(self.peakFieldTBox.GetValue())
                paramList.append(self.rampUpSlopeTBox.GetValue())
                paramList.append(self.rampDownSlopeTBox.GetValue())
                paramList.append(self.rampRateTBox.GetValue())
                paramList.append(self.timePeakTBox.GetValue())
                paramList.append(True)
                paramList.append(False)
                paramList.append(self.debugChkBox.GetValue())
                paramList.append(self.recordChkBox.GetValue())                
            
        else:
            wx.MessageBox('Whoops!')
            return
            
        self.parent.pushTaskToQueue([self.parent.devControl.AF_START_RAMP, paramList])
        return
        
    '''
    '''
    def onCleanCoil(self, event):
        if not self.ramp_in_progress:
            self.getADWinValues()
            self.ramp_in_progress = True
            self.parent.pushTaskToQueue([self.parent.devControl.AF_CLEAN_COIL, [self.debugChkBox.GetValue()]])
        return
        
    '''
    '''
    def onRefreshT(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.AF_REFRESH_T, []])
        return
        
    '''
    '''
    def onSwitch(self, event):
        activeCoil = self.getCoilRBtnSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.AF_SWITCH_COIL, [activeCoil]])
        return
    
    '''
    '''
    def onFreqChanged(self, event):
        self.timePeakTBox.SetValue("{:.3f}".format(self.computePeakHangTime()))
        
    '''
    '''
    def onShow(self, event):
                
        if (self.parent != None):
            self.parent.NOCOMM_Flag = False
            self.parent.modConfig.processData.adwinEnable = True

            coilSelection = self.getCoilRBtnSelection() 
            if (coilSelection == 'Axial'):
                self.sineFreqTBox.SetValue(str(self.parent.modConfig.AfAxialResFreq))
            elif (coilSelection == 'Transverse'):
                self.sineFreqTBox.SetValue(str(self.parent.modConfig.AfTransResFreq))
            else:
                self.sineFreqTBox.SetValue('')
                
            self.timePeakTBox.SetValue("{:.3f}".format(self.computePeakHangTime()))
            self.rampRateTBox.SetValue(str(self.IORate))
        return
               
    '''
    '''
    def onClose(self, event):
        self.Close(force=False)
        return
                              
    '''
        Close frmADWIN_AF form
    '''
    def onClosed(self, event):
        if (self.parent != None):
            if self.parent.panelList:
                if 'ADWinAFControl' in self.parent.panelList.keys():          
                    del self.parent.panelList['ADWinAFControl']
                
        self.Destroy()
        

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmADWIN_AF(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)

        