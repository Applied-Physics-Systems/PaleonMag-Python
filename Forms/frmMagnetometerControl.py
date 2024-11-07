'''
Created on Nov 7, 2024

@author: hd.nguyen
'''
import wx

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self, -1, "This is a PageOne object", (20,20))


class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self, -1, "This is a PageTwo object", (40, 40))


class frmMagnetometerControl(wx.Frame):
    '''
    classdocs
    '''
    parent = None

    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmMagnetometerControl, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        self.nb = wx.Notebook(panel)

        # create the page windows as children of the notebook
        page1 = PageOne(self.nb)
        page2 = PageTwo(self.nb)

        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(page1, "Automatic Data Collection")
        self.nb.AddPage(page2, "Manual Data Collection")
         
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClose)
                                        
        self.SetTitle('Magnetometer Control')
        parentPos = self.parent.GetPosition()
        parentSize = self.parent.GetSize()
        childSize = self.GetSize()
        xOffset = 10
        xPos = parentPos[0] + xOffset
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
            if 'MagnetometerControl' in self.parent.panelList.keys():          
                del self.parent.panelList['MagnetometerControl']
                
        self.Destroy()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmMagnetometerControl(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        