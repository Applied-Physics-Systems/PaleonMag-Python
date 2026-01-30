'''
Created on Jan 21, 2025

@author: hd.nguyen
'''
import time

from Hardware.Device.SerialPortDevice import SerialPortDevice

from ClassModules.Cartesian3D import Cartesian3D

class SQUIDControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate, pathName, comPort, Label, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.label = Label
        self.PortOpen = False 
                
        SerialPortDevice.__init__(self, baudRate, 'SQUIDControl', pathName, comPort, Label, self.parent.modConfig)
                
    '''
    '''
    def getResponse(self):
        respStr = self.readLine()
        
        return '', respStr    
    
    '''
    '''
    def readCount(self, activeAxis):
        cmdStr = activeAxis + 'LC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'SC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def readData(self, activeAxis):
        cmdStr = activeAxis + 'LD\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        cmdStr = activeAxis + 'SD\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def ReadRange(self, activeAxis):
        cmdStr = activeAxis + 'SSR\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
        
        respStr = self.readLine()
        
        return cmdStr, respStr 
        
    '''
    '''
    def resetCount(self, activeAxis):
        cmdStr = activeAxis + 'RC\r'
        self.sendString(cmdStr)
        time.sleep(0.012)
                
        return cmdStr, '' 

    '''
    '''
    def configure(self, activeAxis):
        time.sleep(0.5)
        cmdStr = activeAxis + 'CR1\r'
        self.sendString(cmdStr)
        time.sleep(0.12)
        cmdStr = activeAxis + 'CLC\r'
        self.sendString(cmdStr)
        time.sleep(0.12)
        cmdStr = activeAxis + 'CSE\r'
        self.sendString(cmdStr)
        time.sleep(0.12)
        cmdStr = activeAxis + 'CF1\r'
        self.sendString(cmdStr)
        time.sleep(0.12)
        cmdStr = activeAxis + 'CLP\r'
        self.sendString(cmdStr)
        time.sleep(0.12)        
                
        return cmdStr, '' 
        
    '''
    '''
    def changeRate(self, activeAxis, rate):
        if (rate == 'F'):            
            cmdStr = activeAxis + 'CSE\r'
            self.sendString(cmdStr)
            time.sleep(0.012)
            cmdStr = activeAxis + 'CR1\r'
            self.sendString(cmdStr)
            time.sleep(0.012)

        else:            
            cmdStr = activeAxis + 'CR' + rate + '\r'
            self.sendString(cmdStr)
            time.sleep(0.012)
            
        return cmdStr, ''
    
    '''
    '''
    def ChangeRange(self, axis, ChangeRangeSelected):
        #Select Case ChangeRangeSelected
        if (ChangeRangeSelected == "F"):
            '''
                Set the system up for the extended range flux
                counting stuff. First, enable (turn ON) the
                fast-slew
            '''
            self.sendString(axis + "CSE\r")
            self.sendString(axis + "CR1\r")     # All control rate 1
            
        elif ((ChangeRangeSelected ==  "1") or 
              (ChangeRangeSelected == "T") or 
              (ChangeRangeSelected == "H") or 
              (ChangeRangeSelected == "E")):
            self.sendString(axis + "CR" + ChangeRangeSelected + "\r")
            
        else:
            # This should never happen            
            MsgBox = "Error occurred in ChangeRangeButton: " 
            MsgBox += "invalid range specifed: " + ChangeRangeSelected 
            caption = "ERROR!"
            self.parent.displayMessageBox(caption=caption, message=MsgBox)

        return
   
    '''
    '''
    def latchVal(self, direction = "A", withDelay = False):
        # If Prog_halted Then Exit Sub ' (September 2007 L Carporzen) New version of the Halt button
        if withDelay:
            self.parent.displayStatusBar("Settling...")
            time.sleep(self.parent.modConfig.ReadDelay)
            self.parent.displayStatusBar("")
        
        if (direction == "A"):
            self.LatchCount("A")
            self.LatchData("A")
            
        elif (direction == "X"):
            self.LatchCount("X")
            self.LatchData("X")
            
        elif (direction == "Y"):
            self.LatchCount("Y")
            self.LatchData("Y")
            
        elif (direction == "Z"):
            self.LatchCount("Z")
            self.LatchData("Z")
            
        return
    
    '''
        This function takes a string representing the axis
        being measured, a value measured from the axis,
        and returns a calibrated value, using constants
        previously read from a file.
    '''
    def Calibrate(self, axis, val):
        calibrate = 0.0
        #Select Case axis
        if (axis == "X"):
            calibrate = val * self.parent.modConfig.XCal
        elif (axis == "Y"):
            calibrate = val * self.parent.modConfig.YCal
        elif (axis == "Z"):
            calibrate = val * self.parent.modConfig.ZCal
        else:
            MsgBox = "Error occured in frmSQUID.Calibrate:\n" 
            MsgBox += "Invalid axis argument given to the function."
            self.parent.displayMessageBox(message=MsgBox)

        return calibrate
    
    '''
        This function automatically swtiches the line accessed by
        COM 2 to the 2G Squid boxes, and reads in the value of the
        axis described by 'dir'.  If this is the first zero
        measurement, then isFirstZero should be true
    '''
    def getVal(self, direction, AlreadyLatched=False):        
        if not AlreadyLatched:
            self.latchVal(direction, False)
        
        Count = self.SendCount(direction)
        data = self.SendData(direction)          # Read data
        
        # Check to make sure we're on the right scale ...
        modeFluxCount = True  # !!! Flux counting mode not implemented
        if not modeFluxCount:
            '''
                Ask for range on Squid boxes
                Read range
            '''
            _, rangeStr = self.ReadRange(direction)   # Response like "R1"
            if "1" in rangeStr:
                rangeval = 1
            elif "T" in rangeStr:
                rangeval = 10
            elif "H" in rangeStr:
                rangeval = 100
            elif "E" in rangeStr:
                rangeval = 1000
            else:
                MsgBox = "Error occurred in Measure_getVal:\n" 
                MsgBox += "Invalid range read from 2G Squid boxes: " + rangeStr
                self.parent.displayMessageBox(message=MsgBox)

        else:
            # In flux counting mode, don't need to ask for range
            rangeval = 1
        
        getVal = -1*(data) - Count * rangeval
        return getVal
    
    '''
        This function returns the data gathered from the three axes
        in the magnetometer, reading the squid boxes.
    '''
    def getData(self, AlreadyLatched = False):
        #Dim X As Double, Y As Double, Z As Double
        getData = Cartesian3D()
        if not AlreadyLatched:
            self.latchVal("A", True)   # latch values with delay for a short time
            
        # Gather data from squid boxes
        X = self.getVal("X", True)
        Y = self.getVal("Y", True)
        Z = self.getVal("Z", True)
        
        # Calibrate the data just received
        getData.X = self.Calibrate("X", X)
        getData.Y = self.Calibrate("Y", Y)
        getData.Z = self.Calibrate("Z", Z)

        return getData

    '''
    '''
    def SendCount(self, axis):
        self.sendString(axis + "SC\r")
        sendCount = self.readInt()
        return sendCount 
    
    '''
    '''
    def SendData(self, axis):
        self.sendString(axis + "SD\r")
        sendData = self.readFloat()
        return sendData

    '''
    '''    
    def LatchCount(self, axis):
        self.sendString(axis + "LC\r")
        time.sleep(0.1)
        return
    
    '''
    '''
    def LatchData(self, axis):
        self.sendString(axis + "LD\r")
        time.sleep(0.12)
        return
    
    '''
    '''
    def setCfg(self, activeAxis, cfg):
        cmdStr = activeAxis + cfg + '\r'
        self.sendString(cmdStr)
            
        return cmdStr, ''
    
    '''
    '''
    def CLP(self, axis):
        self.sendString(axis + "CLP\r")
        return
   
    '''
    '''
    def ResetCount(self, axis):
        self.sendString(axis + "RC\r")
        return
   
    '''--------------------------------------------------------------------------------------------
                        
                        IRM/ARM Public API Functions
                        
    --------------------------------------------------------------------------------------------'''                
    def Disconnect(self):
        self.PortOpen = False
        return
    
    