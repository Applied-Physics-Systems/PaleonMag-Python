'''
Created on Sep 25, 2025

@author: hd.nguyen
'''
import wx
import multiprocessing

from Forms.frmTip import frmTip
from Forms.frmFlashingStatus import frmFlashingStatus

from Hardware.DevicesControl import DevicesControl
from Modules.modConfig import ModConfig
from Process.DataExchange import DataExchange

devControl = DevicesControl()

'''
    Flashing message panel to show working in progress
'''
def flashingFunction(flashingMessage):
    app = wx.App(False)
    frmFlashingStatus(parent=None, message=flashingMessage)
    app.MainLoop()
    

'''
    Background task processing
'''
def workerFunction(processData, mainQueue, processQueue, taskID):    
    try:
        if isinstance(processData, str):
            mainQueue.put('None:Task Completed')
            mainQueue.put(processData)
            return
        modConfig = ModConfig(process=processData, queue=mainQueue)
        devControl.setDevicesConfig(modConfig)
        devControl.processQueue = processQueue
        
        deviceID = devControl.runTask(taskID)
        
        processData = devControl.updateProcessData()
                
        mainQueue.put(deviceID + ':Task Completed')    
        mainQueue.put(processData)
                
        devControl.closeDevices()
                
    except Exception as e:
        print(processData)
        print(e)
    
    return

'''
    -----------------------------------------------------------------
'''
class PaleoThread():
    '''
    classdocs
    '''    
    END_OF_SEQUENCE     = 0xFFFF
    PRE_THREAD_PROCESS  = 0xFFFE
    
    FRM_MAGNETOMETER_MAN_RUN = 0x0001
    
    ENDTASK_SYSTEM_INIT = 0
    ENDTASK_MAG_INIT    = 1

    FLASH_DISPLAY_OFF_TIME = 10

    mainQueue = None
    processQueue = None
    process = None    
    taskQueue = []        
    backgroundRunningFlag = False
    flashingCount = FLASH_DISPLAY_OFF_TIME
    flashingMessage = ''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
                                
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Display dialog box for message with option Yes/No
    '''
    def handleMessageBox(self, endMessage):
        messageList = endMessage.split(':')
        captionStr = 'PaleoMag'
        messageStr = None
        handlerStr = ''
        buttonStyle = wx.YES_NO|wx.CENTER
        for message in messageList:
            if 'CaptionStr = ' in message:
                captionStr = message.replace('CaptionStr = ', '')
            elif 'MessageStr = ' in message:
                messageStr = message.replace('MessageStr = ', '')
                messageStr = messageStr.replace(';', '\n')
            elif 'FlashingStr = ' in message:
                self.flashingMessage = message.replace('FlashingStr = ', '')
            elif 'HandlerStr = ' in message:
                handlerStr = message.replace('HandlerStr = ', '')
            elif 'Buttons = ' in message:
                buttonStr = message.replace('Buttons = ', '')
                if 'YES_NO' in buttonStr:
                    buttonStyle = wx.YES_NO|wx.CENTER
                elif 'OK' in buttonStr:
                    buttonStyle = wx.OK|wx.CENTER
                else:
                    buttonStyle = wx.YES_NO|wx.CENTER
                
        if (messageStr != None):
            self.backgroundRunningFlag = False
            dlg = wx.MessageBox(parent=self.parent, message=messageStr, style=buttonStyle, caption=captionStr)
            if (dlg == wx.YES):
                if (handlerStr == 'HomeToCenter'):
                    self.processQueue.put('Continue Flow:')
            elif (dlg == wx.OK):
                self.processQueue.put('Continue Flow:')
                                    
            else:
                self.processQueue.put('Task Aborted')
            self.backgroundRunningFlag = True
                    
        return
    
    '''
        Display dialog box for input data
    '''
    def handleInputBox(self, endMessage):
        messageList = endMessage.split(':')
        if (len(messageList) == 6):
            message = messageList[1].replace('Message = ', '')
            title =  messageList[2].replace('Title = ', '')
            
            try:
                inputValue = int(messageList[3].replace('InputValue = ', ''))
            except:
                inputValue = 0
                
            checkMin = False
            try:                    
                minValue = int(messageList[4].replace('MinValue = ', ''))
                checkMin = True
            except:
                minValue = 0
                
            checkMax = False
            try:
                maxValue = int(messageList[5].replace('MaxValue = ', ''))
                checkMax = True
            except:
                maxValue = 0
            
            newInput = -1
            validInput = False
            while not validInput:
                dialog = wx.TextEntryDialog(None, message.replace(';', '\n'), title, str(inputValue))
                dialog.CenterOnScreen()                
                if (dialog.ShowModal() == wx.ID_OK):
                    inputStr = dialog.GetValue()
                    try:
                        newInput = float(inputStr)
                        validInput = True
                        if checkMin:
                            if (newInput < minValue):
                                validInput = False
                        if checkMax:
                            if (newInput > maxValue):
                                validInput = False
                    except:
                        validInput = False
        
                dialog.Destroy()
            self.processQueue.put('Continue Flow:' + str(newInput))
                    
        return
    
    '''
        string format
            message_0:message_1: ... :message_n
        message_x format
            label = value
    '''
    def handleTaskMessage(self, endMessage):
        messageList = endMessage.split(':')
        if (len(messageList) > 1):
            if messageList[0] in self.parent.panelList.keys():
                self.parent.panelList[messageList[0]].updateGUI(messageList[1:])
        return
    
    '''
        Update program status in the status bar
    '''
    def handleProgramStatus(self, endMessage):
        messageList = endMessage.split(':')
        self.parent.updateTaskStatus(messageList[1])
        return

    '''
    '''
    def handleSetCodeLevel(self, endMessage):
        messageList = endMessage.split(':')
        if (messageList[1] == 'CodeOrange'):
            self.parent.messageBox.SetBackgroundColour('Orange')
        elif (messageList[1] == 'CodeRed'):
            self.parent.messageBox.SetBackgroundColour('Red')
        elif (messageList[1] == 'CodeBlue'):
            self.parent.messageBox.SetBackgroundColour('Cyan')
            
        return

    '''
        If the number of message greater than 2,
        Else display the waring message in the dialog message box 
    '''
    def handleWarningMessage(self, endMessage):
        messageList = endMessage.split(':')
        if (len(messageList) > 2):
            self.parent.updateProgressStatus(messageList[2])
        else:
            wx.MessageBox(messageList[1], style=wx.OK|wx.CENTER, caption='Warning!')
        return
    
    '''
        1. Turn the panel red with error message
        
        2. Display dialog box for the error message
        
        3. After the dialog box error message, turn back the panel to cyan
    '''
    def handleErrorMessage(self, endMessage):
        self.taskQueue = []
        messageList = endMessage.split(':')
        if (len(messageList) > 2):    
            self.parent.messageBox.SetBackgroundColour('Red')           
            wx.MessageBox(messageList[2], caption='PaleonMag')
            self.parent.messageBox.SetBackgroundColour('Cyan')
            
        return
    
    '''
    '''
    def handleTaskCompleted(self, endMessage):
        self.parent.modConfig.processData = self.mainQueue.get()                    
                                                                                                
        # Clean up end of task
        messageList = endMessage.split(':')
        if messageList[0] in self.parent.panelList.keys():
            self.parent.panelList[messageList[0]].runEndTask()  
                            
        # Start new process
        self.backgroundRunningFlag = False
        if (len(self.taskQueue) > 0):
            self.startProcess()
                
        else:
            self.parent.appendMessageBox('Tasks Completed\n')
            self.parent.updateProgressStatus('Tasks Completed')
            self.parent.setStatusColor('Green')
            self.parent.timer.Stop()
            
        return

    '''
    '''
    def handleDictionaryType(self, messageDict):
        try:
            selectedForm = messageDict['Form'] 
            if selectedForm in self.parent.panelList.keys():
                self.parent.panelList[selectedForm].updateGUI(messageDict)
        except:
            return
        
        return
    
    '''
    '''
    def parseDeviceMessages(self, endMessage):
        if isinstance(endMessage, dict):
            self.handleDictionaryType(endMessage)
            
        else:
            if ('Task Completed' in endMessage):
                self.handleTaskCompleted(endMessage)
                                            
            elif ('Error:' in endMessage):
                self.handleErrorMessage(endMessage)
                    
            elif ('MessageBox:' in endMessage):
                self.handleMessageBox(endMessage)
                    
            elif ('InputBox:' in endMessage):
                self.handleInputBox(endMessage)
                
            elif ('Warning:' in endMessage):
                self.handleWarningMessage(endMessage)
                    
            elif ('Program Status:' in endMessage):
                self.handleProgramStatus(endMessage)
    
            elif ('SetCodeLevel:' in endMessage):
                self.handleSetCodeLevel(endMessage)
                    
            else:
                self.handleTaskMessage(endMessage)
                                                                                
        return
        
    '''
    '''
    def sendData(self, dataType, dataStruc):
        if (dataType == 'Sample'):
            dataHolder = DataExchange.parseSampleHolder(dataStruc)
            
        self.processQueue.put(dataHolder)
        return

    '''
        before running a task in a queue, sometime there is a need to update the data
    '''
    def runPreThreadProcess(self, taskID):
        if (taskID == self.FRM_MAGNETOMETER_MAN_RUN):
            self.parent.magControl.manualPage.setMeasurementManualSample()
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Multiprocessing Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
        Before running process in a different thread, do the neccessaries in GUI thread 
    '''
    def startProcess(self):
        runFlag = True
        
        processFunction = self.taskQueue.pop(0)
        taskID = processFunction[0]         
        if (taskID == self.END_OF_SEQUENCE):
            runFlag = False
            paramList = processFunction[1]
            sequenceType = paramList[0]
            if (sequenceType == self.ENDTASK_SYSTEM_INIT):
                tipBox = frmTip(parent=self.parent)
                tipBox.Show()        
            
            elif (sequenceType == self.ENDTASK_MAG_INIT):          
                self.parent.FLAG_MagnetInit = True        # We're done initializing
                self.parent.frmSampleIndexRegistry.Show()
                self.parent.panelList['frmSampleIndexRegistry'] = self.parent.frmSampleIndexRegistry
            self.parent.updateProgressStatus('Tasks Completed')
            self.parent.setStatusColor('Green')
                    
        elif (taskID == self.PRE_THREAD_PROCESS):
            runFlag = False
            self.runPreThreadProcess(processFunction[1])
            
        else:
            if (taskID in self.parent.devControl.messages.keys()):
                self.parent.appendMessageBox(self.parent.devControl.messages[taskID] + '\n')
            self.flashingMessage = None
        
        if runFlag:
            self.backgroundRunningFlag = True
            self.runProcess(processFunction)
        
    '''
        Start a new process which can run concurrently on another CPU core to avoid GUI hangup
    '''
    def runProcess(self, taskID):
        self.parent.timer.Stop()
        self.mainQueue = multiprocessing.Queue()
        self.processQueue = multiprocessing.Queue()
        
        self.process = multiprocessing.Process(target=workerFunction, args=(self.parent.modConfig.processData, self.mainQueue, self.processQueue, taskID))        
        
        self.process.start()
        self.parent.timer.Start(int(200))      # Checking every 200ms 
                
    '''
        Check for task completion
    '''
    def checkProcess(self):
        if (self.process != None):
            try:
                queueSize = self.mainQueue.qsize()
                if (queueSize > 0):
                    for _ in range(0, queueSize):                
                        endMessage = self.mainQueue.get_nowait()
                        self.parseDeviceMessages(endMessage)
                    
            except:
                queueSize = 0
                
            if (self.backgroundRunningFlag):
                self.flashingCount += 1
                if ((self.flashingCount > self.FLASH_DISPLAY_OFF_TIME) and (self.flashingMessage != None)): 
                    flashingProcess = multiprocessing.Process(target=flashingFunction, args=(self.flashingMessage,))
                    flashingProcess.start()
                    self.flashingCount = 0
            else:
                self.flashingCount = 0
                    
        return
    
    '''
        
    '''
    def pushTaskToQueue(self, taskFunction):
        self.taskQueue.append(taskFunction)
        # if no background process running, start one
        if not self.backgroundRunningFlag:
            if (len(self.taskQueue) > 0):
                self.startProcess()
                
        return
    
    '''
        Input: dictionary with 'DataType'
    '''
    def sendDataToWorkerThread(self, dataDict):
        self.processQueue.put(dataDict)
        return
    