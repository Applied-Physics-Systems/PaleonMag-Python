'''
Created on Sep 24, 2025

@author: hd.nguyen
'''

class modFlow():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.old_NOCOMMMODE = False
        
        self.Prog_halted = False
        self.Prog_paused = False
        
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    def Flow_Resume(self):
        self.Prog_paused = False
        self.Prog_halted = False
        self.parent.NOCOMM_MODE = self.old_NOCOMMMODE
        if (self.Prog_paused or self.Prog_halted):
            print('TODO: frmDCMotors.ResumeMove')
            
        print('TODO: frmProgram.updateFlowMenu')
        print('TODO: frmMeasure.updateFlowStatus')
        print('TODO: frmSettings.cmdFlowControl.Caption = "Pause Flow"')   
        return
    
    
        