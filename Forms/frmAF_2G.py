'''
Created on Mar 17, 2025

@author: hd.nguyen
'''
import wx

class frmAF_2G(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent = None, modConfig = None):
        '''
        Constructor
        '''        
        super(frmAF_2G, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        self.modConfig = modConfig
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmAF_2G(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        