'''
Created on Oct 17, 2025

@author: hd.nguyen
'''
import wx

from Modules.modProg import modProg

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
        
        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
             
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
    
    '''
    '''
    def onShow(self, event):
        if event.IsShown():
            if (self.parent != None):
                parentPos = self.parent.GetPosition()
                parentSize = self.parent.GetSize()
                childSize = self.GetSize()
                xOffset = 40
                xPos = int(parentPos[0] + xOffset)
                yPos = int(parentPos[1] + (parentSize[1]-childSize[1])*(2/3))
                frmPos = (xPos, yPos)
                self.SetPosition(frmPos)
                
            else:
                self.Centre()
                
            self.parent.panelList['frmStats'] = self
        
        else:
            del self.parent.panelList['frmStats']
            
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Pubic API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        This procedure is called if we are doing both up and down
        measurements.  It displays error fields specific for this
        kind of measurement
    '''
    def ShowErrors(self, dataDict):
        errangle = dataDict['errangle'] 
        herrangle = dataDict['herrangle'] 
        momentupdown = dataDict['momentupdown']
        
        #framErrors.Visible = True
        self.lblErrAngle.SetValue(modProg.FormatNumber(errangle))
        self.lblHErrAngle.SetValue(modProg.FormatNumber(herrangle))
        self.lblMUDRatio.SetValue(modProg.FormatNumber(momentupdown))
        return

    '''
        This procedure displays statistical information for the
        entire set of data gathered from the magnetometer.  (after
        all 'n' averaging cycles have been completed)
    '''
    def ShowAvgStats(self, dataDict):
        holderX = dataDict['holderX'] 
        holderY = dataDict['holderY']
        holderZ = dataDict['holderZ']
        sdx = dataDict['sdx'] 
        sdy = dataDict['sdy'] 
        sdz = dataDict['sdz']
        crdec = dataDict['crdec']
        crinc = dataDict['crinc'] 
        gdec = dataDict['gdec'] 
        ginc = dataDict['ginc']
        bdec = dataDict['bdec'] 
        binc = dataDict['binc'] 
        momentvol = dataDict['momentvol']
        SigNoise = dataDict['SigNoise'] 
        SigHolder = dataDict['SigHolder'] 
        SigInduced = dataDict['SigInduced']
                
        self.lblHolderX.SetValue('{:.4f}'.format(holderX))
        self.lblHolderY.SetValue('{:.4f}'.format(holderY))
        self.lblHolderZ.SetValue('{:.4f}'.format(holderZ))      # was define by Holder.Average.X before Karin Louzada report the display bug
        self.lblsdX.SetValue(modProg.FormatNumber(sdx))
        self.lblsdY.SetValue(modProg.FormatNumber(sdy))
        self.lblsdZ.SetValue(modProg.FormatNumber(sdz))
        self.lblMomVol.SetValue('{:.4f}'.format(momentvol))
        self.lblCDec.SetValue(modProg.FormatNumber(crdec))
        self.lblCInc.SetValue(modProg.FormatNumber(crinc))
        self.lblGDec.SetValue(modProg.FormatNumber(gdec))
        self.lblGInc.SetValue(modProg.FormatNumber(ginc))
        self.lblBDec.SetValue(modProg.FormatNumber(bdec))
        self.lblBInc.SetValue(modProg.FormatNumber(binc))
        self.lblSigNoise.SetValue(modProg.FormatNumber(SigNoise))
        self.lblSigHold.SetValue(modProg.FormatNumber(SigHolder))
        self.lblSigInd.SetValue(modProg.FormatNumber(SigInduced))
        
        return
    
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageDict):
        if (messageDict['Function'] == 'ShowErrors'):
            self.ShowErrors(messageDict)
            
        elif (messageDict['Function'] == 'ShowAvgStats'):
            self.ShowAvgStats(messageDict)
                    
        return
    
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
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

        
        
        