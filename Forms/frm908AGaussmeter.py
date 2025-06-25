'''
Created on Feb 7, 2025

@author: hd.nguyen
'''
import wx

class frm908AGaussmeter(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frm908AGaussmeter, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        self.SetSize((400, 305))
        self.SetTitle('Gaussmeter Control')
        self.Centre()
        self.Show(True)

    '''
    '''
    @classmethod
    def InitializeDCFieldRecord(self, InWave, RampTimeEst_msec):
        # TODO
        return
    
    '''
    '''
    @classmethod
    def StartDCFieldRecord(self, InWave):
        # TODO
        return True
    
    '''
    '''
    @classmethod
    def StopDCFieldRecord(self, InWave, SaveData = True):
        # TODO
        return True

#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frm908AGaussmeter(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
                        
                