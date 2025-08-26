'''
Created on Feb 7, 2025

@author: hd.nguyen
'''
import wx

class frmCalibrateCoils(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent, InAFMode=False):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmCalibrateCoils, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmCalibrateCoils, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        self.inAFMode = InAFMode
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('AF Coil Calibration')
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
        frame = frmCalibrateCoils(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        
        