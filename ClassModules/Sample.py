'''
Created on Aug 29, 2025

@author: hd.nguyen
'''
import os
import shutil
import math

from datetime import datetime

from ClassModules.MeasurementBlock import MeasurementBlock, MeasurementBlocks
from ClassModules.Cartesian3D import Cartesian3D

from Modules.modProg import modProg

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
        self.UpDownRatio = 0.0
                
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
        self._BackFilePath = ''

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

    @property
    def BackFilePath(self):    
        return self._BackFilePath
    
    @BackFilePath.getter
    def BackFilePath(self):
        if (len(self.parent.BackupFileDir) > 0):                        
            self._BackFilePath = self.parent.BackupFileDir + "\\" + self.parent.SampleCode + "\\" + self.Samplename
        else:
            self._BackFilePath = ''
        
        return self._BackFilePath

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
        
    '''
    '''
    def BackupRockmagData_usingFSO(self):            
        if ((len(os.path.dirname(self.BackFilePath)) == 0) or (len(os.path.dirname(self.SpecFilePath(self.parent))) == 0)):
            return
        
        try:
            TempFileStr = self.parent.BackupFileDir + "\\" + self.parent.SampleCode                                               
            if not os.path.isdir(TempFileStr):
                os.makedirs(TempFileStr, exist_ok=True)
                if not os.path.isdir(TempFileStr):
                    raise FileNotFoundError("Error: Cannot create backup directory")
                        
            shutil.copy(self.SpecFilePath(self.parent) + ".rmg", self.BackFilePath + ".rmg")
        except:
            return
        
        return
   
    '''
    '''
    def BackupSpecFile_usingFSO(self):            
        if ((len(os.path.dirname(self.BackFilePath)) == 0) or (len(os.path.dirname(self.SpecFilePath(self.parent))) == 0)):
            return

        try:        
            TempFileStr = self.parent.BackupFileDir + "\\" + self.parent.SampleCode                                               
            if not os.path.isdir(TempFileStr):
                os.makedirs(TempFileStr, exist_ok=True)
                if not os.path.isdir(TempFileStr):
                    raise FileNotFoundError("Error: Cannot create backup directory")
            
            shutil.copy(self.SpecFilePath(self.parent), self.BackFilePath)
        except:
            return
        
        return   
        
    '''
        new code by Bogue 17 April 2006.  9.96 etc. bug
        WriteNum stuffs any num into 5 spaces, with leading zeroes
    '''
    def WriteNum(self, num):
        if (num > 99999): 
            num = 99999     # Tame really bad ones.
        if (num < -9999): 
            num = -9999
            
        WriteNum = ''
        if (round(num, 1) >= 1000):             # Display oversize as integers
            WriteNum = "{:05}".format(num)
        elif (round(num, 1) <= -100):
            WriteNum = "{:05}".format(num)
        elif (num >= 0):
            WriteNum = "{:05.1f}".format(num)  # Usually here +, <999..
        else:
            WriteNum = "{:05.1f}".format(num)  # or here for -,>-99.
        
        return WriteNum
           
    '''
        Writes inc in a [sp]xx.x or -xx.x format
    '''
    def WriteInc(self, num):    
        if (num > 99999): 
            num = 99999  #Tame really bad ones.
        if (num < -9999): 
            num = -9999
        if (round(num, 1) >= 1000):         # Display oversize as integers
            WriteInc = "{:05}".format(num)
        elif (round(num, 1) <= -100):
            WriteInc = "{:05}".format(num)
        elif (round(num, 1) >= 100):
            WriteInc = "{:5.1f}".format(num)           # Here for bad inc >90...
        elif (num >= 0):
            WriteInc = "{:05.1f}".format(num)     # Here for good + inc
        else:
            WriteInc = "{:05.1f}".format(-num)    # or here for -inc.
        
        return WriteInc
           
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
    def WriteRockmagInfoLine(self, Description, Level=0):
        FilePath = self.SpecFilePath(self.parent) + ".rmg"
        self.WriteRockmagHeaders()
        
        with open(FilePath, 'at') as filenum:
            filenum.write(Description + ",")
            filenum.write(str(Level) + ",")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average.Z * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Susceptibility * self.parent.parent.modConfig.SusceptibilityMomentFactorCGS) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average.X * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.Holder.Average.Y * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" Holder ,")
            filenum.write(" 0 ,")
            filenum.write(" 0 ,")
            filenum.write(str(math.sqrt(abs(self.Holder.Average.X**2 + self.Holder.Average.Y**2 + self.Holder.Average.Z**2)) * self.parent.parent.modConfig.RangeFact) + ",")
            filenum.write(" 0 ,")
            filenum.write(str(self.SampleHeight) + ",")
            filenum.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            
        return

    '''
    '''    
    def WriteRockmagData(self, RMStep, magZ = 0.0, StdDevZ = 0.0, magX = 0.0, StdDevX = 0.0, 
                         magY = 0.0, StdDevY = 0.0, crdec = 0.0, crinc = 0.0, mmnt = 0.0, errangle = 0.0, SampleHeight = 0.0):
        
        FilePath = self.SpecFilePath(self.parent) + ".rmg"
        self.WriteRockmagHeaders()
        filenum = open(FilePath, 'wt') 
        filenum.write(RMStep.StepType + ",")
        filenum.write(str(RMStep.Level) + ",")
        filenum.write(str(RMStep.BiasField) + ",")
        filenum.write(str(RMStep.SpinSpeed) + ",")
        filenum.write(str(RMStep.HoldTime) + ",")
        filenum.write(str(magZ) + ",")
        filenum.write(str(StdDevZ) + ",")
        filenum.write(str(magZ / self.Vol) + ",")
        filenum.write(str(self.Susceptibility) + ",")
        filenum.write(str(magX) + ",")
        filenum.write(str(StdDevX) + ",")
        filenum.write(str(magY) + ",")
        filenum.write(str(StdDevY) +  ",")
        filenum.write(str(RMStep.Remarks) + ",")    # (November 2007 L Carporzen) Remarks column in RMG
        filenum.write(str(crdec) + ",")
        filenum.write(str(crinc) + ",")
        filenum.write(str(mmnt) + ",")
        filenum.write(str(errangle) + ",")
        filenum.write(str(SampleHeight / self.parent.parent.modConfig.UpDownMotor1cm) + ",")
        filenum.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n") # (November 2007 L Carporzen) Date and time column in RMG
        filenum.close()
        self.BackupRockmagData()
        return

    '''
    '  WriteUpMeasurements
    '
    '  Description:       This function dumps the "up" data given to a temp file.
    '''
    def WriteUpMeasurements(self, MData, demag):
        UpFilePath = self.parent.UpFilePath
        cnt = MData.Count
        if (cnt == 0): 
            return

        filenum = None
        if not os.path.exists(UpFilePath):
            # Create the file new if it doesn't exist
            filenum = open(UpFilePath, 'wt')
            filenum.write("Sample" + "|Direction" + "|Blocks" + "|MsmtType" + "|Block" + "|MsmtNum" + "|X,Y,Z" + "\n")
        else:
            filenum = open(UpFilePath, 'at')
        
        for i in range(0, cnt):
            if MData.Item[i].isUp:
                initialString = self.Samplename + "|U|" + str(cnt) + "|"
            else:
                initialString = self.Samplename + "|D|" + str(cnt) + "|"
            
            for j in range(0, 2):
                filenum.write(initialString)
                filenum.write("Z|" + str(i+1) + "|" + str(j+1) + "|")
                filenum.write(MData.Item[i].Baselines[j].WriteString())
                filenum.write("|" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

            for j in range(0, 4):
                filenum.write(initialString)
                filenum.write("S|" + str(i+1) + "|" + str(j+1) + "|")
                filenum.write(MData.Item[i].Sample[j].WriteString())
                filenum.write("|" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            
            for j in range(0, 4):
                filenum.write(initialString)
                filenum.write("H|" + str(i+1) + "|" + str(j+1) + "|")
                filenum.write(MData.Item[i].Holder[j].WriteString())
                filenum.write("|" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        
        filenum.close()
        return

    '''
    '''
    def WriteStatsTable(self, MData, demag):
        
        StatFilePath = self.parent.CurrentStepFilePathPrefix + ".stat"
        if not os.path.exists(StatFilePath):
            # Create the file new if it doesn't exist
            filenum = open(StatFilePath, 'wt') 
            filenum.write("Sample" + "     Sig/Drift" + "     Sig/Holder" + "     Sig/Ind" + "     Sig/Noise" + "     CSD" + "     HorizErrAng" + "     Up/Down" + "\n")
        else:
            filenum = open(StatFilePath, 'at')
        
        filenum.write(self.Samplename)
        filenum.write("     " + self.WriteNum(MData.SigDrift))
        filenum.write("     " + self.WriteNum(MData.SigHolder))
        filenum.write("     " + self.WriteNum(MData.SigInduced))
        filenum.write("     " + self.WriteNum(MData.SigNoise))
        filenum.write("     " + self.WriteNum(MData.FischerSD))
        filenum.write("     " + self.WriteNum(MData.ErrorHorizontal))
        filenum.write("     " + "{:.3f}".format(MData.UpToDown) + "\n")
        filenum.close()
        return
   
    '''
        WriteData
    
        Description:       This function dumps the data given to a specified file.
    
        Revision History:
            Albert Hsiao        2/19/99       Formatted output.
    '''
    def WriteData(self, demag, gdec, ginc, sdec, sinc, 
                        crdec, crinc, mmnt, errangle, 
                        sdx, sdy, sdz, UpToDn = 0):
        FilePath = self.SpecFilePath(self.parent)
        if not os.path.exists(FilePath):
            # Create the file new if it doesn't exist
            filenum = open(FilePath, 'wt') 
            filenum.write("original spec file not found")
            filenum.write("        ")
            filenum.write(self.WriteNum(self._CorePlateStrike) + " ")
            filenum.write(self.WriteNum(self._CorePlateDip) + " ")
            filenum.write(self.WriteNum(self._BeddingStrike) + " ")
            filenum.write(self.WriteNum(self._BeddingDip) + " ")
            filenum.write(self.WriteNum(self._Vol) + "\n")
        else:
            filenum = open(FilePath, 'at') 
        
        ErrorAngle = errangle
        Moment = mmnt
        self.UpDownRatio = UpToDn
        
        if (ErrorAngle > 999): 
            ErrorAngle = 999.9
        filenum.write(str(demag))
        filenum.write(self.WriteNum(gdec) + " ")
        filenum.write(self.WriteInc(ginc) + " ")
        filenum.write(self.WriteNum(sdec) + " ")
        filenum.write(self.WriteInc(sinc) + " ")
        filenum.write("{:08.2E}".format(Moment) + " ")
        filenum.write("{:05.1f}".format(ErrorAngle) + " ")
        filenum.write(self.WriteNum(crdec) + " ")
        filenum.write(self.WriteInc(crinc) + " ")
        filenum.write(modProg.FormatNumber(sdx) + " ")
        filenum.write(modProg.FormatNumber(sdy) + " ")
        filenum.write(modProg.FormatNumber(sdz) + " ")
        filenum.write(self.parent.parent.modConfig.MailFromName + " ")
        filenum.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")   # (August 2007 L Carporzen) Time added for VRM experiments
        filenum.close()        
        return    
       
    '''
    '''
    def ReadUpMeasurements(self):        
        workingBlock = MeasurementBlock()
        CurrentSampleFirstLine = -1
        CurrentSampleLastLine = -1
        TotalBlocks = -1
        currentBlock = 0
        
        readUpMeasurements = MeasurementBlocks()
        UpFilePath = self.parent.UpFilePath
        with open(UpFilePath, 'rt') as filenum:
            the_array = []
            for lines in filenum:
                the_array.append(lines.split("|"))
        
        for r in range(0, len(the_array)):
            readSampname = the_array[r][0]
            if (readSampname == self.Samplename):
                readTotalBlocks = int(the_array[r][2])
                if ((r - 1 + 10 * readTotalBlocks) < len(the_array)):
                    readSampname2 = the_array[r - 1 + 10 * readTotalBlocks][0]
                    if ((readSampname2 == self.Samplename) and (the_array[r][1] == "U")):
                        CurrentSampleFirstLine = r
                        CurrentSampleLastLine = r - 1 + 10 * readTotalBlocks
                                            
        if (CurrentSampleLastLine > CurrentSampleFirstLine):
            TotalBlocks = int(the_array[CurrentSampleFirstLine][2])
            if (TotalBlocks == 0): 
                return readUpMeasurements
            
            for r in range(CurrentSampleFirstLine, CurrentSampleLastLine+1):
                if (int(the_array[r][4]) > currentBlock):
                    if (currentBlock > 0):
                        readUpMeasurements.Add(workingBlock)
                        
                    currentBlock = int(the_array[r][4])
                    workingBlock = MeasurementBlock()
                    if (the_array[r][1] == "D"):
                        workingBlock.isUp = False
                    else:
                        workingBlock.isUp = True
                                    
                readMeastype = the_array[r][3]
                readBlocknum = int(the_array[r][4])
                readMeasnum = int(the_array[r][5]) - 1
                workingvector = Cartesian3D()
                workingvector.ReadString(the_array[r][6])
                if (readMeastype == "Z"):
                    workingBlock.SetBaseline(readMeasnum, workingvector)
                elif (readMeastype == "H"):
                    workingBlock.SetHolder(readMeasnum, workingvector)
                elif (readMeastype == "S"):
                    workingBlock.SetSample(readMeasnum, workingvector)
                
            readUpMeasurements.Add(workingBlock)
            
        else:
            self.parent.parent.displayMessageBox(caption="Critical Error!", message="Sample not found in '.up' file!", pause=True, buttons='OK')
        
        return readUpMeasurements

    '''
    '''
    def BackupRockmagData(self):    
        self.BackupRockmagData_usingFSO()    
        return
    
    '''
    '''
    def BackupSpecFile(self):
        self.BackupSpecFile_usingFSO()
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
    
        
        