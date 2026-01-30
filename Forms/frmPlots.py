'''
Created on Sep 2, 2025

@author: hd.nguyen
'''
import os
import wx
import subprocess

import wx.grid as gridlib

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.animation import FuncAnimation

SIZER_LENGTH = 320
    
class frmPlots(wx.Frame):
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        if (parent != None):
            super(frmPlots, self).__init__(parent, wx.NewIdRef(), style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        else:
            super(frmPlots, self).__init__(parent, wx.NewIdRef())
        self.parent = parent   
        self.index = 0
        
        self.InitUI()
        
    '''
    '''
    def InitUI(self):
        panel = wx.Panel(self)
                        
        XOri = 10
        YOri = 10
        VSizer1 = self.GUI_CreateGrid(panel, XOri, YOri)
        
        XOri += SIZER_LENGTH
        VSizer2 = self.GUI_CreatePlot(panel, XOri, YOri)
        
        XOri += SIZER_LENGTH
        VSizer3 = self.GUI_CreateControl(panel, XOri, YOri)

        HSizer = wx.BoxSizer(wx.HORIZONTAL)
        HSizer.Add(VSizer1, 0, wx.ALL, 5)
        HSizer.Add(VSizer2, 0, wx.ALL, 5)
        HSizer.Add(VSizer3, 0, wx.ALL, 5)
        panel.SetSizer(HSizer)        

        # Add event handler on OnClose
        self.Bind(wx.EVT_CLOSE, self.onClosed)

        self.SetSize((1000, 620))
        self.SetTitle('Plots')
        self.Centre()
    
    '''
    '''
    def GUI_CreateControl(self, panel, XOri, YOri):
        boxLength = SIZER_LENGTH
        boxHeight = 300                                        
        staticBox1 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        
        XOri += 35
        YOri += boxHeight + 10 
        staticBox2 = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        staticText = wx.StaticText(panel, label='Zijderveld (1967) Plot', pos=(XOri, YOri))
        # Make the static text bold
        font = staticText.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        staticText.SetFont(font)        
        
        txtBoxXOffset = 100
        YOffset = 20
        wx.RadioButton(panel, 11, label = 'N - S Orthographic Projection', pos = (XOri + txtBoxXOffset, YOri + YOffset), style = wx.RB_GROUP) 
        wx.RadioButton(panel, 22, label = 'E - W',pos = (XOri + txtBoxXOffset, YOri + 2*YOffset)) 

        txtBoxLength = 50
        txtBoxHeight = 25
        self.previousStepsTBox = wx.TextCtrl(panel, pos=(XOri, YOri + 3*YOffset), size=(txtBoxLength, txtBoxHeight))
        self.previousStepsTBox.SetValue('32')
        txtBoxXOffset = txtBoxLength + 5 
        wx.StaticText(panel, label='Previous Steps', pos=(XOri + txtBoxXOffset, YOri + 3*YOffset + 5))
        
        txtBoxXOffset += 85
        wx.RadioButton(panel, 33, label = 'Core Coordinates', pos = (XOri + txtBoxXOffset, YOri + 3*YOffset), style = wx.RB_GROUP) 
        wx.RadioButton(panel, 44, label = 'Geographic Coordinates',pos = (XOri + txtBoxXOffset, YOri + 4*YOffset)) 
        radioBtn1 = wx.RadioButton(panel, 55, label = 'Bedding Coordinates',pos = (XOri + txtBoxXOffset, YOri + 5*YOffset))
        radioBtn1.SetValue(True)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRGroupChanges)
                
        self.magnitudeChkBox = wx.CheckBox(panel, label='Moment Magnitude', pos=(XOri, YOri + 5*YOffset))
        self.magnitudeChkBox.SetForegroundColour(wx.RED)
        self.magnitudeChkBox.SetValue(True) 
        self.susceptibilityChkBox = wx.CheckBox(panel, label='Susceptibility', pos=(XOri, YOri + 6*YOffset))
        self.susceptibilityChkBox.SetForegroundColour(wx.BLUE)
        self.susceptibilityChkBox.SetValue(True) 
        
        YOri += 5
        txtBoxXOffset = 90
        YOffset = 35
        btnLength = 120
        btnHeight = 30        
        openFileBtn = wx.Button(panel, label='Open SAM File', pos=(XOri + txtBoxXOffset, YOri + 4*YOffset), size=(btnLength, btnHeight))        
        openFileBtn.Bind(wx.EVT_BUTTON, self.onOpenFile)        
        openDirectoryBtn = wx.Button(panel, label='Open SAM Directory', pos=(XOri + txtBoxXOffset, YOri + 5*YOffset), size=(btnLength, btnHeight))        
        openDirectoryBtn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)        
        openSampleFileBtn = wx.Button(panel, label='Open Sample File', pos=(XOri + txtBoxXOffset, YOri + 6*YOffset), size=(btnLength, btnHeight))        
        openSampleFileBtn.Bind(wx.EVT_BUTTON, self.onOpenSampleFile)        
        
        # Create sizer
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(staticBox1, 1, wx.EXPAND)
        VSizer.Add(staticBox2, 1, wx.EXPAND)
        
        return VSizer
    
    '''
    '''
    def GUI_CreatePlot(self, panel, XOri, YOri):
        self.figure = Figure(figsize=(3, 3))
        self.axes = self.figure.add_subplot(111, polar=True) # 1 row, 1 column, 1st subplot
        self.canvas = FigureCanvas(panel, -1, self.figure)       
        self.axes.grid(True)
        self.axes.set_theta_direction(-1)
        self.axes.set_theta_zero_location('N')
        self.axes.set_xticks(np.deg2rad([0, 90, 180, 270]))
        self.axes.set_xticklabels(['N', 'E', 'S', 'W'])
        # Move the xticklabels inside by setting a negative pad
        self.axes.tick_params(axis='x', which='major', pad=-20) # Adjust the value as needed
        self.figure.tight_layout()
        self.axes.set_yticklabels([])
        self.figure.text(0, 0.9, 'Equal Area\nStereoplot')
        self.figure.text(0.01, 0.01, 'Bedding\nCoordinates')
        self.figure.text(0.80, 0.95, 'o Up', color='red')
        self.figure.text(0.80, 0.90, 'o Right', color='Blue')

        # Initial data
        theta_initial = np.linspace(0, 2 * np.pi, 100)
        r_initial = np.sin(theta_initial)
        self.line, = self.axes.plot(theta_initial, r_initial, lw=2) # Store the line object
    
        # Create the animation
        self.updatePlot = FuncAnimation(self.figure, self.updatePolarPlot, frames=200, interval=500, blit=False)

        boxLength = SIZER_LENGTH
        boxHeight = 50                                        
        staticBox = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
                
        # Create sizer
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(self.canvas, 1, wx.EXPAND)
        VSizer.Add(staticBox, 1, wx.EXPAND)
            
        return VSizer
        
    '''
    '''
    def GUI_CreateGrid(self, panel, XOri, YOri):
        comboBoxLength = 100
        comboBoxHeight = 30
        txtBoxXOffset = 50
                
        boxLength = SIZER_LENGTH
        boxHeight = 50                                        
        staticBox = wx.StaticBox(panel, -1, '', pos=(XOri, YOri), size=(boxLength, boxHeight))
        XOri += 10
        YOri += 15
        wx.StaticText(panel, label='Sample', pos=(XOri, YOri + 3))
        self.cmbSamples = wx.ComboBox(panel, value='', pos=(XOri + txtBoxXOffset, YOri), size=(comboBoxLength, comboBoxHeight), choices=[])
        txtBoxXOffset += comboBoxLength + 10 
        self.labelsChkBox = wx.CheckBox(panel, label='Labels', pos=(XOri + txtBoxXOffset, YOri + 5))
        self.labelsChkBox.SetValue(True)
        txtBoxXOffset += 80
        self.labelsChkBox = wx.CheckBox(panel, label='CSD', pos=(XOri + txtBoxXOffset, YOri + 5))
        self.labelsChkBox.SetValue(True)
        
        self.grid = gridlib.Grid(panel, size=(boxLength, 500))
        self.grid.CreateGrid(14, 8)  # 14 rows, 8 columns
        
        # Hide the row labels
        self.grid.HideRowLabels()
                
        VSizer = wx.BoxSizer(wx.VERTICAL)
        VSizer.Add(staticBox, 0, wx.ALL, 5)
        VSizer.Add(self.grid, 0, wx.ALL, 5)
        return VSizer
        
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''          
    '''
    '''
    def updatePolarPlot(self, frame):
        # Generate or load new data for the current frame
        theta_new = np.linspace(0, 2 * np.pi, 100)
        r_new = np.sin(theta_new + frame * 0.1)     # Example: animate a sine wave
        
        self.line.set_ydata(r_new)                  # Update the 'r' data
                
        return self.line,
    
    '''--------------------------------------------------------------------------------------------
                        
                        Event Handler Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def onOpenSampleFile(self, event):
        sampleText = self.cmbSamples.GetValue()
        if (sampleText == ''):
            return
        
        print('TODO: onOpenSampleFile')
        return
    
    '''
    '''
    def onOpenDirectory(self, event):
        sampleText = self.cmbSamples.GetValue()
        if (sampleText == ''):
            return
        
        path_to_folder = r"C:\\Users\\hd.nguyen.APPLIEDPHYSICS\\workspace\\Data\\PaleonMag\\SAM\\Bill2A"  # Use a raw string for paths
        os.startfile(path_to_folder)
                
        print('TODO: onOpenDirectory')
        return
    
    '''
    '''
    def onOpenFile(self, event):
        sampleText = self.cmbSamples.GetValue()
        if (sampleText == ''):
            return
        
        file_path = 'C:\\Temp\\StartRamp_VB.txt'
        subprocess.Popen(['notepad.exe', file_path])
        print('TODO: onOpenFile')
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
        rButtonType = event.EventObject.GetLabel()
        print(rButtonType)
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def ZOrder(self):
        return
    
    '''
    '''
    def RefreshSamples(self):
        
        self.cmbSamples.Clear()
        
        if (self.parent.SampleIndexRegistry.Count == 0):
            return
        
        for i in range(0, self.parent.SampleIndexRegistry.Count):
            if (self.parent.SampleIndexRegistry.Item[i].sampleSet.Count > 0):
                for j in range(0, self.parent.SampleIndexRegistry.Item[i].sampleSet.Count):
                    self.cmbSamples.Append(self.parent.SampleIndexRegistry.Item[i].sampleSet.Item[j].Samplename)
                
        return
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        app = wx.App(False)
        frame = frmPlots(parent=None)
        frame.Show(True)
        
        app.MainLoop()    
        
    except Exception as e:
        print(e)
        
        