'''
Created on Aug 29, 2025

@author: hd.nguyen
'''

from ClassModules.Sample import Samples
from ClassModules.RockmagStep import RockmagSteps

class SampleIndexRegistration():
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent = parent
        self.SampleCode = ''
        self.filedir = ''
        self.filename = ''
        self.locality = ''
        self.BackupFileDir = ''
        self._curDemag = ''
        
        self.avgSteps = 0
        
        self.siteLat = 0.0
        self.siteLong = 0.0
        self.magDec = 0.0
        
        self.doUp = False
        self.doBoth = False
        
        self.measurementSteps = RockmagSteps()
        
        self.RockmagMode = False
        
        self.sampleSet = Samples()
        
    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''        
    @property
    def curDemag(self):
        return self._curDemag
    
    @curDemag.getter
    def curDemag(self):
        if (self.measurementSteps.Count == 0):
            return self._curDemag
            
        else:
            self._curDemag = self.measurementSteps.CurrentStep.DemagStepLabel
            
        return self._curDemag
                        
    '''
    '''
    def loadInfo(self):
        self.sampleSet.Clear()
        self.sampleSet.IndexFile = self.filename
        
        if (self.filename == ''):
            return
        
        with open(self.filename, 'rt') as samFile:
            self.locality = samFile.readline()
            line = samFile.readline()
            lineList = line.split() 
            try:
                self.siteLat = float(lineList[0])
                self.siteLong = float(lineList[1])
                self.magDec = float(lineList[2])
                
            except:
                self.siteLat = 0.0
                self.siteLong = 0.0
                self.magDec = 0.0
                
            for line in samFile:
                self.sampleSet.Add(line)
        
        return
    
'''
    -----------------------------------------------------------------------------------
'''    
class SampleIndexRegistrations():
    '''
    classdocs
    '''


    def __init__(self, parent):
        '''
        Constructor
        '''
        self.parent = parent
        self.Item = []
        self.SampleHolderIndex = None
        self.SampleHolderIndexTag = ''

        self._Count = 0

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''        
    @property
    def Count(self):
        return self._Count
    
    @Count.getter
    def Count(self):
        self._Count = len(self.Item)
        return self._Count
    
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
   
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def GetItem(self, fileName):
        samples = SampleIndexRegistration(self.parent)
        
        for item in self.Item:
            if (item.filename == fileName):
                samples = item
        
        return samples
    
    '''
    '''
    def IsValidSample(self, fileName, sampleName):
        
        status = self.GetItem(fileName).sampleSet.IsValidSample(sampleName)
        
        return status 
        
    '''
    '''
    def SampleCount(self):
        SampleCount = 0
        if (self.Count == 0):
            return
        
        for i in range(0, self.Count):
            SampleCount += self.Item[i].sampleSet.Count
            
        return SampleCount
    
    '''
    '''
    def SampleFileByIndex(self, vindex):
        sampCount = self.SampleCount()
        sampleFileByIndex = ''
        if ((vindex < 0) or (vindex >= sampCount)):
            return sampleFileByIndex
        
        for i in range(0, self.Count):
            if (vindex < self.Item[i].sampleSet.Count):
                break
            else: 
                vindex = vindex - self.Item[i].sampleSet.Count
                    
        sampleFileByIndex = self.Item[i].filename
        
        return sampleFileByIndex
        
    '''
        ' Original State:
        '   1) This was a private function
        '   2) SampleHolderIndex was not deallocated before allocation
        '   3) SampleHolder global variable was not set inside of this subroutine
        '      but was set instead in a code line in modProg following the initialization
        '      of the SampleIndexRegistry object (whose constructor called this subroutine)
        '
        ' Current State:
        '
        '    Inputs:    MeasSusceptibility
        '               Optional Boolean (Default = False)
        '               Allows the calling code to set whether or not the Holder will have it's
        '               susceptibility measured every time.  The default at code start is that
        '               MeasSusceptibility = False.  This can be overwritten later in the code
        '               (in frmSampleIndexRegistry.updateMeasurementSteps)
        '
        '   Outputs:    None
        '
        '   Effects:    Allocates the SampleHolderIndex Sample Registry object within the
        '               main system collection of Sample Index registries.
        '               This subroutine can be used now to overwrite both the old Sample Holder Index object
        '               And to also overwrite the SampleHolder sample object
        '
        '               At the end of this code, the SampleHolder object is overwritten with the
        '               New SampleHolder object that was added to the SampleHolderIndex
        '
        '   Potential Bugs:
        '               If the the SampleHolder object does not exist or is not accessible,
        '               the error is handled and the SampleHolder object will not be overwritten.
        '               Thus, there may be a mismatch between the SampleHolderIndex and the SampleHolder object
        '               Leading to confusion and additional errors downstream in the Paleomag code.
        '
    '''
    def MakeSampleHolder(self, MeasSusceptibility=False):
        # Allocate as a new Sample Index Registry class object
        self.SampleHolderIndex = SampleIndexRegistration(self.parent)
        
        # Setup SampleHolder Index
        self.SampleHolderIndex.filename = self.SampleHolderIndexTag
        self.SampleHolderIndex.avgSteps = 1
        self.SampleHolderIndex.doUp = True
        self.SampleHolderIndex.doBoth = False
        self.SampleHolderIndex.measurementSteps = RockmagSteps()
        self.SampleHolderIndex.sampleSet = Samples()
        
        '''    
            (March 10, 2011 - I Hilburn)
            UGH! This one line has been the source of the wait time on the holder and
            the holder always having it's susceptibility measured.
            Instead of Defaulting measure holder susc. to True
            I'm defaulting it to "False", though allowing that value to be passed in
            as an argument to the MakeSampleHolder command, and then
            will set it to true later in the code.
        '''
        self.SampleHolderIndex.measurementSteps.Add("NRM", MeasureSusceptibility=MeasSusceptibility)
        self.SampleHolderIndex.sampleSet.IndexFile = self.SampleHolderIndexTag
        self.SampleHolderIndex.sampleSet.Add("Holder")
        
        '''
            Reset the Sample stored in SampleHolder global object
            With error checking in case a change is made to the code
            that eliminates the SampleHolder global variable
        '''
        self.parent.modConfig.processData.SampleHolder = self.SampleHolderIndex.sampleSet.getItemWithKey("Holder")
        return
    
    '''
    '''
    def AddSampleIndex(self, sampleindex):
        newSampleIndex = SampleIndexRegistration(self.parent)
        newSampleIndex.filedir = sampleindex.filedir
        newSampleIndex.filename = sampleindex.filename
        newSampleIndex.BackupFileDir = sampleindex.BackupFileDir
        newSampleIndex.SampleCode = sampleindex.SampleCode
        newSampleIndex.avgSteps = sampleindex.avgSteps
        newSampleIndex.doUp = sampleindex.doUp
        newSampleIndex.doBoth = sampleindex.doBoth
        newSampleIndex.measurementSteps = sampleindex.measurementSteps
        newSampleIndex.RockmagMode = sampleindex.RockmagMode
                
        # Delete an entry that match with the current one
        matchFlag = False
        for index in range(0, len(self.Item)):
            if (self.Item[index].filename == newSampleIndex.filename):
                matchFlag = True
                break;
        if matchFlag:
            del self.Item[index]
        
        self.Item.append(newSampleIndex)
        
        return newSampleIndex
        
    '''
    '''
    def Clear(self):
        self.Item = []
        return

        