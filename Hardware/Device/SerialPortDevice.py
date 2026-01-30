import serial
import array
import os
import time

ComPortDict = {'COM1' : 0,
               'COM2' : 1,
               'COM3' : 2,
               'COM4' : 3,
               'COM5' : 4,
               'COM6' : 5,
               'COM7' : 6,
               'COM8' : 7,
               'COM9' : 8}
ParityDict = {'EVEN': serial.PARITY_EVEN,
              'MARK':serial.PARITY_MARK,
              'NAMES':serial.PARITY_NAMES,
              'NONE':serial.PARITY_NONE,
              'ODD':serial.PARITY_ODD,
              'SPACE':serial.PARITY_SPACE}

class SerialPortDevice():
    serialDevice = None
    DeviceDictionary = None
    EOT_CHARACTER = '\x04'
    label = ''
    active = False
    modConfig = None
    
    def __init__(self, baudRate, deviceName, pathName, comPort, Label, modConfig):
        self.label = Label
        self.modConfig = modConfig
        self.PortOpen = False 
        self.comPortValidFlag = False
        self.interruptReadLineFlag = False
        try:            
            self.DeviceDictionary = {}
            # Build dictionary for the instrument
            if 'Hardware\\Hardware' in pathName:
                pathName = pathName.replace('Hardware\\Hardware\\', 'Hardware\\')
            with open( pathName + deviceName + '.txt', 'rt') as deviceFile:
                for line in deviceFile:
                    line = str.strip(line)
                    if line != '':                    
                        deviceCommandList = line.split(';')
                        key = deviceCommandList[0]
                        deviceCommandList.pop(0)
                        self.DeviceDictionary[key] = deviceCommandList
                                    
            # Create instrument module
            port = comPort
            byteSize = self.convertCommandListToString(['BYTESIZE'])
            parity = self.convertCommandListToString(['PARITY'])
            stopBits = self.convertCommandListToString(['STOPBITS'])
            if (self.convertCommandListToString(['TIMEOUT'])=='None'):
                timeOut = None
            else:
                timeOut = int(self.convertCommandListToString(['TIMEOUT'])) 
            if (self.convertCommandListToString(['WRITE_TIMEOUT'])=='None'):
                writeTimeout = None
            else:
                writeTimeout = int(self.convertCommandListToString(['WRITE_TIMEOUT'])) 
            xonXoff = self.convertCommandListToString(['XONXOFF'])
            rtsCts = self.convertCommandListToString(['RTSCTS'])
                            
            if not 'COM-1' in comPort:
                self.comPortValidFlag = True
                self.serialDevice = serial.Serial()
                self.serialDevice.port = port 
                self.serialDevice.baudrate = int(baudRate)
                self.serialDevice.bytesize = int(byteSize)
                self.serialDevice.parity = ParityDict[parity]
                self.serialDevice.stopbits = int(stopBits)
                self.serialDevice.timeout = timeOut
                self.serialDevice.writeTimeout = writeTimeout
                self.serialDevice.xonxoff = int(xonXoff)
                self.serialDevice.rtscts = int(rtsCts)
                
                if not self.serialDevice.isOpen():
                    self.serialDevice.open()
                    self.active = True
                print(self.serialDevice.portstr)
            else:
                raise ValueError('Warning: Invalid Port Number')    
            
        except:
            errorMsg = 'Error: {0} is used by other software'.format(port) 
            print(errorMsg)
            raise Exception(errorMsg)
                
    #===========================================================================
    # Convert a list of commands chunk into one string
    # Input: None
    # Output: Instrument identification string
    def convertCommandListToString(self, commandList):
        try:
            commandString = self.DeviceDictionary[commandList[0]]
            command = ''
            for item in commandString:
                if item=='$VALUE$':
                    command = command + str(commandList[1])
                elif item=='$VALUE2$':
                    command = command + str(commandList[2])
                else:
                    command = command + item
            return command
        except KeyError:
            return ''
        
    #===================================================================================================
    # Send command to the serial device
    #---------------------------------------------------------------------------------------------------
    def sendCommand(self, commandStr, echoEnable):
        self.clearUartBuffer()
        self.serialDevice.write(commandStr + '\r')
        
        if (echoEnable):
            cmdSize = len(commandStr) + 1
            time.sleep(0.01)
            echoStr = ''
            echoStatus = True
            readSize = 0
            toReadSize = 0
            while echoStatus:
                byteSize = self.serialDevice.inWaiting()
                if ((byteSize+readSize)>cmdSize):
                    toReadSize = cmdSize - readSize
                else:
                    toReadSize = byteSize - readSize
                readSize += toReadSize  
                for _ in range(0, toReadSize):
                    readByte = self.readByte()
                    echoStr += readByte
                    if (readByte == '\r'):
                        if (commandStr in echoStr):
                            echoStatus = False
                            break

    #===================================================================================================
    # Send command to the serial device
    #---------------------------------------------------------------------------------------------------
    def sendString(self, commandStr):
        self.clearUartBuffer()    
        time.sleep(0.1)    
        self.serialDevice.write(commandStr.encode())
        
        return

    #===================================================================================================
    # Send command to the serial device
    #---------------------------------------------------------------------------------------------------
    def sendKey(self, echoEnable, keyChar):
        self.serialDevice.write(keyChar)
        if (echoEnable):
            self.readByte()

    #===================================================================================================
    # Check number of sample waiting to be received
    #---------------------------------------------------------------------------------------------------
    def inWaiting(self):
        return self.serialDevice.inWaiting()

    #===================================================================================================
    # Check number of sample waiting to be sent
    #---------------------------------------------------------------------------------------------------
    def outWaiting(self):
        return self.serialDevice.outWaiting()

    #===================================================================================================
    # Send command to the serial device
    #---------------------------------------------------------------------------------------------------
    def sendBinaryCommand(self, commandList):
        commandStr = array.array('B', commandList).tostring()
        self.serialDevice.write(commandStr)

    #===================================================================================================
    # Read a byte from the device
    #---------------------------------------------------------------------------------------------------
    def readByte(self):
        readCharacter = self.serialDevice.read()
        
        return  readCharacter

    #===================================================================================================
    # Read a binary byte from the device and convert to ascii
    #---------------------------------------------------------------------------------------------------
    def readBinaryByte(self):
        readCharacter = self.serialDevice.read()
        readData = readCharacter.encode('hex')
        
        return  readData
    
    #===================================================================================================
    # Read a line from the device
    #---------------------------------------------------------------------------------------------------
    def readLine(self):
        readCharacters = ""
        readLine = ''
        keepReading = True
        while keepReading:
            readCharacters = self.serialDevice.read(self.serialDevice.in_waiting).decode('utf-8')
            readLine += readCharacters
            if (('\x04' in readLine) or ('\n' in readLine) or ('\r' in readLine) or ('\0' in readLine) or self.interruptReadLineFlag):
                keepReading = False 
                    
        return readLine 

    #===================================================================================================
    # Read an interger from the device
    #---------------------------------------------------------------------------------------------------
    def readFloat(self):
        respStr = self.readLine()
        try:
            readValue = float(respStr)
        except:
            readValue = 0.0
            
        return readValue

    #===================================================================================================
    # Read an interger from the device
    #---------------------------------------------------------------------------------------------------
    def readInt(self):
        respStr = self.readLine()
        try:
            readValue = int(respStr)
        except:
            readValue = 0
            
        return readValue

    #===================================================================================================
    # Read a line from the device
    # Input: Start of package, end of package(1st byte), end of package(2nd byte)
    # Output: binary package
    #---------------------------------------------------------------------------------------------------
    def readBinaryPackage(self, SOP, EOP_0, EOP_1):
        try:
            binaryList = []
            asciiList = []
            # Search for beginning of binary package
            SOP_flag = False
            while (SOP_flag==False):
                readCharacter = self.serialDevice.read()
                readData = readCharacter.encode('hex')
                asciiList.append(readData)
                intCharacter = int(readData, 16)
                if (intCharacter==SOP):
                    binaryList.append(intCharacter)
                    SOP_flag = True
    
            # Read until end of package is found        
            EOP_flag = False
            first_EOP = False
            while (EOP_flag==False):
                    readCharacter = self.serialDevice.read()
                    readData = readCharacter.encode('hex')
                    asciiList.append(readData)
                    intCharacter = int(readData, 16)
                    binaryList.append(intCharacter)
                    if (first_EOP==True):
                        if (intCharacter==EOP_1):
                            EOP_flag = True
                        else:
                            first_EOP = False
                    elif (intCharacter==EOP_0):
                        first_EOP = True
                        
            return [binaryList, asciiList]
        except:
            return [[], []]

    #===================================================================================================
    # set end of tranmission character
    #---------------------------------------------------------------------------------------------------
    def setEOTCharacter(self, EOTChar):
        self.EOT_CHARACTER = EOTChar
                        
    #===================================================================================================
    # Wait for data to come in
    #---------------------------------------------------------------------------------------------------
    def waitForData(self):
        readCharacter = '\x00'
        serialData = ''
        EOT_Flag = True
        counter = 0
        while ((EOT_Flag==True)and(counter<10)):
            readCharacter = self.serialDevice.read()
            if (readCharacter==self.EOT_CHARACTER):
                EOT_Flag = False
            serialData += readCharacter 
            time.sleep(1)
            data_left = self.serialDevice.inWaiting()
            readCharacter = self.serialDevice.read(data_left)
            if (readCharacter.find(self.EOT_CHARACTER)!=-1):
                EOT_Flag = False
            serialData += readCharacter
            counter += 1
            
        return serialData 

    #===================================================================================================
    # clear UART buffer
    #---------------------------------------------------------------------------------------------------
    def clearUartBuffer(self):
        self.serialDevice.flushInput()
        self.serialDevice.flushOutput()
        self.serialDevice.reset_input_buffer()
        self.serialDevice.reset_output_buffer()
        return
        
    #===================================================================================================
    # Open device serial port
    #---------------------------------------------------------------------------------------------------
    def openDevice(self):
        if self.comPortValidFlag:
            if not self.serialDevice.isOpen():
                self.serialDevice.open()
            
            return self.serialDevice.isOpen()
        
        else:
            return False
        
    #===================================================================================================
    # Read a line from the device that end with LF
    #---------------------------------------------------------------------------------------------------
    def closeDevice(self):
        self.serialDevice.close()
    
    #===================================================================================================
    # Return port status
    #---------------------------------------------------------------------------------------------------
    def isOpen(self):
        if self.comPortValidFlag:
            return self.serialDevice.isOpen()
        else:
            return False    
    
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd()
        Test = SerialPortDevice(9600, 'IrmArmControl', currentPath)
        serialData = Test.waitForData()
        print(serialData)
        Test.closeDevice()
        
    except:
        print('Error!!')
        