'''
Created on Sep 24, 2025

@author: hd.nguyen
'''
import wx

class frmMeasure(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmMeasure, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmMeasure, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
                
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('Measurement Window')
        self.Centre()
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def initForm(self, functionID):
        if (functionID == 'cmdManHolder_Click'):
            self.parent.modConfig.processData.SampleHolder.SampleHeight = self.parent.magControl.manualPage.txtSampleHeight.GetValue() * self.parent.modConfig.UpDownMotor1cm
            
            '''                                        
                    frmProgram.StatBarNew "Measuring holder..."
                    
                    'DisplayStatus (4)            ' Measuring Holder...
                    frmProgram.mnuViewMeasurement.Enabled = True
                    frmProgram.mnuViewMeasurement.Checked = True
                    
                    Load frmMeasure
                    Load frmStats
                    
                    frmMeasure.HideStats
                    frmMeasure.clearStats
                    frmMeasure.clearData
                    
                    frmMeasure.SetSample "Holder"
                    frmMeasure.MomentX.Visible = False ' (October 2007 L Carporzen) Susceptibility versus demagnetization
                    
                    frmMeasure.framJumps.Top = 5040
                    frmMeasure.framJumps.Left = 5400
                    
                    frmMeasure.InitEqualArea ' (August 2007 L Carporzen) Equal area plot
                    
                    frmMeasure.ZOrder
                    frmMeasure.Show
            '''
            
        return 
    
    '''
    '''
    def updateFlowStatus(self):
        print('TODO: frmMeasure.updateFlowStatus')
        return

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmMeasure(parent=None)
        frame.Show(True)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        
                