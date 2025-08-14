'''
Created on Feb 6, 2025

@author: hd.nguyen
'''
import wx

'''---------------------------------------------------------------------------------------------'''
class Tab_DCMotor1(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_DCMotor2(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_DCMotorXY(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_Magnetometer(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_AFDemag1(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_AFDemag2(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_AFIRMChannels(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_IRM(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_ARM(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_Vacuum(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_Modules(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class Tab_AFTempSensors(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

'''---------------------------------------------------------------------------------------------'''
class SettingsNotebook(wx.Notebook):
    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        panel = Tab_DCMotor1(self)
        self.AddPage(panel, 'DC Motor (1)')
        panel = Tab_DCMotor2(self)
        self.AddPage(panel, 'DC Motor (2)')
        panel = Tab_DCMotorXY(self)
        self.AddPage(panel, 'DC Motor (XY)')
        panel = Tab_Magnetometer(self)
        self.AddPage(panel, 'Magnetometer')
        panel = Tab_AFDemag1(self)
        self.AddPage(panel, 'AF Demag (1)')
        panel = Tab_AFDemag2(self)
        self.AddPage(panel, 'AF Demag (2)')
        panel = Tab_AFIRMChannels(self)
        self.AddPage(panel, 'AF/IRM Channels')
        panel = Tab_IRM(self)
        self.AddPage(panel, 'IRM')
        panel = Tab_ARM(self)
        self.AddPage(panel, 'ARM')
        panel = Tab_Vacuum(self)
        self.AddPage(panel, 'Vacuum')
        panel = Tab_Modules(self)
        self.AddPage(panel, 'Modules')
        panel = Tab_AFTempSensors(self)
        self.AddPage(panel, 'AF Temp. Sensors')

'''---------------------------------------------------------------------------------------------'''
class TabsPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.notebook = SettingsNotebook(self, pos=(10,10), size=kwargs['size'])

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)

'''---------------------------------------------------------------------------------------------'''
class frmSettings(wx.Frame):
    def __init__(self, parent):
        if (parent != None):
            wx.Frame.__init__(self, parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            wx.Frame.__init__(self, parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        self.tabs = TabsPanel(panel, size=(950, 400))
        tabPanelSize = self.tabs.GetSize()

        btnHeight = 30
        yOffset = 10
        xOffset = 10
        largeBtnLength = 150
        smallBtnLength = 100
        calRodBtn = wx.Button(panel, label='Calibration of the rod', pos=(xOffset, tabPanelSize[1]+yOffset), size=(150, btnHeight))
        xPos = 2*xOffset + largeBtnLength 
        resumeRunBtn = wx.Button(panel, label='Resume Run', pos=(xPos, tabPanelSize[1]+yOffset), size=(smallBtnLength, btnHeight))
        xPos += smallBtnLength + 210
        saveIniBtn = wx.Button(panel, label='Save to .INI file', pos=(xPos, tabPanelSize[1]+yOffset), size=(largeBtnLength, btnHeight))
        xPos += largeBtnLength + xOffset 
        cancelBtn = wx.Button(panel, label='Cancel', pos=(xPos, tabPanelSize[1]+yOffset), size=(smallBtnLength, btnHeight))
        xPos += smallBtnLength + xOffset
        saveCurrentBtn = wx.Button(panel, label='Save to Current Session, only', pos=(xPos, tabPanelSize[1]+yOffset), size=(largeBtnLength+50, btnHeight))
        
        self.SetSize((tabPanelSize[0] + 30, tabPanelSize[1] + btnHeight + 6*yOffset))
        self.SetTitle('Settings Dialog')
        self.Centre()
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmSettings(parent=None)
        frame.tabs.notebook.SetSelection(3)
        frame.Show()
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        