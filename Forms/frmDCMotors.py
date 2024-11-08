'''
Created on Oct 22, 2024

@author: hd.nguyen
'''
import wx

class frmDCMotors(wx.Frame):
    '''
    classdocs
    '''
    tipMessage = """Make sure power is on to the following devices\n
1. All three 2G SQUID boxes
2. Motor driver box
3. Bartington susceptibility bridge (set to CGS and 1.0)
4. AF unit and cooling air, with the AF degausser on
   computer control(if you are going to do AF or rockmag)
5. IRM pulse box (if you are going to do rockmag)
6. ARM bias box (if you are going to do rockmag)"""
    parent = None

    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmDCMotors, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()
        
        # Check for enable Motors
        self.checkMotorAvailable()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        btnLength = 120
        smallBtnLength = 60
        samllTxtBoxLength = 50
        btnHeight = 30
        txtBoxHeight = 25
        btnXOri = 20
        btnYOri = 30
        txtBoxOri = btnYOri + 2
        btnXOffset = 150
        btnYOffset = 40
        txtOffset = 18
        
        # First Column
        self.movePosBtn = wx.Button(panel, label='Move To Position', pos=(btnXOri, btnYOri), size=(btnLength, btnHeight))
        homeTopBtn = wx.Button(panel, label='Home to Top', pos=(btnXOri, btnYOri+btnYOffset), size=(btnLength, btnHeight))
        homeTopBtn.Bind(wx.EVT_BUTTON, self.onHomeToTop)
        self.pickupBtn = wx.Button(panel, label='Sample Pickup', pos=(btnXOri, btnYOri+2*btnYOffset), size=(btnLength, btnHeight))
        self.dropoffBtn = wx.Button(panel, label='Sample Dropoff', pos=(btnXOri, btnYOri+3*btnYOffset), size=(btnLength, btnHeight))
        homeCenterBtn = wx.Button(panel, label='Home To Center', pos=(btnXOri, btnYOri+4*btnYOffset), size=(btnLength, btnHeight))
        homeCenterBtn.Bind(wx.EVT_BUTTON, self.onHomeToCenter)
        self.zeroTPBtn = wx.Button(panel, label='Zero T/P', pos=(btnXOri, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        self.pollMotorBtn = wx.Button(panel, label='Poll Motor', pos=(btnXOri, btnYOri+8*btnYOffset), size=(btnLength, btnHeight))
        closeBtn = wx.Button(panel, label='Close', pos=(btnXOri, btnYOri+9*btnYOffset), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
        
        # Second Column
        wx.StaticText(panel, label='Target Position', pos=(btnXOri+btnXOffset, txtBoxOri - txtOffset))
        self.targetPosTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri), size=(btnLength, txtBoxHeight))
        self.changeHeightBtn = wx.Button(panel, label='Change Height', pos=(btnXOri+btnXOffset, btnYOri+btnYOffset), size=(btnLength, btnHeight))
        self.changeAngleTopBtn = wx.Button(panel, label='Change Turn Angle', pos=(btnXOri+btnXOffset, btnYOri+2*btnYOffset), size=(btnLength, btnHeight))
        self.changeHoleBtn = wx.Button(panel, label='Change Hole', pos=(btnXOri+btnXOffset, btnYOri+3*btnYOffset), size=(btnLength, btnHeight))
        self.goXBtn = wx.Button(panel, label='Go to X', pos=(btnXOri+btnXOffset, btnYOri+4*btnYOffset), size=(smallBtnLength, btnHeight))
        self.goXTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset + smallBtnLength + 10, txtBoxOri+4*btnYOffset), size=(samllTxtBoxLength, txtBoxHeight))
        self.spinSampleBtn = wx.Button(panel, label='Spin Sample (rps)', pos=(btnXOri+btnXOffset, btnYOri+5*btnYOffset), size=(btnLength, btnHeight))
        self.relabelPBtn = wx.Button(panel, label='Relabel P', pos=(btnXOri+btnXOffset, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        self.clearPollPBtn = wx.Button(panel, label='Clear Poll Status', pos=(btnXOri+btnXOffset, btnYOri+8*btnYOffset), size=(btnLength, btnHeight))
        
        # Third Column
        wx.StaticText(panel, label='Velocity', pos=(btnXOri+2*btnXOffset, txtBoxOri - txtOffset))
        self.velocityTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri), size=(btnLength, txtBoxHeight))
        self.changeHeightTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+btnYOffset), size=(btnLength, txtBoxHeight))
        self.changeAngleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+2*btnYOffset), size=(btnLength, txtBoxHeight))
        self.changeHoleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+3*btnYOffset), size=(btnLength, txtBoxHeight))
        self.goYBtn = wx.Button(panel, label='Go to Y', pos=(btnXOri+2*btnXOffset, btnYOri+4*btnYOffset), size=(smallBtnLength, btnHeight))
        self.goYTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset + smallBtnLength + 10, txtBoxOri+4*btnYOffset), size=(samllTxtBoxLength, txtBoxHeight))
        self.spinSampleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+5*btnYOffset), size=(btnLength, txtBoxHeight))
        self.setCurrentHoleBtn = wx.Button(panel, label='Set Current Hole', pos=(btnXOri+2*btnXOffset, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        
        #------------------------------------------------------------------------------------------------------------------------
        secondRegion = btnXOri+3*btnXOffset - 10
        wx.StaticLine(panel, pos=(secondRegion, btnYOri), size=(3, 410))
        
        smallBtnLength += 10
        btnXOri += secondRegion 
        btnXOffset = smallBtnLength + 20
        chBoxYOffset = 20
        wx.StaticText(panel, label='Set Position', pos=(btnXOri, txtBoxOri - txtOffset))
        
        # First Column
        self.topBtn = wx.Button(panel, label='Top', pos=(btnXOri, btnYOri), size=(smallBtnLength, btnHeight))
        self.afCoilBtn = wx.Button(panel, label='AF Coil', pos=(btnXOri, btnYOri + btnYOffset), size=(smallBtnLength, btnHeight))
        self.zeroBtn = wx.Button(panel, label='Zero', pos=(btnXOri, btnYOri + 2*btnYOffset), size=(smallBtnLength, btnHeight))
        self.measBtn = wx.Button(panel, label='Meas.', pos=(btnXOri, btnYOri + 3*btnYOffset), size=(smallBtnLength, btnHeight))
        
        # Second Column
        self.irmLoBtn = wx.Button(panel, label='IRM Lo', pos=(btnXOri + btnXOffset, btnYOri), size=(smallBtnLength, btnHeight))
        self.irmHiBtn = wx.Button(panel, label='IRM Hi', pos=(btnXOri + btnXOffset, btnYOri + btnYOffset), size=(smallBtnLength, btnHeight))
        self.sCoilBtn = wx.Button(panel, label='S Coil', pos=(btnXOri + btnXOffset, btnYOri + 2*btnYOffset), size=(smallBtnLength, btnHeight))
        self.loadBtn = wx.Button(panel, label='Load', pos=(btnXOri + btnXOffset, btnYOri + 4*btnYOffset), size=(smallBtnLength, btnHeight))
        
        # Checkbox group
        groupOffset = 0
        chkYOffset = groupOffset + 10 
        wx.StaticBox(panel, -1, 'Connections', pos=(btnXOri + 2*btnXOffset + groupOffset, btnYOri - txtOffset), size=(100, 100))
        self.changerXChkBox = wx.CheckBox(panel, label='Changer (X)', pos=(btnXOri + 2*btnXOffset + chkYOffset, btnYOri))
        self.turningChkBox = wx.CheckBox(panel, label='Turning', pos=(btnXOri + 2*btnXOffset + chkYOffset, btnYOri + chBoxYOffset))
        self.upDownChkBox = wx.CheckBox(panel, label='Up/Down', pos=(btnXOri + 2*btnXOffset + chkYOffset, btnYOri + 2*chBoxYOffset))
        self.changerYChkBox = wx.CheckBox(panel, label='Changer (Y)', pos=(btnXOri + 2*btnXOffset + chkYOffset, btnYOri + 3*chBoxYOffset))
        
        # Radio buttons group
        radioBoxLabels = ['Changer (X)', 'Turning', 'Up/Down', 'Changer (Y)']
        self.rbox = wx.RadioBox(panel, label = 'Active Controls', pos = (btnXOri + 2*btnXOffset + groupOffset, btnYOri + 2*btnYOffset + 10), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_COLS) 
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onRadioBox) 
            
        # Bottom TextBox and Buttons
        txtBoxLength = 200
        txtOffset = 5
        btnXOffset -= 5
        txtBoxYOffset = 30 
        txtBoxOri += 5*btnYOffset + 10
        wx.StaticText(panel, label='Output', pos=(btnXOri, txtBoxOri + txtOffset))
        self.outputTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri ), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Input', pos=(btnXOri, txtBoxOri + txtBoxYOffset + txtOffset))
        self.inputTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        txtBoxLength = 110
        smallBtnLength += 10
        buttonXOffset = txtBoxLength + 10
        buttonYOffset = 2
        btnHeight -= 2
        wx.StaticText(panel, label='Last Pos Read', pos=(btnXOri, txtBoxOri + 2*txtBoxYOffset + txtOffset))
        self.lastPosTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + 2*txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        self.readPosBtn = wx.Button(panel, label='Read Position', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 2*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        wx.StaticText(panel, label='Last Turn Angle', pos=(btnXOri, txtBoxOri + 3*txtBoxYOffset + txtOffset))
        self.lastTurnTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + 3*txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        self.readTurnBtn = wx.Button(panel, label='Read Angle', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 3*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        wx.StaticText(panel, label='Last Hole Read', pos=(btnXOri, txtBoxOri + 4*txtBoxYOffset + txtOffset))
        self.lastHoleTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + 4*txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        self.readHoleBtn = wx.Button(panel, label='Read Hole', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 4*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        
        # Last row of buttons
        btnHeight += 2
        btnXOffset += 17
        txtBoxOri += 5*txtBoxYOffset + 20
        self.resetBtn = wx.Button(panel, label='Reset', pos=(btnXOri, txtBoxOri), size=(smallBtnLength, btnHeight))
        self.stopBtn = wx.Button(panel, label='Stop', pos=(btnXOri + btnXOffset, txtBoxOri), size=(smallBtnLength, btnHeight))
        haltBtn = wx.Button(panel, label='HALT!', pos=(btnXOri + 2*btnXOffset, txtBoxOri), size=(smallBtnLength, btnHeight))
        haltBtn.Bind(wx.EVT_BUTTON, self.onHalt)
        haltBtn.SetBackgroundColour('Red')

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)
        
        self.SetSize((800, 500))
        self.SetTitle('Motor Control')
        self.Centre()
        self.Show(True)
                          
    '''
    '''
    def checkMotorAvailable(self):
        for motor in self.parent.devControl.deviceList:
            if motor.active:
                if 'ChangerX' in motor.label:
                    self.changerXChkBox.SetValue(True)
                elif 'ChangerY' in motor.label:
                    self.changerYChkBox.SetValue(True)
                elif 'Turning' in motor.label:
                    self.turningChkBox.SetValue(True)
                elif 'UpDown' in motor.label:
                    self.upDownChkBox.SetValue(True)
                    
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Move vertical motor to top position
    '''
    def onHomeToTop(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_HOME_TO_TOP, [None]])
        return

    '''
    '''
    def onHomeToCenter(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_HOME_TO_TOP, [None]])
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_HOME_TO_CENTER, [None]])
        return
                
    '''
    '''
    def onRadioBox(self, event):
        print(self.rbox.GetStringSelection() + ' is clicked from Radio Box')
        
    '''
    '''
    def onHalt(self, event):
        self.parent.processQueue.put('Program_Halted')
        
    '''
    '''
    def onClose(self, event):
        self.Close(force=False)

    '''
    '''
    def onClosed(self, event):
        if self.parent.panelList:
            if 'MotorControl' in self.parent.panelList.keys():          
                del self.parent.panelList['MotorControl']
                
        self.Destroy()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmDCMotors(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        
        