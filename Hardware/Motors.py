'''
Created on Feb 11, 2025

@author: hd.nguyen
'''
import os
import time
import configparser
import numpy as np

from Hardware.Device.MotorControl import MotorControl
from Modules.modConfig import ModConfig

class Motors():
    '''
    classdocs
    '''
    MotorPositionMoveToLoadCorner = 900000
    MotorPositionMoveToCenter = -900000
    MoveXYMotorsToLimitSwitch_TimeoutSeconds = 120
    
    upDown = None
    changerX = None
    changerY = None
    turning = None

    currentPath = ''
    modConfig = None
    parent = None

    def __init__(self, path, parent=None, modConfig=None):
        '''
        Constructor
        '''
        self.currentPath = path
        self.modConfig = modConfig
        self.parent = parent
        
    '''--------------------------------------------------------------------------------------------
                        
                        Initialize Functions
                        
    --------------------------------------------------------------------------------------------'''          
    '''
        Open UART serial communication port for motor
    '''
    def openMotorComm(self, device, label, portLabel):    
        comPort = 'COM' + self.modConfig.processData.config['COMPorts'][portLabel]                    
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
                device = MotorControl(57600, self.currentPath, comPort, label, self.modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False
                
        return device, message + '\n'
        
    '''
    '''
    def openMotors(self):
        deviceList = []
        message = ''
        
        self.upDown, respStr = self.openMotorComm(self.upDown, 'UpDown', 'COMPortUpDown')
        message += respStr
        if (self.upDown != None):
            deviceList.append(self.upDown)
        
        self.changerX, respStr = self.openMotorComm(self.changerX, 'ChangerX', 'COMPortChanger')
        message += respStr
        if (self.changerX != None):
            deviceList.append(self.changerX)

        self.changerY, respStr = self.openMotorComm(self.changerY, 'ChangerY', 'COMPortChangerY')
        message += respStr
        if (self.changerY != None):
            deviceList.append(self.changerY)

        self.turning, respStr = self.openMotorComm(self.turning, 'Turning', 'COMPortTurning')
        message += respStr    
        if (self.turning != None):
            deviceList.append(self.turning)
            
        return deviceList, message 
        
    '''
    '''
    def reset(self):
        self.turning.motorReset()
        self.upDown.motorReset()
        self.changerX.motorReset()
        self.changerY.motorReset()
        return

    '''
    '''
    def stop(self):
        self.turning.motorStop()
        self.upDown.motorStop()
        self.changerX.motorStop()
        self.changerY.motorStop()
        return
    
    '''--------------------------------------------------------------------------------------------
                        
                        processing Functions
                        
    --------------------------------------------------------------------------------------------'''          
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
            
        for device in self.parent.deviceList:
            if motorLabel in device.label:
                activeMotor = device
            
        return activeMotor    
        
    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Functions
                        
    --------------------------------------------------------------------------------------------'''  
    '''
    '''
    def upDownHeight(self):
        return self.upDown.readPosition()
        
    '''
        Move the UpDown motor
    '''
    def upDownMove(self, position, speed, waitingForStop=True):
        if (self.parent != None): 
            self.parent.checkProgramHaltRequest()
                
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
            curHole = self.convertPosToHoleXY(curPosX, curPosY)
            
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
                
        if not self.parent.modChanger.isHole(targetHole):
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
        return
                
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
    
        self.moveMotorXY(self.changerX, self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -1, 0)
        self.moveMotorXY(self.changerY, self.MotorPositionMoveToLoadCorner, self.modConfig.ChangerSpeed, False, -2, 0)
       
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
    
    '''
    '''
    def disconnectMotor(self, motorID):
        motorID.PortOpen = False
        motorID.clearUartBuffer()
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Move UpDown Motor to the top
        
        Move the UpDown motor to MeasPos, then wait until it cannot move any more.
    '''
    def HomeToTop(self):        
        # No homing to top if the program has been halted
        if (self.parent != None):
            self.parent.checkProgramHaltRequest()
        
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
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(4)
            yStatus = self.changerY.checkInternalStatus(5)
            if (self.parent != None):
                self.parent.checkProgramHaltRequest()
                        
        # At this point, if not hit the limit switches for XY yet, set error
        xStatus = self.changerX.checkInternalStatus(4)
        yStatus = self.changerY.checkInternalStatus(5) 
        if not ((xStatus == False) and (yStatus == False)):            
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
        while ((xStatus or yStatus) and
               (not self.hasMoveToXYLimit_Timedout(startTime))):
            time.sleep(0.1)
            xStatus = self.changerX.checkInternalStatus(5)
            yStatus = self.changerY.checkInternalStatus(6) 
            if (self.parent != None):
                self.parent.checkProgramHaltRequest()
        
        xStatus = self.changerX.checkInternalStatus(5)
        yStatus = self.changerY.checkInternalStatus(6)
        if not ((xStatus == False) and (yStatus == False)):
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
            
            self.modConfig.processData.HasXYTableBeenHomed = True
            
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
        
        return
        
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
        if (self.parent.modChanger.isValidStart(hole)):
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
            target = self.convertHoleToPos(hole)
            self.changerX.moveMotor(target, self.modConfig.ChangerSpeed, waitingForStop)
            
            if not waitingForStop: 
                return
            curpos = self.changerX.readPosition()
            
            if (int(curpos/fullLoop) != 0): 
                self.changerX.relabelPos(curpos % fullLoop)
            
            curhole = self.changerHole()
            self.modConfig.queue.put('MotorControl:Data: curHole: ' + str(curhole))
            
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
            self.moveMotorAbsoluteXY(self.changerX, targetX, self.modConfig.ChangerSpeed, False)
            self.moveMotorAbsoluteXY(self.changerY, targetY, self.modConfig.ChangerSpeed, waitingForStop)
            
            if not waitingForStop:
                return
            curposX = self.changerX.readPosition()
            curposY = self.changerY.readPosition()
            
            curhole = self.changerHole()
            self.modConfig.queue.put('MotorControl:Data: curHole: ' + str(curhole))
            
            # Because OneStep is negative, the criteria was never reach (always <0 and not >0.02) till the asolute value (May 2007 L Carporzen)
            if (((abs(curposX - targetX) / abs(self.modConfig.OneStep)) > 0.02) or ((abs(curposY - targetY) / abs(self.modConfig.OneStep)) > 0.02)):
                # First try to move to move back to the desired position
                self.moveMotorAbsoluteXY(self.changerX, targetX, 0.5 * self.modConfig.ChangerSpeed)
                self.moveMotorAbsoluteXY(self.changerY, targetY, 0.5 * self.modConfig.ChangerSpeed)
                curposX = self.changerX.readPosition()
                curposY = self.changerY.readPosition()

            #  Quit if fail here, backing off a bit first ...
            if (((abs(curposX - targetX) / abs(self.modConfig.OneStep)) > 0.02) or ((abs(curposY - targetY) / abs(self.modConfig.OneStep)) > 0.02)):
                self.moveMotorAbsoluteXY(self.changerX, (curposX - (curposX - startingPosX) * 0.1), 0.1 * self.modConfig.ChangerSpeed)
                self.moveMotorAbsoluteXY(self.changerY, (curposY - (curposY - startingPosY) * 0.1), 0.1 * self.modConfig.ChangerSpeed)
                time.sleep(0.2)
                errorMessage = "Unacceptable slop moving changer\n"
                errorMessage += "from hole " + str(startinghole) + " to hole " + str(hole) + ".\n\n"
                errorMessage += "Target position X: " + str(targetX) + '\n'
                errorMessage += "Current position X: " + str(curposX) + '\n\n'
                errorMessage += "Target position Y: " + str(targetY) + '\n'
                errorMessage += "Current position Y: " + str(curposY) + '\n\n'
                errorMessage += "Execution has been paused. Please check machine."
                raise ValueError(errorMessage)
        return

    '''
    '''
    def turningMotorAngle(self):
        angle = self.convertPosToAngle(self.turning.readPosition())
                
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
        self.modConfig.queue.put('MotorControl:Data: TurningAngle: ' + str(self.convertPosToAngle(pos)))
        # If TurningMotorAngle != angle Then RelabelPos MotorTurning, pos
        # TurningAngleBox = angle
        return pos
     
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
            errorMessage += str(startingangle) + " degrees to " + str(angle) + " degrees.\n\n" 
            errorMessage += "Target position: " + str(target) + "\n"
            errorMessage += "Current position: " + str(curpos) + "\n\n"
            errorMessage += "Execution has been paused. Please check machine."
            raise ValueError(errorMessage)
        
        CurAngle = self.turningMotorAngle()
        
        CurAngle = CurAngle - int(CurAngle / 360) * 360     # Integer division
        if (CurAngle != self.turningMotorAngle()): 
            self.setTurningMotorAngle(CurAngle)
            
        return                
    
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
            startingPos = self.turning.readPosition()
            self.turningMotorAngle()
            target = startingPos - self.modConfig.TurningMotorFullRotation * speedRPS * Duration
            self.turning.moveMotor(target, abs(self.modConfig.TurningMotor1rps * speedRPS), False)
            
        return
    
    '''
    '''
    def MotorCommDisconnect(self):
        self.disconnectMotor(self.turning)
        self.disconnectMotor(self.changerX)
        self.disconnectMotor(self.changerY)
        self.disconnectMotor(self.upDown)
        return
    
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            self.HomeToTop()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        devicePath = os.getcwd() + '\\Device\\'
        config = configparser.ConfigParser()
        config.read('C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
        modConfig = ModConfig(config=config)          
        
        devControl = Motors(devicePath, modConfig=modConfig)
        devControl.openMotors()
                
        devControl.HomeToCenter()    
        
        devControl.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
        
                