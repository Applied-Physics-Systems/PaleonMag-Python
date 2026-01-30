'''
Created on Aug 29, 2025

@author: hd.nguyen
'''
import os
import re
import math

from datetime import datetime
from ClassModules.MeasurementBlock import MeasurementBlock

class Sample():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent        # SampleIndexRegistration
        
        self.Samplename = ''
        self.sampleHole = 0
        self.IndexFile = ''
        self.SampleHeight = 0
        self.Comment = ''
        self.Susceptibility = 0.0
                
        self.alreadyReadSpec = False
        
        self.Holder = MeasurementBlock()
        
        self._Vol = 1
        self._CorePlateStrike = 0.0
        self._CorePlateDip = 0.0
        self._BeddingStrike = 0.0
        self._BeddingDip = 0.0
        self._FoldAxis = 0.0
        self._FoldPlunge = 0.0
        self._FoldRotation = False

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def Vol(self):    
        return self._Vol
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @Vol.getter
    def Vol(self):
        self.ReadSpec()
        return self._Vol

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @Vol.setter
    def Vol(self, value):
        self._Vol = value
        return 
        
    @property
    def CorePlateStrike(self):    
        return self._CorePlateStrike
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @CorePlateStrike.getter
    def CorePlateStrike(self):
        self.ReadSpec()
        return self._CorePlateStrike

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @CorePlateStrike.setter
    def CorePlateStrike(self, value):
        self._CorePlateStrike = value
        return 
        
    @property
    def CorePlateDip(self):    
        return self._CorePlateDip
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @CorePlateDip.getter
    def CorePlateDip(self):
        self.ReadSpec()
        return self._CorePlateDip

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @CorePlateDip.setter
    def CorePlateDip(self, value):
        self._CorePlateDip = value
        return 
        
    @property
    def BeddingStrike(self):    
        return self._BeddingStrike
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @BeddingStrike.getter
    def BeddingStrike(self):
        self.ReadSpec()
        return self._BeddingStrike

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @BeddingStrike.setter
    def BeddingStrike(self, value):
        self._BeddingStrike = value
        return 
        
    @property
    def BeddingDip(self):    
        return self._BeddingDip
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @BeddingDip.getter
    def BeddingDip(self):
        self.ReadSpec()
        return self._BeddingDip

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @BeddingDip.setter
    def BeddingDip(self, value):
        self._BeddingDip = value
        return 
        
    @property
    def FoldAxis(self):    
        return self._FoldAxis
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @FoldAxis.getter
    def FoldAxis(self):
        self.ReadSpec()
        return self._FoldAxis

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @FoldAxis.setter
    def FoldAxis(self, value):
        self._FoldAxis = value
        return 
        
    @property
    def FoldPlunge(self):    
        return self._FoldPlunge
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @FoldPlunge.getter
    def FoldPlunge(self):
        self.ReadSpec()
        return self._FoldPlunge

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @FoldPlunge.setter
    def FoldPlunge(self, value):
        self._FoldPlunge = value
        return 
        
    @property
    def FoldRotation(self):    
        return self._FoldRotation
    
    '''
        used when assigning a value to the property, on the left side of an assignment.
        Syntax: X.sampleHole = 5
    '''
    @FoldRotation.getter
    def FoldRotation(self):
        self.ReadSpec()
        return self._FoldRotation

    '''
        used when retrieving value of a property, on the right side of an assignment.
        Syntax: Debug.Print X.sampleHole
    '''
    @FoldRotation.setter
    def FoldRotation(self, value):
        self._FoldRotation = value
        return 

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        This function reads the file for the current specimen
        and returns the data in a "Specimen" type
        set some default values in case we get an error
    '''
    def ReadSpec(self):        
        self._CorePlateStrike = 0
        self._CorePlateDip = 0
        self._BeddingStrike = 0
        self._BeddingDip = 0
        self._Vol = 1
        self._FoldRotation = False
        self._FoldAxis = 0
        self._FoldPlunge = 0
        
        if self.alreadyReadSpec: 
            return
                
        FilePath = self.SpecFilePath(self.parent)
        if os.path.exists(FilePath):
            self.alreadyReadSpec = True
            with open(FilePath, 'rt') as filenum:                
                self.Comment = filenum.readline()
                lineStr = filenum.readline()
                self.CorePlateStrike = float(lineStr[8:13])
                self.CorePlateDip = float(lineStr[14:19])
                self.BeddingStrike = float(lineStr[20:25])
                self.BeddingDip = float(lineStr[26:31])
                self.Vol = float(lineStr[32:37])
                if (self.Vol == 0):
                    self.Vol = 1
                    
                if (len(lineStr) > 42):
                    self.FoldRotation = True
                    self.FoldAxis = float(lineStr[38:43])   
                    self.FoldPlunge = float(lineStr[44:49])
                else:
                    self.FoldRotation = False
                    self.FoldAxis = 0.0
                    self.FoldPlunge = 0.0
        return
    
    '''
    '''    
    def WriteRockmagHeaders(self):
        FilePath = self.SpecFilePath(self.parent) + ".rmg"
        if os.path.exists(FilePath):
            with open(FilePath, 'wt') as filenum:
                filenum.write(self.Samplename + ",")
                filenum.write(self.Comment + ",")
                filenum.write("Vol: " + str(self.Vol) + ",")
                filenum.write(" ")
                filenum.write(" ,")
                filenum.write("Level,")
                filenum.write("Bias Field (G),")
                filenum.write("Spin Speed (rps),")
                filenum.write("Hold Time (s),")
                filenum.write("Mz (emu),")
                filenum.write("Std. Dev. Z,")
                filenum.write("Mz/Vol,")
                filenum.write("Moment Susceptibility (emu/Oe),")
                filenum.write("Mx (emu), ")
                filenum.write("Std. Dev. X, ")
                filenum.write("My (emu), ")
                filenum.write("Std. Dev. Y, ")
                filenum.write("Remarks, ")   # (November 2007 L Carporzen) Remarks column in RMG
                filenum.write("Core Dec, ")
                filenum.write("Core Inc, ")
                filenum.write("M (emu), ")
                filenum.write("CSD, ")
                filenum.write("Sample Height (cm), ")
                filenum.write("Date/Time")  # (November 2007 L Carporzen) Date and time column in RMG
            
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def SpecFilePath(self, sampleRegistry):
        if (sampleRegistry != None):
            specPath = sampleRegistry.filedir + '\\' + sampleRegistry.SampleCode + '\\' + self.Samplename
        else:  
            specPath
            
        return specPath                

    '''
    '''
    def WriteRockmagInfoLine(self, Description, Level):
        FilePath = self.SpecFilePath(self.parent) + ".rmg"
        self.WriteRockmagHeaders()
        
        with open(FilePath, 'at') as filenum:
            filenum.write(Description + ",")
            filenum.write(Level + ",")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average().Z * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Susceptibility * self.parent.parent.modConfig.SusceptibilityMomentFactorCGS) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average().X * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average().Y * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" Holder ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(str(math.sqrt(abs(self.Holder.Average().X ^ 2 + self.Holder.Average().Y ^ 2 + self.Holder.Average().Z ^ 2)) * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.SampleHeight) + ",")
            filenum.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))            
            
        return

'''
    -----------------------------------------------------------------------------------
'''
class Samples():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.Item = []
        self.IndexFile = ''        
        self.Count = 0

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def GetItem(self, Samplename):
        sample = Sample()
        
        for item in self.Item:
            if (item.Samplename == Samplename):
                sample = item
        
        return sample
    
    '''
        Is the sample Samplname in the collection?
    '''
    def IsValidSample(self, sampleName):
        status = False
        
        for item in self.Item:
            if (sampleName == item.Samplename):
                status = True
        
        return status
        
    '''
    '''
    def Clear(self):
        self.Item = []
        return
    
    '''
    '''
    def Add(self, sampleName, sampleHole=0):
        objNewMember = Sample(self.parent)
        
        objNewMember.Samplename = sampleName.strip()
        objNewMember.sampleHole = sampleHole
        objNewMember.IndexFile = self.IndexFile.strip()
        
        self.Item.append(objNewMember)
        self.Count = len(self.Item)
        return
    
    '''
    '''
    def getItemWithKey(self, keyStr):
        sample = None
        for eachEntry in self.Item:
            if keyStr in eachEntry.Samplename:
                sample = eachEntry
                break
            
        return sample
    
    '''
    '''
    def getItemWithIndex(self, index):
        return self.Item[index]
    
        