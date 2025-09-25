'''
Created on Sep 24, 2025

@author: hd.nguyen
'''
import wx

class frmChanger(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmChanger, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmChanger, self).__init__(parent, wx.NewIdRef())
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
    def Clear(self):
        print('TODO: frmChanger.Clear')
        return

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmChanger(parent=None)
        frame.Show(True)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                
                