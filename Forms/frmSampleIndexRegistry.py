'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import os
import sys
import wx

import wx.lib.agw.ultimatelistctrl as ULC

from ClassModules.SampleIndexRegistration import SampleIndexRegistration
from ClassModules.RockmagStep import RockmagSteps

from Forms.frmPlots import frmPlots
from Forms.frmRockmagRoutine import frmRockmagRoutine
from Forms.frmRockmagRoutine import ThreeDRenderer
from Forms.frmTestUnit import frmTestUnit
    
'''
    ----------------------------------------------------------------------------------------
'''    
class frmSampleIndexRegistry(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmSampleIndexRegistry, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmSampleIndexRegistry, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.fileReadyToLoad = False
        self.MeasSusc = False
        self.Warning = False
        self.sampleCodeList = []
        self.workingSamIndex = SampleIndexRegistration(self.parent)
        self.frmPlots = frmPlots(self.parent)
        self.frmRockmagRoutine = frmRockmagRoutine(self.parent)
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
                
        # First Column, First box
        XOri = 10
        YOri = 10
        boxLength = 460
        boxHeight = 380
        wx.StaticBox(panel, -1, 'Load SAM File', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_LoadFile(panel, XOri, YOri)

        YOri += boxHeight + 10
        boxHeight = 80
        wx.StaticBox(panel, -1, 'File Info', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_FileInfo(panel, XOri, YOri)

        YOri += boxHeight + 10
        boxHeight = 160
        wx.StaticBox(panel, -1, 'SAM File Registry', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_SAMFileRegistry(panel, XOri, YOri)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.SetSize((500, 700))
        self.SetTitle('Sample Index Register')
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        if (self.parent != None):
            parentPos = self.parent.GetPosition()
            parentSize = self.parent.GetSize()
            childSize = self.GetSize()
            xOffset = 10
            xPos = parentPos[0] + parentSize[0] - childSize[0] - xOffset * 3
            yPos = parentPos[1] + (parentSize[1]-childSize[1])/2
            frmPos = (int(xPos), int(yPos))
            self.SetPosition(frmPos)
        
        else:
            self.Centre() 
        
    '''
    '''  
    def add_column(self, name, width=ULC.ULC_AUTOSIZE_USEHEADER, renderer=None):
        """A helper method to insert a column with a custom renderer."""
        item_info = ULC.UltimateListItem()
        item_info.SetText(name)
        
        if renderer:
            item_info.SetCustomRenderer(renderer)
                    
        self.fileRegistryLCtrl.InsertColumnInfo(self.fileRegistryLCtrl.GetColumnCount(), item_info)        
        self.fileRegistryLCtrl.SetColumnWidth(self.fileRegistryLCtrl.GetColumnCount() - 1, width)

        return
        
    '''
    '''
    def GUI_SAMFileRegistry(self, panel, XOri, YOri):
        XOri += 10 
        YOri += 20

        listLength = 430
        listHeight = 90                                
        self.fileRegistryLCtrl = ULC.UltimateListCtrl(panel, wx.ID_ANY, pos=(XOri, YOri), size=(listLength, listHeight), agwStyle=ULC.ULC_REPORT | ULC.ULC_VRULES | ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL)
        
        # Create our custom renderer instance
        custom_renderer = ThreeDRenderer()
                
        self.add_column('Sample Set', width=70, renderer=custom_renderer)
        self.add_column('Step', width=60, renderer=custom_renderer)
        self.add_column('Do Up?', width=60, renderer=custom_renderer)
        self.add_column('Do Both?', width=60, renderer=custom_renderer)
        self.add_column('Block', width=40, renderer=custom_renderer)
        self.add_column('Path', width=140, renderer=custom_renderer)

        btnLength = 1201
        btnHeight = 30        
        YOffset = listHeight + 10 
        clearRegistryBtn = wx.Button(panel, label='Clear Registry', pos=(XOri, YOri + YOffset), size=(btnLength, btnHeight))        
        clearRegistryBtn.Bind(wx.EVT_BUTTON, self.onClearRegistry)        
                        
        return    
    
    '''
    '''
    def GUI_FileInfo(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        txtBoxLength = 80
        txtBoxHeight = 25        
        YOffset = 20
        wx.StaticText(panel, label='Latitude', pos=(XOri, YOri))
        self.latitudeTBox = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        
        XOffset = txtBoxLength + 10 
        wx.StaticText(panel, label='Longitude', pos=(XOri + XOffset, YOri))
        self.longitudeTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        wx.StaticText(panel, label='Mag. Dec', pos=(XOri + 2*XOffset, YOri))
        self.magDecTBox = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        XOffset = 3*XOffset + 80
        wx.StaticText(panel, label='# of Sample:', pos=(XOri + XOffset, YOri))
        self.sampleCountTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        return

    '''
    '''
    def GUI_LoadFile(self, panel, XOri, YOri):
        XOri += 20
        YOri += 20
        txtBoxXOffset = 100
        YTextOffset = 2
        txtBoxLength = 280
        txtBoxHeight = 25
        btnLength = 30
        btnHeight = 25        
        wx.StaticText(panel, label='Data Directory', pos=(XOri, YOri + YTextOffset))
        self.txtDir = wx.TextCtrl(panel, pos=(XOri + txtBoxXOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        XOffset = txtBoxXOffset + txtBoxLength + 10
        directoryBtn = wx.Button(panel, label='...', pos=(XOri + XOffset, YOri), size=(btnLength, btnHeight))
        directoryBtn.Bind(wx.EVT_BUTTON, self.onDirectory)
        
        YOffset = txtBoxHeight + 10 
        wx.StaticText(panel, label='Sample Code', pos=(XOri, YOri + 2*YTextOffset + YOffset))
        comboBoxLength = 100
        comboBoxHeight = 22
        self.cmbSampCode = wx.ComboBox(panel, value='', pos=(XOri + txtBoxXOffset, YOri + YOffset), size=(comboBoxLength, comboBoxHeight), choices=self.sampleCodeList)
        self.cmbSampCode.Bind(wx.EVT_COMBOBOX, self.onSampleCodeChanged)
        XOffset = txtBoxXOffset + comboBoxLength + 10
        self.fileTBox = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(210, 56), style=wx.TE_MULTILINE|wx.TE_RICH2)
        
        checkBoxLength = 10
        comboBoxLength = 80
        wx.StaticText(panel, label='Backup Data', pos=(XOri, YOri + 2*YTextOffset + 3*YOffset))
        self.chkBck = wx.CheckBox(panel, pos=(XOri + txtBoxXOffset, YOri + 2*YTextOffset + 3*YOffset))
        self.chkBck.SetValue(True)
        XOffset = txtBoxXOffset + checkBoxLength + 10
        self.driveList = self.getWindowsDrives()
        self.backupDataCBox = wx.ComboBox(panel, value='', pos=(XOri + XOffset, YOri + 3*YOffset), size=(comboBoxLength, comboBoxHeight), choices=self.driveList)
        self.backupDataCBox.SetSelection(0)
        XOffset += comboBoxLength + 10
        txtBoxLength = 210
        self.txtBck = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.txtBck.Bind(wx.EVT_TEXT, self.onSAMTextChange)
        
        wx.StaticText(panel, label='Type of\ndemagnetization\nstep:', pos=(XOri, YOri + 4*YOffset))
        XOffset = 72
        
        '''
            optSAMSetDemag(0) = NRM
            optSAMSetDemag(1) = AF
            optSAMSetDemag(2) = TT
            optSAMSetDemag(3) = MW
            optSAMSetDemag(4) = Other
            optSAMSetDemag(5) = RockMag
        '''        
        self.demagType = 'NRM'        
        self.radioButton0 = wx.RadioButton(panel, 11, label = self.demagType, pos = (XOri + txtBoxXOffset, YOri + 4*YOffset), style = wx.RB_GROUP) 
        self.radioButton1 = wx.RadioButton(panel, 22, label = 'AF',pos = (XOri + txtBoxXOffset + XOffset, YOri + 4*YOffset)) 
        self.radioButton2 = wx.RadioButton(panel, 33, label = 'TT',pos = (XOri + txtBoxXOffset + 2*XOffset, YOri + 4*YOffset))
        rButtonOffset = 25        
        self.radioButton3 = wx.RadioButton(panel, 44, label = 'MW', pos = (XOri + txtBoxXOffset, YOri + 4*YOffset + rButtonOffset)) 
        self.radioButton5 = wx.RadioButton(panel, 55, label = 'Rockmag',pos = (XOri + txtBoxXOffset + XOffset, YOri + 4*YOffset + rButtonOffset)) 
        self.radioButton4 = wx.RadioButton(panel, 66, label = 'Other:',pos = (XOri + txtBoxXOffset + 2*XOffset, YOri + 4*YOffset + rButtonOffset))
        self.Bind(wx.EVT_RADIOBUTTON, self.onDemagnetizationRGroup)
        XOffset = txtBoxXOffset + 2*XOffset + 55
        YTextboxOffset = 20
        txtBoxLength = 60
        self.txtSAMSetDemag = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 4*YOffset + YTextboxOffset), size=(txtBoxLength, txtBoxHeight))        
        XOffset += txtBoxLength + 5
        wx.StaticText(panel, label='Level', pos=(XOri + XOffset, YOri + 4*YOffset + 3))
        self.txtSAMSetDemagLevel = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 4*YOffset + YTextboxOffset), size=(40, txtBoxHeight))
        self.txtSAMSetDemagLevel.SetValue('0')
        self.setLevelsBtn = wx.Button(panel, label='Set Levels', pos=(XOri + XOffset, YOri + 4*YOffset + YTextboxOffset), size=(60, txtBoxHeight))
        self.setLevelsBtn.Bind(wx.EVT_BUTTON, self.onSetLevels)
        self.setLevelsBtn.Hide()
        
        YOffset = 5*YOffset + 30
        wx.StaticText(panel, label='Direction\nto Measure:', pos=(XOri, YOri + YOffset))
        self.chkSAMdoUp = wx.CheckBox(panel, label = 'Up', pos=(XOri + txtBoxXOffset, YOri + YOffset))
        self.chkSAMdoUp.SetValue(True)
        XOffset = 60
        self.chkSAMdoDown = wx.CheckBox(panel, label = 'Down', pos=(XOri + txtBoxXOffset + XOffset, YOri + YOffset))
        self.chkSAMdoDown.SetValue(True)
        self.chkSAMalreadyDoneUp = wx.CheckBox(panel, label = 'Up already measured', pos=(XOri + txtBoxXOffset, YOri + YOffset + rButtonOffset))
        XOffset = txtBoxXOffset + 2*XOffset + 40
        wx.StaticText(panel, label='Measurement blocks\nper cycle:', pos=(XOri+ XOffset, YOri + YOffset))
        XOffset += 120
        YTextboxOffset = 5
        self.txtSAMaveragesteps = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset + YTextboxOffset), size=(40, txtBoxHeight))
        self.txtSAMaveragesteps.SetValue('1')
        
        btnLength = 160
        btnHeight = 30        
        YOffset += 60
        wx.StaticText(panel, label='Sample Table\nType', pos=(XOri, YOri + YOffset))
        self.SampleTableTypeLabel = wx.StaticText(panel, label='XY Table', pos=(XOri + txtBoxXOffset, YOri + YOffset))        
        XOffset = 160
        moveToLoadBtn = wx.Button(panel, label='Move To Load Position', pos=(XOri + txtBoxXOffset + XOffset, YOri + YOffset), size=(btnLength, btnHeight))        
        moveToLoadBtn.Bind(wx.EVT_BUTTON, self.onMoveToLoad)        
        
        btnLength = 120
        btnHeight = 30        
        YOffset += 50
        self.chkMeasureSusceptibility = wx.CheckBox(panel, label = 'Measure Susceptibility', pos=(XOri, YOri + YOffset))
        self.chkMeasureSusceptibility.SetValue(True)
        XOffset = txtBoxXOffset + 70
        self.addRegistryBtn = wx.Button(panel, label='Add To Registry', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.addRegistryBtn.Enable(enable=False)
        self.addRegistryBtn.Bind(wx.EVT_BUTTON, self.onAddToRegistry)        
        XOffset += btnLength + 10 
        openSAMBtn = wx.Button(panel, label='Open SAM File', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        openSAMBtn.Bind(wx.EVT_BUTTON, self.onOpenSAMFile)        
        
        return
    
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def get_Float(self, textBox):
        try:
            floatVal = float(textBox.GetValue())
        except:
            floatVal = 0.0
            
        return floatVal

    '''
    '''
    def get_Int(self, textBox):
        try:
            intVal = int(textBox.GetValue())
        except:
            intVal = 0
            
        return intVal
   
    '''
    '''
    def getWindowsDrives(self):
        drives = []
        for x in range(65, 91):  # ASCII values for 'A' to 'Z'
            drive_letter = chr(x) + ":"
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
                
        return drives
    
    '''
    '''
    def clearCmbSampCode(self):
        self.sampleCodeList = []
        self.cmbSampCode.Clear()
        return
    
    '''
        This procedure updates the 'Info' frame with data from the
        sample header file.
    '''
    def ReadSamInfo(self):
        self.fileTBox.SetValue(self.workingSamIndex.locality)
        self.latitudeTBox.SetValue("{:.2f}".format(self.workingSamIndex.siteLat))
        self.longitudeTBox.SetValue("{:.2f}".format(self.workingSamIndex.siteLong))
        self.magDecTBox.SetValue("{:.2f}".format(self.workingSamIndex.magDec))
        self.sampleCountTBox.SetValue(str(self.workingSamIndex.sampleSet.Count))
        return
    
    '''
    '''
    def updateBackupDir(self):
        if self.chkBck.GetValue():
            self.workingSamIndex.BackupFileDir = self.txtBck.GetValue()
        else:
            self.workingSamIndex.BackupFileDir = ''
        return
    
    '''
    '''
    def UpdateMeasureSusceptibility(self):
        for RMStep in self.workingSamIndex.measurementSteps.Item:
            RMStep[0].MeasureSusceptibility = (self.chkMeasureSusceptibility.GetValue() and self.parent.modConfig.EnableSusceptibility)
        
        if (self.chkMeasureSusceptibility.GetValue() and self.parent.modConfig.EnableSusceptibility):        
            self.MeasSusc = True
            
        return
    
    '''
        optSAMSetDemag(0) = NRM
        optSAMSetDemag(1) = AF
        optSAMSetDemag(2) = TT
        optSAMSetDemag(3) = MW
        optSAMSetDemag(4) = Other
        optSAMSetDemag(5) = RockMag
    '''
    def updateMeasurementSteps(self):
        self.workingSamIndex.measurementSteps.Item = []
        
        if (self.demagType == 'AF'):
            self.workingSamIndex.RockmagMode = True
            self.workingSamIndex.measurementSteps.Item = self.frmRockmagRoutine.rmStepList.Item
            self.UpdateMeasureSusceptibility()
            
        elif (self.demagType == 'Rockmag'):
            self.workingSamIndex.RockmagMode = True
            self.workingSamIndex.measurementSteps.Item = self.frmRockmagRoutine.rmStepList.Item
            
            # Check to see if any of the RockMag steps need their susceptibility to be measured
            for i in range(0, self.workingSamIndex.measurementSteps.Count):            
                    if ((self.workingSamIndex.measurementSteps.Item[i][0].MeasureSusceptibility or \
                        self.MeasSusc) and self.parent.modConfig.EnableSusceptibility):                    
                        self.MeasSusc = True
                        break
                        
                    elif not self.parent.modConfig.EnableSusceptibility:                    
                        self.MeasSusc = False
                        self.workingSamIndex.measurementSteps.Item[i][0].MeasureSusceptibility = False
            
            if (self.chkSAMdoUp.GetValue() and (self.workingSamIndex.measurementSteps.Count > 1)):
                self.chkSAMdoDown.SetValue(False)
            
        elif (self.demagType == 'Other:'):
            self.workingSamIndex.measurementSteps = RockmagSteps()
            self.workingSamIndex.measurementSteps.Add(self.txtSAMSetDemag.GetValue(), \
                                                      self.get_Int(self.txtSAMSetDemagLevel), \
                                                      MeasureSusceptibility = \
                                                      (self.chkMeasureSusceptibility.GetValue() and \
                                                       self.parent.modConfig.EnableSusceptibility))
            self.workingSamIndex.RockmagMode = True         # False (March 2008 L Carporzen) Always write the RMG file
            
        else:
            self.workingSamIndex.measurementSteps = RockmagSteps()
            self.workingSamIndex.RockmagMode = True         # False (March 2008 L Carporzen) Always write the RMG file
            self.workingSamIndex.measurementSteps.Add(self.demagType, \
                                                      self.get_Int(self.txtSAMSetDemagLevel), \
                                                      MeasureSusceptibility = \
                                                      (self.chkMeasureSusceptibility.GetValue() and \
                                                      self.parent.modConfig.EnableSusceptibility))
            
        self.workingSamIndex.avgSteps = self.get_Int(self.txtSAMaveragesteps)
        
        # Do final check to see if the susceptibility needs to be measured
        if (self.chkMeasureSusceptibility.GetValue() and self.parent.modConfig.EnableSusceptibility):        
            self.MeasSusc = True            
        
        # Now, overwrite the Sample Holder Sample Index in the global SampleIndexRegistrations object
        self.parent.SampleIndexRegistry.MakeSampleHolder(self.MeasSusc)
        return
    
    '''
    '''
    def UpdateDoUpDoBoth(self):
        if ((self.chkSAMalreadyDoneUp.GetValue() or self.chkSAMdoUp.GetValue()) and self.chkSAMdoDown.GetValue()):
            filedoboth = True
        else:
            filedoboth = False
        
        filedoup = self.chkSAMdoUp.GetValue()
        self.workingSamIndex.doUp = filedoup
        self.workingSamIndex.doBoth = filedoboth
        return
    
    '''
        This function determines whether all the fields have
        valid values.  If not, an error message is given.
        Otherwise, the function returns true.
    '''
    def CheckSetFields(self):
        status = False
        tmpint = self.get_Int(self.txtSAMaveragesteps)
        if (tmpint <= 0):
            wx.MessageBox("Value must be greater than 0.")
            return status
        
        if ((not self.chkSAMdoUp.GetValue()) and \
            (not self.chkSAMdoDown.GetValue())):
            # Neither direction boxes are checked, at least one
            # must be checked to do anything.
            wx.MessageBox("Please select a measurement direction.")
            self.chkSAMdoUp.SetFocus()
            return status
        
        status = True        
        return status
    
    '''
    '''
    def refreshSAMRegistryDisplay(self):
        self.fileRegistryLCtrl.DeleteAllItems()
        
        if self.parent.modConfig.UseXYTableAPS:
            self.SampleTableTypeLabel.SetLabel("XY Table")
        else:
            self.SampleTableTypeLabel.SetLabel("Chain Drive")
        
        #With SampleIndexRegistry
        if (self.parent.SampleIndexRegistry.Count == 0):
            return
        
        count = 1
        for item in self.parent.SampleIndexRegistry.Item:
            # Insert a new row and get its index
            index = self.fileRegistryLCtrl.InsertStringItem(sys.maxsize, str(count))
            
            # Set the text for other columns in that row
            self.fileRegistryLCtrl.SetStringItem(index, 0, item.SampleCode)
            self.fileRegistryLCtrl.SetStringItem(index, 1, item.curDemag)                        
            if item.doUp:
                self.fileRegistryLCtrl.SetStringItem(index, 2, "Y")
            else: 
                self.fileRegistryLCtrl.SetStringItem(index, 2, "N")                
            if item.doBoth: 
                self.fileRegistryLCtrl.SetStringItem(index, 3, "Y")
            else: 
                self.fileRegistryLCtrl.SetStringItem(index, 3, "N")
            self.fileRegistryLCtrl.SetStringItem(index, 4, str(item.avgSteps))
            self.fileRegistryLCtrl.SetStringItem(index, 5, item.filename)                
            count += 1
            
        return
    
    '''
    '''
    def refreshFields(self):
        self.txtDir.SetValue(self.workingSamIndex.filedir)
        self.txtBck.SetValue(self.workingSamIndex.BackupFileDir)
        self.cmbSampCode.SetValue(self.workingSamIndex.SampleCode)
        self.ReadSamInfo()
        if (self.workingSamIndex.BackupFileDir != ''):
            self.chkBck.SetValue(True)
        else:
            self.chkBck.SetValue(False)
        
        self.cmbSampCode.SetValue(self.workingSamIndex.SampleCode)
        if self.workingSamIndex.doBoth:
            self.chkSAMdoDown.SetValue(True)
            if self.workingSamIndex.doUp:
                self.chkSAMdoUp.SetValue(True)
                self.chkSAMalreadyDoneUp.SetValue(False)
            else:
                self.chkSAMdoUp.SetValue(False)
                self.chkSAMalreadyDoneUp.SetValue(True)
            
        else:
            if self.workingSamIndex.doUp:
                self.chkSAMdoUp.SetValue(True)
                self.chkSAMdoDown.SetValue(False)
                self.chkSAMalreadyDoneUp.SetValue(False)
            else:
                self.chkSAMdoUp.SetValue(False)
                self.chkSAMdoDown.SetValue(True)
                self.chkSAMalreadyDoneUp.SetValue(False)
            
        if (self.workingSamIndex.avgSteps > 0):
            self.txtSAMaveragesteps.SetValue(str(self.workingSamIndex.avgSteps))
        else:
            self.txtSAMaveragesteps.SetValue("1")
        
        self.txtSAMSetDemag.SetValue('')
        if (self.workingSamIndex.measurementSteps.Count > 1):
            self.radioButton5.SetValue(True)
            self.frmRockmagRoutine.rmStepList.Item = self.workingSamIndex.measurementSteps.Item
        else:
            if (self.workingSamIndex.curDemag == "TT"):
                self.radioButton2.SetValue(True)
                self.txtSAMSetDemagLevel.SetValue(self.workingSamIndex.curDemag)
            if (self.workingSamIndex.curDemag == "NR"):
                self.radioButton0.SetValue(True)
            if (self.workingSamIndex.curDemag == "MW"):
                self.radioButton3.SetValue(True)
                self.txtSAMSetDemagLevel.SetValue(self.workingSamIndex.curDemag)
            if (self.workingSamIndex.curDemag == "AF"):
                self.radioButton1.SetValue(True)
            if (self.workingSamIndex.curDemag == ''):
                self.radioButton0.SetValue(True)
                self.txtSAMSetDemagLevel.SetValue('')
            else:
                self.radioButton4.SetValue(True)
                self.txtSAMSetDemag.SetValue(self.workingSamIndex.curDemag)
                
        return
    
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onSetLevels(self, event):
        if ((self.demagType == 'AF') or (self.demagType == 'Rockmag')):
            self.frmRockmagRoutine.ZOrder()
            self.frmRockmagRoutine.Show()
        return
    
    '''
    '''
    def fileReadyToLoad(self):
        status = True
        return status
    
    '''
    '''
    def onAddToRegistry(self, event):
        if (self.parent != None):
            if ((not self.parent.magControl.manualPage.cmdManHolder.IsEnabled()) \
                and (not self.parent.magControl.autoPage.cmdChangerEdit.IsEnabled())):
                return
        
        self.updateBackupDir()
        self.updateMeasurementSteps()
        self.UpdateDoUpDoBoth()
        if not self.CheckSetFields(): 
            return
                
        if self.fileReadyToLoad:
            target = self.parent.SampleIndexRegistry.AddSampleIndex(self.workingSamIndex)
            target.loadInfo()
        
        self.refreshSAMRegistryDisplay()
        self.frmPlots.RefreshSamples()
        if (self.parent.magControl.manualPage.cmbManSample.GetValue() != ''):
            self.parent.magControl.RefreshManSampleList()         # (September 2007 L Carporzen) Refresh the sample list
            self.parent.magControl.manualPage.cmbManSample.SetValue('')      # (September 2007 L Carporzen) Empty the sample name in the Manual Data Collection window
        
        if not self.Warning:
            rockmagMsg = ''        
            '''
                (July 2011 - I Hilburn)
                Warning message statements revised to include switching on the Coil thermal sensors   
                optSAMSetDemag(0) = NRM
                optSAMSetDemag(1) = AF
                optSAMSetDemag(2) = TT
                optSAMSetDemag(3) = MW
                optSAMSetDemag(4) = Other
                optSAMSetDemag(5) = RockMag
            '''
            if (((self.demagType == 'AF') or (self.demagType == 'RockMag')) and (self.frmRockmagRoutine.chksusceptibility.GetValue())):     
            # automatically turn on the air
                if self.modConfig.DoDegausserCooling:
                    self.parent.vacuumControl.DegausserCooler(True)
                    rockmagMsg = "Please: \n\n"
                    rockmagMsg += " - Verify the air is on\n"
                    rockmagMsg += " - Make sure the susceptibility meter is well positioned."
                else:
                    rockmagMsg = "Please: \n\n"
                    rockmagMsg += " - Turn the air on\n"
                    rockmagMsg += " - Make sure the susceptibility meter is well positioned."                            
                self.Warning = True
                
            elif ((self.demagType == 'AF') or (self.demagType == 'RockMag')):
                # automatically turn on the air
                if self.modConfig.DoDegausserCooling:
                    self.parent.vacuumControl.DegausserCooler(True)
                    rockmagMsg = "Please: \n\n"
                    rockmagMsg += " - Verify the air is on\n"
                    rockmagMsg += " - Make sure the susceptibility meter is well positioned."
                else:
                    rockmagMsg = "Please: \n\n"
                    rockmagMsg += " - Turn the air on\n"
                    rockmagMsg += " - Make sure the susceptibility meter is well positioned."                    
                self.Warning = True
                
            elif self.chkMeasureSusceptibility.GetValue():
                rockmagMsg = "Please: \n\n"
                rockmagMsg += " - Make sure the susceptibility meter is well positioned.\n"
                self.Warning = True
            
            if (((self.demagType == 'AF') or (self.demagType == 'RockMag')) and (self.modConfig.EnableT1 or self.modConfig.EnableT2)):
                rockmagMsg += " - Switch the power on for the Rockmag coil thermal sensors"
               
            if (len(rockmagMsg) > 0):
                wx.MessageBox(rockmagMsg, style=wx.OK|wx.CENTER, caption='Warning!')
            
        if self.parent.modFlow.Prog_halted:
            self.parent.modMeasure.HolderMeasured = False
            self.parent.modFlow.Flow_Resume()
            self.parent.frmMeasure.updateFlowStatus
            
        return
    
    '''
    '''
    def onOpenSAMFile(self, event):
        self.frmPlots.Show(show=True)
        return
    
    '''
    '''
    def onDemagnetizationRGroup(self, event):
        self.demagType = event.EventObject.GetLabel()
        if ((self.demagType == 'AF') or (self.demagType == 'Rockmag')):
            self.txtSAMSetDemagLevel.Hide()
            self.setLevelsBtn.Show()
        else:
            self.setLevelsBtn.Hide()
            self.txtSAMSetDemagLevel.Show()
                        
        return
   
    '''
    '''
    def onMoveToLoad(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_LOAD, [None]])
        return
    
    '''
    '''
    def onSampleCodeChanged(self, event):
        sampleCode = self.cmbSampCode.GetValue()
         
        directoryPath = os.path.dirname(self.samFilePath)
        directoryPath = os.path.abspath(os.path.join(directoryPath, os.pardir))         
        fileName = directoryPath + '\\' + sampleCode + '\\' + sampleCode + '.sam'
        
        if not (os.path.exists(fileName)):
            return
        
        self.workingSamIndex.SampleCode = sampleCode
        self.workingSamIndex.filedir = directoryPath
        self.workingSamIndex.filename = fileName
        self.workingSamIndex.loadInfo()
        
        self.ReadSamInfo()
        
        # Update the form
        self.fileReadyToLoad = True
        self.addRegistryBtn.Enable(enable=True)
        
        return
   
    '''
    '''
    def onSAMTextChange(self, event):
        
        self.clearCmbSampCode()
        
        directoryPath = os.path.dirname(self.samFilePath)
        directoryPath = os.path.abspath(os.path.join(directoryPath, os.pardir))
        self.txtDir.SetValue(directoryPath)
        
        for eachDir in os.listdir(directoryPath):
            if os.path.isdir(directoryPath + '\\' + eachDir):
                self.cmbSampCode.Append(eachDir)
        if (len(self.cmbSampCode.Items) > 0):
            self.cmbSampCode.SetSelection(0)
            self.onSampleCodeChanged(self.cmbSampCode)
            
        return
   
    '''
    '''
    def onDirectory(self, event):
        dlg = wx.FileDialog(self, "Open", "", "",
                            "Sample description files(*.sam)|*.sam",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.samFilePath = dlg.GetPath()
            self.txtBck.SetValue(self.samFilePath)
        return
    
    '''
    '''
    def onClearRegistry(self, event):
        if (self.parent != None):
            if ((not self.parent.magControl.manualPage.cmdManHolder.IsEnabled()) \
                and (not self.parent.magControl.autoPage.cmdChangerEdit.IsEnabled())):
                return

        self.parent.SampQueue.Clear()
        self.parent.MainChanger.Clear()
        self.parent.SampleIndexRegistry.Clear()
        self.workingSamIndex = SampleIndexRegistration(self.parent)
        self.refreshSAMRegistryDisplay()
        self.refreshFields()
        self.chkBck.SetValue(True)
        self.chkMeasureSusceptibility.SetValue(True)
        self.chkSAMdoUp.SetValue(True)
        self.chkSAMdoDown.SetValue(True)
        self.Warning = False
        return
    
    '''
        Close Tip Dialog box
    '''
    def onClose(self, event):
        if (self.parent != None):
            if self.parent.panelList:
                if 'RegistryControl' in self.parent.panelList.keys():          
                    del self.parent.panelList['RegistryControl']
                
        self.Destroy()

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        testUnit = frmTestUnit()
        frame = frmSampleIndexRegistry(parent=testUnit)
        frame.Show(True)        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                
