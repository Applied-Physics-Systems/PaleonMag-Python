'''
Created on Sep 25, 2025

@author: hd.nguyen
'''
import wx
import multiprocessing

from Forms.frmTip import frmTip
from Forms.frmCalibrateCoils import frmCalibrateCoils
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
def workerFunction(processData, mainQueue, taskID):    
    try:
        if isinstance(processData, str):
            mainQueue.put('None:Task Completed')
            mainQueue.put(processData)
            return
        modConfig = ModConfig(process=processData, queue=mainQueue)
        devControl.setDevicesConfig(modConfig)
        
        deviceID = devControl.runTask(mainQueue, taskID)
        
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
    def parseDeviceMessages(self, endMessage): 
        if ('Task Completed' in endMessage):
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
                self.parent.statusBar.SetStatusText('Tasks Completed', 1)
                self.parent.setStatusColor('Green')
                self.parent.timer.Stop()
                                        
        elif ('Error:' in endMessage):
            self.taskQueue = []
            messageList = endMessage.split(':')
            if (len(messageList) > 2):    
                self.parent.messageBox.SetBackgroundColour('Red')           
                wx.MessageBox(messageList[2], caption='PaleonMag')
                self.parent.messageBox.SetBackgroundColour('Cyan')
                
        elif ('MessageBox:' in endMessage):
            messageList = endMessage.split(':')
            dlg = wx.MessageBox(messageList[2], style=wx.YES_NO|wx.CENTER, caption=messageList[0])
            if (dlg == wx.YES):
                frmCalibrateCoils(self)
        
        elif ('Warning:' in endMessage):
            messageList = endMessage.split(':')
            if (len(messageList) > 2):
                self.parent.statusBar.SetStatusText(messageList[2], 1)     
            else:
                wx.MessageBox(messageList[1], style=wx.OK|wx.CENTER, caption='Warning!')
                
        elif ('Program Status:' in endMessage):
            messageList = endMessage.split(':')
            self.parent.statusBar.SetStatusText(messageList[1], 2)
                
        else:
            '''
                string format
                    message_0:message_1: ... :message_n
                message_x format
                    label = value
            '''
            messageList = endMessage.split(':')
            if (len(messageList) > 1):
                if messageList[0] in self.parent.panelList.keys():
                    self.parent.panelList[messageList[0]].updateGUI(messageList[1:])
                                                                                
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
        if (taskID == self.parent.devControl.MOTOR_HOME_TO_TOP):
            self.parent.appendMessageBox(self.parent.devControl.messages[taskID] + '\n')
            self.flashingMessage = 'Please Wait, Homing To The Top'
            
        elif (taskID == self.parent.devControl.MOTOR_HOME_TO_CENTER):
            self.flashingMessage = 'Please Wait, Homing XY Table'
            noCommStr = 'The XY Stage needs to be homed to the center, now\n\n'
            noCommStr += 'The code will home the Up/Down glass tube to the top limit switch'
            noCommStr += '  before moving the XY stage. HOWEVER, if there are cables or other'
            noCommStr += ' impediments in the way, the XY Stage should not be homed.\n\n'
            noCommStr += 'Do you want the XY stage to be homed to the center position, now?'
            dlg = wx.MessageBox(noCommStr, style=wx.YES_NO|wx.CENTER, caption='Warning: XY State Homing!')
            if (dlg == wx.YES):
                self.parent.appendMessageBox(self.parent.devControl.messages[taskID] + '\n')
            else:
                runFlag = False
        
        elif (taskID == self.END_OF_SEQUENCE):
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
            self.parent.statusBar.SetStatusText('Tasks Completed', 1)
            self.parent.setStatusColor('Green')
        
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
        self.process = multiprocessing.Process(target=workerFunction, args=(self.parent.modConfig.processData, self.mainQueue, taskID))
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
    