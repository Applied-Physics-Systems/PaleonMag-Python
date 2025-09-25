'''
Created on Nov 19, 2024

@author: hd.nguyen
'''
import wx

class frmVacuum(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmVacuum, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmVacuum, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        btnLength = 105
        smallTxtBoxLength = 60
        longTxtBoxLength = 180
        btnHeight = 30
        txtBoxHeight = 25
        btnXOri = 20
        btnYOri = 20
        txtBoxOri = btnYOri + 2
        btnXOffset = 120
        btnYOffset = 40
        
        txtOffset = 5
        txtBoxXOffset = btnXOffset - smallTxtBoxLength - 15
        
        # First Region
        # First Row
        wx.StaticText(panel, label='Output', pos=(btnXOri, txtBoxOri + txtOffset))
        self.outputTBox = wx.TextCtrl(panel, pos=(btnXOri+txtBoxXOffset, txtBoxOri), size=(smallTxtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Input', pos=(btnXOri + btnXOffset, txtBoxOri + txtOffset))
        self.inputTBox = wx.TextCtrl(panel, pos=(btnXOri + txtBoxXOffset + btnXOffset, txtBoxOri), size=(longTxtBoxLength, txtBoxHeight))        
        
        # Second Row
        radioBoxLabels = ['On', 'Off']
        wx.StaticText(panel, label='Vacuum Connect', pos=(btnXOri, txtBoxOri + 3*txtOffset + btnYOffset))
        self.connectRBox = wx.RadioBox(panel, label = '', pos = (btnXOri + btnXOffset, btnYOri + btnYOffset), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        self.connectRBox.SetStringSelection('Off')
        self.connectRBox.Bind(wx.EVT_RADIOBOX,self.onConnectRadioBox) 
        
        # Third Row
        wx.StaticText(panel, label='Vacuum Motor', pos=(btnXOri, txtBoxOri + 4*txtOffset + 2*btnYOffset))
        self.motorRBox = wx.RadioBox(panel, label = '', pos = (btnXOri + btnXOffset, btnYOri + txtOffset + 2*btnYOffset), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        self.motorRBox.SetStringSelection('Off')
        self.motorRBox.Bind(wx.EVT_RADIOBOX,self.onMotorRadioBox)
        
        # Fourth Row
        self.connectBtn = wx.Button(panel, label='Connect', pos=(btnXOri, btnYOri + 4*txtOffset + 3*btnYOffset), size=(btnLength, btnHeight))        
        self.connectBtn.Bind(wx.EVT_BUTTON, self.onConnect)
        resetBtn = wx.Button(panel, label='Reset', pos=(btnXOri + txtBoxXOffset + btnXOffset, btnYOri + 4*txtOffset + 3*btnYOffset), size=(btnLength, btnHeight))
        resetBtn.Bind(wx.EVT_BUTTON, self.onReset)

        # Second Region        
        txtBoxXOffset = 245
        secondRegion = btnYOri + 5*txtOffset + 4*btnYOffset
        wx.StaticLine(panel, pos=(btnXOri, secondRegion), size=(350, 3))
        
        wx.StaticText(panel, label='Degausser Cooler', pos=(btnXOri, secondRegion + 4*txtOffset))
        self.degausserRBox = wx.RadioBox(panel, label = '', pos = (btnXOri + btnXOffset, secondRegion + txtOffset), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_ROWS)
        self.degausserRBox.SetStringSelection('Off')
        self.degausserRBox.Bind(wx.EVT_RADIOBOX,self.onDegausserRadioBox)
        closeBtn = wx.Button(panel, label='Close', pos=(btnXOri + txtBoxXOffset, secondRegion + 3*txtOffset), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
                
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)
                
        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
                
        self.SetSize((400, 310))
        self.SetTitle('Vacuum Control')
        self.Centre()

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    def updateGUI(self, messageList):
        cmdStr = messageList[0]
        respStr = messageList[1]
        self.outputTBox.SetValue(cmdStr)
        self.inputTBox.SetValue(respStr)
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
    def onDegausserRadioBox(self, event):
        mode = self.degausserRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.VACUUM_SET_DEGAUSSER, [mode]])
        return
        
    '''
    '''
    def onMotorRadioBox(self, event):
        mode = self.motorRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.VACUUM_SET_MOTOR, [mode]])
        return
        
    '''
    '''
    def onConnectRadioBox(self, event):
        mode = self.connectRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.VACUUM_SET_CONNECT, [mode]])
        return
        
    '''
    '''
    def onReset(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.VACUUM_RESET, []])
        return
        
    '''
    '''
    def onConnect(self, event):
        if (self.parent.devControl.vacuum == None):
            self.parent.devControl.vacuum = self.parent.devControl.openVacuumComm(self.parent.devControl.vacuum, 
                                                                                'Vacuum', 
                                                                                self.parent.modConfig, 
                                                                                'COMPortVacuum')
        if (self.parent.devControl.vacuum != None):
            self.parent.deviceList.append(self.parent.devControl.vacuum)
            
                                     
        else:
            self.parent.devControl.vacuum.closeDevice()
            self.parent.devControl.vacuum = None
        return
       
    '''
    '''
    def onShow(self, event):
        if (self.parent != None):
            self.parent.NOCOMM_Flag = False
            self.parent.modConfig.processData.vacuumEnable = True
                
            if (self.parent.devControl.vacuum == None):
                self.connectBtn.SetLabel('Connect')
            else:
                self.connectBtn.SetLabel('Disconnect')
        return
        
    '''
    '''
    def onClose(self, event):
        self.Close(force=False)
        return
        
    '''
    '''
    def onClosed(self, event):
        if (self.parent != None):
            if 'VacuumControl' in self.parent.panelList.keys():          
                del self.parent.panelList['VacuumControl']
                
        self.Destroy()
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def DegausserCooler(self, switch):
        if self.parent.NOCOMM_MODE:
            return
        
        self.parent.pushTaskToQueue([self.parent.devControl.VACUUM_SET_DEGAUSSER, [switch]])
        return

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmVacuum(parent=None)
        frame.Show(True)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        