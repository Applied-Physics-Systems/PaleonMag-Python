'''
Created on Sep 9, 2025

@author: hd.nguyen
'''
import os
import wx

import configparser

from Forms.frmMagnetometerControl import frmMagnetometerControl
from Forms.frmSampleIndexRegistry import frmSampleIndexRegistry
from Forms.frmVacuum import frmVacuum
from Forms.frmChanger import frmChanger
from Forms.frmMeasure import frmMeasure

from ClassModules.SampleIndexRegistration import SampleIndexRegistrations
from ClassModules.SampleCommand import SampleCommands

from Modules.modMeasure import modMeasure
from Modules.modFlow import modFlow
from Modules.modConfig import ModConfig

from Hardware.DevicesControl import DevicesControl

from Process.ProcessData import ProcessData
from Process.PaleoThread import PaleoThread

class frmTestUnit(wx.Frame):
    '''
    classdocs
    '''
    panelList = {}
    FLAG_MagnetInit = False     # Whether we've finished initializing the magnetometer
    FLAG_MagnetUse = False      # Whether we've finished using the magnetometer

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.devControl = DevicesControl()
        
        # Check if the system.INI file exist
        inFileName = '..\Paleomag.config'
        iniPath = self.getINIPath(inFileName)        
        if os.path.exists(iniPath):
            self.getConfig(iniPath)
        else: 
            self.openINIFile()
            self.saveINIPath(inFileName)
                
        self.FLAG_MagnetInit = True        # We're done initializing
                
        self.InitUI()        

        self.registryControl = frmSampleIndexRegistry(parent=self)
        self.magControl = frmMagnetometerControl(parent=self)
        
        self.SampleIndexRegistry = SampleIndexRegistrations(parent=self)
        self.SampQueue = SampleCommands()
        self.magControl = frmMagnetometerControl(parent=self)
        self.vacuumControl = frmVacuum(parent=self)
        self.frmMeasure = frmMeasure(parent=self)
        self.MainChanger = frmChanger(parent=self)
        
        self.modMeasure = modMeasure()
        self.modFlow = modFlow()
        self.paleoThread = PaleoThread(parent=self)
       
        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(200)      # Checking every 200ms

    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.messageBox = wx.TextCtrl(panel, -1, size=(1000, 600), style = wx.EXPAND|wx.TE_MULTILINE)
        
        self.SetSize((1500, 1000))
        self.SetTitle('Test Unit')
        self.Centre()

    '''
    '''
    def updateCommStatus(self, statusMessage):
        return
    
    '''
    '''
    def updateProgressStatus(self, statusMessage):
        return

    '''
    '''
    def updateTaskStatus(self, statusMessage):
        return

    '''
    '''
    def updateCurrentTime(self, statusMessage):
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
                
        processData = ProcessData()
        processData.config = config 
    
        self.modConfig = ModConfig(process=processData)
        self.modConfig.parseConfig(config)
        
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

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def appendMessageBox(self, message):
        messageStr = self.messageBox.GetValue()
        messageStr += message
        self.messageBox.SetValue(messageStr)
        
    '''
    '''
    def pushTaskToQueue(self, taskFunction):
        self.paleoThread.pushTaskToQueue(taskFunction)
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Timer event handler
    '''
    def OnTimer(self, event):
        if self.paleoThread.backgroundRunningFlag:
            self.paleoThread.checkProcess()

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        frame = frmTestUnit(parent=None)
        frame.registryControl.Show()
        frame.magControl.Show()
        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        