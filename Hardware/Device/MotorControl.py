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
        
        # parameters from INI file
        self.UpDownTorqueFactor = 40
        self.UpDownMaxTorque = 32000
        self.LiftAcceleration = 90000
        self.UseXYTableAPS = False
        
        self.MotorAddress = '16'
        SerialPortDevice.__init__(self, baudRate, 'MotorControl', pathName, comPort)
       
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary Motor Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Initialize Motor
    '''
    def motorCommConnect(self):
        self.sendString('@255 173 416\r')
        
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
        self.sendString(cmdStr + '\r')
        
        respStr = self.readLine()
        
        return respStr

    '''
        Format the command string to the Silver Lode Command
    '''
    def sendMotorCommand(self, cmdStr):
        if not self.PortOpen:
            self.motorCommConnect()
         
        self.sendString('@' + self.MotorAddress + ' ' + cmdStr + '\r')
        
        time.sleep(0.05)        # Sleep for 100 ms

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
        This command zeros both the Target register and the Position register.
        This removes any Position Error that may exist. This is useful for homing
        routines to denote the current location as Zero so that all other
        locations can be defined as an offset from Zero.
    '''
    def zeroTargetPos(self):
        self.sendMotorCommand('145')        
        return 
            
   
    '''
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
    
    