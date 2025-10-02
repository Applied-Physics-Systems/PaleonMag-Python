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
from Hardware.Device.GaussMeterControl import GaussMeterControl

from Process.ProcessData import ProcessData
from Modules.modConfig import ModConfig

from Modules.modChanger import ModChanger

DEVICE_MOTORS               = 0x0
DEVICE_IRM                  = 0x1
DEVICE_SQUID                = 0x2
DEVICE_VACUUM               = 0x3
DEVICE_AF                   = 0x4
DEVICE_SYSTEM               = 0xF

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
    
    IRM_ARM_INIT            = 0x1001
    IRM_SET_BIAS_FIELD      = 0x1002
    IRM_REFRESH_TEMP        = 0x1003
    IRM_FIRE                = 0x1004
    IRM_FIRE_AT_FIELD       = 0x1005
    IRM_SET_FIELD           = 0x1006
    IRM_ARM_VOLTAGE_OUT     = 0x1007
    IRM_ARM_TOGGLE_SET      = 0x1008
    
    SQUID_READ_COUNT        = 0x2001
    SQUID_READ_DATA         = 0x2002
    SQUID_READ_RANGE        = 0x2003
    SQUID_RESET_COUNT       = 0x2004
    SQUID_CONFIGURE         = 0x2005
    SQUID_CHANGE_RATE       = 0x2006
    SQUID_SET_CFG           = 0x2007
    SQUID_READ              = 0x2008
    
    VACUUM_INIT             = 0x3001
    VACUUM_SET_CONNECT      = 0x3002
    VACUUM_SET_MOTOR        = 0x3003
    VACUUM_RESET            = 0x3004
    VACUUM_SET_DEGAUSSER    = 0x3005
    
    AF_SWITCH_COIL          = 0x4001
    AF_REFRESH_T            = 0x4002
    AF_CLEAN_COIL           = 0x4003
    AF_START_RAMP           = 0x4004
    AF_SET_RELAYS_DEFAULT   = 0x4005
    
    SYSTEM_DISCONNECT       = 0xF001
    
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
                IRM_ARM_INIT: 'Initialize IRM/ARM',
                IRM_SET_BIAS_FIELD: 'Set ARM Bias Field',
                IRM_FIRE: 'Discharge IRM device',                
                IRM_FIRE_AT_FIELD: 'Discharge IRM at field',
                IRM_SET_FIELD: 'Set field level',
                IRM_ARM_VOLTAGE_OUT: 'Set ARM Voltage',
                IRM_ARM_TOGGLE_SET: 'Toggle ARM Set',
                SQUID_READ_COUNT: 'Read count from SQUID',
                SQUID_READ_DATA: 'Read data from SQUID',
                SQUID_READ_RANGE: 'Read range from SQUID',
                SQUID_RESET_COUNT: 'Reset count SQUID',
                SQUID_CONFIGURE: 'Configure SQUID',
                SQUID_CHANGE_RATE:'Change rate for SQUID',
                SQUID_SET_CFG:'Set configuration for SQUID',
                SQUID_READ:'Read from SQUID',
                VACUUM_INIT:'Initialize vacuum',
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
    AF2G = None
    susceptibility = None
    gaussMeter = None
    deviceList = []
    
    devicesAllGoodFlag = False
    programHaltedFlag = False
    programPausedFlag = False

    def __init__(self):
        '''
        Constructor
        '''
        self.currentPath = os.getcwd()
        if 'Forms' in self.currentPath:
            self.currentPath = self.currentPath.replace('\\Forms', '')
        self.currentPath += '\\Hardware\\Device\\'        
        self.DCMotorHomeToTop_StopOnTrue = False
        self.gaussMeter = GaussMeterControl()
                    
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
        if (self.modConfig.EnableAxialIRM or self.modConfig.EnableTransIRM):
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
        
        else:
            return None, '\n'

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
        
        message = ''
        if (self.modConfig.processData.motorsEnable):
            self.motors = Motors(self.currentPath, self, self.modConfig)
            deviceList, message = self.motors.openMotors()
            self.deviceList.extend(deviceList) 

        if (self.modConfig.processData.vacuumEnable):                
            self.vacuum, respStr = self.openVacuumComm(self.vacuum, 'Vacuum', 'COMPortVacuum')
            message += respStr    
            if (self.vacuum != None):
                self.deviceList.append(self.vacuum)

        if (self.modConfig.processData.irmArmEnable):
            self.apsIRM, respStr = self.openIrmArmComm(self.apsIRM, 'IrmArm', 'COMPortApsIrm')
            message += respStr    
            if (self.apsIRM != None):
                self.deviceList.append(self.apsIRM)

        if (self.modConfig.processData.squidEnable):
            self.SQUID, respStr = self.openSQUIDComm(self.SQUID, 'SQUID', 'COMPortSquids')
            message += respStr    
            if (self.SQUID != None):
                self.deviceList.append(self.SQUID)
                
        if (self.modConfig.processData.adwinEnable): 
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
    def checkInterruptRequest(self):
        try:
            message = self.modConfig.queue.get(timeout=0.001)
            if 'Program_Interrupt' in message:
                return True
                
            return False
            
        except:
            return False

    '''
        Check for message from the MainForm
        If Program_Halt request is sent, exit.
        Otherwise, continue
    '''
    def checkProgramHaltRequest(self):
        try:
            message = self.modConfig.queue.get(timeout=0.001)
            if 'Program_Halted' in message:
                self.Flow_Pause()
                return True
                
            return False
            
        except:
            return False
        
    '''
    '''
    def Flow_Pause(self):
        self.modConfig.queue.put('Flow Pause')
        pauseFlag = True
        while pauseFlag:
            try:
                message = self.modConfig.queue.get(timeout=0.1)
                if 'Continue Flow' in message:
                    pauseFlag = False
            except:
                time.sleep(0.01)
                
        return
      
    '''
        Update data for process that has been changed 
        These are the data that are exchanged between processes.
    '''
    def updateProcessData(self):
        if (self.motors != None):
            self.modConfig.processData.PortOpen['UpDown'] = self.motors.upDown.modConfig.processData.PortOpen['UpDown']
            self.modConfig.processData.PortOpen['Turning'] = self.motors.turning.modConfig.processData.PortOpen['Turning']
            self.modConfig.processData.PortOpen['ChangerX'] = self.motors.changerX.modConfig.processData.PortOpen['ChangerX']
            self.modConfig.processData.PortOpen['ChangerY'] = self.motors.changerY.modConfig.processData.PortOpen['ChangerY']
        
        if (self.ADwin != None):
            self.modConfig.processData.ADwinDO = self.ADwin.modConfig.processData.ADwinDO
                        
        return self.modConfig.processData 
                       
    '''
    '''
    def runMotorTask(self, queue, taskID):
        
        if (taskID[0] == self.MOTOR_HOME_TO_TOP):
            self.motors.HomeToTop()
                
        elif (taskID[0] == self.MOTOR_HOME_TO_CENTER):
            xPos, yPos = self.motors.HomeToCenter()
            self.modConfig.queue.put('MotorControl:Data: xPos: ' + str(xPos))
            self.modConfig.queue.put('MotorControl:Data: yPos: ' + str(yPos))

        elif (taskID[0] == self.MOTOR_MOVE):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)
            if (activeMotor != None):
                targetPos = taskID[1][1]
                velocity = taskID[1][2]
                activeMotor.moveMotor(targetPos, velocity)
        
        elif (taskID[0] == self.MOTOR_SAMPLE_PICKUP):
            self.motors.DoSamplePickup()

        elif (taskID[0] == self.MOTOR_SAMPLE_DROPOFF):
            SampleHeight = taskID[1][0] 
            self.motors.DoSampleDropoff(SampleHeight)
            
        elif (taskID[0] == self.MOTOR_ZERO_TP):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)
            if (activeMotor != None):
                activeMotor.zeroTargetPos()

        elif (taskID[0] == self.MOTOR_POLL):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)
            if (activeMotor != None):
                activeMotor.pollMotor()

        elif (taskID[0] == self.MOTOR_CLEAR_POLL):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)
            if (activeMotor != None):
                activeMotor.clearPollStatus()

        elif (taskID[0] == self.MOTOR_RELABEL_POSITION):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)                
            targetPosition = taskID[1][1]
            if (activeMotor != None):
                activeMotor.relabelPos(targetPosition)

        elif (taskID[0] == self.MOTOR_SET_CURRENT_HOLE):
            currentHole = taskID[1][0]
            self.motors.setChangerHole(currentHole)

        elif (taskID[0] == self.MOTOR_CHANGE_HOLE):
            currentHole = taskID[1][0]
            self.motors.changerMotortoHole(currentHole)
        
        elif (taskID[0] == self.MOTOR_GO_TO_X):
            moveMotorPos = taskID[1][0]
            if not self.modConfig.processData.HasXYTableBeenHomed:
                self.motors.HomeToTop()                    # MotorUPDN_TopReset
                self.motors.MotorXYTable_CenterReset()
                
            self.motors.moveMotorXY(self.motors.changerX, moveMotorPos, self.modConfig.ChangerSpeed, False)

        elif (taskID[0] == self.MOTOR_GO_TO_Y):
            moveMotorPos = taskID[1][0]
            if not self.modConfig.processData.HasXYTableBeenHomed:
                self.motors.HomeToTop()                    # MotorUPDN_TopReset
                self.motors.MotorXYTable_CenterReset()
                
            self.motors.moveMotorAbsoluteXY(self.motors.changerY, moveMotorPos, self.modConfig.ChangerSpeed, False)

        elif (taskID[0] == self.MOTOR_SPIN_SAMPLE):
            spinRPS = taskID[1][0]
            self.motors.turningMotorSpin(spinRPS)

        elif (taskID[0] == self.MOTOR_CHANGE_TURN_ANGLE):
            angle = taskID[1][0]
            self.motors.turningMotorRotate(angle)

        elif (taskID[0] == self.MOTOR_CHANGE_HEIGHT):
            height = taskID[1][0]
            self.motors.upDownMove(height, 0)
            
        elif (taskID[0] == self.MOTOR_LOAD):
            self.motors.MoveToCorner()

        elif (taskID[0] == self.MOTOR_READ_POSITION):
            motorStr = taskID[1][0]
            activeMotor = self.motors.getActiveMotor(motorStr)
            if (activeMotor != None):
                activeMotor.readPosition()

        elif (taskID[0] == self.MOTOR_READ_ANGLE):
            angle = self.motors.turningMotorAngle()
            self.modConfig.queue.put('MotorControl:TurningAngle = ' + str(angle))

        elif (taskID[0] == self.MOTOR_READ_HOLE):
            curHole = self.motors.changerHole()
            self.modConfig.queue.put('MotorControl:LastHole = ' + str(curHole))

        elif (taskID[0] == self.MOTOR_RESET):
            self.motors.reset()

        elif (taskID[0] == self.MOTOR_STOP):
            self.motors.stop()
                
        return 'MotorControl'

    '''
    '''
    def runIRMTask(self, queue, taskID):
                
        if (self.apsIRM != None):
            self.apsIRM.parent = self
            self.apsIRM.queue = queue
             
            if (taskID[0] == self.IRM_ARM_INIT):
                self.apsIRM.init_IrmArm()
                    
            elif (taskID[0] == self.IRM_SET_BIAS_FIELD):
                Gauss = taskID[1][0]
                self.apsIRM.SetBiasField(Gauss)                  
                
            elif (taskID[0] == self.IRM_FIRE):
                voltage = taskID[1][0] 
                self.apsIRM.FireIRM(voltage)

            elif (taskID[0] == self.IRM_SET_FIELD):
                field = taskID[1][0]
                self.apsIRM.coilLabel = taskID[1][1]  
                self.apsIRM.IRM_SetField(field, pauseFire=True)
                            
            elif (taskID[0] == self.IRM_FIRE_AT_FIELD):
                field = taskID[1][0]
                self.apsIRM.IRM_FireField(field)
                            
            elif (taskID[0] == self.IRM_REFRESH_TEMP):
                self.apsIRM.RefreshTemp()
                
            elif (taskID[0] == self.IRM_ARM_VOLTAGE_OUT):
                targetVolt = taskID[1][0]
                self.ADwin.DoDAQIO(self.modConfig.ARMVoltageOut, numValue=targetVolt)
                
            elif (taskID[0] == self.IRM_ARM_TOGGLE_SET):
                setState = taskID[1][0]
                self.ADwin.DoDAQIO(self.modConfig.ARMSet, boolValue=setState)
                                                
        return 'IRMControl'

    '''
    '''
    def runSquidTask(self, queue, taskID):

        if (taskID[0] == self.SQUID_READ_COUNT):
            activeAxis = taskID[1][0]
            cmdStr, respStr = self.SQUID.readCount(activeAxis)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.SQUID_READ_DATA):
            activeAxis = taskID[1][0]
            cmdStr, respStr = self.SQUID.readData(activeAxis)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
            
        elif (taskID[0] == self.SQUID_READ_RANGE):
            activeAxis = taskID[1][0]
            cmdStr, respStr = self.SQUID.readRange(activeAxis)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.SQUID_RESET_COUNT):
            activeAxis = taskID[1][0]
            cmdStr, respStr = self.SQUID.resetCount(activeAxis)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.SQUID_CONFIGURE):
            activeAxis = taskID[1][0]
            cmdStr, respStr = self.SQUID.configure(activeAxis)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
            
        elif (taskID[0] == self.SQUID_CHANGE_RATE):
            activeAxis = taskID[1][0]
            rateLabel = taskID[1][1]
            cmdStr, respStr = self.SQUID.changeRate(activeAxis, rateLabel)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.SQUID_SET_CFG):
            activeAxis = taskID[1][0]
            cfgLabel = taskID[1][1]
            cmdStr, respStr = self.SQUID.setCfg(activeAxis, cfgLabel)
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
            
        elif (taskID[0] == self.SQUID_READ):
            cmdStr, respStr = self.SQUID.getResponse()
            queue.put('SQUIDControl:' + cmdStr + ':' + respStr)
                
        return 'SQUIDControl'

    '''
    '''
    def runVacuumTask(self, queue, taskID):

        if (taskID[0] == self.VACUUM_INIT):
            cmdStr, respStr = self.vacuum.init(self.ADwin)                        
            queue.put('VacuumControl:' + cmdStr + ':' + respStr)
            
        elif (taskID[0] == self.VACUUM_SET_CONNECT):
            mode = taskID[1][0]
            switch = False
            if 'On' in mode:
                switch = True
            cmdStr, respStr = self.vacuum.valveConnect(switch)
            queue.put('VacuumControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.VACUUM_SET_MOTOR):
            mode = taskID[1][0]
            switch = False
            if 'On' in mode:
                switch = True
            cmdStr, respStr = self.vacuum.motorPower(self.ADwin, switch)
            queue.put('VacuumControl:' + cmdStr + ':' + respStr)
            
        elif (taskID[0] == self.VACUUM_RESET):
            cmdStr, respStr = self.vacuum.reset()        
            queue.put('VacuumControl:' + cmdStr + ':' + respStr)

        elif (taskID[0] == self.VACUUM_SET_DEGAUSSER):
            mode = taskID[1][0]
            self.vacuum.degausserCooler(mode)
        
        return 'VacuumControl'

    '''
    '''
    def runAFTask(self, queue, taskID):
        
        if (taskID[0] == self.AF_SWITCH_COIL):
            activeCoil = taskID[1][0]
            self.ADwin.trySetRelays_ADwin(activeCoil)
            
        elif (taskID[0] == self.AF_REFRESH_T):
            temp1, temp2 = self.ADwin.refreshTs()
            queue.put('ADWinAFControl:' + temp1 + ':' + temp2)
            
        elif (taskID[0] == self.AF_SET_RELAYS_DEFAULT):
            self.ADwin.TrySetAllRelaysToDefaultPosition_ADwin()
            
        elif (taskID[0] == self.AF_CLEAN_COIL):
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

        return 'ADWinAFControl'

    '''
    '''
    def runSystemTask(self, queue, taskID):
        
        if (taskID[0] == self.SYSTEM_DISCONNECT):
            if (self.motors != None):            
                self.motors.MotorCommDisconnect()
            
            if (self.SQUID != None):
                if self.SQUID.PortOpen:
                    self.SQUID.Disconnect()
            
            if (self.ADwin != None):
                # Added in this IF statement to make sure that the ADWIN board power
                # to the AF / IRM relays is switched off so that the relays don't overheat
                if (('ADWIN' in self.modConfig.AFSystem) and self.modConfig.EnableAF):
                    self.ADwin.SwitchOff_AllRelays()
                elif (('2G' in self.modConfig.AFSystem) and self.modConfig.EnableAF):
                    self.ADwin.AF2GControl.Disconnect()
                
            if (self.vacuum != None):                
                self.vacuum.init(self.ADwin)
                self.vacuum.Disconnect()                

            if (self.susceptibility != None):
                self.susceptibility.Disconnect()

            if (self.gaussMeter != None):                
                if self.gaussMeter.connectFlag:
                    self.gaussMeter.Disconnect()
                
            if (self.ADwin != None):                
                if (self.modConfig.EnableAxialIRM or self.modConfig.EnableTransIRM):
                    self.ADwin.DoDAQIO(self.modConfig.IRMVoltageOut, numValue=0)
        
        return 'SystemControl'

    '''--------------------------------------------------------------------------------------------
                        
                        Main Task Handler
                        
    --------------------------------------------------------------------------------------------'''
    '''
        
    '''
    def runTask(self, queue, taskID):
        self.queue = queue
        deviceStr = 'None'
        try:   
            deviceID = ((taskID[0] & 0xF000) >> 12)          
            if (deviceID == DEVICE_MOTORS):
                deviceStr = self.runMotorTask(queue, taskID)
                
            elif (deviceID == DEVICE_IRM):
                deviceStr = self.runIRMTask(queue, taskID)
                
            elif (deviceID == DEVICE_SQUID):
                deviceStr = self.runSquidTask(queue, taskID)

            elif (deviceID == DEVICE_VACUUM):
                deviceStr = self.runVacuumTask(queue, taskID)

            elif (deviceID == DEVICE_AF):
                deviceStr = self.runAFTask(queue, taskID)
                
            elif (deviceID == DEVICE_SYSTEM):
                deviceStr = self.runSystemTask(queue, taskID)
                                            
        except ValueError as e:
            self.modConfig.queue.put(deviceStr + ':Error: ' + str(e))

        except IOError as e:
            self.modConfig.queue.put(deviceStr + ':MessageBox: ' + str(e))
        
        return deviceStr

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
def runAllMotorsFunctions(queue, devControl):

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
'''
'''
def runRegressionTest():
    devControl = DevicesControl()
    queue = Queue()

    config = configparser.ConfigParser()
    config.read('C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
    processData = ProcessData()
    processData.config = config 

    modConfig = ModConfig(process=processData, queue=queue)
    devControl.setDevicesConfig(modConfig)

    start_time = time.perf_counter()
    runAllMotorsFunctions(queue, devControl)
    devControl.updateProcessData()
                    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
            
    print('Done !!!')
    return
   
if __name__=='__main__':    
    try:    
        runRegressionTest()
                        
    except Exception as e:
        print('Error!! ' + str(e))

