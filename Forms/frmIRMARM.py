'''
Created on Jul 7, 2025

@author: hd.nguyen
'''
import wx

from Forms.frmDAQ_Comm import frmDAQ_Comm
from Forms.frmCalibrateCoils import frmCalibrateCoils
from Forms.frmIRM_VoltageCalibration import frmIRM_VoltageCalibration
from Forms.frmSettings import frmSettings
from Forms.frmTestUnit import frmTestUnit

class frmIRMARM(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent = parent
        if (parent != None):
            super(frmIRMARM, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmIRMARM, self).__init__(parent, wx.NewIdRef())
            
        self.InitUI()
                
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)

        X1Ori = 10
        Y1Ori = 10
        
        # First Column, First box
        box1Length = 150
        box1Height = 120
        wx.StaticBox(panel, -1, 'ARM', pos=(X1Ori, Y1Ori), size=(box1Length, box1Height))
        self.GUI_ARM(panel, X1Ori, Y1Ori)

        # First Column, second box
        Y1Ori += box1Height + 10
        box2Length = box1Length
        box2Height = 250
        wx.StaticBox(panel, -1, 'Coil Temperatures', pos=(X1Ori, Y1Ori), size=(box2Length, box2Height))
        self.GUI_CoilTemperatures(panel, X1Ori, Y1Ori)

        # Second Column, First box
        X2Ori = X1Ori + box1Length + 10 
        Y2Ori = 10
        box3Length = 200
        box3Height = 240
        wx.StaticBox(panel, -1, 'IRM', pos=(X2Ori, Y2Ori), size=(box3Length, box3Height))
        self.GUI_IRM(panel, X2Ori, Y2Ori)

        # Second Column, second box
        Y2Ori += box3Height + 10
        box4Length = box3Length
        box4Height = 130
        wx.StaticBox(panel, -1, 'IRM Calibration', pos=(X2Ori, Y2Ori), size=(box4Length, box4Height))        
        self.GUI_IRMCalibration(panel, X2Ori, Y2Ori)        

        # Third Column, First box
        X3Ori = X2Ori + box3Length + 10 
        Y3Ori = 10
        box5Length = 200
        box5Height = 130
        wx.StaticBox(panel, -1, 'ARM DAQ Controller', pos=(X3Ori, Y3Ori), size=(box5Length, box5Height))
        self.GUI_ARM_DAQ_Controller(panel, X3Ori, Y3Ori)

        # Third Column, Second box
        Y3Ori += box5Height + 10
        box6Length = box5Length
        box6Height = 200
        wx.StaticBox(panel, -1, 'IRM DAQ Controller', pos=(X3Ori, Y3Ori), size=(box6Length, box6Height))
        self.GUI_IRM_DAQ_Controller(panel, X3Ori, Y3Ori)
        
        # Close Button
        Y3Ori += box6Height + 10
        btnLength = box6Length 
        btnHeight = 30
        closeBtn = wx.Button(panel, label='Close', pos=(X3Ori, Y3Ori), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)

        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)

        panelLength = X3Ori + box5Length + 30 
        panelHeight = Y1Ori + box2Height + 60
        self.SetSize((panelLength, panelHeight))
        self.SetTitle('IRM/ARM Controller')
        self.Centre()
        return

    '''
    '''
    def GUI_IRM_DAQ_Controller(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        btnLength = 120
        btnHeight = 25 
        XOffset = btnLength + 10
        txtBoxLength = 50 
        txtBoxHeight = 25        
        irmVBtn = wx.Button(panel, label='IRM V', pos=(XOri, YOri), size=(btnLength, btnHeight))
        irmVBtn.Bind(wx.EVT_BUTTON, self.onIRMV)
        self.irmVTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        self.irmVTBox.SetValue('0.0')

        YOffset = btnHeight + 7 
        readIRMVBtn = wx.Button(panel, label='Read IRM V in', pos=(XOri, YOri + YOffset), size=(btnLength, btnHeight))
        readIRMVBtn.Bind(wx.EVT_BUTTON, self.onReadIRMV)
        self.ReadIrmVTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        irmFireBtn = wx.Button(panel, label='IRM Fire', pos=(XOri, YOri + 2*YOffset), size=(btnLength, btnHeight))
        irmFireBtn.Bind(wx.EVT_BUTTON, self.onIRMFire)
        self.irmFireTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.irmFireTBox.SetValue('Off')
        self.irmFireTBox.SetBackgroundColour(wx.RED)

        irmTrimBtn = wx.Button(panel, label='IRM Trim', pos=(XOri, YOri + 3*YOffset), size=(btnLength, btnHeight))
        irmTrimBtn.Bind(wx.EVT_BUTTON, self.onIRMTrim)
        self.irmTrimTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.irmTrimTBox.SetValue('Off')
        self.irmTrimTBox.SetBackgroundColour(wx.RED)

        btnHeight = 40
        yTxtOffset = 8 
        readIRMPowerBtn = wx.Button(panel, label='Read IRM\nPower Amp V in', pos=(XOri, YOri + 4*YOffset), size=(btnLength, btnHeight))
        readIRMPowerBtn.Bind(wx.EVT_BUTTON, self.onReadIRM)
        self.readIrmPowerTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 4*YOffset + yTxtOffset), size=(txtBoxLength, txtBoxHeight))
        return
        
    '''
    '''
    def GUI_ARM_DAQ_Controller(self, panel, XOri, YOri):
        XOri += 10
        XOffset = 30
        YOri += 20
        btnLength = 120 
        btnHeight = 25
        showBtn = wx.Button(panel, label='Show', pos=(XOri + XOffset, YOri), size=(btnLength, btnHeight))
        showBtn.Bind(wx.EVT_BUTTON, self.onShowARM)

        XOffset = btnLength + 10
        YOffset = btnHeight + 10 
        txtBoxLength = 50 
        txtBoxHeight = 25        
        armVBtn = wx.Button(panel, label='ARM V', pos=(XOri, YOri + YOffset), size=(btnLength, btnHeight))
        armVBtn.Bind(wx.EVT_BUTTON, self.onARMV)
        self.armVTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.armVTBox.SetValue('0.0')

        armSetBtn = wx.Button(panel, label='ARM Set', pos=(XOri, YOri + 2*YOffset), size=(btnLength, btnHeight))
        armSetBtn.Bind(wx.EVT_BUTTON, self.onARMSet)
        self.armSetTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.armSetTBox.SetValue('Off')
        self.armSetTBox.SetBackgroundColour(wx.RED)
        
        return
        
    '''
    '''
    def GUI_IRMCalibration(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        btnLength = 180 
        btnHeight = 30
        calFieldBtn = wx.Button(panel, label='Calibrate IRM Fields', pos=(XOri, YOri), size=(btnLength, btnHeight))
        calFieldBtn.Bind(wx.EVT_BUTTON, self.onCalibrateField)

        YOffset = btnHeight + 5 
        calVoltsBtn = wx.Button(panel, label='Calibrate IRM DAQ Volts', pos=(XOri, YOri + YOffset), size=(btnLength, btnHeight))
        calVoltsBtn.Bind(wx.EVT_BUTTON, self.onCalibrateVolts)
        
        changeSettingBtn = wx.Button(panel, label='Change IRM Settings...', pos=(XOri, YOri + 2*YOffset), size=(btnLength, btnHeight))
        changeSettingBtn.Bind(wx.EVT_BUTTON, self.onChangeSettings)
        return
        
    '''
    '''
    def GUI_IRM(self, panel, XOri, YOri):
        XOri += 10
        YOffset = 20
        txtOffset = 2
        txtBoxXOffset = 80
        txtBoxLength = 50 
        txtBoxHeight = 20
        btnLength = 40
        btnHeight = 25
        XOffset = txtBoxXOffset + txtBoxLength + 10 
        wx.StaticText(panel, label='Voltage', pos=(XOri, YOri + YOffset + txtOffset))
        self.voltageTBox = wx.TextCtrl(panel, value='0', pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        voltageBtn = wx.Button(panel, label='Fire', pos=(XOri + XOffset, YOri + YOffset - txtOffset), size=(btnLength, btnHeight))
        voltageBtn.Bind(wx.EVT_BUTTON, self.onVoltage)
        
        YOffset = 25
        YOri += txtBoxHeight + 10 
        wx.StaticText(panel, label='Peak Field (G)', pos=(XOri, YOri + YOffset + txtOffset))
        self.peakFieldTBox = wx.TextCtrl(panel, value='0', pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        peakFieldBtn = wx.Button(panel, label='Fire', pos=(XOri + XOffset, YOri + YOffset - txtOffset), size=(btnLength, btnHeight))
        peakFieldBtn.Bind(wx.EVT_BUTTON, self.onPeakField)
        
        YOri += YOffset  + txtOffset
        self.axialRBtn = wx.RadioButton(panel, 11, label = 'Axial', pos = (XOri, YOri + YOffset), style = wx.RB_GROUP) 
        self.transRBtn = wx.RadioButton(panel, 22, label = 'Transverse',pos = (XOri, YOri + 2*YOffset)) 
        XOffset = 110
        txtOffset = 5
        btnLength = 70
        interruptBtn = wx.Button(panel, label='Interrupt', pos=(XOri + XOffset, YOri + YOffset + txtOffset), size=(btnLength, btnHeight))
        interruptBtn.Bind(wx.EVT_BUTTON, self.onInterrupt)
        
        self.lockCoilChkBox = wx.CheckBox(panel, label='Lock Coil Selection', pos=(XOri, YOri + 3*YOffset))
        self.polarityChkBox = wx.CheckBox(panel, label='Negative Polarity', pos=(XOri, YOri + 4*YOffset))
        self.lblIRMStatus = wx.StaticText(panel, label='', pos=(XOri + 4*txtOffset, YOri + 5*YOffset))

        btnLength = 120
        txtBoxHeight = 25
        txtBoxXOffset = btnLength + 10 
        readVoltageBtn = wx.Button(panel, label='Read IRM Voltage', pos=(XOri, YOri + 6*YOffset), size=(btnLength, btnHeight))
        readVoltageBtn.Bind(wx.EVT_BUTTON, self.onReadVoltage)
        self.readVoltageTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + 6*YOffset), size=(txtBoxLength, txtBoxHeight))
        
        return 
        
    '''
    '''
    def GUI_CoilTemperatures(self, panel, XOri, YOri):
        XOri += 20
        YOffset = 30
        txtOffset = 20
        txtBoxLength = 90 
        txtBoxHeight = 25
        txtBoxXOffset = txtBoxLength + 5
        txtBoxYOffset = 5
        wx.StaticText(panel, label='Axial Coil', pos=(XOri, YOri + YOffset))
        self.axialTempTBox = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset  + txtOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label=chr(176) + 'C', pos=(XOri + txtBoxXOffset, YOri + YOffset + txtOffset + txtBoxYOffset))

        YOri += YOffset  + txtOffset + 10
        wx.StaticText(panel, label='Transverse Coil', pos=(XOri, YOri + YOffset))
        self.transTempTBox = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset  + txtOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label=chr(176) + 'C', pos=(XOri + txtBoxXOffset, YOri + YOffset + txtOffset + txtBoxYOffset))
        
        YOri += YOffset  + txtOffset + 10
        warningStr = "The AF unit is too\nhot so let's pause a\nlittle bit ..."
        self.lblIRMTooHot = wx.StaticText(panel, label=warningStr, pos=(XOri, YOri + YOffset))
        self.lblIRMTooHot.Hide()

        XOffset = 10
        YOffset += txtBoxHeight + 30
        btnLength = 100
        btnHeight = 30
        refreshTBtn = wx.Button(panel, label='Refresh T', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        refreshTBtn.Bind(wx.EVT_BUTTON, self.onRefreshT)
        
        return
    
    '''
    '''
    def GUI_ARM(self, panel, XOri, YOri):
        XOri += 10
        YOffset = 30
        txtOffset = 2
        txtBoxXOffset = 80
        txtBoxLength = 50 
        txtBoxHeight = 20
        wx.StaticText(panel, label='Bias Field (G)', pos=(XOri, YOri + YOffset + txtOffset))
        self.biasFieldTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.biasFieldTBox.SetValue('0')
        
        XOffset = 10
        YOffset += txtBoxHeight + 30
        btnLength = 100
        btnHeight = 30
        setBtn = wx.Button(panel, label='Set', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        setBtn.Bind(wx.EVT_BUTTON, self.onSet)
                
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
    '''
    def onReadIRM(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_READ_IRM_POWER, []])
        return
    
    '''
    '''
    def onIRMTrim(self, event):
        currentState = self.irmTrimTBox.GetValue()
        if 'Off' in currentState:
            # Need to toggle TTL for IRM Trim shut
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_IRMTRIM, [True]])
            self.irmTrimTBox.SetValue('On')
            self.irmTrimTBox.SetBackgroundColour(wx.GREEN)
            
        elif 'On' in currentState:
            # Need to toggle TTL for IRM Trim open            
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_IRMTRIM, [False]])
            self.irmTrimTBox.SetValue('Off')
            self.irmTrimTBox.SetBackgroundColour(wx.RED)
            
        return
    
    '''
    '''
    def onIRMFire(self, event):
        currentState = self.irmFireTBox.GetValue()
        if 'Off' in currentState:
            # Need to toggle TTL for IRM Fire shut
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_IRMFIRE, [False]])
            self.irmFireTBox.SetValue('On')
            self.irmFireTBox.SetBackgroundColour(wx.GREEN)
            
        elif 'On' in currentState:
            # Need to toggle TTL for IRM Fire open            
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_IRMFIRE, [True]])
            self.irmFireTBox.SetValue('Off')
            self.irmFireTBox.SetBackgroundColour(wx.RED)
            
        return
    
    '''
    '''
    def onReadIRMV(self, event):        
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_IRM_VOLTAGE_IN, []])
        return
    
    '''
    '''
    def onIRMV(self, event):
        try:
            voltageOut = float(self.irmVTBox.GetValue())
        except:
            voltageOut = 0.0
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_IRM_VOLTAGE_OUT, [voltageOut]])
        return
    
    '''
    '''
    def onARMSet(self, event):
        currentState = self.armSetTBox.GetValue()
        if 'Off' in currentState:
            # Need to toggle TTL for ARM shut
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_ARMSET, [False]])
            self.armSetTBox.SetValue('On')
            self.armSetTBox.SetBackgroundColour(wx.GREEN)
            
        elif 'On' in currentState:
            # Need to toggle TTL for ARM open            
            self.parent.pushTaskToQueue([self.parent.devControl.IRM_TOGGLE_ARMSET, [True]])
            self.armSetTBox.SetValue('Off')
            self.armSetTBox.SetBackgroundColour(wx.RED)
            
        return
    
    '''
    '''
    def onARMV(self, event):
        try:
            voltageOut = float(self.armVTBox.GetValue())
        except:
            voltageOut = 0.0
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_ARM_VOLTAGE_OUT, [voltageOut]])
        return
    
    '''
    '''
    def onShowARM(self, event):
        frmDAQ_Comm(self.parent)
        return
    
    '''
    '''
    def onChangeSettings(self, event):
        settingPanel = frmSettings(self.parent)
        settingPanel.tabs.notebook.SetSelection(6)
        settingPanel.Show()
        return
    
    '''
    '''
    def onCalibrateVolts(self, event):
        calibrationVoltage = frmIRM_VoltageCalibration(self.parent)
        calibrationVoltage.ZOrder(0)
        return
        
    '''
    '''
    def onCalibrateField(self, event):
        calibrationCoils = frmCalibrateCoils(self.parent, InAFMode=False)
        calibrationCoils.ZOrder(0)
        return
    
    '''
    '''
    def onReadVoltage(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_AVERAGE_VOLTAGE, []])
        return
   
    '''
    '''
    def onInterrupt(self, event):
        self.parent.mainQueue.put('Program_Interrupt')
        return
       
    '''
    '''
    def onPeakField(self, event):
        try:
            field = float(self.peakFieldTBox.GetValue())
        except:
            field = 0.0 
        
        if (self.axialRBtn.GetValue()):
            coilLabel = 'Axial'
        else:
            coilLabel = 'Transverse'    
        
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_FIRE_AT_FIELD, [field, coilLabel]])
        return
    
    '''
    '''
    def onVoltage(self, event):
        try:
            volts = float(self.voltageTBox.GetValue())
        except:
            volts = 0.0 
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_FIRE, [volts]])
        return

    '''
    '''
    def onRefreshT(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_REFRESH_TEMP, [None]])
        return

    '''
    '''
    def onSet(self, event):
        try:
            biasField = float(self.biasFieldTBox.GetValue())
        except:
            biasField = 0.0
            
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_SET_BIAS_FIELD, [biasField]])
        return
        
    '''
    '''
    def onShow(self, event):
        if (self.parent != None):
            self.parent.NOCOMM_Flag = False
            self.parent.modConfig.processData.irmArmEnable = True
            self.parent.modConfig.processData.adwinEnable = True
        
            if not self.parent.modConfig.EnableAxialIRM:
                self.axialRBtn.Enable(enable=False)
    
            if not self.parent.modConfig.EnableTransIRM:
                self.transRBtn.Enable(enable=False)
                
            if ((not self.parent.modConfig.EnableAxialIRM) and (not self.parent.modConfig.EnableTransIRM)):
                warningMessage = "The IRM Axial & Transverse modules are currently disabled.\nNo IRM's can be performed right now until those settings are changed."
                wx.MessageBox(warningMessage, style=wx.OK|wx.CENTER, caption='Warning')
              
        return
    
    '''
    '''
    def onClose(self, event):
        self.Close(force=False)
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageList):
        for eachEntry in messageList:
            if 'Bias Field = ' in eachEntry:
                self.biasFieldTBox.SetValue(eachEntry.strip().replace('Bias Field = ', ''))
            elif 'ARM Set = ' in eachEntry:
                self.armSetTBox.SetValue(eachEntry.strip().replace('ARM Set = ', ''))
                if 'On' in eachEntry:
                    self.armSetTBox.SetBackgroundColour(wx.GREEN)       
                else:         
                    self.armSetTBox.SetBackgroundColour(wx.RED)
                    
            elif 'ARM V = ' in eachEntry:
                self.armSetTBox.SetValue(eachEntry.strip().replace('ARM V = ', ''))
                
            elif 'Temp1 = ' in eachEntry:
                self.axialTempTBox.SetValue(eachEntry.strip().replace('Temp1 = ', ''))
                
            elif 'Temp2 = ' in eachEntry:
                self.transTempTBox.SetValue(eachEntry.strip().replace('Temp2 = ', ''))
                
            elif 'Coil locked = ' in eachEntry:
                if 'True' in eachEntry:
                    self.lockCoilChkBox.SetValue(True)
                else:
                    self.lockCoilChkBox.SetValue(False)
                    
            elif 'Volts Out = ' in eachEntry:
                self.voltageTBox.SetValue(eachEntry.strip().replace('Volts Out = ', ''))
                
            elif 'Read Voltage = ' in eachEntry:
                self.readVoltageTBox.SetValue(eachEntry.strip().replace('Read Voltage = ', ''))
                
            elif 'Peak Field = ' in eachEntry:
                self.peakFieldTBox.SetValue(eachEntry.strip().replace('Peak Field = ', ''))
                
            elif 'Temp Hot' in eachEntry:
                self.axialTempTBox.SetBackgroundColour('orange')
                self.transTempTBox.SetBackgroundColour('orange')
                self.lblIRMTooHot.Hide()
                
            elif 'Temp Normal' in eachEntry:
                self.axialTempTBox.SetBackgroundColour(wx.NullColour)
                self.transTempTBox.SetBackgroundColour(wx.NullColour)
                self.lblIRMTooHot.Show()
                
            elif 'IRM Trim = ' in eachEntry:
                self.irmTrimTBox.SetValue(eachEntry.strip().replace('IRM Trim = ', ''))
                
            elif 'IRM Fire = ' in eachEntry:
                self.irmFireTBox.SetValue(eachEntry.strip().replace('IRM Fire = ', ''))

            elif 'IRM Status = ' in eachEntry:
                self.lblIRMStatus.SetLabel(eachEntry.strip().replace('IRM Status = ', ''))
                
            elif 'IRM Voltage Read = ' in eachEntry:
                self.ReadIrmVTBox.SetValue(eachEntry.strip().replace('IRM Voltage Read = ', ''))

            elif 'IRM Read Power = ' in eachEntry:
                self.readIrmPowerTBox.SetValue(eachEntry.strip().replace('IRM Read Power = ', ''))
                
            elif 'Back Field Mode = ' in eachEntry:
                backFieldMode = eachEntry.strip().replace('Back Field Mode = ', '')
                if 'True' in backFieldMode:
                    self.polarityChkBox.SetValue(True)
                else:
                    self.polarityChkBox.SetValue(False)                
                            
        return

    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        self.ramp_in_progress = False
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        testUnit = frmTestUnit(path='C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
        irmARMControl = frmIRMARM(parent=testUnit)
        testUnit.panelList['IRMControl'] = irmARMControl
        irmARMControl.Show(True)        
        app.MainLoop()    
        
    except Exception as e:
        print(e)

        