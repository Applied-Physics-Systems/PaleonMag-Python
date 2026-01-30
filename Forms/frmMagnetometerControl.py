'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import wx
import numpy as np

from Process.DataExchange import DataExchange

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
        self.cmdChangerOK = wx.Button(self, label='Start Changer', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.cmdChangerOK.Bind(wx.EVT_BUTTON, self.onStartChanger)
        self.cmdChangerOK.Enable(False)

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
        self.cmdManHolder.Bind(wx.EVT_BUTTON, self.cmdManHolder_Click)
        self.cmdManRun = wx.Button(self, label='Measure Sample', pos=(XOri + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdManRun.Bind(wx.EVT_BUTTON, self.cmdManRun_Click)
        self.cmdManRun.Enable(False)
        
        self.vacuumOnChkBox = wx.CheckBox(self, label='Keep The Vacuum On', pos=(XOri, YOri + 3*YOffset + 12))
        self.cmdOpenSampleFile = wx.Button(self, label='Open Sample File', pos=(XOri + XOffset, YOri + 3*YOffset + 5), size=(btnLength, btnHeight))
        self.cmdOpenSampleFile.Bind(wx.EVT_BUTTON, self.onOpenSampleFile)
        self.cmdOpenSampleFile.Enable(False)

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    def getFloat(self, textBox):
        try:
            floatValue = float(textBox.GetValue())
        except:
            floatValue = 0.0
            
        return floatValue

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
    
    '''
      Summary: Function checks the sign and value of the sample height, returning a false
               if the height does not check out in some way.
     
               If the height has the wrong sign, the function will change the sign of the height
               in txtSampleHeight, call cmdManRun_click again and return a false to the present
               instance of the event handler to close that first instance.
     
               If the height is too great for the sample to fit in the AF region or Susc. coil
               region, a message box will pop-up and say the max allowed height
    '''
    def SampleHeightCheck(self, IsHolder=False):
        status = False
     
        # Store the sample height to local variable in CM's
        SampleHeight = self.getFloat(self.txtSampleHeight)
        
        # First check to see if the the SampleMotorUnits have the correct sign
        if (np.sign(SampleHeight) == np.sign(self.mainForm.modConfig.MeasPos)):        
            '''
                Sample height has the wrong sign, it should have the opposite sign
                as the Measurement Position. (i.e. positive measurement position = negative updownmotor1cm
                conversion factor, which means to get a positive sample motor height, you need a negative
                sample height in cm's first).
                Change the sign of the sample height
            '''
            self.txtSampleHeight.SetValue = str(-1 * SampleHeight)
            
            # Return a false
            status = False
            
            if not IsHolder:                
                # Call the cmdManRun_Click event handler again
                self.cmdManRun_Click()
                
            else:            
                # Call the cmdManHolder_Click event handler again
                self.cmdManHolder_Click()
                            
            # Exit this function
            return status
                    
        '''
            Now, the SampleHeight has the correct sign, can check to make sure
            that the SampleMotorUnis is such that the sample will fit into the AF or susc. coil region
            
            Convert that height / 2 to Sample Motor Units (because the changer system centers the sample
            in the AF or susc. coil; therefore, only need to constrain 1/2 of the sample height.
        '''
        SampleMotorUnits = SampleHeight * self.mainForm.modConfig.UpDownMotor1cm / 2
        
        # Get the Sample Object for this specimen
        specName = self.cmbManSample.GetValue()
        specParent = self.mainForm.SampleIndexRegistry.SampleFileByIndex(self.cmbManSample.GetSelection())
        specimen = self.mainForm.SampleIndexRegistry.GetItem(specParent).sampleSet.GetItem(specName)
        
        # Check to see if the specimen is nothing
        if (specimen == None):
        
            status = False
            
            # Raise a message box to let the user know that they need to select a real sample
            warningMessage = 'Could not find sample: ' + specName + ' in SAM file: \n' 
            warningMessage += specParent + '\n\n'
            warningMessage += 'Please check SAM file or select a different sample.'
            wx.MessageBox(warningMessage, style=wx.OK|wx.CENTER, caption='Whoops!')                   
            return status
                    
        YesSusc = False
        
        # Check to see if susceptibility measurements are being performed on the sample
        #With specimen.Parent            
        for i in range(0, specimen.parent.measurementSteps.Count):        
            # Set the current step index = i
            specimen.parent.measurementSteps.CurrentStepIndex = i
            
            if specimen.parent.measurementSteps.CurrentStep.MeasureSusceptibility:            
                # Toggle the measuring susceptibility flag to true
                YesSusc = True
                
                # Exit the for loop
                break
                                    
        # Now also check to see if rockmag is being done on this sample
        YesRockmag = specimen.parent.RockmagMode
        
        '''            
            If YesSusc = True, and the measure susceptiblity module is enabled
            then need to make sure the sample will be able to be placed within
            the susceptibility coils
        '''
        if (YesSusc and self.mainForm.modConfig.EnableSusceptibility):        
            # Will the sample be able to be fit into the susceptibility coils?
            # If No, then return false and exit the function
            if (abs(SampleMotorUnits) > abs(self.mainForm.modConfig.SCoilPos)):
                '''            
                    Sample height is too large
                    Pop-up a message box
                    Note: Max allowed height = distance in CM to the susc. coil - 0.5 cm for slop
                '''
                warningMessage = "Sample Height is too large to raise the sample into the susceptibility coil.\n"
                warningMessage += "Current Sample Height = " + str(SampleHeight) + " cm\n"
                warningMessage += "Max. Allowed Height = " + "{:.2f}".format(-2 * (self.mainForm.modConfig.SCoilPos / self.mainForm.modConfig.UpDownMotor1cm) - 0.5) + " cm"
                wx.MessageBox(warningMessage, style=wx.OK|wx.CENTER, caption="Bad Height!")
                                              
                # Return false
                return False
                        
        # Now check to see if the sample height is too large to do rockmag
        if (YesRockmag and (abs(SampleMotorUnits) > abs(self.mainForm.modConfig.AFPos))):
            '''
                Wha-oh! Sample height is too large to do rockmag = AF / ARM / IRM
                Pop-up a message box
                Note: Max allowed height = distance in cm to the AF coil center - 0.5 cm for slop
            '''
            warningMessage = "Sample Height is too large to raise the sample into the AF / IRM / ARM coils.\n" 
            warningMessage += "Current Sample Height = " + str(SampleHeight) + " cm\n" 
            warningMessage += "Max. Allowed Height = " + "{:.2f}".format(-2 * (self.mainForm.modConfig.AFPos / self.mainForm.modConfig.UpDownMotor1cm) - 0.5) + " cm"
            wx.MessageBox(warningMessage, style=wx.OK|wx.CENTER, caption="Bad Height!")
    
            # Return False
            return False
            
        # Return True
        status = True
        
        return status
    
    '''
        Disable all commands that use the magnetometer
    '''
    def DisableMagnetCmds(self):
        self.parent.autoPage.cmdChangerEdit.Enable(False)
        self.parent.cmbSusceptibilityScaleFactor.Enable(False)
        self.parent.autoPage.cmdChangerOK.Enable(False)
        self.cmdManHolder.Enable(False)
        self.cmdManRun.Enable(False)
        return

    '''
    '''
    def getManualHolderParams(self):
        manualHolderParams = {}
        manualHolderParams['frmAF_2G_txtWaitingTime'] = self.mainForm.frmAF_2G.txtWaitingTime.GetValue()
        manualHolderParams['frmMeasure_lblDemag'] = self.mainForm.frmMeasure.lblDemag.GetValue()
        manualHolderParams['frmADWIN_AF_Verbose'] = self.mainForm.frmADWIN_AF.debugChkBox.GetValue()
        
        return manualHolderParams

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
    def cmdManHolder_Click(self, event=None):
        # Check to see if the Sample Height is OK
        if not self.SampleHeightCheck(True):
            return
        
        if not self.mainForm.FLAG_MagnetUse:
            
            self.mainForm.FLAG_MagnetUse = True # Notify that we're using magnetometer
            
            self.DisableMagnetCmds()            # Disable buttons that use magnetometer
            try:
                self.mainForm.SampleHolder.SampleHeight = int(float(self.txtSampleHeight.GetValue()) * self.mainForm.modConfig.UpDownMotor1cm)
            except:
                self.mainForm.SampleHolder.SampleHeight = 0

            manualHolderParams = self.getManualHolderParams()
            sampleHolderParams = DataExchange.parseSampleHolder(self.mainForm.SampleHolder)
            sampleIndexRegistryParams = DataExchange.parseSampleIndexRegistry(self.mainForm.SampleIndexRegistry)
            self.mainForm.pushTaskToQueue([self.mainForm.devControl.MEASUREMENT_MANUAL_HOLDER, [manualHolderParams, 
                                                                                                sampleHolderParams, 
                                                                                                sampleIndexRegistryParams]])
            
        return
    
    '''
    '''
    def cmdManRun_Click(self, event=None):
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
        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)

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
        self.cmbSusceptibilityScaleFactor.SetValue(str(self.parent.modConfig.SusceptibilityScaleFactor))
        self.cmbSusceptibilityScaleFactor.Bind(wx.EVT_COMBOBOX, self.onChangeScaleFactor)
        
        return             

    '''
        Serice request from DeviceControl thread
    '''
    def updateGUI(self, messageList):
        if ('Show frmMeasure' in messageList[0]):
            if (len(messageList) >= 2):
                functionID = messageList[1]
                self.parent.frmMeasure.initForm(functionID)
                self.parent.frmMeasure.Show()
                if not 'frmMeasure' in self.parent.panelList.keys():
                    self.parent.panelList['frmMeasure'] = self.parent.frmMeasure
                    
        elif ('cmdManHolder_End' in messageList[0]):
            self.mainForm.FLAG_MagnetUse = False                      # Notify that we stopped        
            self.EnableMagnetCmds()
                            
        return
    
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        return

    

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
       
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''     
    '''
    '''
    def onChangeScaleFactor(self, event):
        try:
            self.parent.modConfig.SusceptibilityScaleFactor = float(self.cmbSusceptibilityScaleFactor.GetValue()) 
        except:
            self.parent.modConfig.SusceptibilityScaleFactor = 0.1
        return
      
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
                if 'frmMagnetometerControl' in self.parent.panelList.keys():          
                    del self.parent.panelList['frmMagnetometerControl']
                
        self.Destroy()
        
    '''
    '''
    def onShow(self, event):
        if (self.parent != None):
            self.parent.modConfig.processData.NOCOMM_MODE = False
            self.parent.modConfig.processData.motorsEnable = True
            self.parent.modConfig.processData.susceptibilityEnable = True
            self.parent.modConfig.processData.adwinEnable = True
            self.parent.modConfig.processData.irmArmEnable = True
            self.parent.modConfig.processData.squidEnable = True
        return
        
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
        