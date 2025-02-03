'''
Created on Oct 31, 2024

@author: hd.nguyen
'''

class ProcessData():
    '''
    classdocs
    '''
    config = None
    frmSettingsVisible = False
    frmSettingsOptions2Visible = False
    frmSettingsChkOverrideHomeToTop_ForMoveMotorAbsoluteXY = False
    HasXYTableBeenHomed = False
    ADwinDO = 0
    
    PortOpen = {'UpDown': False,
                'Turning': False,
                'ChangerX': False,
                'ChangerY': False}

    def __init__(self):
        '''
        Constructor
        '''
        