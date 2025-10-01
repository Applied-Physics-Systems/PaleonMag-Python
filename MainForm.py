'''
Created on Oct 4, 2024

@author: Hung Nguyen 

@company: Applied Physics Systems

Libraries used in this project
    pip install wxPython
    pip install pyserial
    pip install adwin
    pip install PyUniversalLibrary
    pip install matplotlib

'''
import os
import wx
import configparser
from datetime import datetime

from Forms.frmDCMotors import frmDCMotors
from Forms.frmMagnetometerControl import frmMagnetometerControl
from Forms.frmSampleIndexRegistry import frmSampleIndexRegistry
from Forms.frmSQUID import frmSQUID
from Forms.frmVacuum import frmVacuum
from Forms.frmADWIN_AF import frmADWIN_AF
from Forms.frmIRMARM import frmIRMARM
from Forms.frmMeasure import frmMeasure
from Forms.frmChanger import frmChanger

from Hardware.DevicesControl import DevicesControl

from ClassModules.SampleIndexRegistration import SampleIndexRegistrations
from ClassModules.SampleCommand import SampleCommands

from Modules.modMeasure import modMeasure
from Modules.modFlow import modFlow
from Modules.modConfig import ModConfig

from Process.PaleoThread import PaleoThread

VersionNumber = 'Version 0.00.26'

ID_DC_MOTORS        = 0
ID_FILE_REGISTRY    = 1
ID_MAG_CONTROL      = 2
ID_LOG_OUT          = 3
ID_NOCOMM_OFF       = 4
ID_QUIT_EXIT        = 5
ID_SQUID            = 6
ID_VACUUM           = 7
ID_DEMAG_AF         = 8
ID_IRM_ARM          = 9


'''
    Main form for PaleonMag software
'''
class MainForm(wx.Frame):
    '''
    classdocs
    '''
    messageStr = ''
    NOCOMM_Flag = False
    progressColor = 'None'
    panelList = {}
    config = None
    FLAG_MagnetInit = False     # Whether we've finished initializing the magnetometer
    FLAG_MagnetUse = False      # Whether we've finished using the magnetometer
    
    def __init__(self, *args, **kw):
        '''
        Constructor
        '''
        super(MainForm, self).__init__(*args, **kw)
        
        self.image_control = None
        
        self.devControl = DevicesControl()
        
        # Check if the system.INI file exist
        inFileName = 'Paleomag.ini'
        iniPath = self.getINIPath(inFileName)        
        if os.path.exists(iniPath):
            self.getConfig(iniPath)
        else: 
            self.openINIFile()
            self.saveINIPath(inFileName)
        
        self.InitUI()
        self.messageBox.SetValue(self.messageStr)

        self.registryControl = frmSampleIndexRegistry(parent=self)
        self.magControl = frmMagnetometerControl(parent=self)
        self.vacuumControl = frmVacuum(parent=self)
        self.frmMeasure = frmMeasure(parent=self)
        self.MainChanger = frmChanger(parent=self)

        self.SampleIndexRegistry = SampleIndexRegistrations(parent=self)
        self.SampQueue = SampleCommands()
        
        self.modMeasure = modMeasure()
        self.modFlow = modFlow(parent=self)
        self.paleoThread = PaleoThread(parent=self)

        self.checkDevicesComm()

        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(int(200))      # Checking every 200ms

        self.System_Initialize()
                
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
        
        squidItem = wx.MenuItem(diagMenu, ID_SQUID, text = "SQUID", kind = wx.ITEM_NORMAL)
        diagMenu.Append(squidItem)
        
        vacuumItem = wx.MenuItem(diagMenu, ID_VACUUM, text = "Vacuum", kind = wx.ITEM_NORMAL)
        diagMenu.Append(vacuumItem)
        
        subDemagMenu = wx.Menu()
        demagWindowItem = wx.MenuItem(subDemagMenu, ID_DEMAG_AF, text = "AF Demag Window", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(demagWindowItem)
        tunerItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Tuner / Clip Test", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(tunerItem)
        fieldCalibItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Field Calibration", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(fieldCalibItem)
        dataFileItem = wx.MenuItem(subDemagMenu, wx.ID_NEW, text = "AF Data File Settings", kind = wx.ITEM_NORMAL)
        subDemagMenu.Append(dataFileItem)
        diagMenu.AppendSubMenu(subDemagMenu, "AF Demagnetizer")

        irmSubMenu = wx.Menu()
        irmWindowItem = wx.MenuItem(diagMenu, ID_IRM_ARM, text = "IRM / ARM Window", kind = wx.ITEM_NORMAL)
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
        self.toolbar = self.CreateToolBar(style=wx.TB_HORIZONTAL)
        self.toolbar.AddTool(ID_FILE_REGISTRY, 'File Registry', wx.Bitmap('.\\Resources\\GrayButton_FileRegistry.png')) 
        self.toolbar.AddTool(ID_MAG_CONTROL, 'Magnetometer Control', wx.Bitmap('.\\Resources\\GrayButton_MagControl.png'))
        self.toolbar.AddTool(ID_LOG_OUT, 'Log Out', wx.Bitmap('.\\Resources\\YellowButton_LogOut.png'))
        if self.modConfig.NoCommMode:
            self.toolbar.AddTool(ID_NOCOMM_OFF, 'Turn Off NOCOMM Mode', wx.Bitmap('.\\Resources\\NoCommOn.png'))
        else:
            self.toolbar.AddTool(ID_NOCOMM_OFF, 'Turn Off NOCOMM Mode', wx.Bitmap('.\\Resources\\NoCommOff.png'))
        self.toolbar.AddTool(ID_QUIT_EXIT, 'Quit & EXIT', wx.Bitmap('.\\Resources\\RedButton_Exit.png'))
        self.toolbar.Realize()
        self.Bind(wx.EVT_MENU, self.menuhandler)
                        
        self.messageBox = wx.TextCtrl(self, -1, style = wx.EXPAND|wx.TE_MULTILINE)
        self.messageBox.SetBackgroundColour('Cyan')         
                
        # create status bar
        self.statusBar = self.CreateStatusBar(style = wx.BORDER_RAISED)
        self.statusBar.SetFieldsCount(5)        
        self.statusBar.SetStatusWidths([-8, -8, -4, -2, -2])        
        # Create a font object with a larger size (e.g., 12 points)
        font = wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_SWISS))  # You can customize other font attributes
        # Set the font for the status bar
        self.statusBar.SetFont(font)        
        # set text to status bar
        if self.NOCOMM_Flag:
            self.statusBar.SetStatusText("NoCOMM mode on", 0)
        else:
            self.statusBar.SetStatusText("NoCOMM mode off", 0)
        self.Bind(wx.EVT_SIZE, self.OnSize)         # Bind the OnSize event to handle resizing
                
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)
                
        # Set the frame to fullscreen        
        self.SetSize((1500, 1000)) 
        self.SetTitle('PaleoMagnetic Magnetometer Controller Systems - ' + VersionNumber)
        self.Centre() 
        
    '''--------------------------------------------------------------------------------------------
                        
                        Initialization Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
    '''
    def System_Initialize(self):
        if not self.NOCOMM_Flag:
            self.modConfig.processData.motorsEnable = True
            self.modConfig.processData.vacuumEnable = True
            self.modConfig.processData.irmArmEnable = True
            self.modConfig.processData.squidEnable = True
            self.modConfig.processData.adwinEnable = True
            
            # Initialize IRM/ARM
            self.pushTaskToQueue([self.devControl.IRM_ARM_INIT, [None]])
            
            # Initialize Vacuum.
            self.pushTaskToQueue([self.devControl.VACUUM_INIT, [None]])
                
            self.pushTaskToQueue([self.paleoThread.END_OF_SEQUENCE, [self.paleoThread.ENDTASK_SYSTEM_INIT]])        
        return
        
    '''
    '''
    def Magnetometer_Initialize(self):
        self.magControl.Show()
        self.panelList['MagnetometerControl'] = self.magControl                    
                
        if not self.NOCOMM_Flag:
            # Configure SQUID
            self.pushTaskToQueue([self.devControl.SQUID_CONFIGURE, ['A']])
            
            # Move vertical motor to top position
            self.pushTaskToQueue([self.devControl.MOTOR_HOME_TO_TOP, [None]])
            
            if 'ADWIN' in self.modConfig.AFSystem:
                self.pushTaskToQueue([self.devControl.AF_SET_RELAYS_DEFAULT, [None]])
            
            # Move XY Table To Center Position
            if self.modConfig.UseXYTableAPS:
                self.pushTaskToQueue([self.devControl.MOTOR_HOME_TO_CENTER, [None]])
                
            # Initialize Vacuum.
            if self.modConfig.DoVacuumReset:
                self.pushTaskToQueue([self.devControl.VACUUM_RESET, [None]])
                                            
            # if EnableAxialIRM, then discharge
            if self.modConfig.EnableARM:
                self.pushTaskToQueue([self.devControl.IRM_SET_BIAS_FIELD, [0]])
                
            if self.modConfig.EnableAxialIRM:
                self.pushTaskToQueue([self.devControl.IRM_FIRE, [0]])
                
        self.pushTaskToQueue([self.paleoThread.END_OF_SEQUENCE, [self.paleoThread.ENDTASK_MAG_INIT]])
        return
        

    '''--------------------------------------------------------------------------------------------
                        
                        Utilities Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def getINIPath(self, fileName):
        self.paleomagIni = configparser.ConfigParser()
        self.paleomagIni.read(fileName)
        iniPath = self.paleomagIni['Program']['SystemIniPath']
        return iniPath
    
    '''
    '''
    def saveINIPath(self, fileName):
        self.paleomagIni.set('Program', 'SystemIniPath', self.defaultFilePath)
        
        # Write the configuration to an INI file
        with open(fileName, 'w') as configfile:
            self.paleomagIni.write(configfile)        
            
        return
        
    '''
    '''
    def getConfig(self, fileName):
        config = configparser.ConfigParser()
        config.read(fileName)
        self.modConfig = ModConfig(config=config) 
        self.messageStr = self.devControl.setDevicesConfig(self.modConfig)
        self.devControl.closeDevices()
        
        # Set paramters from INI file
        self.NOCOMM_Flag = self.modConfig.NoCommMode 
        return
    
    '''
        Open Dialog box for INI file
    '''
    def openINIFile(self):
        dlg = wx.FileDialog(self, "Open", "", "",
                            "INI files (*.INI)|*.INI",
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.defaultFilePath = dlg.GetPath()
            self.getConfig(self.defaultFilePath)        

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
        
    '''
    '''
    def sendErrorMessage(self, errorMessage):
        self.statusBar.SetBackgroundColour(wx.Colour(255, 0, 0))
        self.statusBar.SetStatusText(errorMessage, 1)
            
    '''
    '''
    def setStatusColor(self, imgColor):
        if (self.progressColor != imgColor):
            self.progressColor = imgColor
            # Load the image
            img = wx.Bitmap('.\\Resources\\' + imgColor + '.png', wx.BITMAP_TYPE_PNG)
            
            # Get the rectangle of the second status bar field
            rect = self.statusBar.GetFieldRect(3)
            
            # Create a StaticBitmap control with the image and position it
            self.image_control = wx.StaticBitmap(self.statusBar, -1, img, pos=rect.GetTopLeft())
                
        return
            
    '''
        
    '''
    def pushTaskToQueue(self, taskFunction):
        if not self.NOCOMM_Flag:
            self.statusBar.SetBackgroundColour(wx.NullColour)
            self.setStatusColor('Red')
            self.statusBar.SetStatusText("Task running ...", 1)
            self.paleoThread.pushTaskToQueue(taskFunction)
            
        else:
            self.sendErrorMessage("Error: Cannot execute due to NoCOMM on");
            
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------''' 
    '''
    '''
    def OnSize(self, event):
        # Reposition the image when the frame is resized
        rect = self.statusBar.GetFieldRect(3)
        if (self.image_control != None): 
            self.image_control.SetPosition(rect.GetTopLeft())
        event.Skip()
            
    '''
        Close MainForm
    '''
    def onClosed(self, event):
        if not self.paleoThread.backgroundRunningFlag:        
            self.paleoThread.runProcess([self.devControl.SYSTEM_DISCONNECT,[None]])
        
        self.Destroy()

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

        elif (menuID == ID_SQUID):
            if not 'SQUIDControl' in self.panelList.keys():
                SQUIDControl = frmSQUID(parent=self)
                SQUIDControl.Show()
                self.panelList['SQUIDControl'] = SQUIDControl

        elif (menuID == ID_VACUUM):
            if not 'VacuumControl' in self.panelList.keys():
                self.vacuumControl.Show()
                self.panelList['VacuumControl'] = self.vacuumControl
            
        elif (menuID == ID_NOCOMM_OFF):
            self.statusBar.SetBackgroundColour(wx.NullColour)
            if self.NOCOMM_Flag:  
                self.NOCOMM_Flag = False
                self.statusBar.SetStatusText('NoCOMM mode off', 0)
                self.toolbar.SetToolNormalBitmap(id=ID_NOCOMM_OFF, bitmap=wx.Bitmap('.\\Resources\\NoCommOff.png'))
            else:
                self.NOCOMM_Flag = True
                self.statusBar.SetStatusText('NoCOMM mode on', 0)
                self.toolbar.SetToolNormalBitmap(id=ID_NOCOMM_OFF, bitmap=wx.Bitmap('.\\Resources\\NoCommOn.png'))
            
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
            
        elif (menuID == ID_DEMAG_AF):
            if not 'ADWinAFControl' in self.panelList.keys():
                demagAfControl = frmADWIN_AF(parent=self)
                demagAfControl.Show()
                self.panelList['ADWinAFControl'] = demagAfControl
                
        elif (menuID == ID_IRM_ARM):
            if not 'IRM_ARM_Control' in self.panelList.keys():
                irmARMControl = frmIRMARM(parent=self)
                irmARMControl.Show()
                self.panelList['IRMControl'] = irmARMControl
            
            
        elif (menuID == ID_QUIT_EXIT):
            if not self.NOCOMM_Flag:
                if (self.paleoThread.process != None): 
                    self.paleoThread.process.terminate()
            self.Close(force=False)
                                                                            
    '''
        Timer event handler
    '''
    def OnTimer(self, event):
        now = datetime.now()
        # Format the time as HH:MM
        formatted_time = now.strftime("%H:%M %p")
        self.statusBar.SetBackgroundColour(wx.NullColour)
        self.statusBar.SetStatusText(formatted_time, 4)
        
        if self.paleoThread.backgroundRunningFlag:
            self.paleoThread.checkProcess()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        frame = MainForm(parent=None, id=-1)
        frame.Maximize(maximize=True)
        frame.Show()
        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        