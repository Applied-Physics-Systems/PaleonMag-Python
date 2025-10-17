'''
Created on Aug 29, 2025

@author: hd.nguyen
'''
class Sample():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.Samplename = ''
        self.sampleHole = 0
        self.IndexFile = ''
        self.SampleHeight = 0
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def SpecFilePath(self, sampleRegistry):
        specPath = sampleRegistry.filedir + '\\' + sampleRegistry.SampleCode + '\\' + self.Samplename  
        return specPath                

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
    
        