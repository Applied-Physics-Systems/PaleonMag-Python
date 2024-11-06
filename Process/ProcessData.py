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
    
    PortOpen = [False, False, False, False]

    def __init__(self):
        '''
        Constructor
        '''
        