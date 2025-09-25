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

from Process.ProcessData import ProcessData

class frmTestUnit(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmTestUnit, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        config = configparser.ConfigParser()
        configPath = 'C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\SVN\\Windows\\Rock Magnetometer\\Paleomag_v3_Hung.INI'
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
        
        self.panelList = []
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((1500, 1000))
        self.SetTitle('Test Unit')
        self.Centre()

    '''
    '''
    def pushTaskToQueue(self, paramList):
        return

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmTestUnit(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        