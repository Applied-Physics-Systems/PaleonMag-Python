'''
Created on Oct 28, 2024

@author: hd.nguyen
'''
import wx

class frmTip(wx.Frame):
    '''
    classdocs
    '''
    tipMessage = """Make sure power is on to the following devices\n
1. All three 2G SQUID boxes
2. Motor driver box
3. Bartington susceptibility bridge (set to CGS and 1.0)
4. AF unit and cooling air, with the AF degausser on
   computer control(if you are going to do AF or rockmag)
5. IRM pulse box (if you are going to do rockmag)
6. ARM bias box (if you are going to do rockmag)"""
    parent = None

    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmTip, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        messageTBox = wx.TextCtrl(panel, pos=(10, 10), size=(350, 150), style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_NO_VSCROLL|wx.TE_READONLY)
        messageTBox.SetValue(self.tipMessage)
        
        btnLength = 120
        btnHeight = 30
        okBtn = wx.Button(panel, label='OK', pos=(240, 170), size=(btnLength, btnHeight))
        okBtn.Bind(wx.EVT_BUTTON, self.onOK)
        
        self.SetSize((390, 250))
        self.SetTitle('Reminder')
        self.Centre()
        self.Show(True)
                          
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''                
    '''
        Close Tip Dialog box
    '''
    def onOK(self, event):
        self.parent.Magnetometer_Initialize()
        
        self.Close()
        
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmTip(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        