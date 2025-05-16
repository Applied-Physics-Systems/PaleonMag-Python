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
        
        self.PortOpen = {'UpDown': False,
                         'Turning': False,
                         'ChangerX': False,
                         'ChangerY': False}
        
        