'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os
import time
import configparser

from Hardware.Device.MotorControl import MotorControl
from Hardware.Device.IrmArmControl import IrmArmControl

from Process.ProcessData import ProcessData
from Process.ModConfig import ModConfig

class DevicesControl():
    '''
    classdocs
    '''
    MOTOR_HOME_TO_TOP       = 0x0001
    MOTOR_HOME_TO_CENTER    = 0x0002
    
    IRM_SET_BIAS_FIELD      = 0x1001
    IRM_FIRE                = 0x1002
    
    MotorPositionMoveToLoadCorner = 900000
    MotorPositionMoveToCenter = -900000
    MoveXYMotorsToLimitSwitch_TimeoutSeconds = 120
        
    lastCmdMove = 1
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
   
    '''--------------------------------------------------------------------------------------------
                        
                        Process Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def retrieveProcessData(self, processData):        
        # Port Open
        for i in range(0, len(self.deviceList)):
            self.deviceList[i].PortOpen = processData.PortOpen[i]
            
    '''
    '''
    def saveProcessData(self, processData):
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
    def upDownMove(self, position, speed, waitingForStop=True):
        if self.checkProgramHaltRequest():
            return
        
        if not (self.programPausedFlag or self.programHaltedFlag):
            self.lastMoveCommand = self.lastCmdMove
            self.lastMoveMotor = 'UpDown'
            self.lastMoveTarget = position
        
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
        stop_state = False
        if self.modConfig.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
            
        print('Start of HomeToCenter')
        # No homing to center if the Up/Down Motor is not homed
        if (self.upDown.checkInternalStatus(4) != stop_state):
            raise ValueError('Could not home to center!  Home to top not complete!')
        
        print('Before Reset')
        
        self.changerX.motorReset()
        self.changerY.motorReset()
        
        print('After Reset')
        
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

        print('Middle of HomeToCenter')
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
            
        print('End of HomeToCenter')
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Functions
                        
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
                self.HomeToCenter()
            
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
        config.read('E:\\Workspace\\SVN\\Windows\\PaleoMag XY 2023\\Settings\\Paleomag_v3_Hung.INI')
        processData = ProcessData()
        processData.config = config 

        modConfig = ModConfig(process=processData, queue=queue)
        devControl.setDevicesConfig(modConfig)
                
        devControl.runTask(queue, [devControl.MOTOR_HOME_TO_TOP, [None]])
                
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
                    