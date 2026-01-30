'''
Created on Sep 24, 2025

@author: hd.nguyen
'''
import wx
import time
import math

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

import matplotlib.patches as patches

LIGHT_PURPLE = wx.Colour(203, 195, 227)
LIGHT_GREEN = wx.Colour(144, 238, 144)
LIGHT_ORANGE = wx.Colour(255, 216, 178)

class frmMeasure(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmMeasure, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmMeasure, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        
        self.InitUI()        
                
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
        
        XOri = 10
        YOri = 10
        VSizer1, box1Length, box1Height = self.GUI_MeasureInfo(panel, XOri, YOri)        
        
        XOri += box1Length + 10
        VSizer2, box2Length, _ = self.GUI_PlotBox(panel, XOri, YOri)
        
        XOri += box2Length + 10
        VSizer3, box3Length, _ = self.GUI_CreateControl(panel, XOri, YOri)
        
        HSizer = wx.BoxSizer(wx.HORIZONTAL)
        HSizer.Add(VSizer1, 0, wx.ALL, 5)
        HSizer.Add(VSizer2, 0, wx.ALL, 5)
        HSizer.Add(VSizer3, 0, wx.ALL, 5)
        panel.SetSizer(HSizer)        

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)

        panelLength = box1Length + box2Length + box3Length + 30
        panelHeight =  box1Height + 10
        self.SetSize((panelLength, panelHeight))
        self.SetTitle('Measurement Window')
        self.Centre()
        return

    '''
    '''
    def GUI_MeasureInfo(self, panel, XOri, YOri):
        # Create sizer
        boxLength = 440
        box1Height = 180
        
        staticBox1 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box1Height))
        self.GUI_SampleSettings(panel, XOri, YOri)

        box2Height = 230
        YOri += box1Height + 10 
        staticBox2 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box2Height))
        self.GUI_DataBoxes(panel, XOri, YOri)

        box3Height = 170
        YOri += box2Height + 10
        staticBox3 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box3Height))
        self.GUI_StatBoxes(panel, XOri, YOri)
        
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(staticBox1, 1, wx.EXPAND)
        VSizer.Add(staticBox2, 1, wx.EXPAND)
        VSizer.Add(staticBox3, 1, wx.EXPAND)

        YOri += box3Height + 10
        return VSizer, boxLength, YOri
    
    '''
    '''
    def GUI_MomentX(self, panel, XOri, YOri):
        txtBoxLength = 75
        txtBoxHeight = 20
        
        XOffset = txtBoxLength + 10 
        YOffset = 17 
        xTexOffset = int(txtBoxLength/2) - 2
                        
        self.lblWarning= wx.StaticText(panel, label="It's up to you to retry manually that measurement !!!", pos=(XOri + xTexOffset, YOri))
        # Get the current font of the static text
        current_font = self.lblWarning.GetFont()

        # Create a new font based on the current font, but with bold weight
        bold_font = wx.Font(current_font.GetPointSize(),
                            current_font.GetFamily(),
                            current_font.GetStyle(),
                            wx.FONTWEIGHT_BOLD,  # Set the weight to bold
                            current_font.GetUnderlined(),
                            current_font.GetFaceName())

        # Set the new bold font to the static text
        self.lblWarning.SetFont(bold_font)
        self.lblWarning.Hide()
        
        wx.StaticText(panel, label='X', pos=(XOri + xTexOffset + 2*XOffset, YOri + YOffset))
        wx.StaticText(panel, label= '\u25B2 4 Positions (emu)', pos=(XOri + xTexOffset, YOri + 2*YOffset + 2))
        self.lblDeltaX = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Y', pos=(XOri + xTexOffset + 3*XOffset, YOri + YOffset))
        self.lblDeltaY = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Z', pos=(XOri + xTexOffset + 4*XOffset, YOri + YOffset))
        self.lblDeltaZ = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        YOffset += 5
        wx.StaticText(panel, label= '\u25B2 4 Positions/Moments', pos=(XOri + xTexOffset, YOri + 3*YOffset + 2))
        self.lblRatioX = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblRatioY = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblRatioZ = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        
        self.lblRed = wx.StaticText(panel, label='Orange = order of magnitude (1 - 5) of the moment, be attentive ...', pos=(XOri, YOri + 5*YOffset))
        self.lblRed.Hide()
        self.lblOrange = wx.StaticText(panel, label='Red = noise higher than 5 times the moment, I am not redoing it ...', pos=(XOri, YOri  + 7*YOffset))
        self.lblOrange.Hide()
        return
    
    '''
    '''
    def GUI_PlotBox(self, panel, XOri, YOri):
        boxLength = 440
        box1Height = 180
        
        self.figure = Figure(figsize=(3, 3))
        self.axes = self.figure.add_subplot(111, aspect='equal') # 1 row, 1 column, 1st subplot
        self.canvas = FigureCanvas(panel, -1, self.figure)       
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.InitEqualArea()
                
        # Initial data
        theta_start = 0
        r_start = 0
        theta_end = 0 
        r_end = 0
        self.theta_line = np.array([theta_start, theta_end])
        self.r_line = np.array([r_start, r_end])
        self.line, = self.axes.plot(self.theta_line, self.r_line, color='red', lw=2)
    
        # Create the animation
        self.updatePlot = FuncAnimation(self.figure, self.updatePolarPlot, frames=200, interval=500, blit=False)
        
        staticBox1 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box1Height))
        # Compute the position of YOri
        _, height = self.figure.get_size_inches()
        XOri += 10
        YOri += int(height*self.figure.dpi) + 10        
        self.MomentX = wx.StaticText(panel, label='', pos=(XOri, YOri))
        self.GUI_MomentX(panel, XOri, YOri)
        
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(self.canvas, 1, wx.EXPAND)
        VSizer.Add(staticBox1, 1, wx.EXPAND)

        YOri += box1Height + 10
        return VSizer, boxLength, YOri

    '''
    '''
    def GUI_CreateControl(self, panel, XOri, YOri):
        boxLength = 340
        boxHeight = 300                                        
        staticBox1 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        
        XOri += 10
        YOri += boxHeight + 10 
        staticBox2 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))

        staticText = wx.StaticText(panel, label='Zijderveld (1967) Plot (N-S Orthographic Projection)', pos=(XOri, YOri))
        # Make the static text bold
        font = staticText.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        staticText.SetFont(font)        
        
        YOffset = 20
        txtBoxLength = 40
        txtBoxHeight = 20
        self.txtZijLines = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.txtZijLines.SetValue('15')
        txtBoxXOffset = txtBoxLength + 5 
        wx.StaticText(panel, label='Previous Steps', pos=(XOri + txtBoxXOffset, YOri + YOffset + 5))
        
        txtBoxXOffset += 100
        radioBtn1 = wx.RadioButton(panel, 11, label = 'Core Coordinates', pos = (XOri + txtBoxXOffset, YOri + YOffset), style = wx.RB_GROUP) 
        wx.RadioButton(panel, 22, label = 'Geographic Coordinates',pos = (XOri + txtBoxXOffset, YOri + 2*YOffset)) 
        wx.RadioButton(panel, 33, label = 'Bedding Coordinates',pos = (XOri + txtBoxXOffset, YOri + 3*YOffset))
        radioBtn1.SetValue(True)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRGroupChanges)
                
        self.magnitudeChkBox = wx.CheckBox(panel, label='Moment Magnitude', pos=(XOri, YOri + 3*YOffset))
        self.magnitudeChkBox.SetForegroundColour(wx.RED)
        self.magnitudeChkBox.SetValue(True) 
        self.susceptibilityChkBox = wx.CheckBox(panel, label='Susceptibility', pos=(XOri, YOri + 4*YOffset))
        self.susceptibilityChkBox.SetForegroundColour(wx.BLUE)
        self.susceptibilityChkBox.SetValue(True) 
        
        YOri += 5
        txtBoxXOffset = 260
        YOffset = 35
        btnLength = 40
        btnHeight = 25        
        cmdHideZij = wx.Button(panel, label='Hide', pos=(XOri + txtBoxXOffset, YOri + 2*YOffset + 5), size=(btnLength, btnHeight))        
        cmdHideZij.Bind(wx.EVT_BUTTON, self.cmdHideZij_Click)        
        
        # Create sizer
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(staticBox1, 1, wx.EXPAND)
        VSizer.Add(staticBox2, 1, wx.EXPAND)
        
        return VSizer, boxLength, boxHeight

    '''
    '''
    def GUI_SampleSettings(self, panel, XOri, YOri):
        XOri += 10
        YOri += 10        
        txtBoxLength = 70
        txtXOffset = 55
        txtBoxHeight = 20
        txtYOffset = 3
        
        # First line
        wx.StaticText(panel, label='Sample', pos=(XOri, YOri + txtYOffset))
        self.lblSampName = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri), size=(txtBoxLength, txtBoxHeight))

        XOffset = txtXOffset + txtBoxLength + 10 
        wx.StaticText(panel, label='Avg. Cycles', pos=(XOri + XOffset , YOri + txtYOffset))
        self.lblAvgCycles = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 10, YOri), size=(txtBoxLength, txtBoxHeight))

        wx.StaticText(panel, label='Demag', pos=(XOri + 2*XOffset + 15, YOri + txtYOffset))
        self.lblDemag = wx.TextCtrl(panel, pos=(XOri + txtXOffset + 2*XOffset, YOri), size=(txtBoxLength, txtBoxHeight))

        # Second line
        txtBoxLength = 340
        YOffset = txtBoxHeight + 10 
        wx.StaticText(panel, label='File Path', pos=(XOri, YOri + txtYOffset + YOffset))
        self.lblDataFileName = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        # Third line
        txtBoxLength = 40
        wx.StaticText(panel, label='Directions', pos=(XOri, YOri + txtYOffset + 2*YOffset))
        self.lblDirs = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        XOffset = txtXOffset + txtBoxLength + 20 
        wx.StaticText(panel, label='Measuring', pos=(XOri + XOffset, YOri + txtYOffset + 2*YOffset))
        self.lblMeasDir = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset + 5, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        txtXOffset = 20
        XOffset = 2*XOffset + 40
        wx.StaticText(panel, label='Nb', pos=(XOri + XOffset, YOri + txtYOffset + 2*YOffset))
        self.lblMeascount = wx.TextCtrl(panel, pos=(XOri + txtXOffset + XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        txtXOffset += txtBoxLength + 5   
        self.lblSampleHeight = wx.TextCtrl(panel, pos=(XOri + XOffset + txtXOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        txtXOffset += txtBoxLength + 2
        wx.StaticText(panel, label='cm', pos=(XOri + XOffset + txtXOffset, YOri + txtYOffset + 2*YOffset))
        
        # Fourth line
        txtXOffset = 55
        wx.StaticText(panel, label='Cup #:', pos=(XOri, YOri + txtYOffset + 3*YOffset))
        self.lblCupNumber = wx.TextCtrl(panel, pos=(XOri + txtXOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        
        # Fifth line
        btnLength = 90
        btnHeight = 30        
        self.cmdHide = wx.Button(panel, label='Hide', pos=(XOri, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.cmdHide.Bind(wx.EVT_BUTTON, self.cmdHide_Click)

        XOffset = btnLength + 10 
        self.cmdPrint = wx.Button(panel, label='Print', pos=(XOri + XOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.cmdPrint.Bind(wx.EVT_BUTTON, self.cmdPrint_Click)

        self.buttonHalt = wx.Button(panel, label='Halt Run', pos=(XOri + 2*XOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.buttonHalt.Bind(wx.EVT_BUTTON, self.buttonHalt_Click)

        self.buttonPause = wx.Button(panel, label='Pause Run', pos=(XOri + 3*XOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))
        self.buttonPause.Bind(wx.EVT_BUTTON, self.buttonPause_Click)
        
        return
    
    '''
    '''
    def GUI_DataBoxes(self, panel, XOri, YOri):
        XOri += 10
        YOri += 5
        
        txtBoxLength = 75
        txtBoxHeight = 20
        XOffset = txtBoxLength + 10 
        YOffset = 17 
                
        # Zero set
        wx.StaticText(panel, label='XZero', pos=(XOri, YOri))
        self.lblMeasXZero0 = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasXZero0.SetBackgroundColour(LIGHT_PURPLE)
        wx.StaticText(panel, label='YZero', pos=(XOri + XOffset, YOri))
        self.lblMeasYZero0 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasYZero0.SetBackgroundColour(LIGHT_GREEN)
        wx.StaticText(panel, label='ZZero', pos=(XOri + 2*XOffset, YOri))
        self.lblMeasZZero0 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZZero0.SetBackgroundColour(LIGHT_ORANGE)

        YOffset += txtBoxHeight + 3 
        self.lblMeasXZero1 = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasXZero1.SetBackgroundColour(LIGHT_PURPLE)
        self.lblMeasYZero1 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasYZero1.SetBackgroundColour(LIGHT_GREEN)
        self.lblMeasZZero1 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZZero1.SetBackgroundColour(LIGHT_ORANGE)

        btnLength = 90
        btnHeight = 30        
        self.cmdShowPlots = wx.Button(panel, label='Show Plots', pos=(XOri + 3*XOffset + 50, YOri), size=(btnLength, btnHeight))
        self.cmdShowPlots.Bind(wx.EVT_BUTTON, self.cmdShowPlots_Click)
        
        textYOffset = 25
        self.lblXSQUID = wx.StaticText(panel, label=' ', pos=(XOri, YOri + YOffset + textYOffset))
        self.lblYSQUID = wx.StaticText(panel, label=' ', pos=(XOri + XOffset, YOri + YOffset + textYOffset))
        self.lblZSQUID = wx.StaticText(panel, label=' ', pos=(XOri + 2*XOffset, YOri + YOffset + textYOffset))
        self.lblRescan = wx.StaticText(panel, label=' ', pos=(XOri + 3*XOffset + 20, YOri + YOffset))
        
        # Measure set
        YOri += 2*YOffset + 10
        YOffset = 17
        textXOffset = 20
        wx.StaticText(panel, label='X', pos=(XOri + textXOffset, YOri))
        self.lblMeasX0 = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasX0.SetBackgroundColour(LIGHT_PURPLE)
        wx.StaticText(panel, label='Y', pos=(XOri + textXOffset + XOffset, YOri))
        self.lblMeasY0 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasY0.SetBackgroundColour(LIGHT_GREEN)
        wx.StaticText(panel, label='Z', pos=(XOri + textXOffset + 2*XOffset, YOri))
        self.lblMeasZ0 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZ0.SetBackgroundColour(LIGHT_ORANGE)
        wx.StaticText(panel, label='Dec', pos=(XOri + textXOffset + 3*XOffset, YOri))
        self.lblCalcDec0 = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Inc', pos=(XOri + textXOffset + 4*XOffset, YOri))
        self.lblCalcInc0 = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        YOri = YOri + YOffset
        YOffset = txtBoxHeight + 5
        self.lblMeasX1 = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasX1.SetBackgroundColour(LIGHT_PURPLE)
        self.lblMeasY1 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasY1.SetBackgroundColour(LIGHT_GREEN)
        self.lblMeasZ1 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZ1.SetBackgroundColour(LIGHT_ORANGE)
        self.lblCalcDec1 = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblCalcInc1 = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        self.lblMeasX2 = wx.TextCtrl(panel, pos=(XOri, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasX2.SetBackgroundColour(LIGHT_PURPLE)
        self.lblMeasY2 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasY2.SetBackgroundColour(LIGHT_GREEN)
        self.lblMeasZ2 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZ2.SetBackgroundColour(LIGHT_ORANGE)
        self.lblCalcDec2 = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblCalcInc2 = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + 2*YOffset), size=(txtBoxLength, txtBoxHeight))

        self.lblMeasX3 = wx.TextCtrl(panel, pos=(XOri, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasX3.SetBackgroundColour(LIGHT_PURPLE)
        self.lblMeasY3 = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasY3.SetBackgroundColour(LIGHT_GREEN)
        self.lblMeasZ3 = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblMeasZ3.SetBackgroundColour(LIGHT_ORANGE)
        self.lblCalcDec3 = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.lblCalcInc3 = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))

        self.lblMeasXZero = [self.lblMeasXZero0, self.lblMeasXZero1]
        self.lblMeasYZero = [self.lblMeasYZero0, self.lblMeasYZero1]
        self.lblMeasZZero = [self.lblMeasZZero0, self.lblMeasZZero1]
        self.lblMeasX = [self.lblMeasX0, self.lblMeasX1, self.lblMeasX2, self.lblMeasX3]
        self.lblMeasY = [self.lblMeasY0, self.lblMeasY1, self.lblMeasY2, self.lblMeasY3]
        self.lblMeasZ = [self.lblMeasZ0, self.lblMeasZ1, self.lblMeasZ2, self.lblMeasZ3]
        self.lblCalcDec = [self.lblCalcDec0, self.lblCalcDec1, self.lblCalcDec2, self.lblCalcDec3]
        self.lblCalcInc = [self.lblCalcInc0, self.lblCalcInc1, self.lblCalcInc2, self.lblCalcInc3]
                
        return

    '''
    '''
    def GUI_StatBoxes(self, panel, XOri, YOri):
        XOri += 10
        
        txtBoxLength = 60
        txtBoxHeight = 20
        XOffset = txtBoxLength + 10 
        YOffset = 17 
        textXOffset = 10
                
        # First Line
        wx.StaticText(panel, label='Avg. X', pos=(XOri + textXOffset, YOri))
        self.lblavgx = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Avg. Y', pos=(XOri + textXOffset + XOffset, YOri))
        self.lblavgy = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Avg. Z', pos=(XOri + textXOffset + 2*XOffset, YOri))
        self.lblavgz = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        btnLength = 90
        btnHeight = 30        
        self.cmdStats = wx.Button(panel, label='Show Stats', pos=(XOri + 4*XOffset + 20, YOri), size=(btnLength, btnHeight))
        self.cmdStats.Bind(wx.EVT_BUTTON, self.cmdStats_Click)
        
        # Second Line
        YOri += YOffset + txtBoxHeight + 10  
        textXOffset = 5
        txtBoxLength = 70
        XOffset = txtBoxLength + 10 
        wx.StaticText(panel, label='Moment', pos=(XOri + textXOffset, YOri))
        self.lblavgmag = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        textXOffset = 15
        wx.StaticText(panel, label='Dec', pos=(XOri + textXOffset + 2*XOffset, YOri))
        self.lblAvgDec = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Inc', pos=(XOri + textXOffset + 3*XOffset, YOri))
        self.lblAvgInc = wx.TextCtrl(panel, pos=(XOri + 3*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='CSD', pos=(XOri + textXOffset + 4*XOffset, YOri))
        self.lblCSD = wx.TextCtrl(panel, pos=(XOri + 4*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))

        # Third Line        
        YOri += YOffset + txtBoxHeight + 10
        txtBoxLength = 100
        XOffset = txtBoxLength + 45  
        textXOffset = 5
        wx.StaticText(panel, label='Signal/Drift', pos=(XOri + textXOffset, YOri))
        self.lblDSigDrift = wx.TextCtrl(panel, pos=(XOri, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Signal/Holder', pos=(XOri + textXOffset + XOffset, YOri))
        self.lblDSigHolder = wx.TextCtrl(panel, pos=(XOri + XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
        wx.StaticText(panel, label='Signal/Induced', pos=(XOri + textXOffset + 2*XOffset, YOri))
        self.lblDSigInduced = wx.TextCtrl(panel, pos=(XOri + 2*XOffset, YOri + YOffset), size=(txtBoxLength, txtBoxHeight))
                
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''          
    '''
    '''
    def updatePolarPlot(self, frame):                
        return self.line,

    '''
        This procedure hides the statistics frame and resizes
        the measurement window
    '''
    def HideStats(self):        
        # Add in a three second pause here
        time.sleep(3)
        
        self.parent.frmStats.Hide()
        return

    '''
        This procedure clears data from the stat data boxes
    '''
    def clearStats(self):
        self.parent.frmStats.cmdPrint.Enable(True)
        self.lblavgx.SetValue('')
        self.lblavgy.SetValue('')
        self.lblavgz.SetValue('')
        self.lblDSigDrift.SetValue('')
        self.lblDSigHolder.SetValue('')
        self.lblDSigInduced.SetValue('')
        self.lblavgmag.SetValue('')
        self.lblCSD.SetValue('')
        return

    '''
        This function clears all the currently displayed data.
    '''
    def clearData(self):        
        self.cmdPrint.Enable(True)
        self.lblMeasXZero0.SetValue('')
        self.lblMeasYZero0.SetValue('')
        self.lblMeasZZero0.SetValue('')
        self.lblMeasXZero1.SetValue('')
        self.lblMeasYZero1.SetValue('')
        self.lblMeasZZero1.SetValue('')
        for i in range(0, 4):
            self.lblMeasX[i].SetValue('')
            self.lblMeasY[i].SetValue('')
            self.lblMeasZ[i].SetValue('')
            self.lblCalcInc[i].SetValue('')
            self.lblCalcDec[i].SetValue('')
        
        return

    '''
        This procedure sets the name of the current sample
        that is being processed by the magnetometer.
    '''
    def SetSample(self, smp):
        self.lblSampName.SetValue(smp)
        self.lblCupNumber.SetValue(str(self.parent.modConfig.processData.SampleHandlerCurrentHole))
        self.parent.frmStats.lblSampName.SetValue(smp)
        self.lblSampleHeight.SetValue('')
        self.lblMeascount.SetValue('')
        self.lblRescan.SetLabel(' ')
        self.lblXSQUID.SetLabel(' ')
        self.lblYSQUID.SetLabel(' ')
        self.lblZSQUID.SetLabel(' ')
        return

    '''
    '''
    def placeTopRight(self):
        parent_size = self.parent.GetSize()
        panel_size = self.GetSize()
        
        XPosition = parent_size.GetWidth() - panel_size.GetWidth() - 40
        if (XPosition < 0):
            XPosition = 0
        YPosition = 100
        self.SetPosition((XPosition, YPosition))
        return

    '''
    '''
    def ZOrder(self):
        return 

    '''
    '''
    def SetField(self, messageList):
        print(messageList)
        
        self.clearData()
        self.HideStats()
        self.clearStats()                
        return

    '''
    '''
    def getInt(self, valueStr):
        try:
            valueInt = int(valueStr)
        except:
            valueInt = 0
            
        return valueInt

    '''
    '''
    def getFloat(self, valueStr):
        try:
            valueFloat = float(valueStr)
        except:
            valueFloat = 0
            
        return valueFloat

    '''
    '''
    def getBool(self, valueStr):
        if 'True' in valueStr:
            valueBool = True
        else:
            valueBool = False
            
        return valueBool

    '''
        Now select the proper format for printing out this range
        information based on the TESTIT variable
    '''
    def FormatNumber(self, testit):
        if ((testit >= 1000000) or (testit <= -100000)):
            frmt = str(int(testit))  
        elif ((testit >= 100000) or (testit <= -10000)):
            frmt = '{:.1f}'.format(testit)
        elif ((testit >= 10000) or (testit <= -1000)):
            frmt = '{:.2f}'.format(testit)
        elif ((testit >= 1000) or (testit <= -100)):
            frmt = '{:.3f}'.format(testit)
        elif ((testit >= 100) or (testit <= -10)):
            frmt = '{:.4f}'.format(testit)
        elif ((testit >= 10) or (testit <= -1)):
            frmt = '{:.5f}'.format(testit)
        else:
            frmt = '{:.5f}'.format(testit)
        
        return frmt 

    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def cmdHide_Click(self, event):
        print('TODO: frmMeasure.cmdHide_Click')
        return

    '''
    '''
    def cmdPrint_Click(self, event):
        print('TODO: frmMeasure.cmdPrint_Click')
        return
    
    '''
    '''
    def buttonHalt_Click(self, event):
        print('TODO: frmMeasure.buttonHalt_Click')
        return
    
    '''
    '''
    def buttonPause_Click(self, event):
        print('TODO: frmMeasure.buttonPause_Click')
        return

    '''
    '''
    def cmdShowPlots_Click(self, event):
        print('TODO: frmMeasure.cmdShowPlots_Click')
        return

    '''
    '''
    def cmdStats_Click(self, event):
        print('TODO: frmMeasure.cmdStats_Click')
        return
        
    '''
    '''
    def onClosed(self, event):
        # Immediately stop the timer
        self.updatePlot.event_source.stop()
        self.canvas.Destroy()
        self.Destroy()
        return
        
    '''
    '''
    def onRGroupChanges(self, event):
        print('TODO: frmMeasure.onRGroupChanges')
        return
    
    '''
    '''
    def cmdHideZij_Click(self, event):
        print('TODO: frmMeasure.cmdHideZij_Click')
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Update GUI Functions
                        
    --------------------------------------------------------------------------------------------'''    
    '''
    '''
    def updateFlowStatus(self):
        print('TODO: frmMeasure.updateFlowStatus')
        return
    
    '''
        This procedure sets some of the information in the
        fields on this form.  It is called by frmMagnetometerControl.
    '''
    def SetFields(self, dataList):
        steps = 0
        demag = ''
        isUp = False
        isBoth = False
        DataFileName = ''
        for eachItem in dataList:
            if ('avgSteps' in eachItem):
                steps = self.getInt(eachItem.replace('avgSteps = ', ''))
            elif ('curDemagLong' in eachItem):
                demag = eachItem.replace('curDemagLong = ', '')
            elif ('doUp' in eachItem):
                isUp = self.getBool(eachItem.replace('doUp = ', ''))
            elif ('doBoth' in eachItem):
                isBoth = self.getBool(eachItem.replace('doBoth = ', ''))
            elif ('filename' in eachItem):
                DataFileName = eachItem.replace('filename = ', '')
    
        self.lblAvgCycles.SetValue(str(steps))
        self.lblDemag.SetValue(demag)
        self.parent.frmStats.lblAvgCycles.SetValue(str(steps))
        self.parent.frmStats.lblDemag.SetValue(demag)
        if isUp: 
            self.lblMeasDir.SetValue("U") 
        else: 
            self.lblMeasDir.SetValue("D")
            
        if isBoth: 
            self.lblDirs.SetValue("U/D")
        else: 
            self.lblDirs.SetValue(self.lblMeasDir.GetValue())
            
        self.parent.frmStats.lblDirs.SetValue(self.lblDirs.GetValue())
        self.lblDataFileName.SetValue(DataFileName)
        self.parent.frmStats.lblDataFileName.SetValue(DataFileName)
        self.lblCupNumber.SetValue(str(self.parent.modConfig.processData.SampleHandlerCurrentHole))
        return
    
    '''
        This routine displays the data fields in dat in the
        appropriate fields in the form. 'num' designates which
        fields to display into
    '''
    def showData(self, dataList):
        datX = 0.0
        datY = 0.0
        datZ = 0.0
        num = 0
        Meascount = 0
        for eachItem in dataList:
            if ('datX' in eachItem):
                datX = self.getFloat(eachItem.replace('datX = ', ''))
            elif ('datY' in eachItem):
                datY = self.getFloat(eachItem.replace('datY = ', ''))
            elif ('datZ' in eachItem):
                datZ = self.getFloat(eachItem.replace('datZ = ', ''))
            elif ('num' in eachItem):
                num = self.getInt(eachItem.replace('num = ', ''))
            elif ('Meascount' in eachItem):
                Meascount = self.getInt(eachItem.replace('Meascount = ', ''))
                
        # Show the height of each sample, measured in automatic sample changer mode (June 2007 L Carporzen)
        if (self.lblSampName.GetValue == "Holder"):
            self.lblSampleHeight.SetValue('{:.1f}'.format(self.parent.SampleHolder.SampleHeight / self.parent.modConfig.UpDownMotor1cm))
        else:
            self.lblSampleHeight.SetValue('{:.1f}'.format(self.parent.modConfig.SampleHeight / self.parent.modConfig.UpDownMotor1cm))
        
        self.lblMeascount = Meascount
        if (num == 0):
            # Show as First Zero data points
            self.lblMeasXZero[0].SetValue(self.FormatNumber(datX))
            self.lblMeasYZero[0].SetValue(self.FormatNumber(datY))
            self.lblMeasZZero[0].SetValue(self.FormatNumber(datZ))
        if ((num >= 1) and (num <= 4)):
            # Show as Data points
            self.lblMeasX[num - 1].SetValue(self.FormatNumber(datX))
            self.lblMeasY[num - 1].SetValue(self.FormatNumber(datY))
            self.lblMeasZ[num - 1].SetValue(self.FormatNumber(datZ))
        if (num == 5):
            # Show as Last Zero data points
            self.lblMeasXZero[1].SetValue(self.FormatNumber(datX))
            self.lblMeasYZero[1].SetValue(self.FormatNumber(datY))
            self.lblMeasZZero[1].SetValue(self.FormatNumber(datZ))
            
        return

    '''
        This function displays angular data in appropriate boxes
    '''
    def ShowAngDat(self, dataList): 
        dec = 0.0
        inc = 0.0
        num = 0
        for eachItem in dataList:
            if ('dec' in eachItem):
                dec = self.getFloat(eachItem.replace('dec = ', ''))
            elif ('inc' in eachItem):
                inc = self.getFloat(eachItem.replace('inc = ', ''))
            elif ('num' in eachItem):
                num = self.getInt(eachItem.replace('num = ', ''))

        self.lblCalcDec[num - 1].SetValue('{:.1f}'.format(dec))
        self.lblCalcInc[num - 1].SetValue('{:.1f}'.format(inc))
        return
    
    '''
        ' This procedure displays statistical information gathered
        ' from a measurement cycle with the magnetometer.
    '''
    def ShowStats(self, dataList): 
        X = 0.0
        Y = 0.0
        Z = 0.0
        dec = 0.0
        inc = 0.0
        SigDrift = 0.0
        SigHold = 0.0
        SigInd = 0.0
        CSD = 0.0
        for eachItem in dataList:
            if ('X' in eachItem):
                X = self.getFloat(eachItem.replace('X = ', ''))
            elif ('Y' in eachItem):
                Y = self.getFloat(eachItem.replace('Y = ', ''))
            elif ('Z' in eachItem):
                Z = self.getFloat(eachItem.replace('Z = ', ''))
            elif ('dec' in eachItem):
                dec = self.getFloat(eachItem.replace('dec = ', ''))
            elif ('inc' in eachItem):
                inc = self.getFloat(eachItem.replace('inc = ', ''))
            elif ('SigDrift' in eachItem):
                SigDrift = self.getFloat(eachItem.replace('SigDrift = ', ''))
            elif ('SigHold' in eachItem):
                SigHold = self.getFloat(eachItem.replace('SigHold = ', ''))
            elif ('SigInd' in eachItem):
                SigInd = self.getFloat(eachItem.replace('SigInd = ', ''))
            elif ('CSD' in eachItem):
                CSD = self.getFloat(eachItem.replace('CSD = ', ''))
        
        self.lblavgx.SetValue(self.FormatNumber(X))
        self.lblavgy.SetValue(self.FormatNumber(Y))
        self.lblavgz.SetValue(self.FormatNumber(Z))
        self.lblavgmag.SetValue('{:.4f}'.format(self.parent.modConfig.RangeFact * math.sqrt(X ** 2 + Y ** 2 + Z ** 2)))
        self.lblAvgDec.SetValue('{:.1f}'.format(dec))
        self.lblAvgInc.SetValue('{:.1f}'.format(inc))
        self.lblDSigDrift.SetValue(self.FormatNumber(SigDrift))
        self.lblDSigHolder.SetValue('{:.4f}'.format(SigHold))
        self.lblDSigInduced.SetValue(self.FormatNumber(SigInd))
        self.lblCSD.SetValue('{:.2f}'.format(CSD))
        return
    
    '''
    '''
    def updateStats(self, dataList):
        MaxX = 0.0
        MinX = 0.0
        MaxY = 0.0
        MinY = 0.0
        MaxZ = 0.0
        MinZ = 0.0
        Vol = 0
        momentvol = 0.0
        for eachItem in dataList:
            if ('MaxX' in eachItem):
                MaxX = self.getFloat(eachItem.replace('MaxX = ', ''))
            elif ('MinX' in eachItem):
                MinX = self.getFloat(eachItem.replace('MinX = ', ''))            
            elif ('MaxY' in eachItem):
                MaxY = self.getFloat(eachItem.replace('MaxY = ', ''))
            elif ('MinY' in eachItem):
                MinY = self.getFloat(eachItem.replace('MinY = ', ''))
            elif ('MaxZ' in eachItem):
                MaxZ = self.getFloat(eachItem.replace('MaxZ = ', ''))
            elif ('MinZ' in eachItem):
                MinZ = self.getFloat(eachItem.replace('MinZ = ', ''))
            elif ('Vol' in eachItem):
                Vol = self.getInt(eachItem.replace('Vol = ', ''))
            elif ('momentvol' in eachItem):
                momentvol = self.getFloat(eachItem.replace('momentvol = ', ''))
                
        self.lblDeltaX.SetValue('{:.4}'.format(self.parent.modConfig.RangeFact * (MaxX - MinX)))
        self.lblRatioX.SetValue('{:.2f}'.format(self.parent.modConfig.RangeFact * (MaxX - MinX) / (Vol * momentvol)))
        self.lblDeltaY.SetValue('{:.4}'.format(self.parent.modConfig.RangeFact * (MaxY - MinY)))
        self.lblRatioY.SetValue('{:.2f}'.format(self.parent.modConfig.RangeFact * (MaxY - MinY) / (Vol * momentvol)))
        self.lblDeltaZ.SetValue('{:.4}'.format(self.parent.modConfig.RangeFact * (MaxZ - MinZ)))
        self.lblRatioZ.SetValue('{:.2f}'.format(self.parent.modConfig.RangeFact * (MaxZ - MinZ) / (Vol * momentvol)))
                                
        self.lblOrange.Hide()
        self.lblRed.Hide()
        self.lblWarning.Hide()
        if ((self.parent.modConfig.RangeFact * (MaxX - MinX) / (Vol * momentvol)) > 0.1 / self.parent.modConfig.JumpThreshold):
            self.lblDeltaX.SetBackgroundColour('orange')
            self.lblRatioX.SetBackgroundColour('orange')
            self.lblOrange.Show()
            if ((self.parent.modConfig.RangeFact * (MaxX - MinX) / (Vol * momentvol)) > 0.5 / self.parent.modConfig.JumpThreshold):
                self.lblDeltaX.SetBackgroundColour('red')
                self.lblRatioX.SetBackgroundColour('red')
                self.lblRed.Show()
                self.lblWarning.Show()
        else:
            self.lblDeltaX.SetBackgroundColour(wx.NullColour)
            self.lblRatioX.SetBackgroundColour(wx.NullColour)
        
        if ((self.parent.modConfig.RangeFact * (MaxY - MinY) / (Vol * momentvol)) > 0.1 / self.parent.modConfig.JumpThreshold):
            self.lblDeltaY.SetBackgroundColour('orange')
            self.lblRatioY.SetBackgroundColour('orange')
            self.lblOrange.Show()
            if ((self.parent.modConfig.RangeFact * (MaxY - MinY) / (Vol * momentvol)) > 0.5 / self.parent.modConfig.JumpThreshold):
                self.lblDeltaY.SetBackgroundColour('red')
                self.lblRatioY.SetBackgroundColour('red')
                self.lblRed.Show()
                self.lblWarning.Show()
        else:        
            self.lblDeltaY.SetBackgroundColour(wx.NullColour)
            self.lblRatioY.SetBackgroundColour(wx.NullColour)
        
        if ((self.parent.modConfig.RangeFact * (MaxZ - MinZ) / (Vol * momentvol)) > 0.1 / self.parent.modConfig.JumpThreshold):
            self.lblDeltaZ.SetBackgroundColour('orange')
            self.lblRatioZ.SetBackgroundColour('orange')
            self.lblOrange.Show()
            if ((self.parent.modConfig.RangeFact * (MaxZ - MinZ) / (Vol * momentvol)) > 0.5 / self.parent.modConfig.JumpThreshold):
                self.lblDeltaZ.SetBackgroundColour('red')
                self.lblRatioZ.SetBackgroundColour('red')
                self.lblRed.Show()
                self.lblWarning.Show()
        else:
            self.lblDeltaZ.SetBackgroundColour(wx.NullColour)
            self.lblRatioZ.SetBackgroundColour(wx.NullColour)

        return

    '''
        (August 2007 L Carporzen) Equal area plot near the measurement window
    '''
    def InitEqualArea(self):
        self.axes.cla()
        self.axes.set_xlim(0, 1)
        self.axes.set_ylim(0, 1)
        self.axes.set_axis_off()
        
        # external circle
        center_x, center_y = 0.5, 0.5
        radius = 0.5
        circle = Circle((center_x, center_y), radius, color='black', fill=False, linewidth=1)
        self.axes.add_patch(circle)             # external circle
        self.axes.plot([0.5, 0.5], [0, 1], color='black', linewidth=1)      # vertical axis
        self.axes.plot([0, 1], [0.5, 0.5], color='black', linewidth=1)      # Horizontal axis
        for i in range(0, 9):
            self.axes.plot([0.5 + math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2, 0.5 + math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2], [0.49, 0.52], color='black', linewidth=1)
            self.axes.plot([0.5 - math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2, 0.5 - math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2], [0.49, 0.52], color='black', linewidth=1)
            self.axes.plot([0.49, 0.52], [0.5 + math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2, 0.5 + math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2], color='black', linewidth=1)
            self.axes.plot([0.49, 0.52], [0.5 - math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2, 0.5 - math.sqrt(1 - math.sin(10 * i * math.pi / 180)) / 2], color='black', linewidth=1)            
        
        self.figure.text(0, 0.9, 'Equal Area\nStereoplot')
        self.figure.text(0.01, 0.01, 'Bedding\nCoordinates')
        self.figure.text(0.80, 0.95, 'o Up', color='red')
        self.figure.text(0.80, 0.90, 'o Down', color='Blue')
        
        self.figure.text(0.515, 0.95, 'N')
        self.figure.text(0.515, 0.01, 'S')
        self.figure.text(0.105, 0.5, 'W')
        self.figure.text(0.85, 0.5, 'E')
        
        return
   
    '''
        (August 2007 L Carporzen) Plot of the current 4 measurements (holder not substracted)
    '''
    def PlotEqualArea(self, dataList):
        dec = 0.0
        inc = 0.0
        for eachItem in dataList:
            if ('dec' in eachItem):
                dec = self.getFloat(eachItem.replace('dec = ', ''))
            elif ('inc' in eachItem):
                inc = self.getFloat(eachItem.replace('inc = ', ''))
        
        L0 = 1 / math.sqrt(math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) + math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180))
        if (inc >= 0):      # Down direction
            L = L0 * math.sqrt(1 - math.sin(inc * math.pi / 180))
            X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01
            Y1 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01)
            X2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01
            Y2 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01)
            rect = patches.Rectangle((X1, Y1), width=(X2-X1), height=(Y2-Y1), 
                                 edgecolor='blue', facecolor='lightblue', 
                                 linewidth=1)
             
        else:   # Up direction
            L = L0 * math.sqrt(1 + math.sin(inc * math.pi / 180))
            X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01
            Y1 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01)
            X2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01
            Y2 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01)
            rect = patches.Rectangle((X1, Y1), width=(X2-X1), height=(Y2-Y1), 
                                 edgecolor='red', facecolor='#FFCCCC', 
                                 linewidth=1)
            
        self.axes.add_patch(rect)
                
        return
    
    '''
        (August 2007 L Carporzen) Plot of the averaged measurement (holder substracted)
    '''
    def AveragePlotEqualArea(self, dataList):
        dec = 0.0
        inc = 0.0
        CSD = 0.0
        for eachItem in dataList:
            if ('dec' in eachItem):
                dec = self.getFloat(eachItem.replace('dec = ', ''))
            elif ('inc' in eachItem):
                inc = self.getFloat(eachItem.replace('inc = ', ''))
            elif ('CSD' in eachItem):
                CSD = self.getFloat(eachItem.replace('CSD = ', ''))
        
        if (CSD > 180): 
            CSD = 0
        L0 = 1 / math.sqrt(math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) + math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180))        
        if (inc >= 0):      # Down direction
            L = L0 * math.sqrt(1 - math.sin(inc * math.pi / 180))
            # Plot of the average measurement as a black square
            X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01
            Y1 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01)
            X2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01
            Y2 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01)
            rect = patches.Rectangle((X1, Y1), width=(X2-X1), height=(Y2-Y1), 
                                 edgecolor='blue', facecolor='lightblue', 
                                 linewidth=1)
            self.axes.add_patch(rect)
            
            if (CSD > 5):       # No calcul for small CSD
                if ((inc + CSD) >= 90):
                    # The center of the equal area is include in the a95 which will be draw as a circle with the CSD as radius
                    ax = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    ay = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + math.sqrt(1 - math.sin((90 - CSD) * math.pi / 180)) / 2
                    bx = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + math.sqrt(1 - math.sin((90 - CSD) * math.pi / 180)) / 2
                    by = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
                else:
                    # Calcul of the coordinates of the axis of the ellipsoid
                    ax = (math.sin((dec + math.asin(math.sin((CSD) * math.pi / 180) / math.cos(inc * math.pi / 180)) * 180 / math.pi) * math.pi / 180) * math.sqrt(1 - math.sin((math.asin(1 - (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180))) * (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180)))))) * 180 / math.pi) * math.pi / 180))) / 2 + 0.5
                    ay = abs(-(math.cos((dec + math.asin(math.sin((CSD) * math.pi / 180) / math.cos(inc * math.pi / 180)) * 180 / math.pi) * math.pi / 180) * math.sqrt(1 - math.sin((math.asin(1 - (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180))) * (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180)))))) * 180 / math.pi) * math.pi / 180))) / 2 + 0.5)
                    bx = (math.sin(dec * math.pi / 180) * math.sqrt(1 - math.sin((inc + CSD) * math.pi / 180))) / 2 + 0.5
                    by = abs(-(math.cos(dec * math.pi / 180) * math.sqrt(1 - math.sin((inc + CSD) * math.pi / 180))) / 2 + 0.5)
                    if (ay > 1): 
                        ay = 1 - (ay - 1)
                    if (by > 1): 
                        by = 1 - (by - 1)
                        
                # Plot of the ellipsoid/circle by small segments (5 degrees)
                for i in range(0, 90):
                    Y1 = 1 -((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by))) * math.sin(i * math.pi / 180))
                    X1 = math.sqrt((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay))) ** 2 * (1 - math.sin(i * math.pi / 180) * math.sin(i * math.pi / 180)))
                    Y2 = 1 - ((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by))) * math.sin((i + 1) * math.pi / 180))
                    X2 = math.sqrt((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay))) ** 2 * (1 - math.sin((i + 1) * math.pi / 180) * math.sin((i + 1) * math.pi / 180)))
                    
                    # Test to don't plot the parts of the ellipsoid/circle which are outside of the plane inc = 0
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2):
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.cos((-dec) * math.pi / 180) + Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.sin((-dec) * math.pi / 180) + Y2 * math.cos((-dec) * math.pi / 180)
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])
                        
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2):
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.cos((-dec) * math.pi / 180) - Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.sin((-dec) * math.pi / 180) - Y2 * math.cos((-dec) * math.pi / 180)
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])
                        
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2):
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.cos((-dec) * math.pi / 180) + Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.sin((-dec) * math.pi / 180) + Y2 * math.cos((-dec) * math.pi / 180)
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])
                        
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2):
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.cos((-dec) * math.pi / 180) - Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.sin((-dec) * math.pi / 180) - Y2 * math.cos((-dec) * math.pi / 180)                        
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])

        else:       # Up direction
            L = L0 * math.sqrt(1 + math.sin(inc * math.pi / 180))
            # Plot of the average measurement as a white square
            X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01
            Y1 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - 0.01)
            X2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01
            Y2 = 1 - (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + 0.01)
            rect = patches.Rectangle((X1, Y1), width=(X2-X1), height=(Y2-Y1), 
                                 edgecolor='red', facecolor='#FFCCCC', 
                                 linewidth=1)
            self.axes.add_patch(rect)
            
            if (CSD > 5):       # No calcul for small CSD
                if ((abs(inc) + CSD) >= 90):
                    # The center of the equal area is include in the a95 which will be draw as a circle with the CSD as radius
                    ax = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    ay = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + math.sqrt(1 - math.sin((90 - CSD) * math.pi / 180)) / 2
                    bx = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + math.sqrt(1 - math.sin((90 - CSD) * math.pi / 180)) / 2
                    by = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
                else:
                    # Calcul of the coordinates of the axis of the ellipsoid
                    ax = (math.sin((dec + math.asin(math.sin((CSD) * math.pi / 180) / math.cos(abs(inc) * math.pi / 180)) * 180 / math.pi) * math.pi / 180) * math.sqrt(1 - math.sin((math.asin(1 - (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180))) * (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180)))))) * 180 / math.pi) * math.pi / 180))) / 2 + 0.5
                    ay = abs(-(math.cos((dec + math.asin(math.sin((CSD) * math.pi / 180) / math.cos(abs(inc) * math.pi / 180)) * 180 / math.pi) * math.pi / 180) * math.sqrt(1 - math.sin((math.asin(1 - (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180))) * (2 * ((-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5) - 0.5) / (-(math.cos(dec * math.pi / 180)))))) * 180 / math.pi) * math.pi / 180))) / 2 + 0.5)
                    bx = (math.sin(dec * math.pi / 180) * math.sqrt(1 - math.sin((abs(inc) + CSD) * math.pi / 180))) / 2 + 0.5
                    by = abs(-(math.cos(dec * math.pi / 180) * math.sqrt(1 - math.sin((abs(inc) + CSD) * math.pi / 180))) / 2 + 0.5)
                    if (ay > 1): 
                        ay = 1 - (ay - 1)
                    if (by > 1): 
                        by = 1 - (by - 1)
                
            # Plot of the ellipsoid/circle by small segments (5 degrees)
            for i in range(0, 30):
                # The up ellipsoid/circle is a dash line
                if (( i % 2) > 0):
                    Y1 = 1 - ((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by))) * math.sin(3 * i * math.pi / 180))
                    X1 = math.sqrt((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay))) ** 2 * (1 - math.sin(3 * i * math.pi / 180) * math.sin(3 * i * math.pi / 180)))
                    Y2 = 1 - ((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - bx) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - by))) * math.sin(3 * (i + 1) * math.pi / 180))
                    X2 = math.sqrt((math.sqrt(((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) * ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ax) + (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay) * (-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - ay))) ** 2 * (1 - math.sin(3 * (i + 1) * math.pi / 180) * math.sin(3 * (i + 1) * math.pi / 180)))
                    # Test to don't plot the parts of the ellipsoid/circle which are outside of the plane inc = 0
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ^ 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2):
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.cos((-dec) * math.pi / 180) + Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.sin((-dec) * math.pi / 180) + Y2 * math.cos((-dec) * math.pi / 180)
                        self.axes.plot([1- X_1, 1 - X_2], [Y_1, Y_2])
                        
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2): 
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.cos((-dec) * math.pi / 180) - Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.sin((-dec) * math.pi / 180) - Y2 * math.cos((-dec) * math.pi / 180)
                        self.axes.plot([1 - X_1, 1- X_2], [Y_1, Y_2])
                          
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2): 
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) + Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.cos((-dec) * math.pi / 180) + Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) + Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.sin((-dec) * math.pi / 180) + Y2 * math.cos((-dec) * math.pi / 180) 
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])
                        
                    if (abs(-(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180) - 0.5)) ** 2 < abs(0.5 ** 2 - ((math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180) - 0.5) ** 2): 
                        X_1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X1 * math.cos((-dec) * math.pi / 180) - Y1 * math.sin((-dec) * math.pi / 180)
                        X_2 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5 - X2 * math.cos((-dec) * math.pi / 180) - Y2 * math.sin((-dec) * math.pi / 180)
                        Y_1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X1 * math.sin((-dec) * math.pi / 180) - Y1 * math.cos((-dec) * math.pi / 180)
                        Y_2 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5 + X2 * math.sin((-dec) * math.pi / 180) - Y2 * math.cos((-dec) * math.pi / 180) 
                        self.axes.plot([1 - X_1, 1 - X_2], [Y_1, Y_2])
                
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def initForm(self, functionID):
        if (functionID == 'cmdManHolder_Click'):
            try:
                sampleHeight = float(self.parent.magControl.manualPage.txtSampleHeight.GetValue())
            except:
                sampleHeight = 0.0
            self.parent.SampleHolder.SampleHeight = sampleHeight * self.parent.modConfig.UpDownMotor1cm
            self.parent.updateTaskStatus("Measuring holder...")
            
            self.parent.updateViewMeasurementWindow(True)
            
            self.HideStats()
            self.clearStats()
            self.clearData()
            
            self.SetSample("Holder")
            self.MomentX.Hide()     # (October 2007 L Carporzen) Susceptibility versus demagnetization
            
            self.placeTopRight()
            
            self.InitEqualArea()    # (August 2007 L Carporzen) Equal area plot
            
            self.ZOrder()
            
        return
    
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageList):            
        if ('InitEqualArea' == messageList[0]):
            self.InitEqualArea()
            
        elif ('SetFields' == messageList[0]):
            self.SetFields(messageList[1:])

        elif ('showData' == messageList[0]):
            self.showData(messageList[1:])

        elif ('ShowAngDat' == messageList[0]):
            self.ShowAngDat(messageList[1:])
            
        elif ('ShowStats' == messageList[0]):
            self.ShowStats(messageList[1:])
            
        elif ('PlotEqualArea' == messageList[0]):
            self.PlotEqualArea(messageList[1:])

        elif ('updateStats' == messageList[0]):
            self.updateStats(messageList[1:])

        elif ('AveragePlotEqualArea' == messageList[0]):
            self.AveragePlotEqualArea(messageList[1:])
            
        return 
        
    '''
        Handle cleanup if neccessary
    '''
    def runEndTask(self):
        return


#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmMeasure(parent=None)
        frame.Show(True)
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        
                