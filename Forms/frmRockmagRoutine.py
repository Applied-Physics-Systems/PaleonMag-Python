'''
Created on Sep 8, 2025

@author: hd.nguyen
'''
import wx
import sys
import math

import wx.lib.agw.ultimatelistctrl as ULC

from Forms.frmTestUnit import frmTestUnit
from ClassModules.RockmagStep import RockmagSteps

'''
    ---------------------------------------------------------------------------------------
'''
class ThreeDRenderer(object):
    """A custom renderer to draw a 3D button effect on the header."""

    def __init__(self):
        # Define colors for the button effect
        self.face_color = wx.Colour(220, 220, 220)  # Light gray face
        self.highlight_color = wx.Colour(245, 245, 245) # Lighter edge
        self.shadow_color = wx.Colour(170, 170, 170)    # Darker edge

    '''
    '''
    def DrawHeaderButton(self, dc, rect, header):
        """Draw the 3D button background and the header text."""
        # Draw the main button rectangle
        dc.SetBrush(wx.Brush(self.face_color))
        dc.SetPen(wx.Pen(self.face_color))
        dc.DrawRectangle(rect)

        # Draw the 3D highlights (top and left edges)
        dc.SetPen(wx.Pen(self.highlight_color))
        dc.DrawLine(rect.GetLeft(), rect.GetTop(), rect.GetRight(), rect.GetTop())
        dc.DrawLine(rect.GetLeft(), rect.GetTop(), rect.GetLeft(), rect.GetBottom())

        # Draw the 3D shadows (bottom and right edges)
        dc.SetPen(wx.Pen(self.shadow_color))
        dc.DrawLine(rect.GetRight(), rect.GetTop(), rect.GetRight(), rect.GetBottom())
        dc.DrawLine(rect.GetLeft(), rect.GetBottom(), rect.GetRight(), rect.GetBottom())
        return
    
    '''
    '''        
    def GetForegroundColour(self):
        """Returns the text color for the header."""
        return wx.BLACK

'''
    ---------------------------------------------------------------------------------------
'''
class frmRockmagRoutine(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmRockmagRoutine, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmRockmagRoutine, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        self.rmgFilePath = ''
        
        self.rmStepList = RockmagSteps(self.parent)
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        # First Column, First box
        XOri = 10
        YOri = 10
        boxLength = 800
        boxHeight = 250
        wx.StaticBox(panel, -1, 'Presets', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_Presets(panel, XOri, YOri)
        
        YOri += boxHeight + 10
        boxHeight = 150
        wx.StaticBox(panel, -1, 'Set Steps', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_SetSteps(panel, XOri, YOri)

        YOri += boxHeight + 10
        boxHeight = 200
        wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        self.GUI_SampleList(panel, XOri, YOri)
        
        panelLength = boxLength + 40
        panelHeight = YOri + boxHeight + 50 
        self.SetSize(panelLength, panelHeight)
        self.SetTitle('Set Rock Mag Routine')
        self.Centre()
        
    '''
    '''    
    def add_column(self, name, width=ULC.ULC_AUTOSIZE_USEHEADER, renderer=None):
        """A helper method to insert a column with a custom renderer."""
        item_info = ULC.UltimateListItem()
        item_info.SetText(name)
        
        if renderer:
            item_info.SetCustomRenderer(renderer)
        
        self.rockmagLCtrl.InsertColumnInfo(self.rockmagLCtrl.GetColumnCount(), item_info)
        self.rockmagLCtrl.SetColumnWidth(self.rockmagLCtrl.GetColumnCount() - 1, width)    
        
    '''
    '''
    def GUI_SampleList(self, panel, XOri, YOri):
        listLength = 800
        listHeight = 150                                
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.rockmagLCtrl = ULC.UltimateListCtrl(panel, wx.ID_ANY, pos=(XOri, YOri), size=(listLength, listHeight), agwStyle=ULC.ULC_REPORT | ULC.ULC_VRULES | ULC.ULC_HRULES | ULC.ULC_SINGLE_SEL)
        
        # Create our custom renderer instance
        custom_renderer = ThreeDRenderer()
                
        self.add_column('#', width=40, renderer=custom_renderer)
        self.add_column('Step Type', width=90, renderer=custom_renderer)
        self.add_column('Level (G)', width=90, renderer=custom_renderer)
        self.add_column('Bias Field (G)', width=90, renderer=custom_renderer)
        self.add_column('Spin (RPS)', width=90, renderer=custom_renderer)
        self.add_column('Hold (sec)', width=90, renderer=custom_renderer)
        self.add_column('Measure ?', width=90, renderer=custom_renderer)
        self.add_column('Suscep ?', width=90, renderer=custom_renderer)
        self.add_column('Remarks', width=100, renderer=custom_renderer)
        
        # Add the ListCtrl to the sizer and make it expandable
        # The wx.EXPAND flag and a non-zero proportion (1) are essential
        sizer.Add(self.rockmagLCtrl, 1, wx.ALL, 5)
        
        XOri += 20
        YOri += listHeight + 10
        btnLength = 120
        btnHeight = 30        
        XOffset = btnLength + 40 
        clearBtn = wx.Button(panel, label='Clear', pos=(XOri, YOri), size=(btnLength, btnHeight))
        clearBtn.Bind(wx.EVT_BUTTON, self.onClear)
        deleteBtn = wx.Button(panel, label='Delete', pos=(XOri + XOffset, YOri), size=(btnLength, btnHeight))
        deleteBtn.Bind(wx.EVT_BUTTON, self.onDelete)
        importBtn = wx.Button(panel, label='Import From .RMG', pos=(XOri + 2*XOffset, YOri), size=(btnLength, btnHeight))
        importBtn.Bind(wx.EVT_BUTTON, self.onImport)
        saveBtn = wx.Button(panel, label='Save To .RMG', pos=(XOri + 3*XOffset, YOri), size=(btnLength, btnHeight))
        saveBtn.Bind(wx.EVT_BUTTON, self.onSave)
        okBtn = wx.Button(panel, label='OK', pos=(XOri + 4*XOffset, YOri), size=(btnLength, btnHeight))
        okBtn.Bind(wx.EVT_BUTTON, self.onOK)
        
        return
        
    '''
    '''
    def GUI_SetSteps(self, panel, XOri, YOri):
        XOri += 10 
        YOri += 20
        
        txtBoxLength = 60        
        txtBoxHeight = 25
        XOffset = txtBoxLength + 40 
        YTextOffset = 5
        self.txtStepSize = wx.TextCtrl(panel, pos=(XOri, YOri), size=(txtBoxLength, txtBoxHeight))
        self.txtStepSize.SetValue('25')
        wx.StaticText(panel, label='G Steps from', pos=(XOri  + 2*XOffset - 80, YOri + YTextOffset))
        self.txtStepMin = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='to', pos=(XOri  + 3*XOffset - 20, YOri + YTextOffset))
        self.txtStepMax = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        self.txtStepMax.SetValue('200')
        
        comboBoxLength = 60 
        comboBoxHeight = 25
        wx.StaticText(panel, label='G of type', pos=(XOri  + 5*XOffset - 60, YOri + YTextOffset))
        self.cmbStepSeq = wx.ComboBox(panel, value='', pos=(XOri + 5*XOffset, YOri + 3), size=(comboBoxLength, comboBoxHeight), choices=['AF', 'AFz', 'IRMz'])
        self.cmbStepSeq.SetSelection(0)
        self.cmbStepSeqScale = wx.ComboBox(panel, value='', pos=(XOri + 6*XOffset, YOri + 3), size=(comboBoxLength, comboBoxHeight), choices=['Linear', 'Log'])
        self.cmbStepSeqScale.SetSelection(0)
        
        btnLength = 60
        btnHeight = 25
        gStepsAddBtn = wx.Button(panel, label='Add', pos=(XOri + 7*XOffset + 15, YOri), size=(btnLength, btnHeight))
        gStepsAddBtn.Bind(wx.EVT_BUTTON, self.onGStepsAdd)

        YOffset = txtBoxHeight + 10 
        self.txtARMSteps = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.txtARMSteps.SetValue('2')
        wx.StaticText(panel, label='G ARM bias steps up to', pos=(XOri  + 3*XOffset - 130, YOri + YOffset + YTextOffset))
        self.txtARMBiasMax = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.txtARMBiasMax.SetValue('8')
        wx.StaticText(panel, label='G in AF field of', pos=(XOri  + 5*XOffset - 90, YOri + YOffset + YTextOffset))
        self.txtAFfieldForARM = wx.TextCtrl(panel, pos=(XOri + 5*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.txtAFfieldForARM.SetValue('1000')
        self.cmbARMStepSeqScale = wx.ComboBox(panel, value='', pos=(XOri + 6*XOffset, YOri + YOffset + 3), size=(comboBoxLength, comboBoxHeight), choices=['Linear', 'Log'])
        self.cmbARMStepSeqScale.SetSelection(0)
        gARMAddBtn = wx.Button(panel, label='Add', pos=(XOri + 7*XOffset + 15, YOri + YOffset), size=(btnLength, btnHeight))
        gARMAddBtn.Bind(wx.EVT_BUTTON, self.onGARMAdd)
        
        XOffset = txtBoxLength + 15
        YTextOffset = 20
        wx.StaticText(panel, label='Step Type', pos=(XOri, YOri + 2*YOffset))
        stepTypeList = ['AF', 'AFz', 'AFmax', 'UAF', 'UAFZ1', 'UAFX1', 'UAFX2', 'aTAFX', 'aTAFY', 'aTAFZ', \
                        'GRM AF', 'ARM', 'IRMz', 'NRM', 'VRM', 'RRM', 'RRMz', 'X']
        self.cmbStepType = wx.ComboBox(panel, value='', pos=(XOri, YOri + 2*YOffset + YTextOffset), size=(comboBoxLength, comboBoxHeight), choices=stepTypeList)
        self.cmbStepType.SetSelection(0)
        wx.StaticText(panel, label='Level', pos=(XOri + XOffset, YOri + 2*YOffset))
        self.txtLevel = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 2*YOffset + YTextOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Bias (G)', pos=(XOri + 2*XOffset, YOri + 2*YOffset))
        self.txtBiasField = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + 2*YOffset + YTextOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Spin (rps)', pos=(XOri + 3*XOffset, YOri + 2*YOffset))
        self.txtSpinSpeed = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + 2*YOffset + YTextOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Hold (s)', pos=(XOri + 4*XOffset, YOri + 2*YOffset))
        self.txtHoldTime = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + 2*YOffset + YTextOffset), size=(txtBoxLength, txtBoxHeight))
        
        YTextOffset = 25
        self.chkMeasure = wx.CheckBox(panel, label = 'Measure', pos=(XOri + 5*XOffset, YOri + 2*YOffset + YTextOffset))
        self.chkMeasure.SetValue(True)
        self.chksusceptibility = wx.CheckBox(panel, label = 'Susceptibility', pos=(XOri + 6*XOffset, YOri + 2*YOffset + YTextOffset))

        YTextOffset = 20
        wx.StaticText(panel, label='Remarks', pos=(XOri + 8*XOffset, YOri + 2*YOffset))
        self.txtRemarks = wx.TextCtrl(panel, pos=(XOri + 8*XOffset, YOri + 2*YOffset + YTextOffset), size=(txtBoxLength, txtBoxHeight))

        stepAddBtn = wx.Button(panel, label='Add', pos=(XOri + 9*XOffset + 40, YOri + 2*YOffset + YTextOffset), size=(btnLength, btnHeight))
        stepAddBtn.Bind(wx.EVT_BUTTON, self.onStepAdd)
        
        return
    
    '''
    '''
    def GUI_Presets(self, panel, XOri, YOri):
        XOri += 10 
        YOri += 20
        
        btnLength = 300
        btnHeight = 30
        buttonLabel = 'Hawaiian Standard AF (25, 50, 100, 200, 400, 800)'
        standardAFBtn = wx.Button(panel, label=buttonLabel, pos=(XOri, YOri), size=(btnLength, btnHeight))
        standardAFBtn.Bind(wx.EVT_BUTTON, self.onStandardAF)
        
        YOri += btnHeight + 10
        buttonLabel = 'Rockmag the "Works"'
        rockmagBtn = wx.Button(panel, label=buttonLabel, pos=(XOri, YOri), size=(btnLength, btnHeight))
        rockmagBtn.Bind(wx.EVT_BUTTON, self.onRockMag)
        
        YOri += btnHeight + 10
        self.chkRMAllNRM = wx.CheckBox(panel, label = 'Measure and AF demagnetize NRM', pos=(XOri, YOri))
        XOffset = 230
        self.chkRMAllNRM3AxisAF = wx.CheckBox(panel, label = 'along all three axes', pos=(XOri + XOffset, YOri))
        XOffset += 150
        self.chkTheWorksMeasSusc = wx.CheckBox(panel, label = 'Measure Susceptibility', pos=(XOri + XOffset, YOri))
        
        YOffset = 30
        self.chkRMAllWithRRM = wx.CheckBox(panel, label = 'RRM (rps):', pos=(XOri, YOri + YOffset))
        self.chkRMAllARM = wx.CheckBox(panel, label = 'ARM Step Size (G):', pos=(XOri, YOri + 2*YOffset))
        self.chkRMAllIRM = wx.CheckBox(panel, label = 'AF/IRM Log Step (G):', pos=(XOri, YOri + 3*YOffset))
        self.chkRMAllBackfieldDemag = wx.CheckBox(panel, label = 'DC Demag via backfield IRM:', pos=(XOri, YOri + 4*YOffset))
        
        XOffset = 200
        txtBoxLength = 60        
        txtBoxHeight = 25
        YAlignment = 5
        XBoxOffset = txtBoxLength + 40 
        self.txtRMAllRRMrpsStep = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri  + YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='to', pos=(XOri  + XOffset + XBoxOffset - 20, YOri + YOffset))
        self.txtRMAllRRMrpsMax = wx.TextCtrl(panel, pos=(XOri + XOffset + XBoxOffset, YOri  + YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllRRMAFField = wx.TextCtrl(panel, pos=(XOri + XOffset + 2*XBoxOffset, YOri  + YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.chkRMAllRRMdoNegative = wx.CheckBox(panel, label = 'and negative rotations', pos=(XOri + XOffset + 3*XBoxOffset, YOri + YOffset))

        self.txtRMAllARMStepSize = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri  + 2*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllARMStepSize.SetValue('1')
        wx.StaticText(panel, label='to', pos=(XOri  + XOffset + XBoxOffset - 20, YOri + 2*YOffset))
        self.txtRMAllARMStepMax = wx.TextCtrl(panel, pos=(XOri + XOffset + XBoxOffset, YOri  + 2*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllARMStepMax.SetValue('9')
        self.txtRMAllAFFieldForARM = wx.TextCtrl(panel, pos=(XOri + XOffset + 2*XBoxOffset, YOri  + 2*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllAFFieldForARM.SetValue('1000')

        self.txtRMAllLogFactor = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri  + 3*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllLogFactor.SetValue('1.3')
        wx.StaticText(panel, label='Min. step size (G):', pos=(XOri  + XOffset + XBoxOffset, YOri + 3*YOffset))
        self.txtRMAllMinStepSize = wx.TextCtrl(panel, pos=(XOri + XOffset + 2*XBoxOffset, YOri  + 3*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllMinStepSize.SetValue('10')
        XBoxOffset += 30
        XOri += XOffset + 2*XBoxOffset + txtBoxLength + 45         
        XBoxOffset = 2*txtBoxLength + 30
        wx.StaticText(panel, label='AF Max (G):', pos=(XOri - txtBoxLength - 10, YOri + 3*YOffset))
        self.txtRMAllAFMax = wx.TextCtrl(panel, pos=(XOri, YOri  + 3*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllAFMax.SetValue('2400')
        wx.StaticText(panel, label='IRM Max (G):', pos=(XOri + XBoxOffset - txtBoxLength - 15, YOri + 3*YOffset))
        self.txtRMAllIRMMax = wx.TextCtrl(panel, pos=(XOri + XBoxOffset, YOri  + 3*YOffset - YAlignment), size=(txtBoxLength, txtBoxHeight))
        self.txtRMAllIRMMax.SetValue('17000')
        
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def ImportRMGRoutine(self, fileName):
        with open(fileName, "rt") as rmgFile:
            rmgFile.readline()
            for line in rmgFile:
                lineList = line.split(',')
                stepType = lineList[0].strip()
                if (stepType == 'UAFZ'):
                    stepType = 'UAFZ1'         # Correct the old UAFZ
                level = int(lineList[1].strip())
                biasField = int(lineList[2].strip())
                spinSpeed = int(lineList[3].strip())
                holdTime = int(lineList[4].strip())
                if (float(lineList[5].strip()) == 0.0):
                    readMeas = False
                else:
                    readMeas = True
                if (float(lineList[8].strip()) == 0.0):
                    readSusceptibility = False
                else:
                    readSusceptibility = True
                self.rmStepList.Add(stepType, level, biasField, spinSpeed, holdTime, readMeas, readSusceptibility)
              
        self.refreshListDisplay()  
        return
    
    '''
    '''
    def SaveRMGRoutine(self, fileName):
        with open(fileName, "w") as file:
            file.write("Level,Bias Field (G),Spin Speed (rps),Hold Time (s),Mz (emu),Std. Dev. Z,Mz/Vol,Moment Susceptibility (emu/Oe),Mx (emu),Std. Dev. X,My (emu),Std. Dev. Y\n")
            for item in self.rmStepList.Item:
                file.write(item[0].StepType + ', ')
                file.write(str(item[0].Level) + ', ')
                file.write(str(item[0].BiasField) + ', ')
                file.write(str(item[0].SpinSpeed) + ', ')
                file.write(str(item[0].HoldTime) + ', ')
                j = 1.00000000000001E-09
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                j = 1.00000000001
                if item[0].MeasureSusceptibility:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')                    
                j = 1.00000000000001E-09
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                if item[0].Measure:
                    file.write(str(j) + ', ')
                else:
                    file.write('0, ')
                if item[0].Measure:
                    file.write(str(j))
                else:
                    file.write('0')
                file.write('\n')
        return
    
    '''
    '''
    def refreshListDisplay(self):
        self.rockmagLCtrl.DeleteAllItems()
        count = 1
        for item in self.rmStepList.Item:
            # Insert a new row and get its index
            index = self.rockmagLCtrl.InsertStringItem(sys.maxsize, str(count))

            # Set the text for other columns in that row
            self.rockmagLCtrl.SetStringItem(index, 1, item[0].StepType)            
            self.rockmagLCtrl.SetStringItem(index, 2, str(item[0].Level))
            self.rockmagLCtrl.SetStringItem(index, 3, str(item[0].BiasField))
            self.rockmagLCtrl.SetStringItem(index, 4, str(item[0].SpinSpeed))
            self.rockmagLCtrl.SetStringItem(index, 5, str(item[0].HoldTime))
            if item[0].Measure:
                self.rockmagLCtrl.SetStringItem(index, 6, 'Y')
            else: 
                self.rockmagLCtrl.SetStringItem(index, 6, 'N')
            if item[0].MeasureSusceptibility:
                self.rockmagLCtrl.SetStringItem(index, 7, 'Y')
            else: 
                self.rockmagLCtrl.SetStringItem(index, 7, 'N')
            self.rockmagLCtrl.SetStringItem(index, 8, item[0].Remarks)
            count += 1
                                        
        return
    
    '''
    '''
    def ZOrder(self):
        print('TODO: frmRockmagRoutine.ZOrder')
        return
    
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
    
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onOK(self, event):
        self.Close()
        return
   
    '''
    '''
    def onSave(self, event):
        dlg = wx.FileDialog(self, "Save File", "", "",
                            "Rockmag files(*.rmg)|*.rmg",
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dlg.ShowModal() == wx.ID_OK:
            rmgFilePath = dlg.GetPath()
            self.SaveRMGRoutine(rmgFilePath)
            
        return
    
    '''
    '''
    def onImport(self, event):
        dlg = wx.FileDialog(self, "Open", "", "",
                            "Rockmag files(*.rmg)|*.rmg",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            rmgFilePath = dlg.GetPath()
            self.ImportRMGRoutine(rmgFilePath)
            
        return
    
    '''
    '''
    def onDelete(self, event):
        selectedIndex = self.rockmagLCtrl.GetFirstSelected()
        self.rmStepList.Remove(selectedIndex)
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onClear(self, event):
        self.rmStepList = RockmagSteps(self.parent)
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onGARMAdd(self, event):
        StepSize = self.get_Int(self.txtARMSteps)
        StepMax = self.get_Int(self.txtARMBiasMax)
        if not self.parent.modConfig.EnableARM:
            return
        
        if ((StepSize == 0) or (StepSize > StepMax)):
            return
        
        if (self.cmbStepSeqScale.GetValue() == "Log"):
            self.rmStepList.Add(self.cmbStepSeq.GetValue(), 0)
            if (StepSize == 1):
                return
            NumSteps = math.log(StepMax) / math.log(StepSize)
            if ((NumSteps - int(NumSteps)) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
    
            for i in range(1, int(math.log(StepMax) / math.log(StepSize))):
                self.rmStepList.Add(self.cmbStepSeq.GetValue(), self.get_Int(self.txtAFfieldForARM), StepSize ** i)
                        
        else:
            if ((StepMax % StepSize) != 0):
                StepMax = StepMax - StepMax % StepSize
                
            for i in range(0, StepMax+1, StepSize):
                self.rmStepList.Add("ARM", self.get_Int(self.txtAFfieldForARM), i)
        
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onStepAdd(self, event):
        if (self.cmbStepType.GetValue() == "NRM"):          # (August 2007 L Carporzen) NRM possible in RockMag
            self.rmStepList.Add(self.cmbStepType.GetValue(), 0, 0, 0, 
                                0, self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), self.txtRemarks.GetValue())
                                
        elif (self.cmbStepType.GetValue() == "X"):          # (June 2009 L Carporzen) Susceptibility only
            self.rmStepList.Add(self.cmbStepType.GetValue(), 0, 0, 0, 
                                0, False, True, self.txtRemarks.GetValue())
            
        elif (self.cmbStepType.GetValue() == "GRM AF"):     # (Sept 2008 L Carporzen) Uniaxial AF: Gyromagnetic remanent magnetization demag from Stephenson 1993
            self.cmbStepType.SetValue("UAFX2")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
                    
            self.cmbStepType.SetValue("UAFZ1")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
                                
            self.cmbStepType.SetValue("UAFX1")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
                        
            self.cmbStepType.SetValue("UAFX2")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
            
            self.cmbStepType.SetValue("UAFZ1")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
            
            self.cmbStepType.SetValue("GRM AF")
            
        elif (self.cmbStepType.GetValue() == "UAF"):        # (March 2008 L Carporzen) Uniaxial AF: measure the sample after each axis demag
            self.cmbStepType.SetValue("UAFX1")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
                
            self.cmbStepType.SetValue("UAFX2")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
            
            self.cmbStepType.SetValue("UAFZ1")
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
            
            self.cmbStepType.SetValue("UAF")
            
        else:
            self.rmStepList.Add(self.cmbStepType.GetValue(), 
                                self.get_Int(self.txtLevel), 
                                self.get_Int(self.txtBiasField), 
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime), 
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
        
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onGStepsAdd(self, event):
        StepSize = self.get_Int(self.txtStepSize)
        StepMax = self.get_Int(self.txtStepMax)
        
        # (August 2010 - I Hilburn) Added in StepMin to step calculation
        StepMin = self.get_Int(self.txtStepMin)
        
        # (August 2010 - I Hilburn) Added in StepMin to step calculation
        if ((StepSize == 0) or \
           (StepSize > StepMax) or \
           (StepMin > StepMax)):
            return
        
        if (self.cmbStepSeqScale.GetValue() == "Log"):            
            # (August 2010 - I Hilburn) Added in StepMin to step calculation
            self.rmStepList.Add(self.cmbStepSeq.GetValue(),
                                StepMin,
                                self.get_Int(self.txtBiasField),
                                self.get_Int(self.txtSpinSpeed),
                                self.get_Int(self.txtHoldTime),
                                self.chkMeasure.GetValue(), 
                                self.chksusceptibility.GetValue(), 
                                self.txtRemarks.GetValue())
                           
            if (StepSize == 1):
                return
            
            # (August 2010 - I Hilburn) Added in StepMin to step calculation
            NumSteps = math.log(StepMax - StepMin) / math.log(StepSize)
            
            if ((NumSteps - int(NumSteps)) > 0.5):            
                NumSteps = int(NumSteps) + 1                
            else:            
                NumSteps = int(NumSteps)
                            
            for i in range(1, NumSteps+1):            
                # (August 2010 - I Hilburn) Added in StepMin to step calculation
                CurStep = StepMin + int(StepSize ** i)
                
                self.rmStepList.Add(self.cmbStepSeq.GetValue(), 
                                    CurStep,
                                    self.get_Int(self.txtBiasField),
                                    self.get_Int(self.txtSpinSpeed),
                                    self.get_Int(self.txtHoldTime),
                                    self.chkMeasure.GetValue(),
                                    self.chksusceptibility.GetValue(),
                                    self.txtRemarks.GetValue())
                                           
        else:        
            # (August 2010 - I Hilburn) Added in StepMin to step calculation
            if (((StepMax - StepMin) % StepSize) != 0):            
                StepMax = StepMax - (StepMax - StepMin) % StepSize
            
            for i in range(StepMin, StepMax+1, StepSize):                
                # (August 2010 - I Hilburn) Added in StepMin to step calculation
                self.rmStepList.Add(self.cmbStepSeq.GetValue(), 
                                    i,
                                    self.get_Int(self.txtBiasField),
                                    self.get_Int(self.txtSpinSpeed),
                                    self.get_Int(self.txtHoldTime),
                                    self.chkMeasure.GetValue(),
                                    self.chksusceptibility.GetValue(), 
                                    self.txtRemarks.GetValue())
                                       
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onStandardAF(self, event):
        self.rmStepList = RockmagSteps(self.parent)
        self.rmStepList.Add("AF", 0)
        for i in range(1, 7):
            self.rmStepList.Add("AF", 25 * (2 ** i))
            
        self.refreshListDisplay()
        return
    
    '''
    '''
    def onRockMag(self, event):
        stepsizeAF = self.get_Float(self.txtRMAllLogFactor)
        stepmaxAF = self.get_Int(self.txtRMAllAFMax)
        
        if (stepmaxAF > self.parent.modConfig.AfAxialMax):
            stepmaxAF = self.parent.modConfig.AfAxialMax
            
        stepmaxIRM = self.get_Int(self.txtRMAllIRMMax)
        minStepSize = self.get_Int(self.txtRMAllMinStepSize)
        if ((stepsizeAF == 0) or (stepsizeAF == 1) or (stepsizeAF > stepmaxAF) or (stepsizeAF > stepmaxIRM)):
            return
        
        if (self.chkRMAllNRM.GetValue() and self.parent.modConfig.EnableAF):
            self.rmStepList.Add("NRM", MeasureSusceptibility=self.chkTheWorksMeasSusc.GetValue())
            if not self.chkRMAllNRM3AxisAF.GetValue():
                if (stepmaxAF > self.parent.modConfig.AfAxialMax):
                    stepmaxAF = self.parent.modConfig.AfAxialMax
                NumSteps = math.log(stepmaxAF) / math.log(stepsizeAF)
                if (NumSteps - int(NumSteps) > 0.5):
                    NumSteps = int(NumSteps) + 1 
                else: 
                    NumSteps = int(NumSteps)
                lastStep = 0
                for i in range(1, NumSteps+1):
                    CurStep = int(stepsizeAF ** i)
                    if (CurStep > self.parent.modConfig.AfAxialMax):
                        CurStep = self.parent.modConfig.AfAxialMax
                    if (((CurStep == 0) or (CurStep > self.parent.modConfig.AfAxialMin)) and (CurStep - lastStep >= minStepSize)):
                        self.rmStepList.Add("AFz", CurStep)
                        lastStep = CurStep
                                    
            else:
                StepMax = stepmaxAF
                if ((StepMax > self.parent.modConfig.AfAxialMax) or (StepMax > self.parent.modConfig.AfTransMax)):
                    if (self.parent.modConfig.AfTransMax > self.parent.modConfig.AfAxialMax):
                        StepMax = self.parent.modConfig.AfAxialMax 
                    else: 
                        StepMax = self.parent.modConfig.AfTransMax
                
                NumSteps = math.log(StepMax) / math.log(stepsizeAF)
                if ((NumSteps - int(NumSteps)) > 0.5):
                    NumSteps = int(NumSteps) + 1 
                else: 
                    NumSteps = int(NumSteps)
                lastStep = 0
                for i in range(1, NumSteps+1):
                    CurStep = int(stepsizeAF ** i)
                    if ((CurStep > self.parent.modConfig.AfAxialMax) or (CurStep > self.parent.modConfig.AfTransMax)):
                        if (self.parent.modConfig.AfTransMax > self.parent.modConfig.AfAxialMax):
                            CurStep = self.parent.modConfig.AfAxialMax 
                        else: 
                            CurStep = self.parent.modConfig.AfTransMax
                    
                    if (((CurStep == 0) or \
                         ((CurStep > self.parent.modConfig.AfAxialMin) and \
                          (CurStep > self.parent.modConfig.AfTransMin))) and \
                         ((CurStep - lastStep) >= minStepSize)):
                        self.rmStepList.Add("AF", CurStep)
                        lastStep = CurStep
                                                                
        # Rotational remanence magnetization acquisition & AF
        if (self.chkRMAllWithRRM.GetValue() and self.parent.modConfig.EnableAF):
            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
            StepSize = self.get_Int(self.txtRMAllRRMrpsStep)
            StepMax = self.get_Int(self.txtRMAllRRMrpsMax)
            field = self.get_Int(self.txtRMAllRRMAFField)
            if ((StepSize == 0) or (StepSize > StepMax)):
                return
            
            for i in range(0, StepMax+1, StepSize):
                self.rmStepList.Add("RRM", field, 0, i, 5)
            
            if self.chkRMAllRRMdoNegative.GetValue():
                self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
                for i in range(0, -StepMax-1, -StepSize):
                    self.rmStepList.Add("RRM", field, 0, i, 5)
                            
            NumSteps = math.log(stepmaxAF) / math.log(stepsizeAF)
            if ((NumSteps - int(NumSteps)) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
            lastStep = 0
            for i in range(1, NumSteps+1):
                CurStep = int(stepsizeAF ** i)
                if (CurStep > self.parent.modConfig.AfAxialMax):
                    CurStep = self.parent.modConfig.AfAxialMax
                if (((CurStep == 0) or (CurStep > self.parent.modConfig.AfAxialMin)) and ((CurStep - lastStep) >= minStepSize)):
                    self.rmStepList.Add("AFz", CurStep)
                    lastStep = CurStep
                                    
        # ARM acquisition & AF demag
        if (self.chkRMAllARM.GetValue() and self.parent.modConfig.EnableARM and self.parent.modConfig.EnableAF):
            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
            StepSize = self.get_Int(self.txtRMAllARMStepSize)
            StepMax = self.get_Int(self.txtRMAllARMStepMax)
            field = self.get_Int(self.txtRMAllAFFieldForARM)
            
            if (field > 0.75 * self.parent.modConfig.AfAxialMax):
                field = 0.75 * self.parent.modConfig.AfAxialMax
            if (StepSize == 0 ):
                return
            
            if ((StepMax % StepSize) != 0):
                StepMax = StepMax - (StepMax % StepSize)
            for i in range(0, StepMax+1, StepSize):
                self.rmStepList.Add("ARM", field, i)
            
            NumSteps = (math.log(stepmaxAF) / math.log(stepsizeAF))
            if ((NumSteps - int(NumSteps)) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
            lastStep = 0
            for i in range(1, NumSteps+1):
                CurStep = int(stepsizeAF ** i)
                if (CurStep > self.parent.modConfig.AfAxialMax): 
                    CurStep = self.parent.modConfig.AfAxialMax
                if (((CurStep == 0) or (CurStep > self.parent.modConfig.AfAxialMin)) and (CurStep - lastStep >= minStepSize)):
                    self.rmStepList.Add("AFz", CurStep)
                    lastStep = CurStep
                
            #Clean last of ARM field possibly left
            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
               
            # IRM pulse and AF demag
            # Only do this sequence if the IRM's are enables
            if (self.parent.modConfig.EnableAxialIRM or self.parent.modConfig.EnableTransIRM):                
                self.rmStepList.Add("IRMz", 0)
                self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
                self.rmStepList.Add("IRMz", field)
                lastStep = 0
                for i in range(1, NumSteps+1):
                    CurStep = int(stepsizeAF ** i)
                    if (CurStep > self.parent.modConfig.AfAxialMax):
                        CurStep = self.parent.modConfig.AfAxialMax
                    if (((CurStep == 0) or (CurStep > self.parent.modConfig.AfAxialMin)) and (CurStep - lastStep >= minStepSize)):
                        self.rmStepList.Add("AFz", CurStep)
                        lastStep = CurStep
                    
        # IRM stepwise and final cleaning
        if (self.chkRMAllIRM.GetValue() and \
            (self.parent.modConfig.EnableAxialIRM or \
             self.parent.modConfig.EnableTransIRM) and \
            self.parent.modConfig.EnableAF):
            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
            self.rmStepList.Add("IRMz", 0, MeasureSusceptibility=(self.chkTheWorksMeasSusc.GetValue()))
            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
            NumSteps = (math.log(self.get_Int(self.txtRMAllIRMMax)) / math.log(stepsizeAF))
            if (NumSteps - int(NumSteps) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
            lastStep = 0
            for i in range(1, NumSteps+1):
                CurStep = int(stepsizeAF ** i)
                if (CurStep > self.parent.modConfig.PulseAxialMax):                    
                    CurStep = self.parent.modConfig.PulseAxialMax
                        
                if (((CurStep == 0) or (CurStep > self.parent.modConfig.PulseAxialMin)) and (CurStep - lastStep >= minStepSize)):
                    self.rmStepList.Add("IRMz", CurStep)
                    lastStep = CurStep
                
            NumSteps = math.log(stepmaxAF) / math.log(stepsizeAF)
            if (NumSteps - int(NumSteps) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
            lastStep = 0
            for i in range(1, NumSteps+1):
                CurStep = int(stepsizeAF ** i)
                if (CurStep > self.parent.modConfig.AfAxialMax):
                    CurStep = self.parent.modConfig.AfAxialMax
                if (((CurStep == 0) or (CurStep > self.parent.modConfig.AfAxialMin)) and (CurStep - lastStep >= minStepSize)):
                    self.rmStepList.Add("AFz", CurStep)
                    lastStep = CurStep

            self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
        
        # IRM backfield DC demag
        if (self.chkRMAllBackfieldDemag.GetValue() and \
            self.parent.modConfig.EnableIRMBackfield and \
            (self.parent.modConfig.EnableAxialIRM or 
             self.parent.modConfig.EnableTransIRM)):
            NumSteps = (math.log(self.get_Int(self.txtRMAllIRMMax)) / math.log(stepsizeAF))
            if (NumSteps - int(NumSteps) > 0.5):
                NumSteps = int(NumSteps) + 1 
            else: 
                NumSteps = int(NumSteps)
            CurStep = int(stepsizeAF ** NumSteps)
            if (CurStep > self.parent.modConfig.PulseAxialMax):                    
                CurStep = self.parent.modConfig.PulseAxialMax
                
            if ((CurStep == 0) or (CurStep > self.parent.modConfig.PulseAxialMin)):
                self.rmStepList.Add("IRMz", CurStep)
            lastStep = CurStep
            for i in range(1, NumSteps):
                CurStep = -int(stepsizeAF ** i)
                if (-CurStep > self.parent.modConfig.PulseAxialMax): 
                    CurStep = -self.parent.modConfig.PulseAxialMax
                    
                if (((CurStep == 0) or (-CurStep > self.parent.modConfig.PulseAxialMin)) and (abs(CurStep - lastStep) >= minStepSize)):
                    self.rmStepList.Add("IRMz", CurStep)
                    lastStep = CurStep                
            
            # Check to see if the AF module is enabled
            if self.parent.modConfig.EnableAF:
                self.rmStepList.Add("AFmax", self.parent.modConfig.AfAxialMax)
                    
        self.refreshListDisplay()
        return
    
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)        
        
        testUnit = frmTestUnit(path='C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')        
        frame = frmRockmagRoutine(parent=testUnit)
        frame.Show()
        app.MainLoop()
        
    except Exception as e:
        print(e)

        