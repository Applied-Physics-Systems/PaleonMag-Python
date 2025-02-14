'''
Created on Feb 7, 2025

@author: hd.nguyen
'''
import wx

class frmFileSave(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmFileSave, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('ADWIN Files')
        self.Centre()
        self.Show(True)

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmFileSave(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        