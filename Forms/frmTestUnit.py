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
from Forms.frmStats import frmStats
from Forms.frmAF_2G import frmAF_2G
from Forms.frmADWIN_AF import frmADWIN_AF
from Forms.frmDCMotors import frmDCMotors
from Forms.frmIRMARM import frmIRMARM

from ClassModules.SampleIndexRegistration import SampleIndexRegistrations
from ClassModules.SampleCommand import SampleCommands
from ClassModules.Sample import Sample

from Modules.modMeasure import modMeasure
from Modules.modFlow import modFlow
from Modules.modConfig import ModConfig

from Hardware.DevicesControl import DevicesControl

from Process.ProcessData import ProcessData
from Process.PaleoThread import PaleoThread
from Forms.frmSQUID import frmSQUID

LISTBOX_LENGTH = 230

class frmTestUnit(wx.Frame):
    '''
    classdocs
    '''
    panelList = {}
    FLAG_MagnetInit = False     # Whether we've finished initializing the magnetometer
    FLAG_MagnetUse = False      # Whether we've finished using the magnetometer
    HolderMeasured = False
    currentTest = ''

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

        self.frmSampleIndexRegistry = frmSampleIndexRegistry(parent=self)
        self.magControl = frmMagnetometerControl(parent=self)
        
        self.SampleHolder = Sample()
        self.SampleIndexRegistry = SampleIndexRegistrations(parent=self)
        self.SampQueue = SampleCommands(parent=self)
        self.vacuumControl = frmVacuum(parent=self)
        self.frmMeasure = frmMeasure(parent=self)
        self.frmStats = frmStats(parent=self)
        self.MainChanger = frmChanger(parent=self)        
        self.frmAF_2G = frmAF_2G(parent=self)
        self.frmADWIN_AF = frmADWIN_AF(parent=self)
        self.frmIRMARM = frmIRMARM(parent=self)
        
        self.modMeasure = modMeasure()
        self.modFlow = modFlow()
        self.paleoThread = PaleoThread(parent=self)
       
        self.modConfig.processData.vacuumEnable = True
        
        # Add timer
        self.timer = wx.Timer(self)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(200)      # Checking every 200ms

    '''
    '''
    def positionWidget(self, widget):
        parentPos = self.GetPosition()
        parentSize = self.GetSize()
        childSize = widget.GetSize()
        xPos = int(parentPos[0] + (parentSize[0]-childSize[0])/2)
        yPos = int(parentPos[1] + (parentSize[1]-childSize[1])/2)
        frmPos = (xPos, yPos)
        widget.SetPosition(frmPos)
        
        return xPos, yPos
    
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
                        
        windowList = ['Magnetometer & SampleIndexRegistry',
                      'Motors Control',
                      'Vacuum Control',
                      'SQUID Control',
                      'IRM/ARM Control',
                      'frmMeasure']
        height = 18*len(windowList)
        self.windowListBox = wx.ListBox(panel, 26, wx.DefaultPosition, (LISTBOX_LENGTH, height), windowList, wx.LB_SINGLE)
        self.positionWidget(self.windowListBox)
        self.windowListBox.Bind(wx.EVT_LISTBOX, self.OnSelect, id=26)        
        
        self.testOptionListBox = wx.ListBox(panel, -1, pos=wx.DefaultPosition, size=(LISTBOX_LENGTH, height), choices=['Test'], style=wx.LB_SINGLE)
        self.testOptionListBox.Bind(wx.EVT_LISTBOX, self.OnTestOption)
        self.testOptionListBox.Hide()
        
        self.messageBox = wx.TextCtrl(panel, -1, pos = (10, 10), size = (200, 300), style = wx.EXPAND|wx.TE_MULTILINE)        
        
        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)
        
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

    '''
        frmProgram.mnuViewMeasurement.Enabled = True
        frmProgram.mnuViewMeasurement.Checked = True
    '''
    def updateViewMeasurementWindow(self, enableFlag):
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
        self.modConfig.processData.NOCOMM_MODE = self.modConfig.NoCommMode 
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
        return

    '''
    '''
    def onShow(self, event):
        xPos, yPos = self.positionWidget(self.windowListBox)
        windowListSize = self.windowListBox.GetSize()
        
        yPos += windowListSize[1] + 200
        self.testOptionListBox.SetPosition((xPos, yPos))
        return
    
    '''
        Close MainForm
    '''
    def onClosed(self, event):
        if not self.paleoThread.backgroundRunningFlag:
            if (self.paleoThread.processQueue != None):
                self.paleoThread.processQueue.put('Program_End')        
            self.paleoThread.runProcess([self.devControl.SYSTEM_DISCONNECT,[None]])
        
        self.Destroy()    

    '''
    '''
    def OnSelect(self, event):
        index = event.GetSelection()
        self.currentTest = self.windowListBox.GetString(index)
        
        if (self.currentTest == 'Magnetometer & SampleIndexRegistry'):
            self.testOptionListBox.Hide()
            self.frmSampleIndexRegistry.Show()
            self.magControl.Show()
            self.panelList['frmMagnetometerControl'] = self.magControl
            
        elif (self.currentTest == 'Motors Control'):
            self.testOptionListBox.Hide()
            motorControl = frmDCMotors(parent=self)
            self.panelList['frmDCMotors'] = motorControl        
            motorControl.Show(True)

        elif (self.currentTest == 'Vacuum Control'):
            self.testOptionListBox.Hide()            
            vacuumControl = frmVacuum(parent=self)
            self.panelList['frmVacuum'] = vacuumControl
            vacuumControl.Show()
            
        elif (self.currentTest == 'SQUID Control'):
            self.testOptionListBox.Hide()
            squidControl = frmSQUID(parent=self)
            self.panelList['frmSQUID'] = squidControl
            squidControl.Show()

        elif (self.currentTest == 'IRM/ARM Control'):
            self.testOptionListBox.Hide()
            self.panelList['frmIRMARM'] = self.frmIRMARM
            self.frmIRMARM.Show()
                    
        elif (self.currentTest == 'frmMeasure'):
            self.panelList['frmMeasure'] = self.frmMeasure
            self.frmMeasure.Show()
            
            options = ['ImportZijRoutine']
            self.testOptionListBox.SetItems(options)
            height = 18*len(options)
            self.testOptionListBox.SetSize((LISTBOX_LENGTH, height))
            self.testOptionListBox.Show()
        
        return

    '''
    '''
    def OnTestOption(self, event):        
        if (self.currentTest == 'frmMeasure'):
            index = event.GetSelection()
            testOption = self.testOptionListBox.GetString(index)
            
            if (testOption == 'ImportZijRoutine'):
                self.frmMeasure.lblDemag.SetValue('NRM 0')
                self.frmMeasure.lblDataFileName.SetValue('C:\\PaleoMag\\Data\\SAM\\Bill2A\\Bill2A.sam')
                dataDict = {'FilePath': 'Bill2A1.1',
                            'crdec': 225.00,
                            'crinc': -3.2865E-8,
                            'momentvol': 4.9469E-6,
                            'refresh': False}
                self.frmMeasure.ImportZijRoutine(dataDict)
                 
        return

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        
        frame = frmTestUnit(parent=None)
        frame.Maximize(maximize=True)
        frame.Show()        
        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        