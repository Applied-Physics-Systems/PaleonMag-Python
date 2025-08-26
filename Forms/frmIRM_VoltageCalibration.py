'''
Created on Jul 17, 2025

@author: hd.nguyen
'''
import wx

class frmIRM_VoltageCalibration(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        try:            
            self.parent = parent
            if (parent != None):
                super(frmIRM_VoltageCalibration, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
            else:
                super(frmIRM_VoltageCalibration, self).__init__(parent, wx.NewIdRef())
                
        except Exception as e:
            print(e)
                
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('Voltage Calibration')
        self.Centre()
        self.Show(True)
                
    '''
    '''
    def ZOrder(self, value):
        print('TODO')
        return 
                
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmIRM_VoltageCalibration(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
