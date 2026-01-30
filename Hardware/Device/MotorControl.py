'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import os
import time
import configparser

from Hardware.Device.SerialPortDevice import SerialPortDevice
from Modules.modConfig import ModConfig

'''
    Notice: Unit ID should be set to 16 on the QuickSilver program.
'''
class MotorControl(SerialPortDevice):
    '''
    classdocs
    '''
    queue = None

    def __init__(self, baudRate, pathName, comPort, Label, parent=None):
        '''
        Constructor
        '''                
        self.parent = parent
        self.MotorAddress = '16'        
        SerialPortDevice.__init__(self, baudRate, 'MotorControl', pathName, comPort, Label, parent.modConfig)
               
    '''--------------------------------------------------------------------------------------------
                        
                        Elementary Motor Command Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Initialize Motor
    '''
    def motorCommConnect(self):
        self.sendString('@255 173 416\r\n')
        
        if 'UpDown' in self.label:
            self.setTorque(self.modConfig.UpDownTorqueFactor, 
                           self.modConfig.UpDownTorqueFactor, 
                           self.modConfig.UpDownTorqueFactor, 
                           self.modConfig.UpDownTorqueFactor)
            
        self.modConfig.processData.PortOpen[self.label] = True
        
        self.readPosition()

    '''
    '''    
    def setTorque(self, ClosedHold, ClosedMove, OpenHold, OpenMove):
        PerTorque = 0.01 * self.modConfig.UpDownMaxTorque     #Value for 1% torque

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
        if not self.modConfig.processData.PortOpen[self.label]:
            self.motorCommConnect()
                
        cmdStr = '@' + self.MotorAddress + ' ' + cmdStr
        self.sendString( cmdStr + '\r\n')
        
        time.sleep(0.01)        # Sleep for 100 ms

        respStr = self.readLine()
        resplist = respStr.split('\n')
                
        # Send Command and its response to the GUI
        if (self.modConfig.queue != None):
            self.modConfig.queue.put('frmDCMotors:Command Exchange: ' + self.label + ';' + cmdStr + ';' + resplist[0])
                
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
    def ZeroTargetPos(self, attempt_number = 1):
        respStr = self.sendMotorCommand('145')
        
        if (not ('*' in respStr) and (attempt_number < 5)):
            time.sleep(0.25)
            self.ZeroTargetPos(attempt_number+1) 
        
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
            time.sleep(0.01)
            
            if (self.label == 'UpDown'):                
                self.parent.UpDownHeight()
            elif (self.label == 'Turning'):
                self.parent.TurningMotorAngle()
            elif (self.label == 'ChangerX'):
                self.parent.ChangerHole()
            elif (self.label == 'ChangerY'):
                self.parent.ChangerHole()
            
            pollPosition = self.readPosition()
            
            # if we're not moving, we're done
            if ((oldPosition[1] == oldPosition[0]) and (oldPosition[0] == pollPosition)):
                finished = True
            elif (abs(oldPosition[1] - oldPosition[0]) < 5) and (abs(oldPosition[0] - pollPosition) < 5):
                finished = True
                
        self.motorStop()
        return
                          
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
        
        Return position in integer
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
            if (position > 0x7FFFFFFF):
                position -= 0x100000000
            
        return position
           
    '''
        Move motor at absolute value, velocity base
    '''
    def moveMotor(self, moveMotorPos, moveMotorVelocity, waitingForStop=True, stopEnable=0, stopCondition=0):
        # Send Command and its response to the GUI
        if (self.modConfig.queue != None):
            self.modConfig.queue.put('frmDCMotors:Motor Info: ' + self.label + ';Position ' + str(moveMotorPos) + ';Velocity ' + str(int(moveMotorVelocity)))
        
        self.pollMotor()
        self.clearPollStatus()
        
        # Set MAV(Move Absolute, Velocity Base) command
        cmdStr = "134 " + str(moveMotorPos) 
        if (self.modConfig.UseXYTableAPS and (self.label == 'UpDown')): 
            cmdStr += " " + str(self.modConfig.LiftAcceleration) + " "
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
        Move motor at absolute value, time base
    '''
    def moveMotorOnTime(self, moveMotorPos, moveMotorAcceleration, waitingForStop=True, stopEnable=0, stopCondition=0):
        # Send Command and its response to the GUI
        if (self.modConfig.queue != None):
            self.modConfig.queue.put('frmDCMotors:Motor Info: ' + self.label + ';Position ' + str(moveMotorPos) + ';Acceleration ' + str(moveMotorAcceleration))
        
        self.pollMotor()
        self.clearPollStatus()
        
        # Set MAV(Move Absolute, Velocity Base) command
        cmdStr = "176 " + str(moveMotorPos) + " "
        cmdStr += str(moveMotorAcceleration) + " 8333 "
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
    
    '''
    '''
    def relabelPos(self, position):
        iPosition = int(position)
        while (abs(self.readPosition() - iPosition) > 10):
            self.ZeroTargetPos()
            # @16 11 10 num 'load register
            self.sendMotorCommand('11 10 ' + str(-1*iPosition))
            # @16 165 1802 ' subtract register 10 from T&P
            self.sendMotorCommand('165 1802')
            
        return 
    
    '''
    '''
    def runTask(self, taskID):
        
        # Test read current position
        if (taskID == 0):
            position = self.readPosition()
            print(position)
            
        # Test move to absolute position on time base
        elif (taskID == 1):
            position = -8000
            moveMotorVelocity = 83      # 0.1 second acceleration
            self.moveMotorOnTime(position, moveMotorVelocity)
            
        # Search for the corner switch
        elif (taskID == 2):
            relativePosition = 50000
            motorID = self.label
            if 'UpDown' in motorID:
                speed = speed = self.modConfig.LiftSpeedNormal
                switch = 4
            elif 'ChangerX' in motorID:
                speed = self.modConfig.ChangerSpeed
                switch = 4
            elif 'ChangerY' in motorID:
                speed = self.modConfig.ChangerSpeed
                switch = 5
            
            searchFlag = True
            self.moveMotorRelative(relativePosition, speed, False, 0, 0)
            while searchFlag: 
                if (self.checkInternalStatus(switch) == False):
                    self.motorStop()
                    currentPosition = self.readPosition()
                    print(currentPosition)                    
                    searchFlag = False
                    
        # Search for the center switch
        elif (taskID == 3):
            relativePosition = -50000
            motorID = self.label
            if 'UpDown' in motorID:
                speed = speed = self.modConfig.LiftSpeedNormal
                switch = 4
            elif 'ChangerX' in motorID:
                speed = self.modConfig.ChangerSpeed
                switch = 5
            elif 'ChangerY' in motorID:
                speed = self.modConfig.ChangerSpeed
                switch = 6
            
            searchFlag = True
            self.moveMotorRelative(relativePosition, speed, False, 0, 0)
            while searchFlag: 
                if (self.checkInternalStatus(switch) == False):
                    self.motorStop()
                    currentPosition = self.readPosition()
                    print(currentPosition)                    
                    searchFlag = False
            
        elif (taskID == 4):
            self.motorStop()
            
        elif (taskID == 5):
            searchFlag = True
            switch = 5
            while searchFlag: 
                if (self.checkInternalStatus(switch) == False):
                    currentPosition = self.readPosition()
                    print(currentPosition)                    
                    searchFlag = False
                    
        # print limit switch
        elif (taskID == 6):
            switch = 6
            print(self.checkInternalStatus(switch))
                            
'''
'''    
if __name__=='__main__':
    try:    
        pathName = os.getcwd() + '\\'
        config = configparser.ConfigParser()
        config.read('C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
        modConfig = ModConfig(config=config)          
        motorID = 'ChangerY'         
        if 'ChangerX' in motorID:
            comPort = 'COM27'
        elif 'ChangerY' in motorID:
            comPort = 'COM28'
        elif 'UpDown' in motorID:
            comPort = 'COM29'
        elif 'Turning' in motorID:
            comPort = 'COM30'
        motorControl = MotorControl(57600, pathName, comPort, motorID, modConfig)
        
        motorControl.runTask(3)
                
        motorControl.closeDevice()
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))

    
            