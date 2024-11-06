'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import time
from Hardware.Device.SerialPortDevice import SerialPortDevice

class MotorControl(SerialPortDevice):
    '''
    classdocs
    '''
    label = ''

    def __init__(self, baudRate, pathName, comPort, Label):
        '''
        Constructor
        '''
        self.label = Label
        self.PortOpen = False 
                
        self.MotorAddress = '16'
        SerialPortDevice.__init__(self, baudRate, 'MotorControl', pathName, comPort)

    '''
        Read an integer value from INI file
    '''
    def getConfig_Int(self, config, section, label, default):
        try:
            value = int(config[section][label])
            return value
        
        except:
            return default         

    '''
       Read boolean value from INI file
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
        Set Motor Config
    '''
    def setMotorConfig(self, config):
        self.DCMotorHomeToTop_StopOnTrue = self.getConfig_Bool(config, 'SteppingMotor', 'DCMotorHomeToTop_StopOnTrue', True)
        self.UpDownTorqueFactor = self.getConfig_Int(config, 'SteppingMotor', 'UpDownTorqueFactor', 40) 
        self.UpDownMaxTorque = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMaxTorque', 32000)   
        self.UpDownMotor1cm = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMotor1cm', 10)    
        self.SampleBottom = self.getConfig_Int(config, 'SteppingMotor', 'SampleBottom', -2385)   
        self.SampleTop = self.getConfig_Int(config, 'SteppingMotor', 'SampleTop', -1979)
        self.LiftSpeedSlow = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedSlow', 4000000)    
        self.LiftSpeedNormal = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedNormal', 25000000)    
        self.LiftSpeedFast = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedFast', 50000000)
        self.LiftAcceleration = self.getConfig_Int(config, 'SteppingMotor', 'LiftAcceleration', 90000)
        self.MeasPos = self.getConfig_Int(config, 'SteppingMotor', 'MeasPos', -30607)
        self.ChangerSpeed = self.getConfig_Int(config, 'SteppingMotor', 'ChangerSpeed', 31000)   

        self.UseXYTableAPS = self.getConfig_Bool(config, 'XYTable', 'UseXYTableAPS', False)
       
        if (self.label == 'UpDown'):
            self.MotorID = config['MotorPrograms']['MotorIDUpDown']
        elif (self.label == 'ChangeX'):
            self.MotorID = config['MotorPrograms']['MotorIDChanger']
        elif (self.label == 'ChangeY'):
            self.MotorID = config['MotorPrograms']['MotorIDChangerY']
        elif (self.label == 'Turning'):
            self.MotorIDTurning = config['MotorPrograms']['MotorIDTurning']
        
       
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary Motor Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Initialize Motor
    '''
    def motorCommConnect(self):
        self.sendString('@255 173 416\r\n')
        
        if 'UpDown' in self.label:
            self.setTorque(self.UpDownTorqueFactor, self.UpDownTorqueFactor, self.UpDownTorqueFactor, self.UpDownTorqueFactor)
            
        self.PortOpen = True
        
        self.readPosition()

    '''
    '''    
    def setTorque(self, ClosedHold, ClosedMove, OpenHold, OpenMove):
        PerTorque = 0.01 * self.UpDownMaxTorque     #Value for 1% torque

        CH = int(ClosedHold * PerTorque)
        CM = int(ClosedMove * PerTorque)
        OH = int(OpenHold * PerTorque)
        OM = int(OpenMove * PerTorque)
        cmdStr = '@' + self.MotorAddress + ' 149 ' 
        cmdStr += format(CH, '04') + ' '   
        cmdStr += format(CM, '04') + ' '
        cmdStr += format(OH, '04') + ' '
        cmdStr += format(OM, '04')
        self.sendString(cmdStr + '\r\n')
        
        respStr = self.readLine()
        
        return respStr

    '''
        Format the command string to the Silver Lode Command
    '''
    def sendMotorCommand(self, cmdStr):
        if not self.PortOpen:
            self.motorCommConnect()
         
        self.sendString('@' + self.MotorAddress + ' ' + cmdStr + '\r\n')
        
        time.sleep(0.01)        # Sleep for 100 ms

        respStr = self.readLine()
        
        return respStr 

    '''--------------------------------------------------------------------------------------------
                        
                        Motor Control Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        This command is used to determine the condition of a unit.
        
        Return: ACK only or Polling Status Word. For a poll with a consistent response see Poll Status Word (PSW).
    '''
    def pollMotor(self):
        respStr = self.sendMotorCommand('0')
        return respStr
    
    '''
        This command is used to clear the Polling Status Word (PSW) bits
        
        Return: ACK only
    '''
    def clearPollStatus(self):
        self.sendMotorCommand('1 65535')
        return        
    
    '''
        The Stop command exits the executing program or motion.
    '''
    def motorStop(self):
        self.sendMotorCommand('3 0')
        return
    
    '''
        The Restart command is provided to cause the device to do a soft reset of the processor and logic circuits.
    '''
    def motorReset(self):
        self.sendMotorCommand('4')
        return
    
    '''
        This command zeros both the Target register and the Position register.
        This removes any Position Error that may exist. This is useful for homing
        routines to denote the current location as Zero so that all other
        locations can be defined as an offset from Zero.
    '''
    def zeroTargetPos(self, attempt_number = 1):
        respStr = self.sendMotorCommand('145')
        
        if (not ('*' in respStr) and (attempt_number < 5)):
            time.sleep(0.25)
            self.zeroTargetPos(attempt_number+1) 
        
        self.readPosition()        
        return             
    
    '''
    '''
    def waitForMotorStop(self):
        # Now wait for motor to indicate that it is finished before continuing
        # We do this by polling the motor repeatedly until the appropriate bit is set in the polling word 
        finished = False
        oldPosition = [0, 0]
        pollPosition = 0
        while not finished:
            oldPosition[1] = oldPosition[0]
            oldPosition[0] = pollPosition              
            pollPosition = self.readPosition()      # Dummy read
            
            time.sleep(0.1)
            pollPosition = self.readPosition()
            
            # if we're not moving, we're done
            if ((oldPosition[1] == oldPosition[0]) and (oldPosition[0] == pollPosition)):
                finished = True
            elif (abs(oldPosition[1] - oldPosition[0]) < 5) and (abs(oldPosition[0] - pollPosition) < 5):
                finished = True
            
        self.motorStop()
                          
    '''
        Check bit from the RIS command response
    '''
    def checkInternalStatus(self, bit):
        status = False
        
        # Chek RIS register: Read internal status word
        respStr = self.sendMotorCommand('20')
        
        if (len(respStr) == 15):
            respList = respStr.split()
            decPos = int(respList[3], 16) & (1 << bit)
            if (decPos > 0):
                status = True
        
        return status
    
    '''
        Read position from RRG command
    '''
    def readPosition(self):
        respStr = self.sendMotorCommand('12 1')
        
        # Parse response
        position = 0
        if (len(respStr) == 20):
            respList = respStr.split()
            upperWord = int(respList[3], 16) * 65536
            lowerWord = int(respList[4], 16)
            position = upperWord + lowerWord
            
        return position
           
    '''
        Move motor at absolute value
    '''
    def moveMotor(self, moveMotorPos, moveMotorVelocity, waitingForStop=True, stopEnable=0, stopCondition=0):
        self.pollMotor()
        self.clearPollStatus()
        
        # Set MAV(Move Absolute, Velocity Base) command
        cmdStr = "134 " + str(moveMotorPos) 
        if (self.UseXYTableAPS and (self.label == 'UpDown')): 
            cmdStr += " " + str(self.LiftAcceleration) + " "
        else:
            cmdStr += " 96637 "  
        cmdStr += str(moveMotorVelocity)
        cmdStr += " " + str(stopEnable) 
        cmdStr += " " + str(stopCondition)
        self.sendMotorCommand(cmdStr)
        
        if waitingForStop:
            self.waitForMotorStop()
            
        return
    
    '''
        Move motor relativiy from the current position
    '''
    def moveMotorRelative(self, moveMotorPos, moveMotorVelocity, waitingForStop=True, stopEnable=0, stopCondition=0):
        self.pollMotor()
        self.clearPollStatus()

        # Set MRV(Move Relative, Velocity Base) command
        cmdStr = "135 " + str(moveMotorPos) 
        cmdStr += " 3000 "  
        cmdStr += str(moveMotorVelocity)
        cmdStr += " " + str(stopEnable) 
        cmdStr += " " + str(stopCondition)
        respStr = self.sendMotorCommand(cmdStr)
        
        if waitingForStop:
            self.waitForMotorStop()
        
        return respStr
    