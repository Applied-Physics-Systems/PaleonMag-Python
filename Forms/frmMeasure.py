'''
Created on Sep 24, 2025

@author: hd.nguyen
'''
import os
import wx
import time
import math

import numpy as np
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

import matplotlib.patches as patches

from Modules.modProg import modProg
from ClassModules.MeasurementBlock import MeasurementBlock
from Process.DataExchange import DataExchange

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
        
        self.Holder = MeasurementBlock()
        self.BOX1_LENGTH = 0
        self.BOX2_LENGTH = 0
        self.BOX3_LENGTH = 0
        self.BOX1_HEIGHT = 0
        self.InitUI()        
                
    '''
    '''
    def InitUI(self):
        self.panel = wx.Panel(self)
        
        XOri = 10
        YOri = 10
        VSizer1, self.BOX1_LENGTH, self.BOX1_HEIGHT = self.GUI_MeasureInfo(self.panel, XOri, YOri)        
        
        XOri += self.BOX1_LENGTH + 10
        VSizer2, self.BOX2_LENGTH, _ = self.GUI_PlotBox(self.panel, XOri, YOri)
        
        XOri += self.BOX2_LENGTH + 10
        VSizer3, self.BOX3_LENGTH, _ = self.GUI_CreateControl(self.panel, XOri, YOri)
        
        HSizer = wx.BoxSizer(wx.HORIZONTAL)
        HSizer.Add(VSizer1, 0, wx.ALL, 5)
        HSizer.Add(VSizer2, 0, wx.ALL, 5)
        HSizer.Add(VSizer3, 0, wx.ALL, 5)
        self.panel.SetSizer(HSizer)

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)

        # Add event handler on OnShow
        self.Bind(wx.EVT_SHOW, self.onShow)

        self.GUI_DisplayData()
        self.SetTitle('Measurement Window')
        self.Centre()
        return

    '''
    '''
    def GUI_placeTopRight(self):
        if (self.parent != None):
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
    def GUI_DisplayAll(self):
        panelLength = self.BOX1_LENGTH + self.BOX2_LENGTH + self.BOX3_LENGTH + 30
        panelHeight =  self.BOX1_HEIGHT + 10
        self.SetSize((panelLength, panelHeight))
        
        self.GUI_placeTopRight()
        return

    '''
    '''
    def GUI_DisplayWithPlot(self):
        panelLength = self.BOX1_LENGTH + self.BOX2_LENGTH + 40
        panelHeight =  self.BOX1_HEIGHT - 160

        # Keep the Zijderveld plot if it's already open        
        panel_size = self.GetSize()
        if (panel_size.GetWidth() < panelLength): 
            self.SetSize((panelLength, panelHeight))
            
            self.GUI_placeTopRight()
        return

    '''
    '''
    def GUI_DisplayWithStats(self):
        panelLength = self.BOX1_LENGTH + self.BOX2_LENGTH + 40
        panelHeight =  self.BOX1_HEIGHT + 10
        
        # Keep the Zijderveld plot if it's already open        
        panel_size = self.GetSize()
        if (panel_size.GetWidth() <= panelLength):         
            self.SetSize((panelLength, panelHeight))
            
            self.GUI_placeTopRight()
        return

    '''
    '''
    def GUI_DisplayData(self):
        panelLength = self.BOX1_LENGTH + 30
        panelHeight =  self.BOX1_HEIGHT - 160
        self.SetSize((panelLength, panelHeight))
        
        self.GUI_placeTopRight()
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
        YOri += 10

        # 1. Define the StaticBox Sizer
        sb_sizer = wx.StaticBoxSizer(self.MomentXBox, wx.VERTICAL)
        
        # 2. Create the Matplotlib Figure and Canvas
        # Tip: Set a small initial figsize to allow the sizer to take control        
        self.MomentXFig = Figure(figsize=(1, 1))
        self.MomentX = self.MomentXFig.add_subplot(111, aspect='equal') # 1 row, 1 column, 1st subplot
        self.MomentXFig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Parent the canvas to the static box                        
        self.MomentXCanvas = FigureCanvas(self.MomentXBox, -1, self.MomentXFig)       
        self.MomentX.set_axis_off()
                
        # 3. Add to sizer with expansion flags
        sb_sizer.Add(self.MomentXCanvas, 1, wx.EXPAND | wx.ALL, 5)
        self.MomentXCanvas.Hide()
                
        # Control
        txtBoxLength = 75
        txtBoxHeight = 20
        
        XOffset = txtBoxLength + 10 
        YOffset = 17 
        xTexOffset = int(txtBoxLength/2) - 2
        
        self.ChkAllSteps = wx.CheckBox(panel, label='Display steps above current', pos=(XOri+XOffset, YOri))
                        
        YOri += 90
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
        self.lblOrange = wx.StaticText(panel, label='Red = noise higher than 5 times the moment, I am not redoing it ...', pos=(XOri, YOri  + 6*YOffset))
        self.lblOrange.Hide()

        # Finalize layout
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(sb_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        return VSizer
    
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
                
        self.MomentXBox = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, box1Height))
        # Compute the position of YOri
        _, height = self.figure.get_size_inches()        
        XOri += 10
        YOri += int(height*self.figure.dpi) + 10        
        MomentXSize = self.GUI_MomentX(panel, XOri, YOri)
        
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(self.canvas, 1, wx.EXPAND)
        VSizer.Add(MomentXSize, 1, wx.EXPAND)

        YOri += box1Height + 10
        return VSizer, boxLength, YOri

    '''
    '''
    def GUI_ZijderveldPlot(self, panel, XOri, YOri):
        self.zijFigure = Figure(figsize=(3, 3))
        self.Zijderveld = self.zijFigure.add_subplot(111, aspect='equal') # 1 row, 1 column, 1st subplot
        self.zijCanvas = FigureCanvas(panel, -1, self.zijFigure)       
        self.zijFigure.subplots_adjust(left=0, right=1, top=1, bottom=0)
                
        # Initial data
        self.zij_line, = self.Zijderveld.plot([-1, 1], [-1, 1], color='red', lw=2)
    
        # Create the animation
        self.updateZijPlot = FuncAnimation(self.zijFigure, self.updateZijderveldPlot, frames=200, interval=500, blit=False)
        self.Zijderveld.cla()
    
        self.Zijderveld.set_xlim(0, 1)
        self.Zijderveld.set_ylim(0, 1)
        self.Zijderveld.set_axis_off()

        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(self.zijCanvas, 1, wx.EXPAND)
        
        return VSizer

    '''
    '''
    def GUI_CreateControl(self, panel, XOri, YOri):
        boxLength = 340
        boxHeight = 300                                        
        wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        staticBox1 = self.GUI_ZijderveldPlot(panel, XOri, YOri)
        
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
        self.optCore = wx.RadioButton(panel, 11, label = 'Core Coordinates', pos = (XOri + txtBoxXOffset, YOri + YOffset), style = wx.RB_GROUP) 
        self.optGeographic = wx.RadioButton(panel, 22, label = 'Geographic Coordinates',pos = (XOri + txtBoxXOffset, YOri + 2*YOffset)) 
        self.optBedding = wx.RadioButton(panel, 33, label = 'Bedding Coordinates',pos = (XOri + txtBoxXOffset, YOri + 3*YOffset))
        self.optCore.SetValue(True)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRGroupChanges)
                
        self.ChkM = wx.CheckBox(panel, label='Moment Magnitude', pos=(XOri, YOri + 3*YOffset))
        self.ChkM.SetForegroundColour(wx.RED)
        self.ChkM.SetValue(True) 
        self.ChkX = wx.CheckBox(panel, label='Susceptibility', pos=(XOri, YOri + 4*YOffset))
        self.ChkX.SetForegroundColour(wx.BLUE)
        self.ChkX.SetValue(True) 

        messageStr = 'Geographic and bedding coordinates are read in the\n'
        messageStr += 'sample file, it could be not valid if you changed the\n'
        messageStr += 'orientation parameters since the previous measurements.'       
        self.lblOrientation = wx.StaticText(panel, label=messageStr, pos=(XOri, YOri + 6*YOffset))
        self.lblOrientation.Hide()
        
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
    '''
    def updateZijderveldPlot(self, frame):                
        return self.zij_line,

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
        self.GUI_DisplayData()
        
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

    '''--------------------------------------------------------------------------------------------
                        
                        Update GUI Functions
                        
    --------------------------------------------------------------------------------------------'''   
    def ShowStatsForm(self):
        self.parent.frmStats.Show()
        return

    '''
    '''
    def updateFlowStatus(self):
        print('TODO: frmMeasure.updateFlowStatus')
        return
    
    '''
        This procedure sets some of the information in the
        fields on this form.  It is called by frmMagnetometerControl.
    '''
    def SetFields(self, dataDict):
        avgSteps = dataDict['avgSteps']
        curDemagLong = dataDict['curDemagLong']
        doUp = dataDict['doUp']
        doBoth = dataDict['doBoth']
        filename = dataDict['filename']
    
        self.lblAvgCycles.SetValue(str(avgSteps))
        self.lblDemag.SetValue(curDemagLong)
        self.parent.frmStats.lblAvgCycles.SetValue(str(avgSteps))
        self.parent.frmStats.lblDemag.SetValue(curDemagLong)
        if doUp: 
            self.lblMeasDir.SetValue("U") 
        else: 
            self.lblMeasDir.SetValue("D")
            
        if doBoth: 
            self.lblDirs.SetValue("U/D")
        else: 
            self.lblDirs.SetValue(self.lblMeasDir.GetValue())
            
        self.parent.frmStats.lblDirs.SetValue(self.lblDirs.GetValue())
        self.lblDataFileName.SetValue(filename)
        self.parent.frmStats.lblDataFileName.SetValue(filename)
        self.lblCupNumber.SetValue(str(self.parent.modConfig.processData.SampleHandlerCurrentHole))
        return
    
    '''
        This routine displays the data fields in dat in the
        appropriate fields in the form. 'num' designates which
        fields to display into
    '''
    def showData(self, dataDict):
        datX = dataDict['X']
        datY = dataDict['Y']
        datZ = dataDict['Z']
        num = dataDict['num']
        Meascount = dataDict['Meascount']
                
        # Show the height of each sample, measured in automatic sample changer mode (June 2007 L Carporzen)
        if (self.lblSampName.GetValue == "Holder"):
            self.lblSampleHeight.SetValue('{:.1f}'.format(self.parent.SampleHolder.SampleHeight / self.parent.modConfig.UpDownMotor1cm))
        else:
            self.lblSampleHeight.SetValue('{:.1f}'.format(self.parent.modConfig.SampleHeight / self.parent.modConfig.UpDownMotor1cm))
        
        self.lblMeascount.SetValue(str(Meascount))
        if (num == 0):
            # Show as First Zero data points
            self.lblMeasXZero[0].SetValue(modProg.FormatNumber(datX))
            self.lblMeasYZero[0].SetValue(modProg.FormatNumber(datY))
            self.lblMeasZZero[0].SetValue(modProg.FormatNumber(datZ))
        if ((num >= 1) and (num <= 4)):
            # Show as Data points
            self.lblMeasX[num - 1].SetValue(modProg.FormatNumber(datX))
            self.lblMeasY[num - 1].SetValue(modProg.FormatNumber(datY))
            self.lblMeasZ[num - 1].SetValue(modProg.FormatNumber(datZ))
        if (num == 5):
            # Show as Last Zero data points
            self.lblMeasXZero[1].SetValue(modProg.FormatNumber(datX))
            self.lblMeasYZero[1].SetValue(modProg.FormatNumber(datY))
            self.lblMeasZZero[1].SetValue(modProg.FormatNumber(datZ))
            
        return

    '''
        This function displays angular data in appropriate boxes
    '''
    def ShowAngDat(self, dataDict): 
        dec = dataDict['dec']
        inc = dataDict['inc']
        num = dataDict['num']

        self.lblCalcDec[num - 1].SetValue('{:.1f}'.format(dec))
        self.lblCalcInc[num - 1].SetValue('{:.1f}'.format(inc))
        return
    
    '''
        ' This procedure displays statistical information gathered
        ' from a measurement cycle with the magnetometer.
    '''
    def ShowStats(self, dataDict): 
        self.GUI_DisplayWithStats()
        
        X = dataDict['X']
        Y = dataDict['Y']
        Z = dataDict['Z']
        dec = dataDict['dec']
        inc = dataDict['inc']
        SigDrift = dataDict['SigDrift']
        SigHold = dataDict['SigHold']
        SigInd = dataDict['SigInd']
        CSD = dataDict['CSD']
        
        self.lblavgx.SetValue(modProg.FormatNumber(X))
        self.lblavgy.SetValue(modProg.FormatNumber(Y))
        self.lblavgz.SetValue(modProg.FormatNumber(Z))
        self.lblavgmag.SetValue('{:.4f}'.format(self.parent.modConfig.RangeFact * math.sqrt(X ** 2 + Y ** 2 + Z ** 2)))
        self.lblAvgDec.SetValue('{:.1f}'.format(dec))
        self.lblAvgInc.SetValue('{:.1f}'.format(inc))
        self.lblDSigDrift.SetValue(modProg.FormatNumber(SigDrift))
        self.lblDSigHolder.SetValue('{:.4f}'.format(SigHold))
        self.lblDSigInduced.SetValue(modProg.FormatNumber(SigInd))
        self.lblCSD.SetValue('{:.2f}'.format(CSD))
        return
    
    '''
    '''
    def updateStats(self, dataDict):
        self.GUI_DisplayWithStats()
        
        MaxX = dataDict['MaxX']
        MinX = dataDict['MinX']
        MaxY = dataDict['MaxY']
        MinY = dataDict['MinY']
        MaxZ = dataDict['MaxZ']
        MinZ = dataDict['MinZ']
        Vol = dataDict['Vol']
        momentvol = dataDict['momentvol']
                
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
    def PlotEqualArea(self, dataDict):
        self.GUI_DisplayWithPlot()
        
        dec = dataDict['dec']
        inc = dataDict['inc']
        
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
    def AveragePlotEqualArea(self, dataDict):
        self.GUI_DisplayWithPlot()
        
        dec = dataDict['dec']
        inc = dataDict['inc']
        CSD = dataDict['CSD']
        
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

    '''
        (August 2007 L Carporzen) Plot of the previous directions
        (June 2008 L Carporzen) Link the previous directions
    '''
    def PlotHistory(self, dec, inc, dec2, inc2):
        L0 = 1 / math.sqrt(math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.cos(dec * math.pi / 180) + math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180) * math.cos(inc * math.pi / 180) * math.sin(dec * math.pi / 180))
        L02 = 1 / math.sqrt(math.cos(inc2 * math.pi / 180) * math.cos(dec2 * math.pi / 180) * math.cos(inc2 * math.pi / 180) * math.cos(dec2 * math.pi / 180) + math.cos(inc2 * math.pi / 180) * math.sin(dec2 * math.pi / 180) * math.cos(inc2 * math.pi / 180) * math.sin(dec2 * math.pi / 180))
        if (inc >= 0):      # Down direction
            L = L0 * math.sqrt(1 - math.sin(inc * math.pi / 180))
            L2 = L02 * math.sqrt(1 - math.sin(inc2 * math.pi / 180))            
            center_x = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
            center_y = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
            radius = 0.005
            circle = Circle((center_x, center_y), radius, color='blue', fill=False, linewidth=1)
            self.axes.add_patch(circle)
            if ((not (inc2 == 0)) and (not (L02 == 0)) and (not (inc == inc2))):
                if ((inc / inc2) > 0):
                    X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    Y1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    X2 = (math.sin(dec2 * math.pi / 180) * L2 / L02) / 2 + 0.5
                    Y2 = -(math.cos(dec2 * math.pi / 180) * L2 / L02) / 2 + 0.5
                    self.axes.plot([1 - X1, 1 - X2], [Y1, Y2], color='blue')
            
        else:       # Up direction
            L = L0 * math.sqrt(1 + math.sin(inc * math.pi / 180))
            L2 = L02 * math.sqrt(1 + math.sin(inc2 * math.pi / 180))
            center_x = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
            center_y = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
            radius = 0.005
            circle = Circle((center_x, center_y), radius, color='red', fill=False, linewidth=1)
            self.axes.add_patch(circle)
            if ((not inc2 == 0) and (not L02 == 0) and (not inc == inc2)):
                if ((inc / inc2) > 0): 
                    X1 = (math.sin(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    Y1 = -(math.cos(dec * math.pi / 180) * L / L0) / 2 + 0.5
                    X2 = (math.sin(dec2 * math.pi / 180) * L2 / L02) / 2 + 0.5
                    Y2 = -(math.cos(dec2 * math.pi / 180) * L2 / L02) / 2 + 0.5
                    self.axes.plot([1 - X1, 1 - X2], [Y1, Y2], color='red')
            
        return
    
   

    '''
        (August 2007 L Carporzen) Zijderveld diagram near the measurement window & the equal area plot
    '''
    def ImportZijRoutine(self, dataDict):
        self.GUI_DisplayAll()
        
        FilePath = dataDict['FilePath'] 
        crdec = dataDict['crdec'] 
        crinc = dataDict['crinc']
        momentvol = dataDict['momentvol'] 
        refresh = dataDict['refresh']
        
        for r in range(0, self.parent.frmSampleIndexRegistry.cmbSampCode.GetCount()):
            samplepath = ''
            itemPath = self.parent.frmSampleIndexRegistry.txtDir.GetValue() + "\\"  
            itemPath += self.parent.frmSampleIndexRegistry.cmbSampCode.Items[r]  
            itemPath += "\\" + FilePath
            if Path(itemPath).exists():                
                if (FilePath == ""): 
                    return
                
                samPath = self.parent.frmSampleIndexRegistry.txtDir.GetValue() + "\\"
                samPath += self.parent.frmSampleIndexRegistry.cmbSampCode.Items[r] 
                samPath += "\\" + self.parent.frmSampleIndexRegistry.cmbSampCode.Items[r] + ".sam"
                if (self.lblDataFileName.GetValue() == samPath): 
                    samplepath = itemPath                                                
        
        if not (len(samplepath) > 0):
            return
        else:
            if (FilePath == ""): 
                return
                    
        if not Path(samplepath + ".rmg").exists():
            self.ChkX.Hide()
        else:
            self.ChkX.Show()        # Allow reading the RMG file for susceptibility versus demagnetization

        if (self.txtZijLines.GetValue() == ''): 
            self.txtZijLines.SetValue('0')
        if (modProg.getInt(self.txtZijLines.GetValue()) < 0): 
            self.txtZijLines.SetValue('0')
        ZijLines = modProg.getInt(self.txtZijLines.GetValue())      # Nb of previous steps plot for the comparison
        
        self.ChkM.Show()
        self.MomentX.clear()     # Clean the plot
        
        # Read the sample file
        with open(samplepath, 'r', encoding='utf-8') as filenum: 
            lines = filenum.readlines()            
        num_rows = len(lines)
        
        if (num_rows < ZijLines + 2): 
            ZijLines = num_rows - 2
        if (ZijLines < 1): 
            return

        ZijX = [0]*ZijLines
        ZijY = [0]*ZijLines
        ZijZ = [0]*ZijLines
        MaxZijX = 0.0000000001
        MaxZijY = 0.0000000001
        MinZijX = -0.0000000001
        MinZijY = -0.0000000001
        p = 0
        MaxMoment = 0.0000000001
        MaxDemag = 0
        MaxSusceptibility = 0.00001
        MinSusceptibility = 0
        
        lblDemagStr = self.lblDemag.GetValue()
        if ((abs(modProg.getInt(modProg.Right(lblDemagStr, 4))) == 0) and not (modProg.Left(lblDemagStr, 3) == "ARM")):
            self.MomentXCanvas.Hide()
            self.ChkM.Hide()
            self.ChkX.Hide()
        else:
            self.MomentXCanvas.Show()
        
        if (modProg.Left(lblDemagStr, 3) == "ARM"): 
            self.ChkAllSteps.SetValue(True)
        
        if ((not self.ChkM.GetValue()) and (not self.ChkX.GetValue())):
            self.MomentXCanvas.Hide()

        # (October 2007 L Carporzen) Susceptibility versus demagnetization below the equal area plot
        if self.MomentXCanvas.IsShown() and self.ChkX.IsShown():
            # Read the RMG file
            with open(samplepath + ".rmg", 'r') as filenum:
                RMGlines = filenum.readlines()
            
            numRMGrows = len(RMGlines)
            if (numRMGrows > (3 * ZijLines)):
                SusceLines = 3 * ZijLines
            else:
                SusceLines = numRMGrows
            
            RMGarray = []
            for r in range(0, SusceLines):
                if (RMGlines[numRMGrows - r -1] == ""): 
                    return
                RMGarray.append(RMGlines[numRMGrows - r - 1].split(","))
          
        DemagStep = [0]*ZijLines 
        Susceptibility = [0]*ZijLines
        for r in range(0, ZijLines):
            readMoment = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 31, 8))
            if self.optCore.GetValue():             # Core coordinates
                readcrdec = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 46, 5))
                readcrinc = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 52, 5))
                if (r > 1):                         # (June 2008 L Carporzen) Link the previous directions
                    readcrdec2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 46, 5))
                    readcrinc2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 52, 5))
                else:
                    readcrdec2 = modProg.getFloat(self.parent.frmStats.lblCDec.GetValue())
                    readcrinc2 = modProg.getFloat(self.parent.frmStats.lblCInc.GetValue())
                    
            if self.optGeographic.GetValue():         # Geographic coordinates
                readcrdec = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 7, 5))
                readcrinc = modProg.getFloat(modProg.Mid(lines[num_rows - r -1], 13, 5))
                if (r > 1):                         # (June 2008 L Carporzen) Link the previous directions
                    readcrdec2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 7, 5))
                    readcrinc2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 13, 5))
                else:
                    readcrdec2 = modProg.getFloat(self.parent.frmStats.lblGDec.GetValue())
                    readcrinc2 = modProg.getFloat(self.parent.frmStats.lblGInc.GetValue())
                
            if self.optBedding.GetValue():          # Bedding coordinates
                readcrdec = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 19, 5))
                readcrinc = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 25, 5))
                if (r > 1):                         # (June 2008 L Carporzen) Link the previous directions
                    readcrdec2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 19, 5))
                    readcrinc2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 25, 5))
                else:
                    readcrdec2 = modProg.getFloat(self.parent.frmStats.lblBDec.GetValue())
                    readcrinc2 = modProg.getFloat(self.parent.frmStats.lblBInc.GetValue())

            if refresh:
                self.lblOrientation.Show()
                self.PlotHistory(readcrdec, readcrinc, readcrdec2, readcrinc2) # (June 2008 L Carporzen) Link the previous directions
            else:
                self.lblOrientation.Hide()
                self.optCore.SetValue(True)
                self.optGeographic.SetValue(False)
                self.optBedding.SetValue(False)
                readcrdec = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 46, 5))
                readcrinc = modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 52, 5))
                if (r > 1):                         # (June 2008 L Carporzen) Link the previous directions
                    readcrdec2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 19, 5))
                    readcrinc2 = modProg.getFloat(modProg.Mid(lines[num_rows - r], 25, 5))
                else:
                    readcrdec2 = modProg.getFloat(self.parent.frmStats.lblBDec.GetValue())
                    readcrinc2 = modProg.getFloat(self.parent.frmStats.lblBInc.GetValue())                
                self.PlotHistory(modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 19, 5)), 
                                 modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 25, 5)), 
                                 readcrdec2, readcrinc2)    # (June 2008 L Carporzen) Link the previous directions
                
            ZijX[r] = readMoment * math.cos(readcrinc * math.pi / 180) * math.cos(readcrdec * math.pi / 180)
            ZijY[r] = readMoment * math.cos(readcrinc * math.pi / 180) * math.sin(readcrdec * math.pi / 180)
            ZijZ[r] = readMoment * math.sin(readcrinc * math.pi / 180)
            if (-ZijX[r] > MaxZijX): 
                MaxZijX = -ZijX[r]
            if (ZijY[r] > MaxZijY): 
                MaxZijY = ZijY[r]
            if (ZijZ[r] > MaxZijX): 
                MaxZijX = ZijZ[r]
            if (-ZijX[r] < MinZijX): 
                MinZijX = -ZijX[r]
            if (ZijY[r] < MinZijY): 
                MinZijY = ZijY[r]
            if (ZijZ[r] < MinZijX): 
                MinZijX = ZijZ[r]
                
            if self.MomentXCanvas.IsShown():
                DemagStep[r] = abs(modProg.getFloat(modProg.Mid(lines[num_rows - r - 1], 3, 3)))
                if self.ChkX.IsShown():
                    for Q in range(p, SusceLines):
                        if (modProg.Left(lines[num_rows - r - 1], 2) == RMGarray[Q][0]):  # Are the 2 letters of the step labels are equals (AF or TT)
                            if (RMGarray[Q][0] == "TT"):
                                Thermal = True
                            else:
                                Thermal = False
                            
                            if (RMGarray[Q][0] == "AF"):
                                AF = True
                            else:
                                AF = False
                            
                            if (DemagStep[r] == abs(modProg.getFloat(modProg.Right(RMGarray[Q][1], 3)))):      # Are the 3 last digits of the step numbers are equals
                                DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                                Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                                p = Q + 1
                                break
                            
                            elif (DemagStep[r] == abs(modProg.getFloat(modProg.Right(RMGarray[Q][1], 4)))):     # Are the 4 last digits of the step numbers are equals
                                DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                                Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                                p = Q + 1
                                break
                            
                        elif (modProg.Left(lines[num_rows - r], 3) == RMGarray[Q][0]):          # Are the 3 letters of the step labels are equals
                            if ((RMGarray[Q][0] == "IRM") or (RMGarray[Q][0] == "ARM") or (RMGarray[Q][0] == "AFz")):
                                AF = True
                            else:
                                AF = False
                            
                            if (DemagStep[r] == abs(modProg.getFloat(modProg.Right(RMGarray[Q][1], 3)))):    # Are the 3 last digits of the step numbers are equals
                                DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                                Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                                p = Q + 1
                                break
                            
                            elif (DemagStep[r] == abs(modProg.getFloat(modProg.Right(RMGarray[Q][1], 4)))):   # Are the 4 last digits of the step numbers are equals
                                DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                                Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                                p = Q + 1
                                break
                            elif (modProg.Left(lines[num_rows - r], 3) == "ARM"):       # Is their only a real number only in the RMG (ARM)
                                DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                                Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                                p = Q + 1
                                break
                            
                        elif (modProg.Left(lines[num_rows - r], 5) == RMGarray[Q][0]):  # Are the step labels are equals to AFmax
                            if (RMGarray[Q][0] == "AFmax"):
                                AF = True
                            else:
                                AF = False
                            
                            DemagStep[r] = abs(modProg.getFloat(RMGarray[Q][1]))
                            Susceptibility[r] = modProg.getFloat(RMGarray[Q][8])
                            p = Q + 1
                            break
                    
                
                if (Susceptibility[r] == ""): 
                    Susceptibility[r] = 0
              
                if (self.ChkAllSteps.GetValue() or (DemagStep[r] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))))):         # We don't want to plot the previous steps with higher demag numbers
                    if (readMoment > MaxMoment): 
                        MaxMoment = readMoment
                    if (DemagStep[r] > MaxDemag): 
                        MaxDemag = DemagStep[r]
                    if (self.ChkX.IsShown() and self.ChkX.GetValue()):
                        if (Susceptibility[r] > MaxSusceptibility): 
                            MaxSusceptibility = Susceptibility[r]
                        if (Susceptibility[r] < MinSusceptibility):
                            MinSusceptibility = Susceptibility[r]
                
        if ((-momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180)) > MaxZijX): 
            MaxZijX = -momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180)
        if ((momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180)) > MaxZijY): 
            MaxZijY = momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180)
        if ((momentvol * math.sin(crinc * math.pi / 180)) > MaxZijX): 
            MaxZijX = momentvol * math.sin(crinc * math.pi / 180)
        if ((-momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180)) < MinZijX): 
            MinZijX = -momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180)
        if ((momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180)) < MinZijY): 
            MinZijY = momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180)
        if ((momentvol * math.sin(crinc * math.pi / 180)) < MinZijX): 
            MinZijX = momentvol * math.sin(crinc * math.pi / 180)
        
        '''
            Plot Zij
        '''   
        if self.MomentXCanvas.IsShown():
            if (abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) > MaxDemag): 
                MaxDemag = abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4)))
            if self.ChkM.GetValue() or self.ChkX.GetValue():
                self.MomentX.plot([0, 1], [0, 0], color='black', linewidth=1)      # Horizontal axis
                self.MomentX.plot([1, 1], [0.02, -0.02], color='black', linewidth=1)      # Horizontal axis
                self.MomentXFig.text(0, -0.02, '0')
                
                self.MomentX.plot([0, 0], [0.02, -0.02], color='black', linewidth=1)      # Horizontal axis
                
                self.MomentXFig.text(1 - 0.06, -0.02, str(MaxDemag))
                
                if Thermal:
                    self.MomentXFig.text(0.5, -0.01, chr(176) + "C")
                elif AF:
                    self.MomentXFig.text(0.5, -0.01, chr(176) + "Oe")
                else:
                    self.MomentXFig.text(0.4, -0.01, "Oe " + chr(176) + "C")
                
            if (momentvol > MaxMoment): 
                MaxMoment = momentvol
            if ((MaxMoment == 0.0000000001) or (MaxDemag == 0)):
                self.ChkM.Hide()
            elif (self.ChkM.IsShown() and self.ChkM.GetValue()):
                self.MomentX.plot([0, 0], [1, 0], color='black', linewidth=1)      # vertical axis
                self.MomentX.plot([-0.02, 0.02], [0, 0], color='black', linewidth=1)      # vertical axis
                self.MomentX.plot([-0.02, 0.02], [1, 1], color='black', linewidth=1)      # vertical axis
                
                self.MomentXFig.text(-0.15, 0.5, 'emu', color='red')                
                self.MomentXFig.text(-0.15, 1.07, '{:.2E}'.format(MaxMoment), color='red')
                self.MomentXFig.text(-0.05, 0.05, '0', color='red')
            
            if self.ChkX.IsShown() or self.ChkX.GetValue():
                if ((self.parent.modConfig.COMPortSusceptibility > 0) and 
                    (self.parent.modConfig.EnableSusceptibility) and 
                    (not modProg.getInt(self.parent.frmSusceptibilityMeter.InputText.GetValue()) == -1)):
                    if ((modProg.getInt(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS) > MaxSusceptibility): 
                        MaxSusceptibility = modProg.getInt(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS
                    if ((modProg.getInt(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS) < MinSusceptibility): 
                        MinSusceptibility = modProg.getInt(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS
                
                if ((MaxSusceptibility == 0.00001) and (MinSusceptibility == 0) or (MaxDemag == 0)):
                    if self.ChkM.GetValue(): 
                        self.ChkX.Hide()
                    if (not self.ChkM.IsShown()) or (not self.ChkM.GetValue()):
                        self.MomentXCanvas.Show()
                        if self.ChkM.GetValue(): 
                            self.ChkM.Hide()
                                                    

        if self.MomentXCanvas.IsShown() and self.ChkX.IsShown() and self.ChkX.GetValue():
            SusceScale = abs(MaxSusceptibility - MinSusceptibility)
            SusceOrig = abs(MinSusceptibility / SusceScale)
            if self.ChkM.IsShown() and self.ChkM.GetValue():
                self.MomentX.plot([0, 0], [1, 0], color='black', linewidth=1)      # vertical axis
                self.MomentX.plot([-0.02, 0.02], [0, 0], color='black', linewidth=1)
                self.MomentX.plot([-0.02, 0.02], [1, 1], color='black', linewidth=1)
            else:
                self.MomentX.plot([0, 0], [1, 0], color='blue', linewidth=1)      # vertical axis
                self.MomentX.plot([-0.02, 0.02], [0, 0], color='blue', linewidth=1)
                self.MomentX.plot([-0.02, 0.02], [1, 1], color='blue', linewidth=1)
            
            self.MomentX.plot([0, 1], [SusceOrig, SusceOrig], color='blue', linewidth=1)      # vertical axis            
            self.MomentX.plot([1, 1], [SusceOrig + 0.02, SusceOrig - 0.02], color='blue', linewidth=1)      # Horizontal axis

            self.MomentXFig.text(-0.05, SusceOrig + 0.05, '0', color='blue')

            CurrentX = -0.15
            if ((1 - SusceOrig) > 0.5):
                CurrentY = 1 - SusceOrig - 0.05 - 0.05
            else:
                CurrentY = 1 - SusceOrig + 0.05 - 0.05            
            self.MomentXFig.text(CurrentX, 1 - CurrentY, 'emu/Oe', color='blue')
            
            self.MomentXFig.text(-0.15, 0.99, '{:.2E}'.format(MaxSusceptibility), color='blue')
            
            if not (MinSusceptibility == 0):
                self.MomentXFig.text(-0.15, -0.01, '{:.2E}'.format(MinSusceptibility), color='blue')
        
        if not ((MaxZijX == MinZijX) or (MaxZijY == MinZijY)):
            # We can plot
            ZijScale = abs(MaxZijX - MinZijX)
            MaxZijX = MaxZijX + 0.05 * ZijScale
            MinZijX = MinZijX - 0.05 * ZijScale
            ZijScale = abs(MaxZijY - MinZijY)
            MaxZijY = MaxZijY + 0.05 * ZijScale
            MinZijY = MinZijY - 0.05 * ZijScale
            if (abs(MaxZijX - MinZijX) > abs(MaxZijY - MinZijY)):
                ZijScale = abs(MaxZijX - MinZijX)   # Same scale for both axis
                ZijHoriOrig = abs(MinZijY / ZijScale) + (1 - abs(MaxZijY - MinZijY) / ZijScale) / 2 # Center the plot in the page
                ZijVertOrig = abs(MinZijX / ZijScale)   # The lowest and highest values are on the borders of the plot
            else:
                ZijScale = abs(MaxZijY - MinZijY)   # Same scale for both axis
                ZijHoriOrig = abs(MinZijY / ZijScale) # The lowest and highest values are on the borders of the plot
                ZijVertOrig = abs(MinZijX / ZijScale) + (1 - abs(MaxZijX - MinZijX) / ZijScale) / 2 # Center the plot in the page

            # Axis lines            
            self.Zijderveld.plot([ZijHoriOrig, ZijHoriOrig], [1, 0], color='black', linewidth=1)      # vertical axis            
            self.Zijderveld.plot([0, 1], [1 - ZijVertOrig, 1 - ZijVertOrig], color='black', linewidth=1)      # horizontal axis
            # N/S/E/W labels
            self.zijFigure.text(0, 0.95 - ZijVertOrig, 'W')
            self.zijFigure.text(1 - 0.025, 0.95 - ZijVertOrig, 'E')
            self.zijFigure.text(ZijHoriOrig - 0.055, 0.96, 'N  Up')
            self.zijFigure.text(ZijHoriOrig - 0.055, 0.04, 'S  Down')
            
            circle = Circle((ZijHoriOrig - 0.06, 1 - 0.02), 0.02, color='blue', fill=False, linewidth=1)
            self.Zijderveld.add_patch(circle)             # external circle
            
            circle = Circle((ZijHoriOrig + 0.08, 1 - 0.02), 0.02, color='red', fill=False, linewidth=1)
            self.Zijderveld.add_patch(circle)             # external circle
                        
            if (ZijHoriOrig >= 0.5):
                CurrentX = 0.04
            else:
                CurrentX = 0.7            
            CurrentY = 0
            self.zijFigure.text(CurrentX, 0.95 - CurrentY, 'View: ' + '{:.2E}'.format(ZijScale) + ' emu')
            
            if (ZijHoriOrig >= 0.5):
                CurrentX = 0.04
            else:
                CurrentX = 0.7            
            CurrentY = 1 - 0.04            
            self.zijFigure.text(CurrentX, 1 - CurrentY, 'Last: ' + '{:.2E}'.format(momentvol) + ' emu')
            
            for r in range(0, ZijLines):        # Circles for each step
                lines[num_rows - r -1] = ""
                if self.MomentXCanvas.IsShown():
                    if (self.ChkAllSteps.GetValue() or (DemagStep[r] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))))):
                        if (self.ChkM.IsShown() and self.ChkM.GetValue() and (not (math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) == 0))): 
                            circle = Circle((DemagStep[r] / MaxDemag, math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) / MaxMoment), 0.005, color='red', fill=False, linewidth=1)
                            self.MomentX.add_patch(circle)
                        if (self.ChkX.IsShown() and self.ChkX.GetValue()):
                            if not (Susceptibility[r] == 0): 
                                circle = Circle((DemagStep[r] / MaxDemag, Susceptibility[r] / SusceScale + SusceOrig), 0.005, color='blue', fill=False, linewidth=1)
                                self.MomentX.add_patch(circle)
                                                            
                circle = Circle((ZijY[r] / ZijScale + ZijHoriOrig, 1 + ZijX[r] / ZijScale - ZijVertOrig), 0.005, color='blue', fill=False, linewidth=1)
                self.Zijderveld.add_patch(circle)             
                circle = Circle((ZijY[r] / ZijScale + ZijHoriOrig, 1 - ZijZ[r] / ZijScale - ZijVertOrig), 0.005, color='red', fill=False, linewidth=1)
                self.Zijderveld.add_patch(circle)             # external circle
            
            for r in range(0, ZijLines - 1):    # Link each step by a line
                if self.MomentXCanvas.IsShown():
                    if (self.ChkAllSteps.GetValue() or 
                       (DemagStep[r] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4)))) and 
                       (DemagStep[r + 1] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))))):
                        if (self.ChkM.IsShown() and self.ChkM.GetValue() and not (math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) == 0) or (math.sqrt(ZijX[r + 1] ** 2 + ZijY[r + 1] ** 2 + ZijZ[r + 1] ** 2) == 0)):
                            self.MomentX.plot([DemagStep[r] / MaxDemag,
                                               DemagStep[r + 1] / MaxDemag], 
                                              [math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) / MaxMoment,
                                               math.sqrt(ZijX[r + 1] ** 2 + ZijY[r + 1] ** 2 + ZijZ[r + 1] ** 2) / MaxMoment], 
                                              color='red', linewidth=1)
                        if self.ChkX.IsShown() and self.ChkX.GetValue():
                            if not ((Susceptibility[r] == 0) or (Susceptibility[r + 1] == 0)): 
                                self.MomentX.plot([DemagStep(r) / MaxDemag,
                                                   DemagStep(r + 1) / MaxDemag], 
                                                  [(Susceptibility[r] / SusceScale - SusceOrig),
                                                   (Susceptibility[r + 1] / SusceScale - SusceOrig)], 
                                                  color='blue', linewidth=1)
                
                self.Zijderveld.plot([ZijY[r] / ZijScale + ZijHoriOrig, ZijY[r + 1] / ZijScale + ZijHoriOrig], [1 + ZijX[r] / ZijScale - ZijVertOrig, 1 + ZijX[r + 1] / ZijScale - ZijVertOrig], color='blue', linewidth=1)
                self.Zijderveld.plot([ZijY[r] / ZijScale + ZijHoriOrig, ZijY[r + 1] / ZijScale + ZijHoriOrig], [1 - ZijZ[r] / ZijScale - ZijVertOrig, 1 - ZijZ[r + 1] / ZijScale - ZijVertOrig ], color='red', linewidth=1)
            
            # Design a cross for the last step
            self.Zijderveld.plot([momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig - 0.015,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig + 0.015], [
                                  1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig + 0.015, 
                                  1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig - 0.015], 
                                  color='blue', linewidth=1)
            self.Zijderveld.plot([momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig - 0.015,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig + 0.015], 
                                 [1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig - 0.015,
                                  1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig + 0.015], 
                                 color='blue', linewidth=1)            
            self.Zijderveld.plot([momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig - 0.015,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig + 0.015], 
                                 [1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig + 0.015,
                                  1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig - 0.015], 
                                 color='red', linewidth=1)
            self.Zijderveld.plot([momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig - 0.015,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig + 0.015], 
                                 [1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig - 0.015,
                                  1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig + 0.015], 
                                 color='red', linewidth=1)

            ## Design a big circle around the cross for the last step
            circle = Circle((momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig, 
                             1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig), 
                             0.02, color='blue', fill=False, linewidth=1)
            self.Zijderveld.add_patch(circle)             

            circle = Circle((momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig, 
                             1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig), 
                             0.02, color='red', fill=False, linewidth=1)
            self.Zijderveld.add_patch(circle)             
            
            if self.MomentXCanvas.IsShown():
                if (self.ChkM.IsShown() and self.ChkM.GetValue()):
                    self.MomentX.plot([abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag - 0.015,
                                       abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag + 0.015], 
                                      [momentvol / MaxMoment + 0.015,
                                       momentvol / MaxMoment - 0.015], 
                                      color='red', linewidth=1)

                    self.MomentX.plot([abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag - 0.015,
                                       abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag + 0.015], 
                                      [momentvol / MaxMoment - 0.015,
                                       momentvol / MaxMoment + 0.015], 
                                      color='red', linewidth=1)
                    circle = Circle((abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag, 
                                     momentvol / MaxMoment), 
                                     0.02, color='red', fill=False, linewidth=1)
                    self.MomentX.add_patch(circle)
            
                if (self.ChkX.IsShown() and self.ChkX.GetValue()):
                    self.MomentX.plot([abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag - 0.015,
                                       abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag + 0.015], 
                                      [(modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig) + 0.015,
                                       (modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig) - 0.015], 
                                      color='blue', linewidth=1)

                    self.MomentX.plot([abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag - 0.015,
                                       abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag + 0.015], 
                                      [(modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig) - 0.015,
                                       (modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig) + 0.015], 
                                      color='blue', linewidth=1)

                    circle = Circle((abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag, 
                                     (modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig)), 
                                     0.02, color='blue', fill=False, linewidth=1)
                    self.MomentX.add_patch(circle)
            
            
            if (ZijLines > 0):
                r = 1

            # Link the last step to the previous ones
            self.Zijderveld.plot([ZijY[r] / ZijScale + ZijHoriOrig,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig], 
                                 [1 + ZijX[r] / ZijScale - ZijVertOrig, 
                                  1 + momentvol * math.cos(crinc * math.pi / 180) * math.cos(crdec * math.pi / 180) / ZijScale - ZijVertOrig], 
                                 color='blue', linewidth=1)

            self.Zijderveld.plot([ZijY[r] / ZijScale + ZijHoriOrig,
                                  momentvol * math.cos(crinc * math.pi / 180) * math.sin(crdec * math.pi / 180) / ZijScale + ZijHoriOrig], 
                                 [1 - ZijZ[r] / ZijScale - ZijVertOrig, 
                                  1 - momentvol * math.sin(crinc * math.pi / 180) / ZijScale - ZijVertOrig], 
                                 color='black', linewidth=1)

            if self.MomentXCanvas.IsShown():
                if (self.ChkM.IsShown() and self.ChkM.GetValue() and (self.ChkAllSteps.GetValue() or (DemagStep[r] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))))) and not (math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) == 0)):
                    self.MomentX.plot([DemagStep[r] / MaxDemag,
                                       abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))) / MaxDemag], 
                                       [math.sqrt(ZijX[r] ** 2 + ZijY[r] ** 2 + ZijZ[r] ** 2) / MaxMoment,
                                       momentvol / MaxMoment], 
                                       color='red', linewidth=1)
            
                if (self.ChkX.IsShown() and self.ChkX.GetValue()):
                    if ((self.ChkAllSteps.GetValue() or (DemagStep[r] <= abs(modProg.getFloat(modProg.Right(self.lblDemag.GetValue(), 4))))) and not (Susceptibility[r] == 0)): 
                        self.MomentX.plot([DemagStep[r] / MaxDemag,
                                           1], 
                                          [(Susceptibility[r] / SusceScale + SusceOrig),
                                           (modProg.getFloat(self.parent.frmSusceptibilityMeter.InputText.GetValue()) * self.parent.modConfig.SusceptibilityMomentFactorCGS / SusceScale + SusceOrig)], 
                                          color='blue', linewidth=1)
                        
                                 
        return

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
    def onShow(self, event):
        if event.IsShown():
            self.GUI_DisplayAll()
            
        return
    
    '''
    '''
    def onClosed(self, event):
        # Immediately stop the timer
        self.updatePlot.event_source.stop()
        self.updateZijPlot.event_source.stop()
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
        self.Zijderveld.plot([0, 1], [0.5, 0.5], color='black')
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
            self.MomentXCanvas.Hide()     # (October 2007 L Carporzen) Susceptibility versus demagnetization
            
            self.GUI_placeTopRight()
            
            self.InitEqualArea()    # (August 2007 L Carporzen) Equal area plot
            
            self.ZOrder()
            
        return
    
    '''
        Display infomration for the running background process
    '''
    def updateGUI(self, messageDict):            
        if (messageDict['Function'] == 'InitEqualArea'):
            self.InitEqualArea()
            
        elif (messageDict['Function'] == 'SetFields'):
            self.SetFields(messageDict)

        elif (messageDict['Function'] == 'showData'):
            self.showData(messageDict)

        elif (messageDict['Function'] == 'ShowAngDat'):
            self.ShowAngDat(messageDict)
            
        elif (messageDict['Function'] == 'ShowStats'):
            self.ShowStats(messageDict)
            
        elif (messageDict['Function'] == 'PlotEqualArea'):
            self.PlotEqualArea(messageDict)

        elif (messageDict['Function'] == 'updateStats'):
            self.updateStats(messageDict)

        elif (messageDict['Function'] == 'AveragePlotEqualArea'):
            self.AveragePlotEqualArea(messageDict)

        elif (messageDict['Function'] == 'ImportZijRoutine'):
            messageDict['FilePath'] = self.lblSampName.GetValue()
            self.ImportZijRoutine(messageDict)
            
        elif (messageDict['Function'] == 'ShowStatsForm'):
            self.ShowStatsForm()
            
        elif (messageDict['Function'] == 'loadMeasurementBlock'):
            self.Holder = DataExchange.loadMeasurementBlock(messageDict)
            
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
        
                