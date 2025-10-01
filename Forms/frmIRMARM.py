'''
Created on Jul 7, 2025

@author: hd.nguyen
'''
import wx

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
        box1Height = 100
        wx.StaticBox(panel, -1, 'ARM', pos=(X1Ori, Y1Ori), size=(box1Length, box1Height))
        self.GUI_ARM(panel, X1Ori, Y1Ori)

        # First Column, second box
        Y1Ori += box1Height + 10
        box2Length = box1Length
        box2Height = 220
        wx.StaticBox(panel, -1, 'Coil Temperatures', pos=(X1Ori, Y1Ori), size=(box2Length, box2Height))
        self.GUI_CoilTemperatures(panel, X1Ori, Y1Ori)

        # Second Column, First box
        X2Ori = X1Ori + box1Length + 10 
        Y2Ori = 10
        box3Length = 200
        box3Height = 270
        wx.StaticBox(panel, -1, 'IRM', pos=(X2Ori, Y2Ori), size=(box3Length, box3Height))
        self.GUI_IRM(panel, X2Ori, Y2Ori)

        # Second Column, second box
        Y2Ori += box3Height + 20
        
        # Close Button
        btnLength = box3Length
        btnHeight = 30
        closeBtn = wx.Button(panel, label='Close', pos=(X2Ori, Y2Ori), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)

        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)

        panelLength = X2Ori + box3Length + 30 
        panelHeight = Y1Ori + box2Height + 60
        self.SetSize((panelLength, panelHeight))
        self.SetTitle('IRM/ARM Controller')
        self.Centre()
        return
                        
    '''
    '''
    def GUI_IRM(self, panel, XOri, YOri):
        XOri += 10
        YOffset = 30
        txtOffset = 2
        txtBoxXOffset = 80
        txtBoxLength = 50 
        txtBoxHeight = 25
        btnLength = 40
        btnHeight = 25
        XOffset = txtBoxXOffset + txtBoxLength + 10 
        setFieldBtn = wx.Button(panel, label='Set', pos=(XOri + XOffset, YOri + YOffset - txtOffset), size=(btnLength, btnHeight))
        setFieldBtn.Bind(wx.EVT_BUTTON, self.onSetField)
        
        YOffset = 17
        YOri += txtBoxHeight + 10 
        wx.StaticText(panel, label='Peak Field (G)', pos=(XOri, YOri + YOffset + txtOffset))
        self.peakFieldTBox = wx.TextCtrl(panel, value='0', pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        YOffset = 35
        self.fireFieldBtn = wx.Button(panel, label='Fire', pos=(XOri + XOffset, YOri + YOffset - txtOffset), size=(btnLength, btnHeight))
        self.fireFieldBtn.Bind(wx.EVT_BUTTON, self.onFireField)
        self.fireFieldBtn.Enable(False)
        
        YOri += YOffset  + txtOffset
        self.axialRBtn = wx.RadioButton(panel, 11, label = 'Axial', pos = (XOri, YOri + YOffset), style = wx.RB_GROUP) 
        self.transRBtn = wx.RadioButton(panel, 22, label = 'Transverse',pos = (XOri, YOri + 2*YOffset))
         
        txtOffset = 5        
        self.lockCoilChkBox = wx.CheckBox(panel, label='Lock Coil Selection', pos=(XOri, YOri + 3*YOffset))
        self.lockCoilChkBox.Enable(False)
        self.polarityChkBox = wx.CheckBox(panel, label='Negative Polarity', pos=(XOri, YOri + 4*YOffset))
        self.polarityChkBox.Enable(False)
        self.lblIRMStatus = wx.StaticText(panel, label='', pos=(XOri + 4*txtOffset, YOri + 5*YOffset))
                
        return 
        
    '''
    '''
    def GUI_CoilTemperatures(self, panel, XOri, YOri):
        XOri += 20
        YOffset = 20
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
        refreshTBtn = wx.Button(panel, label='Read Temp.', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        refreshTBtn.Bind(wx.EVT_BUTTON, self.onRefreshT)
        
        return
    
    '''
    '''
    def GUI_ARM(self, panel, XOri, YOri):
        XOri += 10
        YOffset = 20
        txtOffset = 2
        txtBoxXOffset = 80
        txtBoxLength = 50 
        txtBoxHeight = 20
        wx.StaticText(panel, label='Bias Field (G)', pos=(XOri, YOri + YOffset + txtOffset))
        self.biasFieldTBox = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.biasFieldTBox.SetValue('0')
        
        XOffset = 10
        YOffset += txtBoxHeight + 15
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
    def onFireField(self, event):
        self.fireFieldBtn.Enable(False)
        self.lblIRMStatus.SetLabel('')

        field = self.peakFieldTBox.GetValue()
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_FIRE_AT_FIELD, [field]])
        return
    
    '''
    '''
    def onSetField(self, event):
        self.lblIRMStatus.SetLabel('Charging ...')
        try:
            field = int(self.peakFieldTBox.GetValue())
        except:
            field = 0.0
            
        if (field < 0):
            self.polarityChkBox.SetValue(True)
        else:
            self.polarityChkBox.SetValue(False)
        
        if (self.axialRBtn.GetValue()):
            coilLabel = 'Axial'
        else:
            coilLabel = 'Transverse'    
        
        self.fireFieldBtn.Enable(False)
        self.parent.pushTaskToQueue([self.parent.devControl.IRM_SET_FIELD, [field, coilLabel]])
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
                    
            elif 'Set Field = Done' in eachEntry:
                self.fireFieldBtn.Enable(True)
                            
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
        
        testUnit = frmTestUnit()
        irmARMControl = frmIRMARM(parent=testUnit)
        testUnit.panelList['IRMControl'] = irmARMControl
        irmARMControl.Show(True)        
        app.MainLoop()    
        
    except Exception as e:
        print(e)

        