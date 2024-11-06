'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os
import time

from Hardware.Device.MotorControl import MotorControl

class DevicesControl():
    '''
    classdocs
    '''
    HOME_TO_TOP     = 0x0001
    HOME_TO_CENTER  = 0x0002
    MotorPositionMoveToLoadCorner = 900000
    MotorPositionMoveToCenter = -900000
    MoveXYMotorsToLimitSwitch_TimeoutSeconds = 120
    
    frmSettingsVisible = True
    frmSettingsOptions2Visible = True
    frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY = True
    
    lastCmdMove = 1
    
    upDown = None
    changerX = None
    changerY = None
    turning = None
    deviceList = []
    
    devicesAllGoodFlag = False
    programHaltedFlag = False
    programPausedFlag = False

    def __init__(self):
        '''
        Constructor
        '''
        self.currentPath = os.getcwd()
        self.currentPath += '\\Hardware\\Device'        
        self.DCMotorHomeToTop_StopOnTrue = False
                    
    '''
        Set parameter from INI files for each motor
    '''
    def setDevicesConfig(self, config):                        
        message = self.openDevices(config)
        
        if (self.devicesAllGoodFlag):
            self.upDown.setMotorConfig(config)
            self.changerX.setMotorConfig(config)
            self.changerY.setMotorConfig(config)
            self.turning.setMotorConfig(config)
        
        return message

    '''
    '''
    def openDevice(self, device, comPort, label):        
        message = ''
        if (device != None):
            if (device.openDevice()):
                message += device.label + ' opened' 
            else:
                message += device.label + ' fail to open'
                self.devicesAllGoodFlag = False
        else:
            try:            
                message += label + ': ' + comPort  
                device = MotorControl(57600, self.currentPath, comPort, label)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False

        
        return device, message + '\n'
        
    '''
    '''
    def openDevices(self, config):
        self.devicesAllGoodFlag = True
                
        message = '\n'
        self.deviceList = []
        comPort = 'COM' + config['COMPorts']['COMPortUpDown']        
        self.upDown, respStr = self.openDevice(self.upDown, comPort, 'UpDown')
        message += respStr
        if (self.upDown != None):
            self.deviceList.append(self.upDown)
        
        comPort = 'COM' + config['COMPorts']['COMPortChanger']
        self.changerX, respStr = self.openDevice(self.changerX, comPort, 'ChangerX')
        message += respStr
        if (self.changerX != None):
            self.deviceList.append(self.changerX)

        comPort = 'COM' + config['COMPorts']['COMPortChangerY']
        self.changerY, respStr = self.openDevice(self.changerY, comPort, 'ChangerY')
        message += respStr
        if (self.changerY != None):
            self.deviceList.append(self.changerY)

        comPort = 'COM' + config['COMPorts']['COMPortTurning']
        self.turning, respStr = self.openDevice(self.turning, comPort, 'Turning')
        message += respStr    
        if (self.turning != None):
            self.deviceList.append(self.turning)
        
        return message 

    '''
    '''
    def closeDevice(self, device):
        if (device != None):
            if (device.serialDevice.isOpen()):
                device.closeDevice()
                
    '''
    '''
    def closeDevices(self):
        for device in self.deviceList:
            self.closeDevice(device)

    '''
        Check for message from the MainForm
        If Program_Halt request is sent, exit.
        Otherwise, continue
    '''
    def checkProgramHaltRequest(self, queue):
        try:
            if self.programHaltedFlag:
                return True
            else:
                message = queue.get(timeout=0.1)
                if 'Program_Halted' in message:
                    self.programHaltedFlag = True
                    return True
                
            return False
            
        except:
            return False
   
    '''--------------------------------------------------------------------------------------------
                        
                        Process Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def retrieveProcessData(self, processData):
        self.frmSettingsVisible = processData.frmSettingsVisible
        self.frmSettingsOptions2Visible = processData.frmSettingsOptions2Visible
        self.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY = processData.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY
        
        # Port Open
        for i in range(0, len(self.deviceList)):
            self.deviceList[i].PortOpen = processData.PortOpen[i]
            
    '''
    '''
    def saveProcessData(self, processData):
        processData.frmSettingsVisible = self.frmSettingsVisible
        processData.frmSettingsOptions2Visible = self.frmSettingsOptions2Visible
        processData.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY = self.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY

        # PortOpen
        processData.PortOpen = []
        for device in self.deviceList:
            processData.PortOpen.append(device.PortOpen)
        
        return processData

    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Functions
                        
    --------------------------------------------------------------------------------------------'''   
    '''
        Move the UpDown motor
    '''
    def upDownMove(self, queue, position, speed, waitingForStop=True):
        if self.checkProgramHaltRequest(queue):
            return
        
        if not (self.programPausedFlag or self.programHaltedFlag):
            self.lastMoveCommand = self.lastCmdMove
            self.lastMoveMotor = 'UpDown'
            self.lastMoveTarget = position
        
        movementSign = 1
        startingPos = self.upDown.readPosition()
        if (position < startingPos):
            movementSign = -1
            
        upDownSpeeds = [self.upDown.LiftSpeedSlow, self.upDown.LiftSpeedNormal, self.upDown.LiftSpeedFast]
        self.upDown.moveMotor(position, upDownSpeeds[speed], waitingForStop)
        if not waitingForStop:
            return
        
        curPos = self.upDown.readPosition()
        # Back off a bit and try again if off
        if ((abs(curPos - position) > 100) and (position != 0)):
            self.upDown.moveMotor((curPos + startingPos) / 2, self.upDown.LiftSpeedSlow)
            self.upDown.moveMotor(position, upDownSpeeds[speed])
            curPos = self.upDown.readPosition()
            
        # Quit here if this is bad
        if ((abs(curPos - position) > 150) and (position != 0)):
            self.upDown.moveMotor((curPos - 100 * movementSign), 0.5 * self.upDown.LiftSpeedSlow)
            time.sleep(0.2)
            self.upDown.motorStop()
            errorMessage = 'Unacceptable slop on up/down motor moving from\n'
            errorMessage += str(startingPos) + ' to ' + str(position) + ' at speed ' + str(upDownSpeeds[speed]) + '.\n'
            errorMessage += 'Target position = ' + str(position) + '\n'
            errorMessage += 'Current position = ' + str(curPos) + '\n'
            errorMessage += 'Execution has been paused. Please check machine.'
            self.programHaltedFlag = True
            raise ValueError(errorMessage)
        
    '''
        Move the X and Y Motor
    '''
    def moveMotorXY(self, queue, motorid, moveMotorPos, moveMotorVelocity, waitingForStop=True, stopEnable=0, stopCondition=0):
        # If Settings form and XY Motors tab are active, and Override Home to Top is clicked,
        # then only need to check position of up/down tube (greater than or equal to sample bottom)
        if (self.frmSettingsVisible and  
            self.frmSettingsOptions2Visible and
            self.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY):
            
            up_down_position = self.upDown.readPosition()
            if (abs(up_down_position) > (abs(self.changerX.SampleBottom) + 50)):
                self.upDownMove(queue, self.upDown.SampleTop, 0)
                
            upDownPosition = self.upDown.readPosition()
            if (abs(upDownPosition) >= (abs(self.upDown.SampleBottom) + 50)):
                self.programHaltedFlag = True
                raise ValueError('Tried to move to X,Y motors, but UP/Down Motor is in the way and will not respond to a move motor command.')

        else:
            # Verify that the up/down motor is homed to top
            stop_state = False
            if self.upDown.DCMotorHomeToTop_StopOnTrue:
                stop_state = True
                
            # Home Up/Down motor to top
            self.HomeToTop(queue)
            
            if (self.upDown.checkInternalStatus(4) != stop_state):
                self.programHaltedFlag = True
                raise ValueError('Could not move X,Y motors!  Home to top not complete!')
            
        motorid.moveMotorRelative(moveMotorPos, moveMotorVelocity, waitingForStop, stopEnable, stopCondition)        
        
        return
    
    '''
        Check for timeout
    '''
    def hasMoveToXYLimit_Timedout(self, startTime):
        start_time = startTime
        current_time = time.time()

        if (current_time < (start_time + self.MoveXYMotorsToLimitSwitch_TimeoutSeconds)):
            return False
        else:
            return True
       
    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Move UpDown Motor to the top
    '''
    def HomeToTop(self, queue):        
        # No homing to top if the program has been halted
        if self.checkProgramHaltRequest(queue):
            return
        
        stop_state = False
        if self.upDown.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
        
        # If switch already tripped, do nothing
        if (self.upDown.checkInternalStatus(4) == stop_state):
            current_updown_pos = self.upDown.readPosition()
            # If the current position is larger than 1cm, set the current position as the new Zero Target
            if (abs(current_updown_pos) > (self.upDown.UpDownMotor1cm/10)):
                self.upDown.zeroTargetPos()
            return 
                    
        # If up/down position is greater than the sample bottom, use the normal lift speed
        # otherwise, a sample has just been dropped off on the changer belt
        # and the home to top speed needs to be slower
        speed = self.upDown.LiftSpeedNormal
        if (abs(self.upDown.readPosition()) <= abs(self.upDown.SampleBottom)):
            # ???????????? - Why this particular speed?
            speed = 0.25 * (self.upDown.LiftSpeedNormal + 3 * self.upDown.LiftSpeedSlow)
        
        self.upDown.moveMotor(-2 * self.upDown.MeasPos, speed, True, -1, int(stop_state))
              
        # Check to see if the motor has reached the limit switch      
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            self.upDown.moveMotor(-2 * self.upDown.MeasPos, self.upDown.LiftSpeedSlow, True)

        # Check if the limit switch get hit, set error if not                    
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            queue.put('Error: Homed to top but did not hit switch!')
            
        upDownPos = self.upDown.readPosition()
        self.upDown.zeroTargetPos()
        
        return upDownPos
            
    '''
        Move the XY table to the center
    '''
    def HomeToCenter(self, queue):
        stop_state = False
        if self.upDown.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
        
        # No homing to center if the Up/Down Motor is not homed
        if (self.upDown.checkInternalStatus(4) != stop_state):
            queue.put('Error: Could not home to center!  Home to top not complete!')
            return
        
        self.changerX.motorReset()
        self.changerY.motorReset()
        
        # Wait 1 second for motor power cycle process to finish
        time.sleep(1)
        startTime = time.time()
        
        # Move motor a relative number of motor units, 
        # and stop if signal from the load corner limit switch is logic low
        self.moveMotorXY(queue, self.changerX, self.MotorPositionMoveToLoadCorner, self.changerX.ChangerSpeed, False, -1, 0)
        time.sleep(0.1)
        
        self.moveMotorXY(queue, self.changerY, self.MotorPositionMoveToLoadCorner, self.changerY.ChangerSpeed, False, -2, 0)
        
        # Wait for limit switches or timeout
        xStatus = self.changerX.checkInternalStatus(4)
        yStatus = self.changerY.checkInternalStatus(5) 
        while ((xStatus or yStatus) and
               (not self.checkProgramHaltRequest(queue)) and
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(4)
            yStatus = self.changerY.checkInternalStatus(5) 
        
        # At this point, if not hit the limit switches for XY yet, set error
        xStatus = self.changerX.checkInternalStatus(4)
        yStatus = self.changerY.checkInternalStatus(5) 
        if (xStatus and yStatus):            
            if self.hasMoveToXYLimit_Timedout(startTime):
                errorMessage = 'Error: Home XY Stage, move motors to Load Corner limit switches timed-out after '
                errorMessage += str(self.MoveXYMotorsToLimitSwitch_TimeoutSeconds) + ' seconds'
            else:
                errorMessage = 'Error: Homed XY Stage to center but did not hit load corner limit switch(es)!'
                
            queue.put(errorMessage)
            return
        
        # Reset both X and Y motor controllers
        # This will reset both motor positions to 0 motor encoder counts, but this is okay
        # as the homing process will rezero the motor positions relative to the
        # center X and Y optical limit switches
        self.changerX.motorReset()
        self.changerY.motorReset()
        
        # Wait 1 second for motor power cycle process to finish
        time.sleep(1)
        startTime = time.time()
        
        # Now Move to center limit switches
        # Move motor a relative number of motor units, and stop if signal from the center limit switch is logic low
        self.moveMotorXY(queue, self.changerX, self.MotorPositionMoveToCenter, self.changerX.ChangerSpeed, False, -2, 0)
        time.sleep(0.1)
        self.moveMotorXY(queue, self.changerY, self.MotorPositionMoveToCenter, self.changerY.ChangerSpeed, False, -3, 0)

        # Wait for limit switches or timeout
        xStatus = self.changerX.checkInternalStatus(5)
        yStatus = self.changerY.checkInternalStatus(6) 
        while ((xStatus and yStatus) and
               (not self.checkProgramHaltRequest(queue)) and
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(5)
            yStatus = self.changerY.checkInternalStatus(6) 
            
        xStatus = self.changerX.checkInternalStatus(5)
        yStatus = self.changerY.checkInternalStatus(6) 
        if (xStatus and yStatus):
            if self.hasMoveToXYLimit_Timedout(startTime):
                errorMessage = 'Error: Home XY Stage, move motors to Center limit switches timed-out after '
                errorMessage += str(self.MoveXYMotorsToLimitSwitch_TimeoutSeconds) + ' seconds'
            else:
                errorMessage = 'Error: Homed XY Stage to center but did not hit positive limit switch(es)!'
            
            queue.put(errorMessage)
            return
        
        else:
            self.changerX.zeroTargetPos()
            time.sleep(0.25)
            self.changerY.zeroTargetPos()
            time.sleep(0.25)
            
            xPos = self.changerX.readPosition()
            yPos = self.changerY.readPosition()
            queue.put('Data: xPos: ' + str(xPos))
            queue.put('Data: yPos: ' + str(yPos))
            
        return
        
        
    '''
        
    '''
    def runTask(self, queue, taskID):
        try:
            if (taskID == self.HOME_TO_TOP):
                self.HomeToTop(queue)
                    
            elif (taskID == self.HOME_TO_CENTER):
                self.HomeToCenter(queue)
            
        except ValueError as e:
            queue.put('Error: ' + str(e))
        
        return
            