'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os

from Hardware.Device.MotorControl import MotorControl

class DevicesControl():
    '''
    classdocs
    '''
    HOME_TO_TOP     = 0x0001
    HOME_TO_CENTER  = 0x0002
    
    upDown = None
    changerX = None
    changerY = None
    turning = None
    deviceList = []
    
    devicesAllGoodFlag = False
    programHaltedFlag = False

    def __init__(self):
        '''
        Constructor
        '''
        self.currentPath = os.getcwd()
        self.currentPath += '\\Hardware\\Device'        
        self.DCMotorHomeToTop_StopOnTrue = False
    
    '''
    '''
    def getConfig_Int(self, config, section, label, default):
        try:
            value = int(config[section][label])
            return value
        
        except:
            return default         

    '''
    '''
    def getConfig_Bool(self, config, section, label, default):
        try:
            value = False
            if ('True'.lower() == config[section][label].lower()):
                value = True
            return value 
        
        except:
            return default         
        
    '''
    '''
    def setMotorConfig(self, device):
        device.UpDownTorqueFactor = self.UpDownTorqueFactor
        device.UpDownMaxTorque = self.UpDownMaxTorque
        device.UseXYTableAPS = self.UseXYTableAPS
        device.LiftAcceleration = self.LiftAcceleration
        
    '''
    '''
    def setDevicesConfig(self, config):
        # Read COM Port settings from INI file
        self.upDownComPort = 'COM' + config['COMPorts']['COMPortUpDown']
        self.changerXComPort = 'COM' + config['COMPorts']['COMPortChanger']
        self.changerYComPort = 'COM' + config['COMPorts']['COMPortChangerY']
        self.turningComPort = 'COM' + config['COMPorts']['COMPortTurning']
        
        self.DCMotorHomeToTop_StopOnTrue = self.getConfig_Bool(config, 'SteppingMotor', 'DCMotorHomeToTop_StopOnTrue', True)
        self.UpDownTorqueFactor = self.getConfig_Int(config, 'SteppingMotor', 'UpDownTorqueFactor', 40) 
        self.UpDownMaxTorque = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMaxTorque', 32000)   
        self.UpDownMotor1cm = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMotor1cm', 10)    
        self.SampleBottom = self.getConfig_Int(config, 'SteppingMotor', 'SampleBottom', -2385)   
        self.LiftSpeedSlow = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedSlow', 4000000)    
        self.LiftSpeedNormal = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedNormal', 25000000)    
        self.LiftSpeedFast = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedFast', 50000000)
        self.LiftAcceleration = self.getConfig_Int(config, 'SteppingMotor', 'LiftAcceleration', 90000)
        self.MeasPos = self.getConfig_Int(config, 'SteppingMotor', 'MeasPos', -30607)    

        self.MotorIDChangerX = config['MotorPrograms']['MotorIDChanger']
        self.MotorIDChangerY = config['MotorPrograms']['MotorIDChangerY']
        self.MotorIDUpDown = config['MotorPrograms']['MotorIDUpDown']
        self.MotorIDTurning = config['MotorPrograms']['MotorIDTurning']
        
        self.UseXYTableAPS = self.getConfig_Bool(config, 'XYTable', 'UseXYTableAPS', False)
        
        message = self.openDevices()
        self.upDown.MotorAddress = self.MotorIDUpDown 
        self.setMotorConfig(self.upDown)
        self.changerX.MotorAddress = self.MotorIDChangerX
        self.setMotorConfig(self.changerX)
        self.changerY.MotorAddress = self.MotorIDChangerY
        self.setMotorConfig(self.changerY)
        self.turning.MotorAddress = self.MotorIDTurning
        self.setMotorConfig(self.turning)
        
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
    def openDevices(self):
        self.devicesAllGoodFlag = True
        
        message = '\n'
        self.deviceList = []        
        self.upDown, respStr = self.openDevice(self.upDown, self.upDownComPort, 'UpDown')
        message += respStr
        if (self.upDown != None):
            self.deviceList.append(self.upDown)
        
        self.changerX, respStr = self.openDevice(self.changerX, self.changerXComPort, 'ChangerX')
        message += respStr
        if (self.changerX != None):
            self.deviceList.append(self.changerX)

        self.changerY, respStr = self.openDevice(self.changerY, self.changerYComPort, 'ChangerY')
        message += respStr
        if (self.changerY != None):
            self.deviceList.append(self.changerY)

        self.turning, respStr = self.openDevice(self.turning, self.turningComPort, 'Turning')
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
            
        except:
            return False
   
    '''--------------------------------------------------------------------------------------------
                        
                        Process Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def retrieveProcessData(self, processData):
        # Port Open
        for i in range(0, len(processData.PortOpen)):
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
                        
                        Motor Control Task Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Move UpDown Motor to the top
    '''
    def HomeToTop(self, queue):        
        # No homing to top if the program has been halted
        if self.checkProgramHaltRequest(queue):
            return
        
        print(self.DCMotorHomeToTop_StopOnTrue)
        stop_state = False
        if self.DCMotorHomeToTop_StopOnTrue:
            stop_state = True
        
        # If switch already tripped, do nothing
        if (self.upDown.checkInternalStatus(4) == stop_state):
            current_updown_pos = self.upDown.readPosition()
            # If the current position is larger than 1cm, set the current position as the new Zero Target
            if (abs(current_updown_pos) > (self.UpDownMotor1cm/10)):
                self.upDown.zeroTargetPos()
            return 
                    
        # If up/down position is greater than the sample bottom, use the normal lift speed
        # otherwise, a sample has just been dropped off on the changer belt
        # and the home to top speed needs to be slower
        speed = self.LiftSpeedNormal
        if (abs(self.upDown.readPosition()) <= abs(self.SampleBottom)):
            # ???????????? - Why this particular speed?
            speed = 0.25 * (self.LiftSpeedNormal + 3 * self.LiftSpeedSlow)
        
        self.upDown.moveMotor(-2 * self.MeasPos, speed, True, -1, int(stop_state))
              
        # Check to see if the motor has reached the limit switch      
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            self.upDown.moveMotor(-2 * self.MeasPos, self.LiftSpeedSlow, True)

        # Check if the limit switch get hit, set error if not                    
        if not (self.upDown.checkInternalStatus(4) == stop_state):
            queue.put('Error: Homed to top but did not hit switch!')
            
    '''
    '''
    def HomeToCenter(self, queue):
        print('TODO: Home To Center')
        
    '''
        
    '''
    def runTask(self, queue, taskID):
        if (taskID == self.HOME_TO_TOP):
            self.HomeToTop(queue)
                
        elif (taskID == self.HOME_TO_CENTER):
            self.HomeToCenter(queue)
            
            