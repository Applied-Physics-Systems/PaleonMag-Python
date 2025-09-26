'''
Created on Sep 9, 2025

@author: hd.nguyen
'''
import wx

import configparser

from Forms.frmMagnetometerControl import frmMagnetometerControl
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

    def __init__(self, parent=None, path=''):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.devControl = DevicesControl()
        config = configparser.ConfigParser()
        configPath = path
        config.read(configPath)
        processData = ProcessData()
        processData.config = config 
    
        self.modConfig = ModConfig(process=processData)
        self.modConfig.parseConfig(config)
        
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
                
        self.InitUI()        
       
                # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(int(200))      # Checking every 200ms

    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.messageBox = wx.TextCtrl(panel, -1, size=(1000, 600), style = wx.EXPAND|wx.TE_MULTILINE)
        
        self.SetSize((1500, 1000))
        self.SetTitle('Test Unit')
        self.Centre()

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
        frame = frmTestUnit(parent=None, path='C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI')
        frame.Show()
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        