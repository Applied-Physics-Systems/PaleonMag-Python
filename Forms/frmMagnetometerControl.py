'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import wx

class AutoPage(wx.Panel):
    def __init__(self, noteBook, parent, mainForm):
        wx.Panel.__init__(self, noteBook)
        self.parent = parent
        self.mainForm = mainForm
        
        XOri = 10
        XOffset = 20 
        YOri = 10
        YOffset = 60
        btnLength = 120
        btnHeight = 30        
        self.cmdChangerEdit = wx.Button(self, label='Modify', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.cmdChangerEdit.Bind(wx.EVT_BUTTON, self.onCmdChangerEdit)

        XOffset += btnLength + 60
        self.startChangerBtn = wx.Button(self, label='Start Changer', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.startChangerBtn.Bind(wx.EVT_BUTTON, self.onStartChanger)
        self.startChangerBtn.Enable(False)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onCmdChangerEdit(self, event):
        print('TODO: onCmdChangerEdit')
        return
    
    '''
    '''
    def onStartChanger(self, event):
        print('TODO: onStartChanger')
        return

'''
    -------------------------------------------------------------------------------------------------
'''
class ManualPage(wx.Panel):
    def __init__(self, noteBook, parent, mainForm):
        wx.Panel.__init__(self, noteBook)
        self.parent = parent
        self.mainForm = mainForm
        
        XOri = 60
        ytextOffset = 5
        XOffset = 150 
        YOri = 10
        
        comboBoxLength = 100
        comboBoxHeight = 30
        wx.StaticText(self, label='Choose Sample', pos=(XOri, YOri + ytextOffset))
        self.sampleList = []        
        self.cmbManSample = wx.ComboBox(self, value='', pos=(XOri + XOffset, YOri), size=(comboBoxLength, comboBoxHeight), choices=self.sampleList)
        self.cmbManSample.Bind(wx.EVT_TEXT, self.onSampleChanged)

        YOffset = comboBoxHeight + 5
        textBoxHeight = 25
        wx.StaticText(self, label='Sample Height (cm):', pos=(XOri, YOri + ytextOffset + YOffset))
        self.txtSampleHeight = wx.TextCtrl(self, pos=(XOri + XOffset, YOri + YOffset), size=(comboBoxLength, textBoxHeight))

        btnLength = 120
        btnHeight = 30        
        self.cmdManHolder = wx.Button(self, label='Measure Holder', pos=(XOri, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdManHolder.Bind(wx.EVT_BUTTON, self.onCmdManHolder)
        self.cmdManRun = wx.Button(self, label='Measure Sample', pos=(XOri + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdManRun.Bind(wx.EVT_BUTTON, self.onCmdManRun)
        self.cmdManRun.Enable(False)
        
        self.vacuumOnChkBox = wx.CheckBox(self, label='Keep The Vacuum On', pos=(XOri, YOri + 3*YOffset + 12))
        self.cmdOpenSampleFile = wx.Button(self, label='Open Sample File', pos=(XOri + XOffset, YOri + 3*YOffset + 5), size=(btnLength, btnHeight))
        self.cmdOpenSampleFile.Bind(wx.EVT_BUTTON, self.onOpenSampleFile)
        self.cmdOpenSampleFile.Enable(False)

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        This procedure enables the commands that require use of the
        magnetometer once the magnetometer is initialized.  We know when
        it is initialized when the flag FLAG_MagnetInit is true.
    '''
    def EnableMagnetCmds(self):
        if (self.mainForm.FLAG_MagnetInit and (not self.mainForm.FLAG_MagnetUse)):
            self.parent.autoPage.cmdChangerEdit.Enable(True)
            self.cmdManHolder.Enable(True)
            self.parent.cmbSusceptibilityScaleFactor.Enabled = True
            self.EnableMagnetRun()
        
        return
    
    '''
        When the sample selected is changed, and a valid sample is
        selected, then enable the cmdManRun button, so we can run the
        sample.
    '''
    def EnableMagnetRun(self):
        if (self.mainForm.FLAG_MagnetInit and \
            (not self.mainForm.FLAG_MagnetUse) and \
            (not self.cmdManRun.IsEnabled())):
            # The button is not enabled and we are allowed to enable it
            if (self.cmbManSample.GetSelection != -1):
                # We have selected a sample in the combo box
                self.cmdManRun.Enable(True)        # Enable the Run button
                
        return

    '''
        (June 2008 L Carporzen) Visualisation of the data instead of looking at the text file
    '''
    def DataAnalysis_SampleFile(self, filename):
        sampleName = self.cmbManSample.GetValue()
        if (sampleName == ''):
            return
        
        self.mainForm.registryControl.frmPlots.RefreshSamples()
        self.mainForm.registryControl.frmPlots.cmbSamples.SetValue(sampleName)
        self.mainForm.registryControl.frmPlots.ZOrder()
        self.mainForm.registryControl.frmPlots.Show()
        self.mainForm.registryControl.frmPlots.SetFocus()
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onSampleChanged(self, event):
        sampleName = self.cmbManSample.GetValue().strip()
        if (sampleName == ''):
            return
        
        self.EnableMagnetCmds()
        specName = sampleName
        specParent = self.mainForm.SampleIndexRegistry.SampleFileByIndex(self.cmbManSample.GetSelection())
        
        if self.mainForm.SampleIndexRegistry.IsValidSample(specParent, specName):            
            self.cmdOpenSampleFile.Enable(True)            
            specimen = self.mainForm.SampleIndexRegistry.GetItem(specParent).sampleSet.GetItem(specName)            
            if (specimen.SampleHeight > 0):       
                sampleHeight = specimen.SampleHeight / self.mainForm.modConfig.UpDownMotor1cm 
            else:                
                sampleHeight = self.mainForm.modConfig.SampleHeight / self.mainForm.modConfig.UpDownMotor1cm
            self.txtSampleHeight.SetValue("{:.2f}".format(sampleHeight))
            
        else:            
            self.cmdOpenSampleFile.Enable(False)
                
        return
    
    '''
    '''
    def onCmdManHolder(self, event):
        print('TODO: onCmdManHolder')
        return
    
    '''
    '''
    def onCmdManRun(self, event):
        print('TODO: onCmdManRun')
        return
    
    '''
    '''
    def onOpenSampleFile(self, event):
        sampleName = self.cmbManSample.GetValue() 
        if (sampleName == ''):
            return
        
        specName = sampleName
        specParent = self.mainForm.SampleIndexRegistry.SampleFileByIndex(self.cmbManSample.GetSelection())
        
        if self.mainForm.SampleIndexRegistry.IsValidSample(specParent, specName):            
            specimen = self.mainForm.SampleIndexRegistry.GetItem(specParent).sampleSet.GetItem(specName)
            filename = specimen.SpecFilePath(self.mainForm.SampleIndexRegistry.GetItem(specParent))
        
        self.DataAnalysis_SampleFile(filename)
        return

'''
    -------------------------------------------------------------------------------------------------
'''
class frmMagnetometerControl(wx.Frame):
    '''
    classdocs
    '''
    parent = None

    def __init__(self, parent):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmMagnetometerControl, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmMagnetometerControl, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI(parent)
        
    '''
    '''
    def InitUI(self, mainForm):
        panel = wx.Panel(self)
        noteBookLength = 100
        noteBookHeight = 190
        self.nb = wx.Notebook(panel, size=(noteBookLength, noteBookHeight))

        # create the page windows as children of the notebook
        self.autoPage = AutoPage(self.nb, self, mainForm)
        self.manualPage = ManualPage(self.nb, self, mainForm)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.autoPage, "Automatic Data Collection")
        self.nb.AddPage(self.manualPage, "Manual Data Collection")
         
        # Bind the event handler
        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
                 
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.ALL, border=5)
        panel.SetSizer(sizer)

        XOri = 10
        YOri = noteBookHeight + 20
        self.GUI_GlobalOptions(panel, XOri, YOri)

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.SetSize((400, 280))                                        
        self.SetTitle('Magnetometer Control')
        if (self.parent != None):
            parentPos = self.parent.GetPosition()
            parentSize = self.parent.GetSize()
            childSize = self.GetSize()
            xOffset = 10
            xPos = parentPos[0] + xOffset
            yPos = parentPos[1] + (parentSize[1]-childSize[1])/2
            frmPos = (xPos, yPos)
            self.SetPosition(frmPos)
            
        else:
            self.Centre() 
            
        return
    
    '''
    '''
    def GUI_GlobalOptions(self, panel, XOri, YOri):
        self.showMotionChkBox = wx.CheckBox(panel, label='Slow Motions', pos=(XOri, YOri))
        
        XOffset = 205
        wx.StaticText(panel, label='Susceptibility Scale', pos=(XOri + XOffset, YOri))
        
        XOffset += 110
        YOffset = -3
        comboBoxLength = 50
        comboBoxHeight = 22
        self.scaleList = ['1.0', '0.1']
        self.cmbSusceptibilityScaleFactor = wx.ComboBox(panel, value='', pos=(XOri + XOffset, YOri + YOffset), size=(comboBoxLength, comboBoxHeight), choices=self.scaleList)
        self.cmbSusceptibilityScaleFactor.SetSelection(1)
        
        return             

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
       
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''       
    '''
    '''
    def onPageChanged(self, event):
        self.RefreshManSampleList()
        return
    
    '''
        Close Tip Dialog box
    '''
    def onClose(self, event):
        if (self.parent != None):
            if self.parent.panelList:
                if 'MagnetometerControl' in self.parent.panelList.keys():          
                    del self.parent.panelList['MagnetometerControl']
                
        self.Destroy()
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Adds fields to the combobox
        cmbManSamp, so the user can manually select samples to view
        or measure.
    '''
    def RefreshManSampleList(self):
        self.manualPage.cmbManSample.Clear()
    
        if (self.parent.SampleIndexRegistry.Count == 0):
            return
        
        for i in range(0, self.parent.SampleIndexRegistry.Count):
            if (self.parent.SampleIndexRegistry.Item[i].sampleSet.Count > 0):
                for j in range(0, self.parent.SampleIndexRegistry.Item[i].sampleSet.Count):
                    self.manualPage.cmbManSample.Append(self.parent.SampleIndexRegistry.Item[i].sampleSet.Item[j].Samplename)
                
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        magControl = frmMagnetometerControl(parent=None)
        magControl.Show()        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        