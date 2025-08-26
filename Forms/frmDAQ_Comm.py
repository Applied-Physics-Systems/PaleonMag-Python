'''
Created on Aug 22, 2025

@author: hd.nguyen
'''
import wx

class frmDAQ_Comm(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmDAQ_Comm, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmDAQ_Comm, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('DAQ Boards Comm Controller')
        self.Centre()
        self.Show(True)

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmDAQ_Comm(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)        
        
        