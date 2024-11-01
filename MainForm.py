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

from Forms.frmDCMotors import frmDCMotors
from Forms.frmTip import frmTip
from Hardware.DevicesControl import DevicesControl
from Process.ProcessData import ProcessData

VersionNumber = 'Version 0.00.04'

ID_DC_MOTORS        = 0
ID_FILE_REGISTRY    = 1
ID_MAG_CONTROL      = 2
ID_LOG_OUT          = 3
ID_NOCOMM_OFF       = 4
ID_QUIT_EXIT        = 5

devControl = DevicesControl()

'''
    Background task processing
'''
def workerFunction(queue, taskID):
    processData = queue.get()
    devControl.setDevicesConfig(processData.config)
    devControl.retrieveProcessData(processData)
    
    devControl.runTask(queue, taskID)
    
    processData = devControl.saveProcessData(processData)
    devControl.closeDevices()
    queue.put('Task Completed')    
    queue.put(processData)

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
    
    def __init__(self, *args, **kw):
        '''
        Constructor
        '''
        super(MainForm, self).__init__(*args, **kw)
        self.devControl = DevicesControl()
        self.processData = ProcessData()
        
        self.openINIFile()
        
        self.InitUI()
        self.messageBox.SetValue(self.messageStr)

        self.checkDevicesComm()

        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        tipBox = frmTip(parent=self)
        tipBox.devices = self.devControl
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
                
        self.SetSize((1500, 1000)) 
        self.SetTitle('Paleonmagnetic Magnetometer Controller Systems - ' + VersionNumber)
        self.Centre() 
        self.Show(True)

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
            self.processData.config = config 
            self.messageStr = self.devControl.setDevicesConfig(config)
            self.devControl.closeDevices()

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
        
        self.backgroundRunningFlag = True
        processFunction = self.taskQueue.pop(0)
        if (processFunction == self.devControl.HOME_TO_TOP):
            self.appendMessageBox('Run HomeToTop\n')
            
        elif (processFunction == self.devControl.HOME_TO_CENTER):
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
        
        if runFlag:
            self.runProcess(processFunction)
        
    '''
        Start a new process which can run concurrently on another CPU core to avoid GUI hangup
    '''
    def runProcess(self, taskID):
        self.processQueue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=workerFunction, args=(self.processQueue, taskID))
        self.process.start()
        self.processQueue.put(self.processData)
        
        self.timer.Start(int(200))      # Checking every 200ms
                
    '''
        Check for task completion
    '''
    def checkProcess(self):
        if (self.process != None):
            try:
                endMessage = self.processQueue.get(timeout=0.01)
                if ('Task Completed' in endMessage):
                    self.processData = self.processQueue.get()
                    self.process.join()
                    # Start new process
                    if (len(self.taskQueue) > 0):
                        self.startProcess()
                            
                    else:
                        self.backgroundRunningFlag = False
                        self.appendMessageBox('Tasks Completed')
                        self.timer.Stop()
                        
                elif ('Error:' in endMessage):
                    self.taskQueue = []
                    messageList = endMessage.split(':')
                    if (len(messageList) > 1):                          
                        self.messageBox.SetBackgroundColour('LightRed')           
                        wx.MessageBox(messageList[1], caption='PaleonMag')
                        self.messageBox.SetBackgroundColour('Cyan')
                    
                return
                    
            except:
                return
            
    '''
        
    '''
    def pushTaskToQueue(self, taskFunction):
        if not self.NOCOMM_Flag:
            self.taskQueue.append(taskFunction)
            # if no background process running, start one
            if not self.backgroundRunningFlag:
                if (len(self.taskQueue) > 0):
                    self.startProcess()

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
            dcMotor = frmDCMotors(parent=self)
            dcMotor.Show()
            
        elif (menuID == ID_NOCOMM_OFF):
            self.NOCOMM_Flag = False
            message = self.messageBox.GetValue()
            message += self.devControl.openDevices()
            self.messageBox.SetValue(message)
            
        elif (menuID == ID_QUIT_EXIT):
            self.Close(force=False)
                        
            
    '''
        Timer event handler
    '''
    def OnTimer(self, event):
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
        