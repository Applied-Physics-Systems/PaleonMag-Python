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
    SHOW_FORMS          = 0xFFFE
    ENDTASK_SYSTEM_INIT = 0
    ENDTASK_MAG_INIT    = 1

    FLASH_DISPLAY_OFF_TIME = 10

    mainQueue = None
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
        captionStr = ''
        messageStr = None
        handlerStr = ''
        for message in messageList:
            if 'CaptionStr = ' in message:
                captionStr = message.replace('CaptionStr = ', '')
            if 'MessageStr = ' in message:
                messageStr = message.replace('MessageStr = ', '')
                messageStr = messageStr.replace(';', '\n')
            if 'FlashingStr = ' in message:
                self.flashingMessage = message.replace('FlashingStr = ', '')
            if 'HandlerStr = ' in message:
                handlerStr = message.replace('HandlerStr = ', '')
                
        if (messageStr != None):
            self.backgroundRunningFlag = False
            dlg = wx.MessageBox(messageStr, style=wx.YES_NO|wx.CENTER, caption=captionStr)
            if (dlg == wx.YES):
                if (handlerStr == 'HomeToCenter'):
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
                
            try:                    
                minValue = int(messageList[4].replace('MinValue = ', ''))
            except:
                minValue = 0
                
            try:
                maxValue = int(messageList[5].replace('MaxValue = ', ''))
            except:
                maxValue = 0
            
            newInput = -1
            while not ((newInput >= minValue) and (newInput <= maxValue)):
                dialog = wx.TextEntryDialog(None, message.replace(';', '\n'), title, str(inputValue))
                dialog.CenterOnScreen()                
                if (dialog.ShowModal() == wx.ID_OK):
                    inputStr = dialog.GetValue()
                    try:
                        newInput = int(inputStr)
                    except:
                        newInput = -1
        
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
    def parseDeviceMessages(self, endMessage):
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
                
        else:
            self.handleTaskMessage(endMessage)
                                                                                
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
                self.parent.registryControl.Show()
                self.parent.panelList['RegistryControl'] = self.parent.registryControl
            self.parent.updateProgressStatus('Tasks Completed')
            self.parent.setStatusColor('Green')
            
        elif (taskID == self.SHOW_FORMS):
            self.handleShowForms(processFunction[1])
            runFlag = False
        
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
    def handleShowForms(self, formParams):
        formID = formParams[0]
        functionID = formParams[1]
        if (formID == 'frmMeasure'):
            self.parent.frmMeasure.initForm(functionID)
            self.parent.frmMeasure.Show()
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
    