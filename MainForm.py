'''
Created on Oct 4, 2024

@author: Hung Nguyen 

@company: Applied Physics Systems

Libraries used in this project
    pip install wxPython
    pip install pyserial

'''
import wx
from Forms.frmDCMotors import frmDCMotors
from Forms.frmTip import frmTip
import multiprocessing

VersionNumber = 'Version 0.00.03'

ID_DC_MOTORS = 0

'''
    Background task processing
'''
def workerFunction(queue, taskID):
    print('Test multiprocessing ' + str(taskID))

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

    def __init__(self, *args, **kw):
        '''
        Constructor
        '''
        super(MainForm, self).__init__(*args, **kw)
        
        self.InitUI()

        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

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
        toolbar.AddTool(wx.ID_ANY, 'File Registry', wx.Bitmap('.\\Resources\\GrayButton_FileRegistry.png')) 
        toolbar.AddTool(wx.ID_ANY, 'Magnetometer Control', wx.Bitmap('.\\Resources\\GrayButton_MagControl.png'))
        toolbar.AddTool(wx.ID_ANY, 'Log Out', wx.Bitmap('.\\Resources\\YellowButton_LogOut.png'))
        toolbar.AddTool(wx.ID_ANY, 'Turn Off NOCOMM Mode', wx.Bitmap('.\\Resources\\GrayButton_TurnOff.png'))
        toolbar.AddTool(wx.ID_ANY, 'Quit & EXIT', wx.Bitmap('.\\Resources\\RedButton_Exit.png'))
        toolbar.Realize()
                
        self.text = wx.TextCtrl(self, -1, style = wx.EXPAND|wx.TE_MULTILINE)
        self.text.SetBackgroundColour('Cyan')         
        self.Bind(wx.EVT_MENU, self.menuhandler)
                
        self.SetSize((1500, 1000)) 
        self.SetTitle('Paleonmagnetic Magnetometer Controller Systems - ' + VersionNumber)
        self.Centre() 
        self.Show(True)

    '''--------------------------------------------------------------------------------------------
                        
                        Background tasks
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def HomeToTop(self):
        print('TODO: Home To Top')

    '''
    '''
    def HomeToCenter(self):
        print('TODO: Home To Center')

    '''--------------------------------------------------------------------------------------------
                        
                        Multiprocessing Functions
                        
    --------------------------------------------------------------------------------------------'''        
    '''
        Start a new process which can run concurrently on another CPU core to avoid GUI hangup
    '''
    def startProcess(self, taskID):
        self.processQueue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=workerFunction, args=(self.processQueue, taskID))
        self.process.start()
        self.timer.Start(int(1000*0.5))      # Checking every half second
                
    '''
        Check for task completion
    '''
    def checkProcess(self):
        if (self.process != None):
            if not self.process.is_alive():
                if (len(self.taskQueue) > 0):
                    self.backgroundRunningFlag = True
                    processFunction = self.taskQueue.pop(0)
                    self.startProcess(processFunction)
                else:
                    self.backgroundRunningFlag = False
                    self.timer.Stop()
                
    '''
    '''
    def pushTaskToQueue(self, taskFunction):
        self.taskQueue.append(taskFunction)
        if not self.backgroundRunningFlag:
            if (len(self.taskQueue) > 0):
                self.backgroundRunningFlag = True
                processFunction = self.taskQueue.pop(0)
                self.startProcess(processFunction)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
        
    '''
        Handle selected menu Item
    '''
    def menuhandler(self, event): 
        menuID = event.GetId()
                 
        if (menuID == wx.ID_NEW): 
            self.text.AppendText("TODO"+"\n")
            
        elif (menuID == ID_DC_MOTORS):
            dcMotor = frmDCMotors(parent=None, id=-1)
            dcMotor.Show()
        
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
        