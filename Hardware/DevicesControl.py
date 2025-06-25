'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os
import time
import configparser

from Hardware.Motors import Motors
from Hardware.Device.IrmArmControl import IrmArmControl
from Hardware.Device.SQUIDControl import SQUIDControl
from Hardware.Device.VacuumControl import VacuumControl
from Hardware.Device.ADWinControl import ADWinControl

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
    
    SQUID_READ_COUNT        = 0x2001
    SQUID_READ_DATA         = 0x2002
    SQUID_READ_RANGE        = 0x2003
    SQUID_RESET_COUNT       = 0x2004
    SQUID_CONFIGURE         = 0x2005
    SQUID_CHANGE_RATE       = 0x2006
    SQUID_SET_CFG           = 0x2007
    SQUID_READ              = 0x2008
    
    VACUUM_SET_CONNECT      = 0x3001
    VACUUM_SET_MOTOR        = 0x3002
    VACUUM_RESET            = 0x3003
    VACUUM_SET_DEGAUSSER    = 0x3004
    
    AF_SWITCH_COIL          = 0x4001
    AF_REFRESH_T            = 0x4002
    AF_CLEAN_COIL           = 0x4003
    AF_START_RAMP           = 0x4004
    
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
                IRM_FIRE: 'Discharge IRM device',
                SQUID_READ_COUNT: 'Read count from SQUID',
                SQUID_READ_DATA: 'Read data from SQUID',
                SQUID_READ_RANGE: 'Read range from SQUID',
                SQUID_RESET_COUNT: 'Reset count SQUID',
                SQUID_CONFIGURE: 'Configure SQUID',
                SQUID_CHANGE_RATE:'Change rate for SQUID',
                SQUID_SET_CFG:'Set configuration for SQUID',
                SQUID_READ:'Read from SQUID',
                VACUUM_SET_CONNECT:'Set vacuum connection on/off',
                VACUUM_SET_MOTOR:'Set vacuum motor on/off',
                VACUUM_RESET:'Reset vacuum',
                VACUUM_SET_DEGAUSSER:'Set degausser cooler on/off',
                AF_SWITCH_COIL: 'Switch AF Coil',
                AF_REFRESH_T: 'AF Refresh Temperature',
                AF_CLEAN_COIL: 'AF Clean Coils',
                AF_START_RAMP: 'AF Start Ramp'}
            
    modConfig = None
    
    motors = None
    vacuum = None
    apsIRM = None
    SQUID = None
    ADwin = None
    deviceList = []
    
    devicesAllGoodFlag = False
    programHaltedFlag = False
    programPausedFlag = False

    def __init__(self):
        '''
        Constructor
        '''
        self.currentPath = os.getcwd()
        self.currentPath += '\\Hardware\\Device\\'        
        self.DCMotorHomeToTop_StopOnTrue = False
                    
    '''
        Set parameter from INI files for each motor
    '''
    def setDevicesConfig(self, modConfig):  
        self.modConfig = modConfig
        self.modChanger = ModChanger(self.modConfig)
        message = self.openDevices()
        
        return message

    '''
        Open UART serial communication port for IRM/ARM
    '''
    def openIrmArmComm(self, device, label, portLabel):        
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
                device = IrmArmControl(9600, self.currentPath, comPort, label, self.modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False
        
        return device, message + '\n'

    '''
        Open UART serial communication port for Vacuum
    '''
    def openVacuumComm(self, device, label, portLabel):
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
                device = VacuumControl(9600, self.currentPath, comPort, label, self.modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False
        
        return device, message + '\n'

    '''
        Open UART serial communication port for motor
    '''
    def openSQUIDComm(self, device, label, portLabel):        
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
                device = SQUIDControl(1200, self.currentPath, comPort, label, self.modConfig)
            except:
                message += ' Failed to open'
                self.devicesAllGoodFlag = False
                
        return device, message + '\n'
        
    '''
    '''
    def openDevices(self):
        self.devicesAllGoodFlag = True
                        
        self.deviceList = []
        
        self.motors = Motors(self.currentPath, self, self.modConfig)
        deviceList, message = self.motors.openMotors()
        self.deviceList.extend(deviceList) 
        
        self.vacuum, respStr = self.openVacuumComm(self.vacuum, 'Vacuum', 'COMPortVacuum')
        message += respStr    
        if (self.vacuum != None):
            self.deviceList.append(self.vacuum)

        self.apsIRM, respStr = self.openIrmArmComm(self.apsIRM, 'IrmArm', 'COMPortApsIrm')
        message += respStr    
        if (self.apsIRM != None):
            self.deviceList.append(self.apsIRM)

        self.SQUID, respStr = self.openSQUIDComm(self.SQUID, 'SQUID', 'COMPortSquids')
        message += respStr    
        if (self.SQUID != None):
            self.deviceList.append(self.SQUID)
        
        try:
            self.ADwin = ADWinControl(self.currentPath, modConfig=self.modConfig)
        except Exception as e:
            print('Error: Initializing ADWinControl; ' + str(e))
            self.ADwin = None
        
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
        Update data for process that has been changed 
        These are the data that are exchanged between processes.
    '''
    def updateProcessData(self):
        self.modConfig.processData.PortOpen['UpDown'] = self.motors.upDown.modConfig.processData.PortOpen['UpDown']
        self.modConfig.processData.PortOpen['Turning'] = self.motors.turning.modConfig.processData.PortOpen['Turning']
        self.modConfig.processData.PortOpen['ChangerX'] = self.motors.changerX.modConfig.processData.PortOpen['ChangerX']
        self.modConfig.processData.PortOpen['ChangerY'] = self.motors.changerY.modConfig.processData.PortOpen['ChangerY']
        self.modConfig.processData.ADwinDO = self.ADwin.modConfig.processData.ADwinDO
                        
        return self.modConfig.processData 
           
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

        return

    '''--------------------------------------------------------------------------------------------
                        
                        Vacuum Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Vacuum_valveConnect(self, mode):
        if not self.modConfig.EnableVacuum:
            return

        if 'On' in mode:
            cmdStr, respStr = self.vacuum.setValveConnect()
            self.ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=True)
        else:
            cmdStr, respStr = self.vacuum.clearValveConnect()
            self.ADwin.DoDAQIO(self.modConfig.VacuumToggleA, boolValue=False)
            
        return cmdStr, respStr
        
    '''
    '''
    def Vacuum_motorPower(self, mode):
        if not self.modConfig.EnableVacuum:
            return
        
        if 'On' in mode:
            cmdStr, respStr = self.vacuum.setVacuumOn()
            self.ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=True)
        else:
            cmdStr, respStr = self.vacuum.setVacuumOff()
            self.ADwin.DoDAQIO(self.modConfig.MotorToggle, boolValue=False)
        
        return cmdStr, respStr
        
    '''
    '''
    def Vacuum_degausserCooler(self, mode):
        if not self.modConfig.EnableDegausserCooler:
            return
        
        if 'On' in mode:
            self.ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=True)
        else:
            self.ADwin.DoDAQIO(self.modConfig.DegausserToggle, boolValue=False)
        
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Main Task Handler
                        
    --------------------------------------------------------------------------------------------'''
    '''
        
    '''
    def runTask(self, queue, taskID):
        self.queue = queue
        deviceID = 'None'
        try:            
            if (taskID[0] == self.MOTOR_HOME_TO_TOP):
                deviceID = 'MotorControl'
                self.motors.HomeToTop()
                    
            elif (taskID[0] == self.MOTOR_HOME_TO_CENTER):
                deviceID = 'MotorControl'
                xPos, yPos = self.motors.HomeToCenter()
                self.modConfig.queue.put('MotorControl:Data: xPos: ' + str(xPos))
                self.modConfig.queue.put('MotorControl:Data: yPos: ' + str(yPos))

            elif (taskID[0] == self.MOTOR_MOVE):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)
                if (activeMotor != None):
                    targetPos = taskID[1][1]
                    velocity = taskID[1][2]
                    activeMotor.moveMotor(targetPos, velocity)
            
            elif (taskID[0] == self.MOTOR_SAMPLE_PICKUP):
                deviceID = 'MotorControl'
                self.motors.DoSamplePickup()

            elif (taskID[0] == self.MOTOR_SAMPLE_DROPOFF):
                deviceID = 'MotorControl'
                SampleHeight = taskID[1][0] 
                self.motors.DoSampleDropoff(SampleHeight)
                
            elif (taskID[0] == self.MOTOR_ZERO_TP):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.zeroTargetPos()

            elif (taskID[0] == self.MOTOR_POLL):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.pollMotor()

            elif (taskID[0] == self.MOTOR_CLEAR_POLL):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.clearPollStatus()

            elif (taskID[0] == self.MOTOR_RELABEL_POSITION):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)                
                targetPosition = taskID[1][1]
                if (activeMotor != None):
                    activeMotor.relabelPos(targetPosition)

            elif (taskID[0] == self.MOTOR_SET_CURRENT_HOLE):
                deviceID = 'MotorControl'
                currentHole = taskID[1][0]
                self.motors.setChangerHole(currentHole)

            elif (taskID[0] == self.MOTOR_CHANGE_HOLE):
                deviceID = 'MotorControl'
                currentHole = taskID[1][0]
                self.motors.changerMotortoHole(currentHole)
            
            elif (taskID[0] == self.MOTOR_GO_TO_X):
                deviceID = 'MotorControl'
                moveMotorPos = taskID[1][0]
                if not self.modConfig.processData.HasXYTableBeenHomed:
                    self.motors.HomeToTop()                    # MotorUPDN_TopReset
                    self.motors.MotorXYTable_CenterReset()
                    
                self.motors.moveMotorXY(self.motors.changerX, moveMotorPos, self.modConfig.ChangerSpeed, False)

            elif (taskID[0] == self.MOTOR_GO_TO_Y):
                deviceID = 'MotorControl'
                moveMotorPos = taskID[1][0]
                if not self.modConfig.processData.HasXYTableBeenHomed:
                    self.motors.HomeToTop()                    # MotorUPDN_TopReset
                    self.motors.MotorXYTable_CenterReset()
                    
                self.motors.moveMotorAbsoluteXY(self.motors.changerY, moveMotorPos, self.modConfig.ChangerSpeed, False)

            elif (taskID[0] == self.MOTOR_SPIN_SAMPLE):
                deviceID = 'MotorControl'
                spinRPS = taskID[1][0]
                self.motors.turningMotorSpin(spinRPS)

            elif (taskID[0] == self.MOTOR_CHANGE_TURN_ANGLE):
                deviceID = 'MotorControl'
                angle = taskID[1][0]
                self.motors.turningMotorRotate(angle)

            elif (taskID[0] == self.MOTOR_CHANGE_HEIGHT):
                deviceID = 'MotorControl'
                height = taskID[1][0]
                self.motors.upDownMove(height, 0)
                
            elif (taskID[0] == self.MOTOR_LOAD):
                deviceID = 'MotorControl'
                self.motors.MoveToCorner()

            elif (taskID[0] == self.MOTOR_READ_POSITION):
                deviceID = 'MotorControl'
                motorStr = taskID[1][0]
                activeMotor = self.motors.getActiveMotor(motorStr)
                if (activeMotor != None):
                    activeMotor.readPosition()

            elif (taskID[0] == self.MOTOR_READ_ANGLE):
                deviceID = 'MotorControl'
                angle = self.motors.turningMotorAngle()
                self.modConfig.queue.put('MotorControl:Data: TurningAngle: ' + str(angle))

            elif (taskID[0] == self.MOTOR_READ_HOLE):
                deviceID = 'MotorControl'
                self.motors.changerHole()

            elif (taskID[0] == self.MOTOR_RESET):
                deviceID = 'MotorControl'
                self.motors.reset()

            elif (taskID[0] == self.MOTOR_STOP):
                deviceID = 'MotorControl'
                self.motors.stop()
            
            elif (taskID[0] == self.IRM_FIRE):
                deviceID = 'IRMControl'
                voltage = taskID[1][0] 
                self.FireIRM(voltage)

            elif (taskID[0] == self.SQUID_READ_COUNT):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cmdStr, respStr = self.SQUID.readCount(activeAxis)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.SQUID_READ_DATA):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cmdStr, respStr = self.SQUID.readData(activeAxis)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
                
            elif (taskID[0] == self.SQUID_READ_RANGE):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cmdStr, respStr = self.SQUID.readRange(activeAxis)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.SQUID_RESET_COUNT):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cmdStr, respStr = self.SQUID.resetCount(activeAxis)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.SQUID_CONFIGURE):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cmdStr, respStr = self.SQUID.configure(activeAxis)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
                
            elif (taskID[0] == self.SQUID_CHANGE_RATE):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                rateLabel = taskID[1][1]
                cmdStr, respStr = self.SQUID.changeRate(activeAxis, rateLabel)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.SQUID_SET_CFG):
                deviceID = 'SQUIDControl'
                activeAxis = taskID[1][0]
                cfgLabel = taskID[1][1]
                cmdStr, respStr = self.SQUID.setCfg(activeAxis, cfgLabel)
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
                
            elif (taskID[0] == self.SQUID_READ):
                deviceID = 'SQUIDControl'
                cmdStr, respStr = self.SQUID.getResponse()
                queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
            
            elif (taskID[0] == self.VACUUM_SET_CONNECT):
                deviceID = 'VacuumControl'
                mode = taskID[1][0]
                cmdStr, respStr = self.Vacuum_valveConnect(mode)
                queue.put('VacuumControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.VACUUM_SET_MOTOR):
                deviceID = 'VacuumControl'
                mode = taskID[1][0]
                cmdStr, respStr = self.Vacuum_motorPower(mode)
                queue.put('VacuumControl:' + cmdStr + ':' + respStr)
                
            elif (taskID[0] == self.VACUUM_RESET):
                deviceID = 'VacuumControl'        
                cmdStr, respStr = self.vacuum.reset()        
                queue.put('VacuumControl:' + cmdStr + ':' + respStr)

            elif (taskID[0] == self.VACUUM_SET_DEGAUSSER):
                deviceID = 'VacuumControl'                
                mode = taskID[1][0]
                self.Vacuum_degausserCooler(mode)
                
            elif (taskID[0] == self.AF_SWITCH_COIL):
                deviceID = 'ADWinAFControl'
                activeCoil = taskID[1][0]
                self.ADwin.trySetRelays_ADwin(activeCoil)
                
            elif (taskID[0] == self.AF_REFRESH_T):
                deviceID = 'ADWinAFControl'                
                temp1, temp2 = self.ADwin.refreshTs()
                queue.put('ADWinAFControl:' + temp1 + ':' + temp2)
                
            elif (taskID[0] == self.AF_CLEAN_COIL):
                deviceID = 'ADWinAFControl'
                Verbose = taskID[1][0]        
                self.ADwin.executeRamp(self.modConfig.AxialCoilSystem, 
                                       self.modConfig.AfAxialMax, 
                                       PeakHangTime = 0, 
                                       CalRamp = True, 
                                       ClipTest = False, 
                                       Verbose=Verbose)
                
                queue.put('ADWinAFControl:Active Coil = Transverse')
        
                self.ADwin.executeRamp(self.modConfig.TransverseCoilSystem, 
                                       self.modConfig.AfTransMax, 
                                       PeakHangTime = 0, 
                                       CalRamp = True, 
                                       ClipTest = False, 
                                       Verbose=Verbose)                

            elif (taskID[0] == self.AF_START_RAMP):
                deviceID = 'ADWinAFControl'
                    
                if (len(taskID[1]) == 10):
                    AFCoilSystem = self.modConfig.getCoilSystem(taskID[1][0])
                    PeakValue = self.modConfig.getParam_Float(taskID[1][1])
                    UpSlope = self.modConfig.getParam_Float(taskID[1][2])
                    DownSlope = self.modConfig.getParam_Float(taskID[1][3])
                    IORate = self.modConfig.getParam_Float(taskID[1][4])
                    PeakHangTime = self.modConfig.getParam_Float(taskID[1][5])
                    CalRamp = taskID[1][6]
                    ClipTest = taskID[1][7]
                    Verbose = taskID[1][8]
                    DoDCFieldRecord = taskID[1][9]
                    self.ADwin.executeRamp(AFCoilSystem, 
                                           PeakValue,
                                           UpSlope = UpSlope,
                                           DownSlope = DownSlope,
                                           IORate = IORate, 
                                           PeakHangTime = PeakHangTime, 
                                           CalRamp = CalRamp, 
                                           ClipTest = ClipTest, 
                                           Verbose = Verbose,
                                           DoDCFieldRecord = DoDCFieldRecord)
                elif (len(taskID[1]) == 8):
                    AFCoilSystem = self.modConfig.getCoilSystem(taskID[1][0])
                    PeakValue = self.modConfig.getParam_Float(taskID[1][1].strip())
                    IORate = self.modConfig.getParam_Float(taskID[1][2].strip())
                    PeakHangTime = self.modConfig.getParam_Float(taskID[1][3].strip())
                    CalRamp = taskID[1][4]
                    ClipTest = taskID[1][5]
                    Verbose = taskID[1][6]
                    DoDCFieldRecord = taskID[1][7]    
                    self.ADwin.executeRamp(AFCoilSystem, 
                                           PeakValue,
                                           IORate = IORate, 
                                           PeakHangTime = PeakHangTime, 
                                           CalRamp = CalRamp, 
                                           ClipTest = ClipTest, 
                                           Verbose = Verbose,
                                           DoDCFieldRecord = DoDCFieldRecord)
                    
                        
        except ValueError as e:
            self.modConfig.queue.put(deviceID + ':Error: ' + str(e))

        except IOError as e:
            self.modConfig.queue.put(deviceID + ':MessageBox: ' + str(e))
        
        return deviceID

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
# Unit Testing Module
#---------------------------------------------------------------------------------------------------    
'''
'''                    
def runAllMotorsFunctions(devControl):

        print('MOTOR_HOME_TO_TOP')
        devControl.runTask(queue, [devControl.MOTOR_HOME_TO_TOP, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_HOME_TO_CENTER')
        devControl.runTask(queue, [devControl.MOTOR_HOME_TO_CENTER, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_MOVE')
        devControl.runTask(queue, [devControl.MOTOR_MOVE, ['UpDown', 1000, 1000]])
        devControl.updateProcessData()
        
        print('MOTOR_SAMPLE_PICKUP')
        devControl.runTask(queue, [devControl.MOTOR_SAMPLE_PICKUP, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_SAMPLE_DROPOFF')
        devControl.runTask(queue, [devControl.MOTOR_SAMPLE_DROPOFF, [1000]])
        devControl.updateProcessData()
        
        print('MOTOR_ZERO_TP')
        devControl.runTask(queue, [devControl.MOTOR_ZERO_TP, ['UpDown']])
        devControl.updateProcessData()
        
        print('MOTOR_POLL')
        devControl.runTask(queue, [devControl.MOTOR_POLL, ['UpDown']])
        devControl.updateProcessData()
        
        print('MOTOR_CLEAR_POLL')
        devControl.runTask(queue, [devControl.MOTOR_CLEAR_POLL, ['UpDown']])
        devControl.updateProcessData()
        
        print('MOTOR_RELABEL_POSITION')
        devControl.runTask(queue, [devControl.MOTOR_RELABEL_POSITION, ['UpDown', 329422]])
        devControl.updateProcessData()
        
        print('MOTOR_SET_CURRENT_HOLE')                
        devControl.runTask(queue, [devControl.MOTOR_SET_CURRENT_HOLE, [50]])
        devControl.updateProcessData()
                
        print('MOTOR_CHANGE_HOLE')                
        devControl.runTask(queue, [devControl.MOTOR_CHANGE_HOLE, [60]])
        devControl.updateProcessData()
        
        print('MOTOR_GO_TO_X')                
        devControl.runTask(queue, [devControl.MOTOR_GO_TO_X, [1000]])
        devControl.updateProcessData()
        
        print('MOTOR_GO_TO_Y')                
        devControl.runTask(queue, [devControl.MOTOR_GO_TO_Y, [1000]])
        devControl.updateProcessData()
        
        print('MOTOR_SPIN_SAMPLE')                
        devControl.runTask(queue, [devControl.MOTOR_SPIN_SAMPLE, [1000]])
        devControl.updateProcessData()
        
        print('MOTOR_CHANGE_TURN_ANGLE')                
        devControl.runTask(queue, [devControl.MOTOR_CHANGE_TURN_ANGLE, [90]])
        devControl.updateProcessData()
        
        print('MOTOR_CHANGE_HEIGHT')                
        devControl.runTask(queue, [devControl.MOTOR_CHANGE_HEIGHT, [100]])
        devControl.updateProcessData()
        
        print('MOTOR_LOAD')                
        devControl.runTask(queue, [devControl.MOTOR_LOAD, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_READ_POSITION')                
        devControl.runTask(queue, [devControl.MOTOR_READ_POSITION, ['UpDown']])
        devControl.updateProcessData()
        
        print('MOTOR_READ_ANGLE')                
        devControl.runTask(queue, [devControl.MOTOR_READ_ANGLE, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_READ_HOLE')                
        devControl.runTask(queue, [devControl.MOTOR_READ_HOLE, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_RESET')                
        devControl.runTask(queue, [devControl.MOTOR_RESET, [None]])
        devControl.updateProcessData()
        
        print('MOTOR_STOP')                
        devControl.runTask(queue, [devControl.MOTOR_STOP, [None]])
        processData = devControl.updateProcessData()                                        
                    
        return processData
    
'''
'''    
if __name__=='__main__':
    try:    
        devControl = DevicesControl()
        queue = Queue()

        config = configparser.ConfigParser()
        config.read('C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
        processData = ProcessData()
        processData.config = config 

        modConfig = ModConfig(process=processData, queue=queue)
        devControl.setDevicesConfig(modConfig)

        start_time = time.perf_counter()
        #runAllMotorsFunctions(devControl)
        print('AF_CLEAN_COIL')
        devControl.runTask(queue, [devControl.AF_CLEAN_COIL, [True]])
        devControl.updateProcessData()
                        
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds")
                
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))

