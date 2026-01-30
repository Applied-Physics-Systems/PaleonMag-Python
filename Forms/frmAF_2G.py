'''
Created on Mar 17, 2025

@author: hd.nguyen
'''
import wx

class frmAF_2G(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent = None):
        '''
        Constructor
        '''        
        if (parent != None):
            super(frmAF_2G, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmAF_2G, self).__init__(parent, wx.NewIdRef())
        self.parent = parent
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        XOri = 10
        YOri = 10
        textBoxLength = 30
        textBoxHeight = 20
        
        self.txtWaitingTime = wx.TextCtrl(panel, pos=(XOri, YOri), size=(textBoxLength, textBoxHeight))
        XOffset = textBoxLength + 5 
        wx.StaticText(panel, label='Waiting time (in s)\nbetwwen ramps', pos=(XOri + XOffset, YOri))
        
        self.SetSize((400, 305))
        self.SetTitle('2G AF Degausser')
        self.Centre()
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmAF_2G(parent=None)
        frame.Show()
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        