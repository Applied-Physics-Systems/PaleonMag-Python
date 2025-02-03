'''
Created on Feb 3, 2025

@author: hd.nguyen
'''
import wx

class frmADWIN_AF(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmADWIN_AF, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
                
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
                
        self.SetSize((500, 700))
        self.SetTitle('ADWIN AF Ramp')
        self.Centre()
        self.Show(True)

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''                
    '''
        Close Tip Dialog box
    '''
    def onClose(self, event):
        if self.parent.panelList:
            if 'RegistryControl' in self.parent.panelList.keys():          
                del self.parent.panelList['RegistryControl']
                
        self.Destroy()

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmADWIN_AF(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)

        