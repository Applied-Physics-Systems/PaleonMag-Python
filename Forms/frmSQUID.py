'''
Created on Nov 19, 2024

@author: hd.nguyen
'''
import wx

class frmSQUID(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        super(frmSQUID, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        btnLength = 105
        smallBtnLength = 50
        smallTxtBoxLength = 60
        btnHeight = 30
        smallBtnHeight = 22
        txtBoxHeight = 25
        btnXOri = 20
        btnYOri = 20
        txtBoxOri = btnYOri + 2
        btnXOffset = 120
        btnYOffset = 40
        
        txtOffset = 5
        txtBoxXOffset = btnXOffset - smallTxtBoxLength - 15
        txtBoxYOffset = 40 
        
        # First Column
        wx.StaticText(panel, label='Output', pos=(btnXOri, txtBoxOri + txtBoxYOffset + txtOffset))
        self.outputTBox = wx.TextCtrl(panel, pos=(btnXOri+txtBoxXOffset, txtBoxOri + txtBoxYOffset), size=(smallTxtBoxLength, txtBoxHeight))
        # Radio buttons group
        radioBoxLabels = ['X', 'Y', 'Z', 'A']
        self.activeMotroRBox = wx.RadioBox(panel, label = '', pos = (btnXOri, btnYOri + 2*btnYOffset), choices = radioBoxLabels,
                                majorDimension = 1, style = wx.RA_SPECIFY_COLS) 
        cr1Btn = wx.Button(panel, label='CR1', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset), size=(smallBtnLength, smallBtnHeight))
        clcBtn = wx.Button(panel, label='CLC', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        cseBtn = wx.Button(panel, label='CSE', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 2*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        cf1Btn = wx.Button(panel, label='CF1', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 3*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        clpBtn = wx.Button(panel, label='CLP', pos=(btnXOri + txtBoxXOffset, btnYOri + 2*btnYOffset + 4*smallBtnHeight), size=(smallBtnLength, smallBtnHeight))
        configBtn = wx.Button(panel, label='Configure SQUID', pos=(btnXOri, btnYOri + 5*btnYOffset), size=(btnLength, btnHeight))
        
        # Second Column        
        connectBtn = wx.Button(panel, label='Connect', pos=(btnXOri + btnXOffset, btnYOri), size=(btnLength, btnHeight))
        wx.StaticText(panel, label='Input', pos=(btnXOri + btnXOffset, txtBoxOri + txtBoxYOffset + txtOffset))
        self.inputTBox = wx.TextCtrl(panel, pos=(btnXOri + txtBoxXOffset + btnXOffset, txtBoxOri + txtBoxYOffset), size=(smallTxtBoxLength, txtBoxHeight))
        readCountBtn = wx.Button(panel, label='Read Count', pos=(btnXOri + btnXOffset, btnYOri + 2*btnYOffset), size=(btnLength, btnHeight))        
        readDataBtn = wx.Button(panel, label='Read Data', pos=(btnXOri + btnXOffset, btnYOri + 3*btnYOffset), size=(btnLength, btnHeight))
        readRangeBtn = wx.Button(panel, label='Read Range', pos=(btnXOri + btnXOffset, btnYOri + 4*btnYOffset), size=(btnLength, btnHeight))
        
        # Third Column
        closeBtn = wx.Button(panel, label='Close', pos=(btnXOri + 2*btnXOffset, btnYOri), size=(btnLength, btnHeight))
        closeBtn.Bind(wx.EVT_BUTTON, self.onClose)
        resetCountBtn = wx.Button(panel, label='Reset Count', pos=(btnXOri + 2*btnXOffset, btnYOri + 2*btnYOffset), size=(btnLength, btnHeight))
        readBtn = wx.Button(panel, label='Read', pos=(btnXOri + 2*btnXOffset, btnYOri + 5*btnYOffset), size=(btnLength, btnHeight))
        
        # Button group
        microBtnLength = 30
        microBtnHeight = 22
        groupOffset = 0
        groupXOffset = 5
        groupYOffset = groupOffset + 20 
        btnXOri += 2*btnXOffset
        wx.StaticBox(panel, -1, 'Change Range', pos=(btnXOri + groupOffset, btnYOri + 3*btnYOffset), size=(110, 70))
        btnYOri += 3*btnYOffset + groupYOffset 
        fRangeBtn = wx.Button(panel, label='F', pos=(btnXOri + groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        tRangeBtn = wx.Button(panel, label='T', pos=(btnXOri + 8*groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        eRangeBtn = wx.Button(panel, label='E', pos=(btnXOri + 15*groupXOffset, btnYOri), size=(microBtnLength, microBtnHeight))
        oneRangeBtn = wx.Button(panel, label='1', pos=(btnXOri + groupXOffset, btnYOri+ microBtnHeight + 2), size=(microBtnLength, microBtnHeight))
        hRangeBtn = wx.Button(panel, label='H', pos=(btnXOri + 8*groupXOffset, btnYOri+ microBtnHeight + 2), size=(microBtnLength, microBtnHeight))
        
        self.SetSize((400, 305))
        self.SetTitle('SQUID Control')
        self.Centre()
        self.Show(True)
        
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onClose(self, event):
        self.Close(force=False)
        return
        
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmSQUID(parent=None)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        

        
        