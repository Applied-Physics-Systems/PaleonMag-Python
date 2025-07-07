'''
Created on Feb 7, 2025

@author: hd.nguyen
'''
import wx

class frmAFTuner(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmAFTuner, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('MCC AF Tuner')
        self.Centre()
        self.Show(True)

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmAFTuner(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                