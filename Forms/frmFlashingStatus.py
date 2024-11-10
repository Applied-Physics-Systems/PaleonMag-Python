'''
Created on Nov 5, 2024

@author: hd.nguyen
'''
import wx

class frmFlashingStatus(wx.Frame):
    '''
    classdocs
    '''

    def __init__(self, parent, message):
        '''
        Constructor
        '''
        super(frmFlashingStatus, self).__init__(parent)
        self.InitUI(message)

        # Add timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(1000)

    '''
    '''
    def InitUI(self, message):
        panel = wx.Panel(self)
        
        text = wx.StaticText(panel, label=message, pos=(10, 10))
        font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        text.SetFont(font)
                
        self.SetSize((400, 100))
        self.Centre()
        #self.SetWindowStyle(wx.STAY_ON_TOP)
        self.Show()
        
    '''
    '''
    def OnTimer(self, event):
        self.timer.Stop()
        self.Close()

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)        
        frame = frmFlashingStatus(parent=None, message='Test')
        app.MainLoop()    
        
    except Exception as e:
        print(e)
