'''
Created on Nov 19, 2024

@author: hd.nguyen
'''
import wx

class frmSQUID(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmSQUID, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        btnLength = 105
        smallBtnLength = 50
        smallTxtBoxLength = 60
        btnHeight = 30
        smallBtnHeight = 22
        txtBoxHeight = 25
        btnXOri = 20
        btnYOri = 20
        txtBoxOri = btnYOri + 2
        btnXOffset = 120
        btnYOffset = 40
        
        txtOffset = 5
        txtBoxXOffset = btnXOffset - smallTxtBoxLength - 15
        txtBoxYOffset = 40 
        
        # First Column
        wx.StaticText(panel, label='Output', pos=(btnXOri, txtBoxOri + txtBoxYOffset + txtOffset))
        self.outputTBox = wx.TextCtrl(panel, pos=(btnXOri+txtBoxXOffset, txtBoxOri + txtBoxYOffset), size=(smallTxtBoxLength, txtBoxHeight))
        # Radio buttons group
        radioBoxLabels = ['X', 'Y', 'Z', 'A']
        self.activeMotroRBox = wx.RadioBox(panel, label = '', pos = (btnXOri, btnYOri + 2*btnYOffset), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_COLS)
        self.activeMotroRBox.SetStringSelection('X') 
        cr1Btn = wx.Button(panel, label='CR1', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset), size=(smallBtnLength, smallBtnHeight))
        cr1Btn.Bind(wx.EVT_BUTTON, self.onSetCfg)
        clcBtn = wx.Button(panel, label='CLC', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        clcBtn.Bind(wx.EVT_BUTTON, self.onSetCfg)
        cseBtn = wx.Button(panel, label='CSE', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 2*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        cseBtn.Bind(wx.EVT_BUTTON, self.onSetCfg)
        cf1Btn = wx.Button(panel, label='CF1', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 3*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        cf1Btn.Bind(wx.EVT_BUTTON, self.onSetCfg)
        clpBtn = wx.Button(panel, label='CLP', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 4*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        clpBtn.Bind(wx.EVT_BUTTON, self.onSetCfg)
        configBtn = wx.Button(panel, label='Configure SQUID', pos=(btnXOri, btnYOri + 5*btnYOffset), size=(btnLength, btnHeight))
        configBtn.Bind(wx.EVT_BUTTON, self.onConfigure)  
        
        # Second Column        
        self.connectBtn = wx.Button(panel, label='Connect', pos=(btnXOri + btnXOffset, btnYOri), size=(btnLength, btnHeight))
        self.connectBtn.Bind(wx.EVT_BUTTON, self.onConnect)
        wx.StaticText(panel, label='Input', pos=(btnXOri + btnXOffset, txtBoxOri + txtBoxYOffset + txtOffset))
        self.inputTBox = wx.TextCtrl(panel, pos=(btnXOri + txtBoxXOffset + btnXOffset, txtBoxOri + txtBoxYOffset), size=(smallTxtBoxLength, txtBoxHeight))
        readCountBtn = wx.Button(panel, label='Read Count', pos=(btnXOri + btnXOffset, btnYOri + 2*btnYOffset), size=(btnLength, btnHeight))
        readCountBtn.Bind(wx.EVT_BUTTON, self.onReadCount)        
        readDataBtn = wx.Button(panel, label='Read Data', pos=(btnXOri + btnXOffset, btnYOri + 3*btnYOffset), size=(btnLength, btnHeight))
        readDataBtn.Bind(wx.EVT_BUTTON, self.onReadData)
        readRangeBtn = wx.Button(panel, label='Read Range', pos=(btnXOri + btnXOffset, btnYOri + 4*btnYOffset), size=(btnLength, btnHeight))
        readRangeBtn.Bind(wx.EVT_BUTTON, self.onReadRange)
        
        # Third Column
        closeBtn = wx.Button(panel, label='Close', pos=(btnXOri + 2*btnXOffset, btnYOri), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
        resetCountBtn = wx.Button(panel, label='Reset Count', pos=(btnXOri + 2*btnXOffset, btnYOri + 2*btnYOffset), size=(btnLength, btnHeight))
        resetCountBtn.Bind(wx.EVT_BUTTON, self.onResetCount)
        readBtn = wx.Button(panel, label='Read', pos=(btnXOri + 2*btnXOffset, btnYOri + 5*btnYOffset), size=(btnLength, btnHeight))
        readBtn.Bind(wx.EVT_BUTTON, self.onRead)
        
        # Button group
        microBtnLength = 30
        microBtnHeight = 22
        groupOffset = 0
        groupXOffset = 5
        groupYOffset = groupOffset + 20 
        btnXOri += 2*btnXOffset
        wx.StaticBox(panel, -1, 'Change Range', pos=(btnXOri + groupOffset, btnYOri + 3*btnYOffset), size=(110, 70))
        btnYOri += 3*btnYOffset + groupYOffset 
        fRangeBtn = wx.Button(panel, label='F', pos=(btnXOri + groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        fRangeBtn.Bind(wx.EVT_BUTTON, self.onChangeRate)
        tRangeBtn = wx.Button(panel, label='T', pos=(btnXOri + 8*groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        tRangeBtn.Bind(wx.EVT_BUTTON, self.onChangeRate)
        eRangeBtn = wx.Button(panel, label='E', pos=(btnXOri + 15*groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        eRangeBtn.Bind(wx.EVT_BUTTON, self.onChangeRate)
        oneRangeBtn = wx.Button(panel, label='1', pos=(btnXOri + groupXOffset, btnYOri+ microBtnHeight + 2), size=(microBtnLength, microBtnHeight))
        oneRangeBtn.Bind(wx.EVT_BUTTON, self.onChangeRate)
        hRangeBtn = wx.Button(panel, label='H', pos=(btnXOri + 8*groupXOffset, btnYOri+ microBtnHeight + 2), size=(microBtnLength, microBtnHeight))
        hRangeBtn.Bind(wx.EVT_BUTTON, self.onChangeRate)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)

        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
        
        self.SetSize((400, 305))
        self.SetTitle('SQUID Control')
        self.Centre()
        self.Show(True)

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
    def onRead(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.SQUID_READ, []])
        return 
    
    '''
    '''
    def onSetCfg(self, event):
        activeAxis = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.SQUID_SET_CFG, [activeAxis, event.EventObject.Label]])
        return 
        
    '''
    '''
    def onChangeRate(self, event):
        activeAxis = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.SQUID_CHANGE_RATE, [activeAxis, event.EventObject.Label]])
        return
        
    '''
    '''
    def onConfigure(self, event):
        activeAxis = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.SQUID_CONFIGURE, [activeAxis]])
        return
    
    '''
    '''
    def onResetCount(self, event):
        activeAxis = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.SQUID_RESET_COUNT, [activeAxis]])
        return
        
    '''
    '''
    def onConnect(self, event):
        if (self.parent.devControl.SQUID == None):
            self.parent.devControl.SQUID = self.parent.devControl.openSQUIDComm(self.parent.devControl.SQUID, 
                                                                                'SQUID', 
                                                                                self.parent.modConfig, 
                                                                                'COMPortSquids')
        if (self.parent.devControl.SQUID != None):
            self.parent.deviceList.append(self.parent.devControl.SQUID)
            
                                     
        else:
            self.parent.devControl.SQUID.closeDevice()
            self.parent.devControl.SQUID = None
        return
            
    '''
    '''
    def onReadCount(self, event):    
        activeAxis = self.activeMotroRBox.GetStringSelection()
        if (activeAxis == 'A'):
            self.parent.sendErrorMessage('Error: A axis is not valid.')
        else:
            self.parent.pushTaskToQueue([self.parent.devControl.SQUID_READ_COUNT, [activeAxis]])
        return

    '''
    '''
    def onReadData(self, event):    
        activeAxis = self.activeMotroRBox.GetStringSelection()
        if (activeAxis == 'A'):
            self.parent.sendErrorMessage('Error: A axis is not valid.')
        else:
            self.parent.pushTaskToQueue([self.parent.devControl.SQUID_READ_DATA, [activeAxis]])
        return

    '''
    '''
    def onReadRange(self, event):    
        activeAxis = self.activeMotroRBox.GetStringSelection()
        if (activeAxis == 'A'):
            self.parent.sendErrorMessage('Error: A axis is not valid.')
        else:
            self.parent.pushTaskToQueue([self.parent.devControl.SQUID_READ_RANGE, [activeAxis]])
        return
                
    '''
    '''
    def onShow(self, event):
        if (self.parent.devControl.SQUID != None):
            self.connectBtn.SetLabel('Disconnect')
        else:
            self.connectBtn.SetLabel('Connect')
            
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
            if 'SQUIDControl' in self.parent.panelList.keys():          
                del self.parent.panelList['SQUIDControl']
                
        self.Destroy()
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmSQUID(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        

        
        