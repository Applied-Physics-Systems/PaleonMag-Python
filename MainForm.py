'''
Created on Oct 4, 2024

@author: Hung Nguyen 

@company: Applied Physics Systems

Libraries used in this project
    pip install wxPython
    pip install pyserial

'''
import wx
import multiprocessing
import configparser
from datetime import datetime

from Forms.frmDCMotors import frmDCMotors
from Forms.frmTip import frmTip
from Forms.frmFlashingStatus import frmFlashingStatus
from Forms.frmMagnetometerControl import frmMagnetometerControl
from Forms.frmSampleIndexRegistry import frmSampleIndexRegistry

from Hardware.DevicesControl import DevicesControl
from Process.ModConfig import ModConfig

VersionNumber = 'Version 0.00.08'

ID_DC_MOTORS        = 0
ID_FILE_REGISTRY    = 1
ID_MAG_CONTROL      = 2
ID_LOG_OUT          = 3
ID_NOCOMM_OFF       = 4
ID_QUIT_EXIT        = 5

FLASH_DISPLAY_OFF_TIME = 10

devControl = DevicesControl()

'''
    Background task processing
'''
def workerFunction(queue, taskID):
    try:
        processData = queue.get()
        if isinstance(processData, str):
            queue.put('Task Completed')
            queue.put(processData)
            return
        modConfig = ModConfig(process=processData, queue=queue)
        devControl.setDevicesConfig(modConfig)
        devControl.retrieveProcessData(processData)
        
        devControl.runTask(queue, taskID)
        
        processData = devControl.saveProcessData(processData)
        devControl.closeDevices()
        queue.put('Task Completed')    
        queue.put(processData)
        
    except Exception as e:
        print(processData)
        print(e)

'''
    Main form for PaleonMag software
'''
class MainForm(wx.Frame):
    '''
    classdocs
    '''
    processQueue = None
    process = None
    taskQueue = []
    backgroundRunningFlag = False
    messageStr = ''
    NOCOMM_Flag = False
    processQueue = None
    flashingCount = FLASH_DISPLAY_OFF_TIME
    flashingMessage = ''
    panelList = {}
    config = None
    
    def __init__(self, *args, **kw):
        '''
        Constructor
        '''
        super(MainForm, self).__init__(*args, **kw)
        self.devControl = DevicesControl()
        
        self.openINIFile()
        
        self.InitUI()
        self.messageBox.SetValue(self.messageStr)

        self.checkDevicesComm()

        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(int(200))      # Checking every 200ms

        tipBox = frmTip(parent=self)
        tipBox.Show()

    '''--------------------------------------------------------------------------------------------
                        
                        GUI Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def createHelpMenu(self):
        helpMenu = wx.Menu()

        indexItem = wx.MenuItem(helpMenu, wx.ID_NEW, text = "Index", kind = wx.ITEM_NORMAL)
        helpMenu.Append(indexItem)
                
        return helpMenu 

    '''
    '''
    def createWindowsMenu(self):
        windowsMenu = wx.Menu()
        
        windowsMenu.AppendCheckItem(103,"Checkable") 
                
        return windowsMenu 

    '''
    '''
    def createDiagnosticsMenu(self):
        diagMenu = wx.Menu()
        
        motorItem = wx.MenuItem(diagMenu, ID_DC_MOTORS, text = "DC Motors", kind = wx.ITEM_NORMAL)
        diagMenu.Append(motorItem)
        
        squidItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "SQUID", kind = wx.ITEM_NORMAL)
        diagMenu.Append(squidItem)
        
        vacuumItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "Vacuum", kind = wx.ITEM_NORMAL)
        diagMenu.Append(vacuumItem)
        
        subDemagMenu = wx.Menu()
        demagWindowItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Demag Window", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(demagWindowItem)
        tunerItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Tuner / Clip Test", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(tunerItem)
        fieldCalibItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Field Calibration", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(fieldCalibItem)
        dataFileItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Data File Settings", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(dataFileItem)
        diagMenu.AppendSubMenu(subDemagMenu, "AF Demagnetizer")

        irmSubMenu = wx.Menu()
        irmWindowItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "IRM / ARM Window", kind = wx.ITEM_NORMAL)
        irmSubMenu.Append(irmWindowItem)
        diagMenu.AppendSubMenu(irmSubMenu, "IRM/ARM")

        meterItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "908A Gaussmeter", kind = wx.ITEM_NORMAL)
        diagMenu.Append(meterItem)

        daqItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "DAQ Comm", kind = wx.ITEM_NORMAL)
        diagMenu.Append(daqItem)

        bridgeItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "Susceptibility Bridge", kind = wx.ITEM_NORMAL)
        diagMenu.Append(bridgeItem)

        vrmItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "VRM Data Collection", kind = wx.ITEM_NORMAL)
        diagMenu.Append(vrmItem)

        emailItem = wx.MenuItem(diagMenu, wx.ID_NEW, text = "Test Email", kind = wx.ITEM_NORMAL)
        diagMenu.Append(emailItem)
        
        return diagMenu 

    '''
    '''
    def createFlowMenu(self):
        flowMenu = wx.Menu()
        
        runItem = wx.MenuItem(flowMenu, wx.ID_NEW, text = "Running", kind = wx.ITEM_NORMAL)
        flowMenu.Append(runItem)
        
        return flowMenu 

    '''
    '''
    def createViewMenu(self):
        viewMenu = wx.Menu()
        
        statusBar = wx.MenuItem(viewMenu, wx.ID_NEW, text = "Status Bar", kind = wx.ITEM_NORMAL)
        viewMenu.Append(statusBar)
        
        return viewMenu 
        
    '''
    '''
    def createFileMenu(self):
        fileMenu = wx.Menu() 
        
        newItem = wx.MenuItem(fileMenu, wx.ID_NEW, text = "New", kind = wx.ITEM_NORMAL) 
        fileMenu.Append(newItem)         
        
        logoutItem = wx.MenuItem(fileMenu, wx.ID_NEW, text = "Log Out", kind = wx.ITEM_NORMAL) 
        fileMenu.Append(logoutItem) 
         
        quitItem = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Exit\tCtrl+Q')         
        fileMenu.Append(quitItem) 

        return fileMenu 
        
    '''
        Build graphic user interface for the main form
    '''
    def InitUI(self):
               
        # Add Menu bar on the top 
        menubar = wx.MenuBar()
        
        fileMenu = self.createFileMenu()
        viewMenu = self.createViewMenu()
        flowMenu = self.createFlowMenu()
        diagMenu = self.createDiagnosticsMenu()
        windowsMenu = self.createWindowsMenu()
        helpMenu = self.createHelpMenu()
        menubar.Append(fileMenu, '&File')
        menubar.Append(viewMenu, '&View')
        menubar.Append(flowMenu, '&Flow')
        menubar.Append(diagMenu, '&Diagnostics')
        menubar.Append(windowsMenu, '&Windows')  
        menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(menubar)         
        
        # Add Toolbar below the Menu
        toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL)
        toolbar.AddTool(ID_FILE_REGISTRY, 'File Registry', wx.Bitmap('.\\Resources\\GrayButton_FileRegistry.png')) 
        toolbar.AddTool(ID_MAG_CONTROL, 'Magnetometer Control', wx.Bitmap('.\\Resources\\GrayButton_MagControl.png'))
        toolbar.AddTool(ID_LOG_OUT, 'Log Out', wx.Bitmap('.\\Resources\\YellowButton_LogOut.png'))
        toolbar.AddTool(ID_NOCOMM_OFF, 'Turn Off NOCOMM Mode', wx.Bitmap('.\\Resources\\GrayButton_TurnOff.png'))
        toolbar.AddTool(ID_QUIT_EXIT, 'Quit & EXIT', wx.Bitmap('.\\Resources\\RedButton_Exit.png'))
        toolbar.Realize()
        self.Bind(wx.EVT_MENU, self.menuhandler)
                
        self.messageBox = wx.TextCtrl(self, -1, style = wx.EXPAND|wx.TE_MULTILINE)
        self.messageBox.SetBackgroundColour('Cyan')         
                
        # create status bar
        self.statusBar = self.CreateStatusBar(style = wx.BORDER_RAISED)
        self.StatusBar.SetFieldsCount(4)
        self.StatusBar.SetStatusWidths([-8, -8, -3, -1])
        # set text to status bar
        if self.NOCOMM_Flag:
            self.statusBar.SetStatusText("NoCOMM mode on", 0)
        else:
            self.statusBar.SetStatusText("NoCOMM mode off", 0)
        
        self.SetSize((1500, 1000)) 
        self.SetTitle('Paleonmagnetic Magnetometer Controller Systems - ' + VersionNumber)
        self.Centre() 
        self.Show(True)
        
    '''--------------------------------------------------------------------------------------------
                        
                        Initialization Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
    '''
    def Magnetometer_Initialize(self):
        magControl = frmMagnetometerControl(parent=self)
        magControl.Show()
        self.panelList['MagnetometerControl'] = magControl                    
        
        registryControl = frmSampleIndexRegistry(parent=self)
        registryControl.Show()
        self.panelList['RegistryControl'] = registryControl
        
        if not self.NOCOMM_Flag:
            # Move vertical motor to top position
            self.pushTaskToQueue([self.devControl.MOTOR_HOME_TO_TOP, [None]])
            
            # Move XY Table To Center Position
            if (self.modConfig.UseXYTableAPS):
                self.pushTaskToQueue([self.devControl.MOTOR_HOME_TO_CENTER, [None]])
                
            # Initialize Vacuum.
            if (self.modConfig.DoVacuumReset):
                print('TODO: DoVacuumReset')
                
            # if EnableAxialIRM, then discharge
            if self.modConfig.EnableARM:
                #self.pushTaskToQueue([self.devControl.IRM_SET_BIAS_FIELD, [0]])
                print('TODO: Set bias field with DAQ board')
                
            if self.modConfig.EnableAxialIRM:
                self.pushTaskToQueue([self.devControl.IRM_FIRE, [0]])
        

    '''--------------------------------------------------------------------------------------------
                        
                        Utilities Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
        Open Dialog box for INI file
    '''
    def openINIFile(self):
        dlg = wx.FileDialog(self, "Open", "", "",
                            "All files (*.*)|*.*",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.defaultFilePath = dlg.GetPath()        
            config = configparser.ConfigParser()
            config.read(self.defaultFilePath)
            self.modConfig = ModConfig(config=config) 
            self.messageStr = self.devControl.setDevicesConfig(self.modConfig)
            self.devControl.closeDevices()
            
            # Set paramters from INI file
            self.NOCOMM_Flag = self.modConfig.NoCommMode 

    '''
        Check if all device are connected OK
    '''
    def checkDevicesComm(self):
        if not self.devControl.devicesAllGoodFlag:
            wx.MessageBox('Invalid Port Number', caption='PaleonMag')
            
            noCommStr = 'Would you like to switch on NOCOMM mode?\n\n'
            noCommStr += 'This will prevent the PaleonMag program from trying to connect with any peripheral devices,'
            noCommStr += ' and can be turn off by clicking on the "Turn off NOCOMM mode" button in the Main program window'
            dlg = wx.MessageBox(noCommStr, style=wx.YES_NO|wx.CENTER, caption='PaleonMag')
            if (dlg == wx.YES):
                self.NOCOMM_Flag = True

    '''
    '''
    def appendMessageBox(self, message):
        messageStr = self.messageBox.GetValue()
        messageStr += message
        self.messageBox.SetValue(messageStr)

    '''--------------------------------------------------------------------------------------------
                        
                        Multiprocessing Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
        Before running process in a different thread, do the neccessaries in GUI thread 
    '''
    def startProcess(self):
        runFlag = True
        
        processFunction = self.taskQueue.pop(0)
        if (processFunction[0] == self.devControl.MOTOR_HOME_TO_TOP):
            self.appendMessageBox('Run HomeToTop\n')
            self.flashingMessage = 'Please Wait, Homing To The Top'
            
        elif (processFunction[0] == self.devControl.MOTOR_HOME_TO_CENTER):
            self.flashingMessage = 'Please Wait, Homing XY Table'
            noCommStr = 'The XY Stage needs to be homed to the center, now\n\n'
            noCommStr += 'The code will home the Up/Down glass tube to the top limit switch'
            noCommStr += '  before moving the XY stage. HOWEVER, if there are cables or other'
            noCommStr += ' impediments in the way, the XY Stage should not be homed.\n\n'
            noCommStr += 'Do you want the XY stage to be homed to the center position, now?'
            dlg = wx.MessageBox(noCommStr, style=wx.YES_NO|wx.CENTER, caption='Warning: XY State Homing!')
            if (dlg == wx.YES):
                self.appendMessageBox('Run HomeToCenter\n')
            else:
                runFlag = False

        elif (processFunction[0] == self.devControl.IRM_FIRE):
            self.appendMessageBox('Run Discharge IRM device\n')

        
        if runFlag:
            self.backgroundRunningFlag = True
            self.runProcess(processFunction)
        
    '''
        Start a new process which can run concurrently on another CPU core to avoid GUI hangup
    '''
    def runProcess(self, taskID):
        self.timer.Stop()
        self.processQueue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=workerFunction, args=(self.processQueue, taskID))
        self.process.start()
        self.processQueue.put(self.modConfig.processData)        
        self.timer.Start(int(200))      # Checking every 200ms 
                
    '''
        Check for task completion
    '''
    def checkProcess(self):
        if (self.process != None):
            try:
                endMessage = self.processQueue.get(timeout=0.01)
                if ('Task Completed' in endMessage):
                    self.backgroundRunningFlag = False
                    self.processData = self.processQueue.get()
                    self.process.join()
                    # Start new process
                    if (len(self.taskQueue) > 0):
                        self.startProcess()
                            
                    else:
                        self.appendMessageBox('Tasks Completed\n')
                        self.statusBar.SetStatusText('Tasks Completed', 1)
                        self.timer.Stop()
                        
                elif ('Error:' in endMessage):
                    self.taskQueue = []
                    messageList = endMessage.split(':')
                    if (len(messageList) > 1):                          
                        self.messageBox.SetBackgroundColour('Red')           
                        wx.MessageBox(messageList[1], caption='PaleonMag')
                        self.messageBox.SetBackgroundColour('Cyan')
                
                elif ('Warning:' in endMessage):
                    messageList = endMessage.split(':')
                    if (len(messageList) > 1):
                        self.statusBar.SetStatusText(messageList[1], 1)     
                        
                elif ('Command Exchange:' in endMessage):
                    messageList = endMessage.split(':')
                    if (len(messageList) > 1):
                        print(messageList[1])                      
                                        
                return
                    
            except:
                if (self.backgroundRunningFlag):
                    self.flashingCount += 1
                    if (self.flashingCount > FLASH_DISPLAY_OFF_TIME): 
                        flashingPanel = frmFlashingStatus(self, self.flashingMessage)
                        flashingPanel.Show()
                        self.flashingCount = 0
                else:
                    self.flashingCount = 0
                    
                return
            
    '''
        
    '''
    def pushTaskToQueue(self, taskFunction):
        if not self.NOCOMM_Flag:
            self.statusBar.SetStatusText("Task running ...", 1)
            self.taskQueue.append(taskFunction)
            # if no background process running, start one
            if not self.backgroundRunningFlag:
                if (len(self.taskQueue) > 0):
                    self.startProcess()
        else:
            self.statusBar.SetStatusText("Error: Cannot execute due to NoCOMM on", 1)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''                
    '''
        Handle selected menu Item
    '''
    def menuhandler(self, event): 
        menuID = event.GetId()
                 
        if (menuID == wx.ID_NEW): 
            self.messageBox.AppendText("TODO"+"\n")
            
        elif (menuID == ID_DC_MOTORS):
            if not 'MotorControl' in self.panelList.keys():
                dcMotorControl = frmDCMotors(parent=self)
                dcMotorControl.Show()
                self.panelList['MotorControl'] = dcMotorControl
            
        elif (menuID == ID_NOCOMM_OFF):
            if self.NOCOMM_Flag:  
                self.NOCOMM_Flag = False
                self.statusBar.SetStatusText('NoCOMM mode off', 0)
            else:
                self.NOCOMM_Flag = True
                self.statusBar.SetStatusText('NoCOMM mode on', 0)
            
        elif (menuID == ID_MAG_CONTROL):
            if not 'MagnetometerControl' in self.panelList.keys():
                magControl = frmMagnetometerControl(parent=self)
                magControl.Show()
                self.panelList['MagnetometerControl'] = magControl                    

        elif (menuID == ID_FILE_REGISTRY):
            if not 'RegistryControl' in self.panelList.keys():
                registryControl = frmSampleIndexRegistry(parent=self)
                registryControl.Show()
                self.panelList['RegistryControl'] = registryControl                    
            
        elif (menuID == ID_QUIT_EXIT):
            if not self.NOCOMM_Flag:
                if (self.processQueue != None): 
                    self.processQueue.put('Program_Halted')
            self.Close(force=False)
                
        # Set focus on panels
        if (menuID != ID_QUIT_EXIT):
            for panel in self.panelList.values():
                panel.SetFocus()
                                    
    '''
        Timer event handler
    '''
    def OnTimer(self, event):
        now = datetime.now()
        # Format the time as HH:MM
        formatted_time = now.strftime("%H:%M %p")
        self.statusBar.SetStatusText(formatted_time, 3)
        
        if self.backgroundRunningFlag:
            self.checkProcess()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = MainForm(parent=None, id=-1)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        