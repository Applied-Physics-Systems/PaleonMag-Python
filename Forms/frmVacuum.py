'''
Created on Nov 19, 2024

@author: hd.nguyen
'''
import wx

class frmVacuum(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmVacuum, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 300))
        self.SetTitle('Vacuum Control')
        self.Centre()
        self.Show(True)

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmVacuum(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        