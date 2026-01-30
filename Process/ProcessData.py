'''
Created on Oct 31, 2024

@author: hd.nguyen
'''

class ProcessData():
    '''
    classdocs
    '''    
    def __init__(self):
        '''
        Constructor
        '''
        self.config = None
        self.NOCOMM_MODE = False
        self.frmSettingsVisible = False
        self.frmSettingsOptions2Visible = False
        self.frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY = False
        self.HasXYTableBeenHomed = False
        self.ADwinDO = 0
        self.ADwin_optCalRamp = 0
        self.ADwin_monitorTrigVolt = 0.0
        self.ADwin_peakField = 0.0
        self.ADwin_rampPeakVoltage = 0.0
        self.ADwin_rampUpSlope = 0
        self.ADwin_rampDownSlope = 0
        self.motorsEnable = False
        self.vacuumEnable = False
        self.irmArmEnable = False
        self.squidEnable = False
        self.adwinEnable = False
        self.susceptibilityEnable = False
        self.SampleHandlerCurrentHole = 1
        self.SampleNameCurrent = ''
        self.SampleStepCurrent = ''
        self.EnableHolderMomentTooHighRemeasurements = False
                
        self.PortOpen = {'UpDown': False,
                         'Turning': False,
                         'ChangerX': False,
                         'ChangerY': False}
        
        