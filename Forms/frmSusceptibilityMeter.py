'''
Created on Nov 5, 2025

@author: hd.nguyen
'''
import wx

class frmSusceptibilityMeter(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent = None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmSusceptibilityMeter, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmSusceptibilityMeter, self).__init__(parent, wx.NewIdRef())
        self.parent = parent
        
        self.InitUI()        

        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timerMessage = '' 
        self.startTime = 0       
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        XOri = 10
        YOri = 20
        txtBoxLength = 70
        txtXOffset = 50
        txtBoxHeight = 20
        txtYOffset = 3

        # First line
        wx.StaticText(panel, label='Output', pos=(XOri, YOri + txtYOffset))
        self.OutputText = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri), size=(txtBoxLength, txtBoxHeight))

        XOffset = txtXOffset + txtBoxLength + 30 
        txtBoxLength = 160
        wx.StaticText(panel, label='Input', pos=(XOri + XOffset , YOri + txtYOffset))
        self.InputText = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset, YOri), size=(txtBoxLength, txtBoxHeight))
        
        # Second line
        YOffset = txtBoxHeight + 20
        txtBoxLength = 310
        wx.StaticText(panel, label='Status', pos=(XOri, YOri + txtYOffset + YOffset))
        self.StatusText = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        
        # Third line
        btnLength = 110
        btnHeight = 30        
        self.cmdZero = wx.Button(panel, label='Zero', pos=(XOri + txtXOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdZero.Bind(wx.EVT_BUTTON, self.cmdZero_Click)
        
        XOffset = txtXOffset + btnLength
        btnLength = 150
        self.cmdLagTime = wx.Button(panel, label='Calibrate Lag Time', pos=(XOri + txtXOffset + XOffset, YOri + 2*YOffset), size=(btnLength, btnHeight))
        self.cmdLagTime.Bind(wx.EVT_BUTTON, self.cmdLagTime_Click)
        
        # Fourth line
        btnLength = 110
        self.cmdMeasure = wx.Button(panel, label='Measure', pos=(XOri + txtXOffset, YOri + 3*YOffset), size=(btnLength, btnHeight))
        self.cmdMeasure.Bind(wx.EVT_BUTTON, self.cmdZero_Click)
        
        # Fifth line
        self.ConnectButton = wx.Button(panel, label='Connect', pos=(XOri, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.ConnectButton.Bind(wx.EVT_BUTTON, self.ConnectButton_Click)

        XOffset += 90
        self.cmdClose = wx.Button(panel, label='Close', pos=(XOri + XOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.cmdClose.Bind(wx.EVT_BUTTON, self.cmdClose_Click)
        
        YOri += 6*YOffset
        self.SetSize((400,  YOri))
        self.SetTitle('Susceptibility Meter')
        self.Centre()
        self.Show(True)

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageList):
        for eachEntry in messageList:
            if ('Input Text = ' in eachEntry):
                self.InputText.SetValue(eachEntry.replace('Input Text = ', ''))
    
            elif ('Output Text = ' in eachEntry):
                self.OutputText.SetValue(eachEntry.replace('Output Text = ', ''))
                
            elif ('Status Text = ' in eachEntry):
                self.StatusText.SetValue(eachEntry.replace('Status Text = ', ''))
                
            elif ('Start Timer = ' in eachEntry):
                self.timerMessage = eachEntry.replace('Start Timer = ', '')
                self.startTime = 0
                self.timer.Start(100)      # Checking every 100ms

            elif ('Stop Timer' in eachEntry):
                self.timer.Stop()      
            
        return
    
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        return    
        
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def cmdZero_Click(self, event):
        print('TODO: frmSusceptibilityMeter.cmdZero_Click')
        return

    '''
    '''
    def cmdLagTime_Click(self, event):
        print('TODO: frmSusceptibilityMeter.cmdLagTime_Click')
        return

    '''
    '''
    def cmdMeasure_Click(self, event):
        print('TODO: frmSusceptibilityMeter.cmdMeasure_Click')
        return
    
    '''
    '''
    def ConnectButton_Click(self, event):
        print('TODO: frmSusceptibilityMeter.ConnectButton_Click')
        return

    '''
    '''
    def cmdClose_Click(self, event):
        print('TODO: frmSusceptibilityMeter.cmdClose_Click')
        return
        
    '''
    '''
    def OnTimer(self, event):
        # Calculate elapsed time in seconds
        self.startTime += 1
        self.StatusText.SetValue(self.timerMessage + ": {:.1f}".format(self.startTime/10) + ' seconds')
        return
            
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmSusceptibilityMeter(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                
        