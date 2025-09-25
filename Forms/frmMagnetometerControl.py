'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import wx

class AutoPage(wx.Panel):
    def __init__(self, parent, mainForm):
        wx.Panel.__init__(self, parent)
        self.mainForm = mainForm
        
        XOri = 10
        XOffset = 20 
        YOri = 10
        YOffset = 60
        btnLength = 120
        btnHeight = 30        
        self.modifyBtn = wx.Button(self, label='Modify', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.modifyBtn.Bind(wx.EVT_BUTTON, self.onModify)

        XOffset += btnLength + 60
        self.startChangerBtn = wx.Button(self, label='Start Changer', pos=(XOri + XOffset, YOri + YOffset), size=(btnLength, btnHeight))
        self.startChangerBtn.Bind(wx.EVT_BUTTON, self.onStartChanger)
        self.startChangerBtn.Enable(False)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onModify(self, event):
        print('TODO: onModify')
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
    def __init__(self, parent, mainForm):
        wx.Panel.__init__(self, parent)
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

        YOffset = comboBoxHeight + 5
        textBoxHeight = 25
        wx.StaticText(self, label='Sample Height (cm):', pos=(XOri, YOri + ytextOffset + YOffset))
        self.sampleHeightTBox = wx.TextCtrl(self, pos=(XOri + XOffset, YOri + YOffset), size=(comboBoxLength, textBoxHeight))

        btnLength = 120
        btnHeight = 30        
        self.measureHolderBtn = wx.Button(self, label='Measure Holder', pos=(XOri, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.measureHolderBtn.Bind(wx.EVT_BUTTON, self.onMeasureHolder)
        self.measureSampleBtn = wx.Button(self, label='Measure Sample', pos=(XOri + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.measureSampleBtn.Bind(wx.EVT_BUTTON, self.onMeasureSample)
        self.measureSampleBtn.Enable(False)
        
        self.vacuumOnChkBox = wx.CheckBox(self, label='Keep The Vacuum On', pos=(XOri, YOri + 3*YOffset + 12))
        self.openSampleBtn = wx.Button(self, label='Open Sample File', pos=(XOri + XOffset, YOri + 3*YOffset + 5), size=(btnLength, btnHeight))
        self.openSampleBtn.Bind(wx.EVT_BUTTON, self.onOpenSampleFile)
        self.openSampleBtn.Enable(False)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onMeasureHolder(self, event):
        print('TODO: onMeasureHolder')
        return
    
    '''
    '''
    def onMeasureSample(self, event):
        print('TODO: onMeasureSample')
        return
    
    '''
    '''
    def onOpenSampleFile(self, event):
        print('TODO: onOpenSampleFile')
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
        self.autoPage = AutoPage(self.nb, mainForm)
        self.manualPage = ManualPage(self.nb, mainForm)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.autoPage, "Automatic Data Collection")
        self.nb.AddPage(self.manualPage, "Manual Data Collection")
         
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
        self.sampleCodeCBox = wx.ComboBox(panel, value='', pos=(XOri + XOffset, YOri + YOffset), size=(comboBoxLength, comboBoxHeight), choices=self.scaleList)
        self.sampleCodeCBox.SetSelection(1)
        
        return             
       
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''                
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
        frame = frmMagnetometerControl(parent=None)
        frame.Show()
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        