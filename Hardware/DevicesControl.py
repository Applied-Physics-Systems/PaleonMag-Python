'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os
import time
import configparser
import numpy as np

from Hardware.Device.MotorControl import MotorControl
from Hardware.Device.IrmArmControl import IrmArmControl

from Process.ProcessData import ProcessData
from Process.ModConfig import ModConfig
from Process.ModChanger import ModChanger

class DevicesControl():
    '''
    classdocs
    '''
    MOTOR_HOME_TO_TOP       = 0x0001
    MOTOR_HOME_TO_CENTER    = 0x0002
    MOTOR_MOVE              = 0x0003
    MOTOR_SAMPLE_PICKUP     = 0x0004
    MOTOR_SAMPLE_DROPOFF    = 0x0005
    MOTOR_ZERO_TP           = 0x0006
    MOTOR_POLL              = 0x0007
    MOTOR_CLEAR_POLL        = 0x0008
    MOTOR_RELABEL_POSITION  = 0x0009
    MOTOR_SET_CURRENT_HOLE  = 0x000A
    MOTOR_CHANGE_HOLE       = 0x000B
    MOTOR_GO_TO_X           = 0x000C
    MOTOR_GO_TO_Y           = 0x000D
    MOTOR_SPIN_SAMPLE       = 0x000E
    MOTOR_CHANGE_TURN_ANGLE = 0x000F
    MOTOR_CHANGE_HEIGHT     = 0x0010
    MOTOR_LOAD              = 0x0011
    MOTOR_READ_POSITION     = 0x0012
    MOTOR_READ_ANGLE        = 0x0013
    MOTOR_READ_HOLE         = 0x0014
    MOTOR_RESET             = 0x0015    
    MOTOR_STOP              = 0x0016
    
    IRM_SET_BIAS_FIELD      = 0x1001
    IRM_FIRE                = 0x1002
    
    messages = {MOTOR_HOME_TO_TOP: 'Run HomeToTop\n',
                MOTOR_HOME_TO_CENTER: 'Run HomeToCenter\n',
                MOTOR_MOVE: 'Move Motor To Target Position',
                MOTOR_SAMPLE_PICKUP: 'Sample Pickup',
                MOTOR_SAMPLE_DROPOFF: 'Sample Dropoff',
                MOTOR_ZERO_TP: 'Zero Target Position',
                MOTOR_POLL: 'Poll Motor',
                MOTOR_CLEAR_POLL: 'Clear Poll Motor Status',
                MOTOR_RELABEL_POSITION: 'Relabel Position',
                MOTOR_SET_CURRENT_HOLE: 'Set Current Hole',
                MOTOR_CHANGE_HOLE: 'Change Hole',
                MOTOR_GO_TO_X: 'Go to X',
                MOTOR_GO_TO_Y: 'Go to Y',
                MOTOR_SPIN_SAMPLE: 'Spin Sample',
                MOTOR_CHANGE_TURN_ANGLE: 'Change Turn Angle',
                MOTOR_CHANGE_HEIGHT: 'Change Height',
                MOTOR_LOAD: 'Load',
                MOTOR_READ_POSITION: 'Read Position',
                MOTOR_READ_ANGLE: 'Read Angle', 
                MOTOR_READ_HOLE: 'Read Hole',
                MOTOR_RESET: 'Reset',
                MOTOR_STOP: 'Stop',                
                IRM_FIRE: 'Discharge IRM device'}
    
    MotorPositionMoveToLoadCorner = 900000
    MotorPositionMoveToCenter = -900000
    MoveXYMotorsToLimitSwitch_TimeoutSeconds = 120
        
    modConfig = None
    
    upDown = None
    changerX = None
    changerY = None
    turning = None
    vacuum = None
    apsIRM = None
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
    def setDevicesConfig(self, modConfig):  
        self.modConfig = modConfig
        self.modChanger = ModChanger(self.modConfig)
        message = self.openDevices(modConfig)
        
        return message

    '''
        Open UART serial communication port for motor
    '''
    def openMotorComm(self, device, comPort, label, modConfig):        
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
                device = MotorControl(57600, self.currentPath, comPort, label, modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False
        
        return device, message + '\n'

    '''
        Open UART serial communication port for motor
    '''
    def openIrmArmComm(self, device, comPort, label, modConfig):        
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
                device = IrmArmControl(9600, self.currentPath, comPort, label, modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False

        
        return device, message + '\n'
        
    '''
    '''
    def openDevices(self, modConfig):
        self.devicesAllGoodFlag = True
                
        message = '\n'
        self.deviceList = []
        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortUpDown']        
        self.upDown, respStr = self.openMotorComm(self.upDown, comPort, 'UpDown', modConfig)
        message += respStr
        if (self.upDown != None):
            self.deviceList.append(self.upDown)
        
        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortChanger']
        self.changerX, respStr = self.openMotorComm(self.changerX, comPort, 'ChangerX', modConfig)
        message += respStr
        if (self.changerX != None):
            self.deviceList.append(self.changerX)

        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortChangerY']
        self.changerY, respStr = self.openMotorComm(self.changerY, comPort, 'ChangerY', modConfig)
        message += respStr
        if (self.changerY != None):
            self.deviceList.append(self.changerY)

        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortTurning']
        self.turning, respStr = self.openMotorComm(self.turning, comPort, 'Turning', modConfig)
        message += respStr    
        if (self.turning != None):
            self.deviceList.append(self.turning)

        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortVacuum']
        self.vacuum, respStr = self.openMotorComm(self.vacuum, comPort, 'Vacuum', modConfig)
        message += respStr    
        if (self.vacuum != None):
            self.deviceList.append(self.vacuum)

        comPort = 'COM' + modConfig.processData.config['COMPorts']['COMPortApsIrm']
        self.apsIRM, respStr = self.openIrmArmComm(self.apsIRM, comPort, 'IrmArm', modConfig)
        message += respStr    
        if (self.apsIRM != None):
            self.deviceList.append(self.apsIRM)
        
        return message 

    '''
    '''
    def closeDevice(self, device):
        if (device != None):
            if (device.isOpen()):
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
    def checkProgramHaltRequest(self):
        try:
            if self.programHaltedFlag:
                return True
            else:
                message = self.modConfig.queue.get(timeout=0.1)
                if 'Program_Halted' in message:
                    self.programHaltedFlag = True
                    return True
                
            return False
            
        except:
            return False
   
    '''
    '''
    def getActiveMotor(self, motorStr):
        activeMotor = None
        motorLabel = 'UpDown'
        if 'Changer (X)' in motorStr:
            motorLabel = 'ChangerX'
        elif 'Changer (Y)' in motorStr:
            motorLabel = 'ChangerY'
        elif 'Turning' in motorStr:
            motorLabel = 'Turning'
        elif 'Up/Down' in motorStr:
            motorLabel = 'UpDown'
            
        for device in self.deviceList:
            if motorLabel in device.label:
                activeMotor = device
            
        return activeMotor    
   
    '''
        Update data for process that has been changed 
    '''
    def updateProcessData(self):
        self.modConfig.processData.PortOpen['UpDown'] = self.upDown.modConfig.processData.PortOpen['UpDown']
        self.modConfig.processData.PortOpen['Turning'] = self.turning.modConfig.processData.PortOpen['Turning']
        self.modConfig.processData.PortOpen['ChangerX'] = self.changerX.modConfig.processData.PortOpen['ChangerX']
        self.modConfig.processData.PortOpen['ChangerY'] = self.changerY.modConfig.processData.PortOpen['ChangerY']
                
        return self.modConfig.processData 
   
    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Functions
                        
    --------------------------------------------------------------------------------------------'''  
    '''
    '''
    def upDownHeight(self):
        return self.upDown.GetPosition()
        
    '''
        Move the UpDown motor
    '''
    def upDownMove(self, position, speed, waitingForStop=True):
        if self.checkProgramHaltRequest():
            return
                
        movementSign = 1
        startingPos = self.upDown.readPosition()
        if (position < startingPos):
            movementSign = -1
            
        upDownSpeeds = [self.modConfig.LiftSpeedSlow, self.modConfig.LiftSpeedNormal, self.modConfig.LiftSpeedFast]
        self.upDown.moveMotor(position, upDownSpeeds[speed], waitingForStop)
        if not waitingForStop:
            return
        
        curPos = self.upDown.readPosition()
        # Back off a bit and try again if off
        if ((abs(curPos - position) > 100) and (position != 0)):
            self.upDown.moveMotor((curPos + startingPos) / 2, self.modConfig.LiftSpeedSlow)
            self.upDown.moveMotor(position, upDownSpeeds[speed])
            curPos = self.upDown.readPosition()
            
        # Quit here if this is bad
        if ((abs(curPos - position) > 150) and (position != 0)):
            self.upDown.moveMotor((curPos - 100 * movementSign), 0.5 * self.modConfig.LiftSpeedSlow)
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
    def moveMotorXY(self, motorid, moveMotorPos, moveMotorVelocity, waitingForStop=True, stopEnable=0, stopCondition=0):
        # If Settings form and XY Motors tab are active, and Override Home to Top is clicked,
        # then only need to check position of up/down tube (greater than or equal to sample bottom)
        if (self.modConfig.processData.frmSettingsVisible and  
            self.modConfig.processData.frmSettingsOptions2Visible and
            self.modConfig.processData.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY):
            
            up_down_position = self.upDown.readPosition()
            if (abs(up_down_position) > (abs(self.changerX.SampleBottom) + 50)):
                self.upDownMove(self.upDown.SampleTop, 0)
                
            upDownPosition = self.upDown.readPosition()
            if (abs(upDownPosition) >= (abs(self.modConfig.SampleBottom) + 50)):
                self.programHaltedFlag = True
                raise ValueError('Tried to move to X,Y motors, but UP/Down Motor is in the way and will not respond to a move motor command.')

        else:
            # Verify that the up/down motor is homed to top
            stop_state = False
            if self.modConfig.DCMotorHomeToTop_StopOnTrue:
                stop_state = True
                
            # Home Up/Down motor to top
            self.HomeToTop()
            
            if (self.upDown.checkInternalStatus(4) != stop_state):
                self.programHaltedFlag = True
                raise ValueError('Could not move X,Y motors!  Home to top not complete!')
            
        motorid.moveMotorRelative(moveMotorPos, moveMotorVelocity, waitingForStop, stopEnable, stopCondition)        
        
        return
    
    '''
    '''
    def moveMotorAbsoluteXY(self, motorid, moveMotorPos, MoveMotorVelocity, waitingForStop=True, StopEnable=0, StopCondition=0):
        # Verify that the up/down motor is homed to top
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
            
        # Home up/down motor to top
        self.HomeToTop()
        
        # No homing to center if the Up/Down Motor is not homed
        if (self.upDown.checkInternalStatus(4) != stop_state):
            errorMessage = 'Could not move X,Y motors!  Home to top not complete!'
            raise ValueError(errorMessage)
        
        motorid.pollMotor()
        motorid.clearPollStatus()
        commandStr = '134 ' + str(moveMotorPos) + ' '
        commandStr += ' 483184 ' + str(MoveMotorVelocity) + ' '
        commandStr += str(StopEnable) + ' ' + str(StopCondition)
        motorid.sendMotorCommand(commandStr)
        if waitingForStop:
            motorid.waitForMotorStop()
        
    
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

    '''
    '''
    def convertPosToHole(self, pos):
        FullLoop = (self.modConfig.SlotMax - self.modConfig.SlotMin + 1)
        hole = (pos / self.modConfig.OneStep) % FullLoop
        if (hole <= 0):
            hole = hole + (self.modConfig.SlotMax - self.modConfig.SlotMin + 1)
            
        return hole

    '''
    '''
    def convertPosToHoleXY(self, posX, posY):
        holeXY = -1
        for i in range(1, 101):
            testX = abs(posX - self.modConfig.XYTablePositions(i, 0))
            testXb = (testX < 1000)
            
            testY = abs(posY - self.modConfig.XYTablePositions(i, 1))
            testYb = (testY < 1000)
            
            if (testXb and testYb):
                holeXY = i
                break
            
        if (holeXY == -1):
            holeXY = self.modConfig.SlotMin
            
        return holeXY

    '''
    '''
    def convertPosToAngle(self, pos):
        angle = (pos / (-1 * self.modConfig.TurningMotorFullRotation)) * 360
        
        return angle 

    '''
    '''
    def convertAngleToPos(self, angle):
        pos = int(-1 * self.modConfig.TurningMotorFullRotation * angle / 360)
        
        return pos

    '''
    '''
    def changerHole(self):
        if not self.modConfig.UseXYTableAPS:
            # Chain Drive
            curPos = self.changerX.readPosition()
            curHole = self.convertPosToHole(curPos)
            
        else:
            # We are using an XY Table
            curPosX = self.changerX.readPosition()
            curPosY = self.changerY.readPosition()
            curHole = self.ConvertPosToHoleXY(curPosX, curPosY)
            
        return curHole 
       
    '''
    '''
    def convertHoleToPos(self, hole):
        fullLoop = abs((self.modConfig.SlotMax - self.modConfig.SlotMin + 1) * self.modConfig.OneStep)
        currentPos = self.changerX.readPosition()
        self.changerHole()
        targetHole = hole
        targetHolePosRaw = self.modConfig.OneStep * hole
        stepsToGo = (targetHolePosRaw - currentPos) % fullLoop
        
        if (abs(stepsToGo) > (fullLoop / 2)):
            if (stepsToGo > 0):
                stepsToGo = stepsToGo - fullLoop
            else:
                stepsToGo = stepsToGo + fullLoop
                
        if not self.modChanger.isHole(targetHole):
            if (stepsToGo > 0):
                stepsToGo = stepsToGo + self.modConfig.SampleHoleAlignmentOffset * self.modConfig.OneStep
            else:
                stepsToGo = stepsToGo + self.modConfig.SampleHoleAlignmentOffset * self.modConfig.OneStep
                
        holePos = int(stepsToGo + currentPos)
                
        return holePos
                
    '''
    '''
    def MotorXYTable_CenterReset(self):
        xPos, yPos = self.HomeToCenter()
        self.modConfig.updateXYTablePositions(0, 0, xPos)
        self.modConfig.updateXYTablePositions(0, 1, yPos)
                
    '''
        To enable the Quicksilver motors to return to the home position, center of the XY Table
        correctly.  Both X and Y axis must find the center of the table and stop there correctly
        (Stop Condition = if logic bit #1 becomes true, stop all motion on Up/Down motor;
        When the home position limit switch is pressed, logic bit #1 changes from false to true.)

        Note: untested.  Requires planning of limit switches to fix code and verify code works properly    
    '''
    def MoveToCorner(self):
        self.HomeToTop()
        
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = 1
        
        # No homing to center if the Up/Down Motor is not homed
        if (self.upDown.checkInternalStatus(4) != stop_state):
            errorMessage = "Could not move to corner!  Home to top not complete!"
            raise ValueError(errorMessage)
                
        start_time = time.time()
    
        self.changerX.moveMotorXY(self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -1, 0)
        self.changerY.MoveMotorXY(self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -2, 0)
       
        # Move to load corner
        while ((self.changerX.checkInternalStatus(4) != False) or (self.changerY.checkInternalStatus(5) != False)):                 
            time.sleep(0.1)        
        
        if not ((self.changerX.checkInternalStatus( 4) == False) and (self.changerY.checkInternalStatus(5) == False)):
            if (self.HasMoveToXYLimit_Timedout(start_time)):            
                # Home to center has timed out
                errorMessage =  "Move XY Stage to Load Corner timed-out after: " 
                errorMessage += str(self.MoveXYMotorsToLimitSwitch_TimeoutSeconds) + "seconds."                              
            else:
                errorMessage = "Moved XY Stage to Load Corner but did not hit load corner limit switch(es)!"           
            raise ValueError(errorMessage)
            
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Move UpDown Motor to the top
    '''
    def HomeToTop(self):        
        # No homing to top if the program has been halted
        if self.checkProgramHaltRequest():
            return
        
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
        
        # If switch already tripped, do nothing
        if (self.upDown.checkInternalStatus(4) == stop_state):
            current_updown_pos = self.upDown.readPosition()
            # If the current position is larger than 1cm, set the current position as the new Zero Target
            if (abs(current_updown_pos) > (self.modConfig.UpDownMotor1cm/10)):
                self.upDown.zeroTargetPos()
            return 
                    
        # If up/down position is greater than the sample bottom, use the normal lift speed
        # otherwise, a sample has just been dropped off on the changer belt
        # and the home to top speed needs to be slower
        speed = self.modConfig.LiftSpeedNormal
        if (abs(self.upDown.readPosition()) <= abs(self.modConfig.SampleBottom)):
            # ???????????? - Why this particular speed?
            speed = 0.25 * (self.modConfig.LiftSpeedNormal + 3 * self.modConfig.LiftSpeedSlow)
        
        self.upDown.moveMotor(-2 * self.modConfig.MeasPos, speed, True, -1, int(stop_state))
              
        # Check to see if the motor has reached the limit switch      
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            self.upDown.moveMotor(-2 * self.modConfig.MeasPos, self.modConfig.LiftSpeedSlow, True)

        # Check if the limit switch get hit, set error if not                    
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            raise ValueError('Homed to top but did not hit switch!')
            
        upDownPos = self.upDown.readPosition()
        self.upDown.zeroTargetPos()
        
        return upDownPos
            
    '''
        Move the XY table to the center
    '''
    def HomeToCenter(self):
        xPos = 0 
        yPos = 0
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
            
        # No homing to center if the Up/Down Motor is not homed
        if (self.upDown.checkInternalStatus(4) != stop_state):
            raise ValueError('Could not home to center!  Home to top not complete!')
        
        self.changerX.motorReset()
        self.changerY.motorReset()
        
        # Wait 1 second for motor power cycle process to finish
        time.sleep(1)
        startTime = time.time()
        
        # Move motor a relative number of motor units, 
        # and stop if signal from the load corner limit switch is logic low
        self.moveMotorXY(self.changerX, self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -1, 0)
        time.sleep(0.1)
        
        self.moveMotorXY(self.changerY, self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -2, 0)
        
        # Wait for limit switches or timeout
        xStatus = self.changerX.checkInternalStatus(4)
        yStatus = self.changerY.checkInternalStatus(5) 
        while ((xStatus or yStatus) and
               (not self.checkProgramHaltRequest()) and
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(4)
            yStatus = self.changerY.checkInternalStatus(5) 
        
        # At this point, if not hit the limit switches for XY yet, set error
        xStatus = self.changerX.checkInternalStatus(4)
        yStatus = self.changerY.checkInternalStatus(5) 
        if (xStatus and yStatus):            
            if self.hasMoveToXYLimit_Timedout(startTime):
                errorMessage = 'Home XY Stage, move motors to Load Corner limit switches timed-out after '
                errorMessage += str(self.MoveXYMotorsToLimitSwitch_TimeoutSeconds) + ' seconds'
            else:
                errorMessage = 'Homed XY Stage to center but did not hit load corner limit switch(es)!'
                
            raise ValueError(errorMessage)
        
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
        self.moveMotorXY(self.changerX, self.MotorPositionMoveToCenter, self.modConfig.ChangerSpeed, False, -2, 0)
        time.sleep(0.1)
        self.moveMotorXY(self.changerY, self.MotorPositionMoveToCenter, self.modConfig.ChangerSpeed, False, -3, 0)

        # Wait for limit switches or timeout
        xStatus = self.changerX.checkInternalStatus(5)
        yStatus = self.changerY.checkInternalStatus(6) 
        while ((xStatus and yStatus) and
               (not self.checkProgramHaltRequest()) and
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(5)
            yStatus = self.changerY.checkInternalStatus(6) 
            
        xStatus = self.changerX.checkInternalStatus(5)
        yStatus = self.changerY.checkInternalStatus(6) 
        if (xStatus and yStatus):
            if self.hasMoveToXYLimit_Timedout(startTime):
                errorMessage = 'Home XY Stage, move motors to Center limit switches timed-out after '
                errorMessage += str(self.MoveXYMotorsToLimitSwitch_TimeoutSeconds) + ' seconds'
            else:
                errorMessage = 'Homed XY Stage to center but did not hit positive limit switch(es)!'
            
            raise ValueError(errorMessage)
        
        else:
            self.changerX.zeroTargetPos()
            time.sleep(0.25)
            self.changerY.zeroTargetPos()
            time.sleep(0.25)
            
            xPos = self.changerX.readPosition()
            yPos = self.changerY.readPosition()
            self.modConfig.queue.put('Data: xPos: ' + str(xPos))
            self.modConfig.queue.put('Data: yPos: ' + str(yPos))
            
            self.modConfig.HasXYTableBeenHomed = True
            
        return xPos, yPos 

    '''
    '''
    def DoSamplePickup(self):
        self.upDown.setTorque(self.modConfig.PickupTorqueThrottle * self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.PickupTorqueThrottle * self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.PickupTorqueThrottle * self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.PickupTorqueThrottle * self.modConfig.UpDownTorqueFactor)
        self.upDown.moveMotor(self.modConfig.SampleBottom, self.modConfig.LiftSpeedSlow)
        currentPos = self.upDownHeight()
        
        self.upDown.zeroTargetPos()
        
        self.upDown.relabelPos(currentPos)
        self.upDown.setTorque(self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.UpDownTorqueFactor, 
                              self.modConfig.UpDownTorqueFactor)
        
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
            
        if (self.upDown.checkInternalStatus(4) == stop_state):
            errorMessage = 'Quartz tube at sample top but homing switch still set. Check for switch failure.'
            raise ValueError(errorMessage)
        
    '''
    '''
    def DoSampleDropoff(self, SampleHeight):
        self.upDown.pollMotor()
        self.upDown.clearPollStatus()
        
        if self.modConfig.UseXYTableAPS:
            self.upDown.moveMotor(self.modConfig.SampleBottom + (SampleHeight - 0.1 * SampleHeight), self.modConfig.LiftSpeedSlow, True)
        else:
            self.upDown.moveMotor(self.modConfig.SampleBottom + 1.1 * SampleHeight, self.modConfig.LiftSpeedSlow, True)

        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
            
        if (self.upDown.checkInternalStatus(4) == stop_state):
            errorMessage = 'Dropped off sample, but homing switch still set. Check for switch failure.'
            raise ValueError(errorMessage)
        
    '''
    '''
    def setChangerHole(self, hole):
        if (self.modChanger.isValidStart(hole)):
            if not self.modConfig.UseXYTableAPS:
                self.changerX.relabelPos(self.convertHoleToPos(hole))
            else:
                self.changerX.relabelPos(self.modConfig.convertHoletoPosX(hole))
                self.changerY.relabelPos(self.modConfig.convertHoletoPosY(hole))
                
            self.changerHole()
            
        return
        
    '''
    '''
    def changerMotortoHole(self, hole, waitingForStop=True):
        # Let's get the sample rod out of the way if necessary
        if (abs(self.upDownHeight()) > abs(self.modConfig.SampleBottom) * 0.1): 
            self.HomeToTop()
        
        if not self.modConfig.UseXYTableAPS:
            # This is the routine to use a Chain Drive System
            fullLoop = (self.modConfig.SlotMax - self.modConfig.SlotMin + 1) * self.modConfig.OneStep
            startingPos = self.changerX.readPosition()
            curpos = startingPos
            
            if (int(curpos/fullLoop) != 0): 
                self.changerX.relabelPos(curpos % fullLoop)
            startinghole = self.changerHole()
            target = self.convertHoletoPos(hole)
            self.changerX.moveMotor(target, self.modConfig.ChangerSpeed, waitingForStop)
            
            if not waitingForStop: 
                return
            curpos = self.changerX.readPosition()
            
            if (int(curpos/fullLoop) != 0): 
                self.changerX.relabelPos(curpos % fullLoop)
            
            curhole = self.changerHole()
            self.modConfig.queue.put('Data: curHole: ' + str(curhole))
            
            # Because OneStep is negative, the criteria was never reach (always <0 and not >0.02) till the asolute value (May 2007 L Carporzen)
            if ((abs(curpos - target) / abs(self.modConfig.OneStep)) > 0.02):
                # First try to move to move back to the desired position
                self.changerX.moveMotor(target, 0.5 * self.modConfig.ChangerSpeed)
                curpos = self.changerX.readPosition()
            
            # Quit if fail here, backing off a bit first ...
            if ((abs(curpos - target) / abs(self.modConfig.OneStep)) > 0.02):
                self.changerX.moveMotor((curpos - (curpos - startingPos) * 0.1), 0.1 * self.modConfig.ChangerSpeed)
                time.sleep(0.2)
                errorMessage = "Unacceptable slop moving changer\n"
                errorMessage += "from hole " + str(startinghole) + " to hole " + str(hole) + ".\n\n"
                errorMessage += "Target position: " + str(target) + "\n"
                errorMessage += "Current position: " + str(curpos) + "\n\n"
                errorMessage += "Execution has been paused. Please check machine."
                raise ValueError(errorMessage)
        else:
            # We Are using the XY Table
            if not self.modConfig.processData.HasXYTableBeenHomed:           
                self.MotorXYTable_CenterReset()
            
            startingPosX = self.changerX.readPosition()
            startingPosY = self.changerY.readPosition()
            curposX = startingPosX
            curposY = startingPosY
            
            startinghole = self.changerHole()
            targetX = self.modConfig.convertHoletoPosX(hole)
            targetY = self.modConfig.convertHoletoPosY(hole)
            
            # Then Move Directly To the position, always approaching from the corner
            self.changerX.moveMotorAbsoluteXY(targetX, self.modConfig.ChangerSpeed, False)
            self.changerY.moveMotorAbsoluteXY(targetY, self.modConfig.ChangerSpeed, waitingForStop)
            
            if not waitingForStop:
                return
            curposX = self.changerX.readPosition()
            curposY = self.changerY.readPosition()
            
            curhole = self.changerHole()
            self.modConfig.queue.put('Data: curHole: ' + str(curhole))
            
            # Because OneStep is negative, the criteria was never reach (always <0 and not >0.02) till the asolute value (May 2007 L Carporzen)
            if (((abs(curposX - targetX) / abs(self.modConfig.OneStep)) > 0.02) or ((abs(curposY - targetY) / abs(self.modConfig.OneStep)) > 0.02)):
                # First try to move to move back to the desired position
                self.changerX.moveMotorAbsoluteXY(targetX, 0.5 * self.modConfig.ChangerSpeed)
                self.changerY.moveMotorAbsoluteXY(targetY, 0.5 * self.modConfig.ChangerSpeed)
                curposX = self.changerX.readPosition()
                curposY = self.changerY.readPosition()

            #  Quit if fail here, backing off a bit first ...
            if (((abs(curpos - target) / abs(self.modConfig.OneStep)) > 0.02) or ((abs(curpos - target) / abs(self.modConfig.OneStep)) > 0.02)):
                self.changerX.moveMotorAbsoluteXY((curposX - (curposX - startingPosX) * 0.1), 0.1 * self.modConfig.ChangerSpeed)
                self.changerY.moveMotorAbsoluteXY((curposY - (curposY - startingPosY) * 0.1), 0.1 * self.modConfig.ChangerSpeed)
                time.sleep(0.2)
                errorMessage = "Unacceptable slop moving changer\n"
                errorMessage += "from hole " + str(startinghole) + " to hole " + str(hole) + ".\n\n"
                errorMessage += "Target position X: " + str(targetX) + '\n'
                errorMessage += "Current position X: " + str(curposX) + '\n\n'
                errorMessage += "Target position Y: " + str(targetY) + '\n'
                errorMessage += "Current position Y: " + str(curposY) + '\n\n'
                errorMessage += "Execution has been paused. Please check machine."
                raise ValueError(errorMessage)

    '''
    '''
    def turningMotorAngle(self):
        angle = self.convertPosToAngle(self.turning.readPosition())
        self.modConfig.queue.put('Data: TurningAngle: ' + str(angle))
        
        return angle 
           
    '''
    '''
    def setTurningMotorAngle(self, angle):
        # Get the sign of the turning motor full rotation setting
        turnSign = np.sign(self.modConfig.TurningMotorFullRotation)
        
        # Get the current motor position
        pos = self.turning.readPosition()
        
        # If the motor position is less than zero and TurningMotorFullRotation is positive
        # OR, if the motor position is greater than zero and TurningMotorFullRotation is negative
        # Then add TurningMotorFullRotation to pos until pos is within 5% of +/- TurningMotorFullRotation
        if ((pos < 0) and (turnSign == 1)):
            # If TurningMotorFullRotation > 0, then pos is increasing in value to more than
            # -0.95 * TurningMotorFullRotation.
            while (pos <= (-1*self.modConfig.TurningMotorFullRotation * 0.95)):
                pos = pos + self.modConfig.TurningMotorFullRotation
                
        elif ((pos > 0) and (turnSign == -1)):
            # If TurningMotorFullRotation < 0, then pos is decreasing in value to less than
            # -0.05 * TurningMotorFullRotation.
            while (pos >= (-1*self.modConfig.TurningMotorFullRotation * 0.05)):
                pos = pos + self.modConfig.TurningMotorFullRotation
           
        elif ((pos < 0) and (turnSign == -1)):
            # If TurningMotorFullRotation < 0, then pos is increasing in value to more than
            # '0.95 * TurningMotorFullRotation.
            while (pos <= (self.modConfig.TurningMotorFullRotation * 0.95)):
                pos = pos - self.modConfig.TurningMotorFullRotation
            
        elif (abs(pos) < abs(self.modConfig.TurningMotorFullRotation * 0.05)):
            # Do nothing
            # This is the close enough
            pass
        else:
            # If TurningMotorFullRotation > 0, then pos is decreasing in value to less than
            # '0.95 * Abs(TurningMotorFullRotation).
            while (pos >= abs(self.modConfig.TurningMotorFullRotation * 0.05)):
                pos = pos - abs(self.modConfig.TurningMotorFullRotation)
        
        self.turning.relabelPos(pos)
        self.modConfig.queue.put('Data: TurningAngle: ' + str(self.convertPosToAngle(pos)))
        # If TurningMotorAngle != angle Then RelabelPos MotorTurning, pos
        # TurningAngleBox = angle
     
    '''
    '''
    def turningMotorRotate(self, angle, waitingForStop=True):
        startingPos = self.turning.readPosition()
        startingangle = self.turningMotorAngle()
        
        target = self.convertAngleToPos(angle)
        self.turning.moveMotor(target, self.modConfig.TurnerSpeed, waitingForStop)
        if not waitingForStop:
            return
        
        CurAngle = self.turningMotorAngle()
        if (abs((CurAngle - angle) % 360) > 3):
            # First try to move to move back to the desired position
            # MoveMotor MotorTurning, startingPos, TurnerSpeed, pauseOverride:=True
            # curpos = ReadPosition(MotorTurning)            
            self.turning.moveMotor(target, self.modConfig.TurnerSpeed)
            CurAngle = self.turningMotorAngle()
        
        # Quit here if this is bad ...
        if (abs((CurAngle - angle) % 360) > 3):
            curpos = self.turning.readPosition()
            # Here start the lines which could be remove for rockmag measurements:
            self.turning.moveMotor((curpos - (curpos - startingPos) * 0.1), 0.1 * self.modConfig.TurnerSpeed)
            time.sleep(0.2)     # Can be remove to don't wait
            
            errorMessage = "Unacceptable slop on turning motor from\n"
            errorMessage += str(startingangle) + "degrees to " + str(angle) + " degrees.\n\n" 
            errorMessage += "Target position: " + str(target) + "\n"
            errorMessage += "Current position: " + str(curpos) + "\n\n"
            errorMessage += "Execution has been paused. Please check machine."
            raise ValueError(errorMessage)
        
        CurAngle = self.turningMotorAngle()
        
        CurAngle = CurAngle - int(CurAngle / 360) * 360     # Integer division
        if (CurAngle != self.turningMotorAngle()): 
            self.setTurningMotorAngle(CurAngle)                
    
    '''
    '''
    def turningMotorSpin(self, speedRPS, Duration=60):
        if (speedRPS == 0):
            self.turning.motorStop()
            activeAngle = self.turningMotorAngle()
            CurAngle = activeAngle - int(activeAngle / 360) * 360
            if (CurAngle != activeAngle): 
                self.setTurningMotorAngle(CurAngle)
                
            activeAngle = self.turningMotorAngle()
            if (CurAngle != activeAngle): 
                self.setTurningMotorAngle(CurAngle)
                
            if (abs(CurAngle) > 10):
                target = 360
            else:
                target = 0
            
            self.turningMotorRotate(target)
            self.turning.waitForMotorStop()
            self.setTurningMotorAngle(0)
            CurAngle = self.turningMotorAngle()
        else:
            startingPos = self.turing.readPosition()
            startingangle = self.turningMotorAngle()
            target = startingPos - self.modConfig.TurningMotorFullRotation * speedRPS * Duration
            self.turning.moveMotor(target, abs(self.modConfig.TurningMotor1rps * speedRPS), False)
        
    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Control Functions
                        
    --------------------------------------------------------------------------------------------'''   
    '''
    '''
    def FireAPS_AtCalibratedTarget(self, target):
        if (target == 0):
            # Discharging IRM device
            self.apsIRM.SendZeroCommand_ToApsIRMDevice_AndWaitForReply()
            time.sleep(1)
            return
        
        else:
            self.apsIRM.SetApsIrmPolarity_FromTargetValue(target)
            level_in_positive_gauss = int(abs(target))
            self.apsIRM.SetApsIrmRange_FromGaussLevel(level_in_positive_gauss)
            
            # Check if level is in range
            if (level_in_positive_gauss > self.modConfig.PulseAxialMax):
                warningMessage = 'Warning: Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is above the currently set value for the Maximum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMax) + ' ' + self.modConfig.AFUnits
                self.queue.put(warningMessage)
                return 
            
            elif (level_in_positive_gauss < self.modConfig.PulseAxialMin):
                warningMessage = 'Warning: Target IRM Peak Field (' + str(level_in_positive_gauss) + ' '
                warningMessage += self.modConfig.AFUnits + ') is below the currently set value for the Minimum IRM Peak Field ('
                warningMessage += str(self.modConfig.PulseAxialMax) + ' ' + self.modConfig.AFUnits
                self.queue.put(warningMessage)
                return
                
            target_level = str(level_in_positive_gauss)
            
            # Catch Flow Pause or Flow Halt
            if (self.checkProgramHaltRequest()):
                return

            # Set IRM Field Level
            self.apsIRM.SetApsIrmLevel(target_level)

            # Catch Flow Pause or Flow Halt
            if (self.checkProgramHaltRequest()):
                return

            # Tell APS IRM to execute pulse
            self.apsIRM.executeApsIrmPulse()
            
            # Wait for Done signal
            while True:
                my_local_response = self.apsIRM.GetApsIrmResponse(self.apsIRM.APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                if  self.apsIRM.APS_DONE_STRING in my_local_response:
                    return
                
                # Catch Flow Pause or Flow Halt
                if (self.checkProgramHaltRequest()):
                    return
                
                # Send warning message
                warningMessage = 'Warning: Over ' + str(self.apsIRM.APS_GET_RESPONSE_SERIAL_COMM_TIMEOUT_IN_SECONDS)
                warningMessage += ' seconds have elapsed since the IRM Fire Command was sent '
                warningMessage += 'for an IRM Pulse at ' + target_level + ' ' + self.modConfig.AFUnits + ' and '
                warningMessage += ' no ' + self.apsIRM.APS_DONE_STRING + ' response has been received from the APS IRM Device.'
                self.queue.put(warningMessage)                            
            
    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def FireIRM(self, voltage, CalibrationMode=False):
        if 'ASC' in self.modConfig.IRMSystem:
            print('TODO: Implement FireASC_IrmAtPulseVolts voltage, CalibrationMode')
        else:
            self.FireAPS_AtCalibratedTarget(voltage)
        

    '''--------------------------------------------------------------------------------------------
                        
                        Main Task Handler
                        
    --------------------------------------------------------------------------------------------'''
    '''
        
    '''
    def runTask(self, queue, taskID):
        self.queue = queue
        try:
            if (taskID[0] == self.MOTOR_HOME_TO_TOP):
                self.HomeToTop()
                    
            elif (taskID[0] == self.MOTOR_HOME_TO_CENTER):
                _, _ = self.HomeToCenter()

            elif (taskID[0] == self.MOTOR_MOVE):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)
                if (activeMotor != None):
                    targetPos = taskID[1][1]
                    velocity = taskID[1][2]
                    activeMotor.moveMotor(targetPos, velocity)
            
            elif (taskID[0] == self.MOTOR_SAMPLE_PICKUP):
                self.DoSamplePickup()

            elif (taskID[0] == self.MOTOR_SAMPLE_DROPOFF):
                SampleHeight = taskID[1][0] 
                self.DoSampleDropoff(SampleHeight)
                
            elif (taskID[0] == self.MOTOR_ZERO_TP):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.zeroTargetPos()

            elif (taskID[0] == self.MOTOR_POLL):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.pollMotor()

            elif (taskID[0] == self.MOTOR_CLEAR_POLL):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.clearPollStatus()

            elif (taskID[0] == self.MOTOR_RELABEL_POSITION):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)                
                targetPosition = taskID[1][1]
                if (activeMotor != None):
                    activeMotor.relabelPos(targetPosition)

            elif (taskID[0] == self.MOTOR_SET_CURRENT_HOLE):
                currentHole = taskID[1][0]
                self.setChangerHole(currentHole)

            elif (taskID[0] == self.MOTOR_CHANGE_HOLE):
                currentHole = taskID[1][0]
                self.changerMotortoHole(currentHole)
            
            elif (taskID[0] == self.MOTOR_GO_TO_X):
                moveMotorPos = taskID[1][0]
                if not self.modConfig.modConfig.HasXYTableBeenHomed:
                    self.HomeToTop()                    # MotorUPDN_TopReset
                    self.MotorXYTable_CenterReset()
                    
                self.moveMotorXY(self.changerX, moveMotorPos, self.modConfig.ChangerSpeed, False)

            elif (taskID[0] == self.MOTOR_GO_TO_Y):
                moveMotorPos = taskID[1][0]
                if not self.modConfig.modConfig.HasXYTableBeenHomed:
                    self.HomeToTop()                    # MotorUPDN_TopReset
                    self.MotorXYTable_CenterReset()
                    
                self.moveMotorAbsoluteXY(self.changerY, moveMotorPos, self.modConfig.ChangerSpeed, False)

            elif (taskID[0] == self.MOTOR_SPIN_SAMPLE):
                spinRPS = taskID[1][0]
                self.turningMotorSpin(spinRPS)

            elif (taskID[0] == self.MOTOR_CHANGE_TURN_ANGLE):
                angle = taskID[1][0]
                self.turningMotorRotate(angle)

            elif (taskID[0] == self.MOTOR_CHANGE_HEIGHT):
                height = taskID[1][0]
                self.upDownMove(height, 0)
                
            elif (taskID[0] == self.MOTOR_LOAD):
                self.MoveToCorner()

            elif (taskID[0] == self.MOTOR_READ_POSITION):
                motorStr = taskID[1][0]
                activeMotor = self.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.readPosition()

            elif (taskID[0] == self.MOTOR_READ_ANGLE):
                self.turningMotorAngle()

            elif (taskID[0] == self.MOTOR_READ_HOLE):
                self.changerHole()

            elif (taskID[0] == self.MOTOR_RESET):
                self.turning.motorReset()
                self.upDown.motorReset()
                self.changerX.motorReset()
                self.changerY.motorReset()

            elif (taskID[0] == self.MOTOR_STOP):
                self.turning.motorStop()
                self.upDown.motorStop()
                self.changerX.motorStop()
                self.changerY.motorStop()
            
            elif (taskID[0] == self.IRM_FIRE):
                voltage = taskID[1][0] 
                self.FireIRM(voltage)
            
        except ValueError as e:
            self.modConfig.queue.put('Error: ' + str(e))
        
        return

#===================================================================================================
# Test Queue
#---------------------------------------------------------------------------------------------------
class Queue():
    def __init__(self):
        print('Test Queue')
        
    '''
    '''
    def put(self, message):
        print(message)

    '''
    '''
    def get(self):
        return 'Test'
                
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        devControl = DevicesControl()
        queue = Queue()

        config = configparser.ConfigParser()
        config.read('C:\\Temp\\PaleonMag\\Settings\\Paleomag_v3_Hung.INI')
        processData = ProcessData()
        processData.config = config 

        modConfig = ModConfig(process=processData, queue=queue)
        devControl.setDevicesConfig(modConfig)
                
        devControl.runTask(queue, [devControl.MOTOR_HOME_TO_TOP, [None]])
        processData = devControl.updateProcessData()
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
                    