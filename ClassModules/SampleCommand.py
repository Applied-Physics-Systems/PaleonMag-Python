'''
Created on Sep 24, 2025

@author: hd.nguyen
'''

commandMeasure = "Meas"
commandInitUp = "InitUp"
commandHolder = "Holder"
commandFlip = "Flip"
commandFin = "Fin"
commandGoto = "Goto"

class SampleCommand():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.Key = ''
        self.commandType = ''
        self.FileID = ''
        self.Sample = ''
        self.Hole = ''

'''
    -----------------------------------------------------------------------------------
'''
class SampleCommands():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.Item = []
        self.maxAvgStepsOfFiles = 0
        
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
        
    @property
    def maxAvgSteps(self):
        return self._DemagStepLabel
    
    @maxAvgSteps.getter
    def maxAvgSteps(self):
        self.countFileCalls()
        if (self.maxAvgStepsOfFiles < 1):
            maxAvgSteps = 1
        else:
            maxAvgSteps = self.maxAvgStepsOfFiles
        
        return maxAvgSteps

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def countFileCalls(self):        
        WhichFilesLoaded = [0]*self.parent.SampleIndexRegistry.Count
        
        for i in range(0, self.Count):
            if (self.parent.SampleIndexRegistry.IsValidFile(self.Item[i].fileid)):
                targetFile = self.parent.SampleIndexRegistry.index(self.Item[i].fileid)
                if (WhichFilesLoaded[targetFile] == 0):
                    if (self.maxAvgStepsOfFiles < self.parent.SampleIndexRegistry.Item[targetFile].avgSteps):
                        self.maxAvgStepsOfFiles = self.parent.SampleIndexRegistry[targetFile].avgSteps
                                
                WhichFilesLoaded[targetFile] = WhichFilesLoaded[targetFile] + 1
            
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Clear(self):
        self.Item = []
        return
        
   
