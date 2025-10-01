'''
Created on Oct 22, 2024

@author: hd.nguyen
'''
import wx

from Forms.frmTestUnit import frmTestUnit

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
        if (parent != None):
            super(frmDCMotors, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
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
        movePosBtn = wx.Button(panel, label='Move To Position', pos=(btnXOri, btnYOri), size=(btnLength, btnHeight))
        movePosBtn.Bind(wx.EVT_BUTTON, self.onMoveMotor)
        homeTopBtn = wx.Button(panel, label='Home to Top', pos=(btnXOri, btnYOri+btnYOffset), size=(btnLength, btnHeight))
        homeTopBtn.Bind(wx.EVT_BUTTON, self.onHomeToTop)
        pickupBtn = wx.Button(panel, label='Sample Pickup', pos=(btnXOri, btnYOri+2*btnYOffset), size=(btnLength, btnHeight))
        pickupBtn.Bind(wx.EVT_BUTTON, self.onSamplePickup)
        dropoffBtn = wx.Button(panel, label='Sample Dropoff', pos=(btnXOri, btnYOri+3*btnYOffset), size=(btnLength, btnHeight))
        dropoffBtn.Bind(wx.EVT_BUTTON, self.onSampleDropoff)
        homeCenterBtn = wx.Button(panel, label='Home To Center', pos=(btnXOri, btnYOri+4*btnYOffset), size=(btnLength, btnHeight))
        homeCenterBtn.Bind(wx.EVT_BUTTON, self.onHomeToCenter)
        zeroTPBtn = wx.Button(panel, label='Zero T/P', pos=(btnXOri, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        zeroTPBtn.Bind(wx.EVT_BUTTON, self.onZeroTargetPosition)
        pollMotorBtn = wx.Button(panel, label='Poll Motor', pos=(btnXOri, btnYOri+8*btnYOffset), size=(btnLength, btnHeight))
        pollMotorBtn.Bind(wx.EVT_BUTTON, self.onPollMotor)
        closeBtn = wx.Button(panel, label='Close', pos=(btnXOri, btnYOri+9*btnYOffset), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
        
        # Second Column
        wx.StaticText(panel, label='Target Position', pos=(btnXOri+btnXOffset, txtBoxOri - txtOffset))
        self.targetPosTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri), size=(btnLength, txtBoxHeight))
        changeHeightBtn = wx.Button(panel, label='Change Height', pos=(btnXOri+btnXOffset, btnYOri+btnYOffset), size=(btnLength, btnHeight))
        changeHeightBtn.Bind(wx.EVT_BUTTON, self.onChangeHeight)
        changeAngleTopBtn = wx.Button(panel, label='Change Turn Angle', pos=(btnXOri+btnXOffset, btnYOri+2*btnYOffset), size=(btnLength, btnHeight))
        changeAngleTopBtn.Bind(wx.EVT_BUTTON, self.onChangeTurnAngle)
        changeHoleBtn = wx.Button(panel, label='Change Hole', pos=(btnXOri+btnXOffset, btnYOri+3*btnYOffset), size=(btnLength, btnHeight))
        changeHoleBtn.Bind(wx.EVT_BUTTON, self.onChangeHole)
        goXBtn = wx.Button(panel, label='Go to X', pos=(btnXOri+btnXOffset, btnYOri+4*btnYOffset), size=(smallBtnLength, btnHeight))
        goXBtn.Bind(wx.EVT_BUTTON, self.onGoX)
        self.goXTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset + smallBtnLength + 10, txtBoxOri+4*btnYOffset), size=(samllTxtBoxLength, txtBoxHeight))
        spinSampleBtn = wx.Button(panel, label='Spin Sample (rps)', pos=(btnXOri+btnXOffset, btnYOri+5*btnYOffset), size=(btnLength, btnHeight))
        spinSampleBtn.Bind(wx.EVT_BUTTON, self.onSpinSample)
        relabelPBtn = wx.Button(panel, label='Relabel P', pos=(btnXOri+btnXOffset, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        relabelPBtn.Bind(wx.EVT_BUTTON, self.onRelabelPos)
        clearPollPBtn = wx.Button(panel, label='Clear Poll Status', pos=(btnXOri+btnXOffset, btnYOri+8*btnYOffset), size=(btnLength, btnHeight))
        clearPollPBtn.Bind(wx.EVT_BUTTON, self.onClearPoll)
        
        # Third Column
        wx.StaticText(panel, label='Velocity', pos=(btnXOri+2*btnXOffset, txtBoxOri - txtOffset))
        self.velocityTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri), size=(btnLength, txtBoxHeight))
        self.changeHeightTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+btnYOffset), size=(btnLength, txtBoxHeight))
        self.changeAngleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+2*btnYOffset), size=(btnLength, txtBoxHeight))
        self.changeHoleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+3*btnYOffset), size=(btnLength, txtBoxHeight))
        goYBtn = wx.Button(panel, label='Go to Y', pos=(btnXOri+2*btnXOffset, btnYOri+4*btnYOffset), size=(smallBtnLength, btnHeight))
        goYBtn.Bind(wx.EVT_BUTTON, self.onGoY)
        self.goYTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset + smallBtnLength + 10, txtBoxOri+4*btnYOffset), size=(samllTxtBoxLength, txtBoxHeight))
        self.spinSampleTBox = wx.TextCtrl(panel, pos=(btnXOri+2*btnXOffset, txtBoxOri+5*btnYOffset), size=(btnLength, txtBoxHeight))
        setCurrentHoleBtn = wx.Button(panel, label='Set Current Hole', pos=(btnXOri+2*btnXOffset, btnYOri+7*btnYOffset), size=(btnLength, btnHeight))
        setCurrentHoleBtn.Bind(wx.EVT_BUTTON, self.onSetCurrentHole)
        
        #------------------------------------------------------------------------------------------------------------------------
        secondRegion = btnXOri+3*btnXOffset - 10
        wx.StaticLine(panel, pos=(secondRegion, btnYOri), size=(3, 410))
        
        smallBtnLength += 10
        btnXOri += secondRegion 
        btnXOffset = smallBtnLength + 20
        chBoxYOffset = 20
        wx.StaticText(panel, label='Set Position', pos=(btnXOri, txtBoxOri - txtOffset))
        
        # First Column
        topBtn = wx.Button(panel, label='Top', pos=(btnXOri, btnYOri), size=(smallBtnLength, btnHeight))
        topBtn.Bind(wx.EVT_BUTTON, self.onSetTop)
        afCoilBtn = wx.Button(panel, label='AF Coil', pos=(btnXOri, btnYOri + btnYOffset), size=(smallBtnLength, btnHeight))
        afCoilBtn.Bind(wx.EVT_BUTTON, self.onSetAFCoil)
        zeroBtn = wx.Button(panel, label='Zero', pos=(btnXOri, btnYOri + 2*btnYOffset), size=(smallBtnLength, btnHeight))
        zeroBtn.Bind(wx.EVT_BUTTON, self.onSetZero)
        measBtn = wx.Button(panel, label='Meas.', pos=(btnXOri, btnYOri + 3*btnYOffset), size=(smallBtnLength, btnHeight))
        measBtn.Bind(wx.EVT_BUTTON, self.onSetMeas)
        
        # Second Column
        self.irmLoBtn = wx.Button(panel, label='IRM Lo', pos=(btnXOri + btnXOffset, btnYOri), size=(smallBtnLength, btnHeight))
        self.irmHiBtn = wx.Button(panel, label='IRM Hi', pos=(btnXOri + btnXOffset, btnYOri + btnYOffset), size=(smallBtnLength, btnHeight))
        sCoilBtn = wx.Button(panel, label='S Coil', pos=(btnXOri + btnXOffset, btnYOri + 2*btnYOffset), size=(smallBtnLength, btnHeight))
        sCoilBtn.Bind(wx.EVT_BUTTON, self.onSetCoil)
        loadBtn = wx.Button(panel, label='Load', pos=(btnXOri + btnXOffset, btnYOri + 4*btnYOffset), size=(smallBtnLength, btnHeight))
        loadBtn.Bind(wx.EVT_BUTTON, self.onLoad)
        
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
        self.activeMotroRBox = wx.RadioBox(panel, label = 'Active Controls', pos = (btnXOri + 2*btnXOffset + groupOffset, btnYOri + 2*btnYOffset + 10), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_COLS) 
        self.activeMotroRBox.Bind(wx.EVT_RADIOBOX,self.onRadioBox) 
            
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
        readPosBtn = wx.Button(panel, label='Read Position', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 2*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        readPosBtn.Bind(wx.EVT_BUTTON, self.onReadPosition)
        wx.StaticText(panel, label='Last Turn Angle', pos=(btnXOri, txtBoxOri + 3*txtBoxYOffset + txtOffset))
        self.lastTurnTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + 3*txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        readTurnBtn = wx.Button(panel, label='Read Angle', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 3*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        readTurnBtn.Bind(wx.EVT_BUTTON, self.onReadAngle)
        wx.StaticText(panel, label='Last Hole Read', pos=(btnXOri, txtBoxOri + 4*txtBoxYOffset + txtOffset))
        self.lastHoleTBox = wx.TextCtrl(panel, pos=(btnXOri+btnXOffset, txtBoxOri + 4*txtBoxYOffset), size=(txtBoxLength, txtBoxHeight))
        readHoleBtn = wx.Button(panel, label='Read Hole', pos=(btnXOri + btnXOffset + buttonXOffset, txtBoxOri + 4*txtBoxYOffset - buttonYOffset), size=(smallBtnLength, btnHeight))
        readHoleBtn.Bind(wx.EVT_BUTTON, self.onReadHole)
        
        # Last row of buttons
        btnHeight += 2
        btnXOffset += 17
        txtBoxOri += 5*txtBoxYOffset + 20
        resetBtn = wx.Button(panel, label='Reset', pos=(btnXOri, txtBoxOri), size=(smallBtnLength, btnHeight))
        resetBtn.Bind(wx.EVT_BUTTON, self.onReset)
        stopBtn = wx.Button(panel, label='Stop', pos=(btnXOri + btnXOffset, txtBoxOri), size=(smallBtnLength, btnHeight))
        stopBtn.Bind(wx.EVT_BUTTON, self.onStop)
        haltBtn = wx.Button(panel, label='HALT!', pos=(btnXOri + 2*btnXOffset, txtBoxOri), size=(smallBtnLength, btnHeight))
        haltBtn.Bind(wx.EVT_BUTTON, self.onHalt)
        haltBtn.SetBackgroundColour('Red')

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)
        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
        
        self.SetSize((800, 500))
        self.SetTitle('Motor Control')
        self.Centre()
        self.Show(True)
                          
    '''
    '''
    def checkMotorAvailable(self):
        if (self.parent != None):
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
                    
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageList):
        if ('Command Exchange' in messageList[0]):
            self.parent.modConfig.parseCommandExchange(messageList[1].strip())
        elif ('Motor Info' in messageList[0]):
            self.parent.modConfig.parseMotorInfo(messageList[1].strip())
        elif ('Data' in messageList[0]):
            self.parent.modConfig.parseMotorData(messageList[1].strip(), messageList[2].strip())
            
        self.outputTBox.SetValue(self.parent.modConfig.outCommand)
        self.inputTBox.SetValue(self.parent.modConfig.inResponse)
        self.lastPosTBox.SetValue(self.parent.modConfig.lastPositionRead)
        self.targetPosTBox.SetValue(self.parent.modConfig.targetPosition)
        self.velocityTBox.SetValue(self.parent.modConfig.velocity)
        self.goXTBox.SetValue(self.parent.modConfig.xPos)
        self.goYTBox.SetValue(self.parent.modConfig.yPos)
        self.spinSampleTBox.SetValue(self.parent.modConfig.turningAngle)
            
        if 'ChangerX' in self.parent.modConfig.activeMotor:
            self.activeMotroRBox.SetSelection(0)
        elif 'Turning' in self.parent.modConfig.activeMotor:
            self.activeMotroRBox.SetSelection(1)
        elif 'UpDown' in self.parent.modConfig.activeMotor:
            self.activeMotroRBox.SetSelection(2)
        elif 'ChangerY' in  self.parent.modConfig.activeMotor:
            self.activeMotroRBox.SetSelection(3)
            
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        return
            
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
    def onMoveMotor(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection()
        tartgetPosition = int(self.targetPosTBox.GetValue())
        velocity = int(self.velocityTBox.GetValue())
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_MOVE, [activeMotor, tartgetPosition, velocity]])
        return
        
    '''
    '''
    def onSamplePickup(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_SAMPLE_PICKUP, [None]])
        return
        
    '''
    '''
    def onSampleDropoff(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_SAMPLE_DROPOFF, [self.parent.modConfig.SampleHeight]])
        return
        
    '''
    '''
    def onZeroTargetPosition(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_ZERO_TP, [activeMotor]])
        return
       
    '''
    '''
    def onPollMotor(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_POLL, [activeMotor]])
        return
    
    '''
    '''
    def onClearPoll(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection()
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_CLEAR_POLL, [activeMotor]])
        return        
        
    '''
    '''
    def onRelabelPos(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection()
        tartgetPosition = int(self.targetPosTBox.GetValue())
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_CLEAR_POLL, [activeMotor, tartgetPosition]])
        return        
        
    '''
    '''
    def onChangeHole(self, event):
        try:
            currentHole = float(self.changeHoleTBox.GetValue())
        except:
            currentHole = 0.0
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_CHANGE_HOLE, [currentHole]])
        return 
        
    '''
    '''
    def onSetCurrentHole(self, event):
        try:
            currentHole = int(self.changeHoleTBox.GetValue())
        except:
            currentHole = 0
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_SET_CURRENT_HOLE, [currentHole]])
        return
                
    '''
    '''
    def onSetTop(self, event):
        self.targetPosTBox.SetValue('0')
        self.changeHeightTBox.SetValue('0')
        return
        
    '''
        Set the value of the place to move to the center of the Af coils
    '''
    def onSetMeas(self, event):
        measStr = str(int(self.modConfig.MeasPos + self.modConfig.SampleHeight / 2))
        self.targetPosTBox.SetValue(measStr)
        self.changeHeightTBox.SetValue(measStr)
        return 
    
    '''
    '''
    def onSetCoil(self, event):
        self.targetPosTBox.SetValue(str(self.modConfig.SCoilPos))
        self.changeHeightTBox.SetValue(str(self.modConfig.SCoilPos))
        return
        
    '''
    '''
    def onSetZero(self, event):
        self.targetPosTBox.SetValue(str(self.modConfig.ZeroPos))
        self.changeHeightTBox.SetValue(str(self.modConfig.ZeroPos))
        return        
        
    '''
    '''
    def onGoX(self, event):
        xPos = self.goXTBox.GetValue() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_GO_TO_X, [xPos]])
        return
        
    '''
    '''
    def onGoY(self, event):
        yPos = self.goYTBox.GetValue() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_GO_TO_Y, [yPos]])
        return
        
    '''
    '''
    def onSpinSample(self, event):
        spinRPS = self.spinSampleTBox.GetValue() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_SPIN_SAMPLE, [spinRPS]])
        return
        
    '''
    '''
    def onChangeTurnAngle(self, event):
        turnAngle = self.changeAngleTBox.GetValue() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_CHANGE_TURN_ANGLE, [turnAngle]])
        return
        
    '''
    '''
    def onChangeHeight(self, event):
        height = self.changeHeightTBox.GetValue() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_CHANGE_HEIGHT, [height]])
        return
        
    '''
    '''
    def onSetAFCoil(self, event):
        # Set the value of the place to move to the center of the Af coils
        self.targetPosTBox.SetValue(str(self.modConfig.AFPos))
        self.changeHeightTBox.SetValue(str(self.modConfig.AFPos))
        return
    
    def onLoad(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_LOAD, [None]])
        return
        
    '''
    '''
    def onReadPosition(self, event):
        activeMotor = self.activeMotroRBox.GetStringSelection() 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_READ_POSITION, [activeMotor]])
        return
       
    '''
    '''
    def onReadAngle(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_READ_ANGLE, [None]])
        return
        
    '''
    '''
    def onReadHole(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_READ_HOLE, [None]])
        return
       
    '''
    '''
    def onReset(self, event): 
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_RESET, [None]])
        return        
        
    '''
    '''
    def onStop(self, event):
        self.parent.pushTaskToQueue([self.parent.devControl.MOTOR_STOP, [None]])
        return        
        
    '''
    '''
    def onRadioBox(self, event):
        return
        
    '''
    '''
    def onHalt(self, event):
        self.parent.processQueue.put('Program_Halted')
        self.parent.process.terminate()
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
            if self.parent.panelList:
                if 'MotorControl' in self.parent.panelList.keys():          
                    del self.parent.panelList['MotorControl']
                
        self.Destroy()
        return
    
    '''
    '''
    def onShow(self, event):
        if (self.parent != None):
            self.parent.NOCOMM_Flag = False
            self.parent.modConfig.processData.motorsEnable = True
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        testUnit = frmTestUnit()
        motorControl = frmDCMotors(parent=testUnit)
        testUnit.panelList['MotorControl'] = motorControl
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        
        