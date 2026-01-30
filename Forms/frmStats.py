'''
Created on Oct 17, 2025

@author: hd.nguyen
'''
import wx

class frmStats(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmStats, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmStats, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
                
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        boxLength = 420
        box1Height = 120
        XOri = 10
        YOri = 0        
        wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box1Height))
        self.GUI_SampleInfo(panel, XOri, YOri)

        box2Height = 240
        YOri += box1Height 
        wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box2Height))
        self.GUI_StatsBoxes(panel, XOri, YOri)

        box3Height = 70
        YOri += box2Height 
        wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box3Height))
        self.GUI_SummaryBoxes(panel, XOri, YOri)
        
        panelLength = boxLength + 40
        panelHeight = YOri + box3Height + 50  
        self.SetSize((panelLength, panelHeight))
        self.SetTitle('Sample Statistics')
        self.Centre()
        return
    
    '''
    '''
    def GUI_SampleInfo(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        txtBoxLength = 70
        txtXOffset = 55
        txtBoxHeight = 20
        txtYOffset = 3
        
        # First line
        wx.StaticText(panel, label='Sample', pos=(XOri, YOri + txtYOffset))
        self.lblSampName = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri), size=(txtBoxLength, txtBoxHeight))

        XOffset = txtXOffset + txtBoxLength + 10 
        wx.StaticText(panel, label='Avg. Cycles', pos=(XOri + XOffset , YOri + txtYOffset))
        self.lblAvgCycles = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 10, YOri), size=(txtBoxLength, txtBoxHeight))

        wx.StaticText(panel, label='Demag', pos=(XOri + 2*XOffset + 15, YOri + txtYOffset))
        self.lblDemag = wx.TextCtrl(panel, pos=(XOri + txtXOffset + 2*XOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        
        # Second line
        txtBoxLength = 340
        YOffset = txtBoxHeight + 10 
        wx.StaticText(panel, label='File Path', pos=(XOri, YOri + txtYOffset + YOffset))
        self.lblDataFileName = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        # Third line
        txtBoxLength = 40
        wx.StaticText(panel, label='Directions', pos=(XOri, YOri + txtYOffset + 2*YOffset))
        self.lblDirs = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        btnLength = 60
        btnHeight = 25        
        XOffset += 130 
        self.cmdHide = wx.Button(panel, label='Hide', pos=(XOri + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdHide.Bind(wx.EVT_BUTTON, self.cmdHide_Click)

        XOffset += btnLength + 10 
        self.cmdPrint = wx.Button(panel, label='Print', pos=(XOri + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdPrint.Bind(wx.EVT_BUTTON, self.cmdPrint_Click)
        
        return
    
    '''
    '''
    def GUI_StatsBoxes(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        txtBoxLength = 70
        txtXOffset = 80
        txtBoxHeight = 20
        txtYOffset = 3
        
        # First line
        wx.StaticText(panel, label='Std. Dev. X', pos=(XOri, YOri + txtYOffset))
        self.lblsdX = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri), size=(txtBoxLength, txtBoxHeight))

        XOffset = txtXOffset + txtBoxLength + 80 
        wx.StaticText(panel, label='Signal/Noise', pos=(XOri + XOffset , YOri + txtYOffset))
        self.lblSigNoise = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 10, YOri), size=(txtBoxLength, txtBoxHeight))

        # Second line
        YOffset = txtBoxHeight + 10 
        wx.StaticText(panel, label='Std. Dev. Y', pos=(XOri, YOri + txtYOffset + YOffset))
        self.lblsdY = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        wx.StaticText(panel, label='Signal/Holder', pos=(XOri + XOffset , YOri + txtYOffset + YOffset))
        self.lblSigHold = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 10, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        # Third line
        YOffset = txtBoxHeight + 10 
        wx.StaticText(panel, label='Std. Dev. Z', pos=(XOri, YOri + txtYOffset + 2*YOffset))
        self.lblsdZ = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        wx.StaticText(panel, label='Signal/Induced', pos=(XOri + XOffset , YOri + txtYOffset + 2*YOffset))
        self.lblSigInd = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 10, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        # Fourth line
        textXOffset = 10
        textYOffset = 17
        XOffset = txtBoxLength + 10
        wx.StaticText(panel, label='Holder X', pos=(XOri + textXOffset, YOri + 3*YOffset))
        self.lblHolderX = wx.TextCtrl(panel, pos=(XOri, YOri + textYOffset + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Holder Y', pos=(XOri + textXOffset + XOffset, YOri + 3*YOffset))
        self.lblHolderY = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + textYOffset + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Holder Z', pos=(XOri + textXOffset + 2*XOffset, YOri + 3*YOffset))
        self.lblHolderZ = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + textYOffset + 3*YOffset), size=(txtBoxLength, txtBoxHeight))

        txtBoxLength = 120
        boxOffset = 30
        wx.StaticText(panel, label='Moment/Vol Ratio', pos=(XOri + textXOffset + 3*XOffset + boxOffset, YOri + 3*YOffset))
        self.lblMomVol = wx.TextCtrl(panel, pos=(XOri + 3*XOffset + boxOffset, YOri + textYOffset + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        
        # Fifth line
        txtBoxLength = 70
        textXOffset = 160
        YOri += textYOffset + 3*YOffset + txtBoxHeight + 10
        wx.StaticText(panel, label='Average Dec:', pos=(XOri, YOri + 17))
        wx.StaticText(panel, label='Core', pos=(XOri + textXOffset + 20, YOri))
        self.lblCDec = wx.TextCtrl(panel, pos=(XOri + textXOffset, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Geographic', pos=(XOri + textXOffset + XOffset + 5, YOri))
        self.lblGDec = wx.TextCtrl(panel, pos=(XOri + textXOffset + XOffset, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Bedding', pos=(XOri + textXOffset + 2*XOffset + 15, YOri))
        self.lblBDec = wx.TextCtrl(panel, pos=(XOri + textXOffset + 2*XOffset, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        
        # Sixth line
        wx.StaticText(panel, label='Average Inc:', pos=(XOri, YOri + 17 + YOffset))
        self.lblCInc = wx.TextCtrl(panel, pos=(XOri + textXOffset, YOri + textYOffset + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblGInc = wx.TextCtrl(panel, pos=(XOri + textXOffset + XOffset, YOri + textYOffset + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblBInc = wx.TextCtrl(panel, pos=(XOri + textXOffset + 2*XOffset, YOri + textYOffset + YOffset), size=(txtBoxLength, txtBoxHeight))
        
        return
    
    '''
    '''
    def GUI_SummaryBoxes(self, panel, XOri, YOri):
        XOri += 10
        YOri += 20
        txtBoxLength = 120
        txtBoxHeight = 20
        textYOffset = 17
        XOffset = txtBoxLength + 15 
        
        # First line
        wx.StaticText(panel, label='Circular Std. Dev.', pos=(XOri + 15, YOri))
        self.lblErrAngle = wx.TextCtrl(panel, pos=(XOri, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Horiz. Err. Angle', pos=(XOri + XOffset + 15, YOri))
        self.lblHErrAngle = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Up/Down Ratio', pos=(XOri + 2*XOffset + 20, YOri))
        self.lblMUDRatio = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + textYOffset), size=(txtBoxLength, txtBoxHeight))
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def cmdHide_Click(self, event):
        print('TODO: frmStats.cmdHide_Click')
        return

    '''
    '''
    def cmdPrint_Click(self, event):
        print('TODO: frmStats.cmdPrint_Click')
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmStats(parent=None)
        frame.Show(True)
        app.MainLoop()    
        
    except Exception as e:
        print(e)

        
        
        