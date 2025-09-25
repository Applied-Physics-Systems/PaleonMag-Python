'''
Created on Aug 29, 2025

@author: hd.nguyen
'''
class Sample():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Samplename = ''
        self.sampleHole = 0
        self.IndexFile = ''

'''
    -----------------------------------------------------------------------------------
'''
class Samples():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Item = []
        self.IndexFile = ''        
        self.Count = 0
        
    '''
    '''
    def Clear(self):
        self.Item = []
        return
    
    '''
    '''
    def Add(self, sampleName, sampleHole=0):
        objNewMember = Sample()
        
        objNewMember.Samplename = sampleName
        objNewMember.sampleHole = sampleHole
        objNewMember.IndexFile = self.IndexFile
        
        self.Item.append(objNewMember)
        self.Count = len(self.Item)
        return
    
    '''
    '''
    def getItemWithKey(self, keyStr):
        sample = None
        for eachEntry in self.Item:
            if (keyStr == eachEntry.IndexFile):
                sample = eachEntry
                break
            
        return sample
    
    '''
    '''
    def getItemWithIndex(self, index):
        return self.Item[index]
    
        