'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import wx

class frmSampleIndexRegistry(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmSampleIndexRegistry, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        self.SetSize((500, 700))
        self.SetTitle('Sample Index Register')
        
        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        parentPos = self.parent.GetPosition()
        parentSize = self.parent.GetSize()
        childSize = self.GetSize()
        xOffset = 10
        xPos = parentPos[0] + parentSize[0] - childSize[0] - xOffset * 3
        yPos = parentPos[1] + (parentSize[1]-childSize[1])/2
        frmPos = (xPos, yPos)
        self.SetPosition(frmPos)
        
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
        frame = frmSampleIndexRegistry(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                
