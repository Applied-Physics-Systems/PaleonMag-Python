'''
Created on Oct 29, 2025

@author: hd.nguyen
'''
from ClassModules.RockmagStep import RockmagStep
from ClassModules.Sample import Sample
from ClassModules.SampleIndexRegistration import SampleIndexRegistration

class DataExchange:
    '''
    classdocs
    
    '''
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    @classmethod
    def parseRockmagSteps(cls, measurementSteps):
        dataDict = {}
        
        dataDict['CurrentStepIndex'] = measurementSteps.CurrentStepIndex
        dataDict['NextStepID'] = measurementSteps.nextStepID
        dataDict['Count'] = measurementSteps._Count
        dataDict['Item'] = []
        for item in measurementSteps.Item: 
            stepDict = {}
            stepDict['BiasField'] = item.BiasField
            stepDict['SpinSpeed'] = item.SpinSpeed
            stepDict['HoldTime'] = item.HoldTime            
            stepDict['StepType'] = item.StepType
            stepDict['Key'] = item.key
            stepDict['Remarks'] = item.Remarks                    
            stepDict['Measure'] = item.Measure
            stepDict['MeasureSusceptibility '] = item.MeasureSusceptibility             
            stepDict['_Level'] = item._Level
            stepDict['_DemagStepLabel'] = item._DemagStepLabel
            dataDict['Item'].append(stepDict)
        
        return dataDict

    '''
    '''
    @classmethod
    def loadRockmagSteps(cls, dataDict, measurementSteps, parent):
        
        measurementSteps.CurrentStepIndex = dataDict['CurrentStepIndex'] 
        measurementSteps.nextStepID = dataDict['NextStepID'] 
        measurementSteps._Count = dataDict['Count'] 
        
        measurementSteps.Item = []
        for item in dataDict['Item']: 
            rockmagStep = RockmagStep(parent)
            rockmagStep.BiasField = item['BiasField'] 
            rockmagStep.SpinSpeed = item['SpinSpeed']
            rockmagStep.HoldTime = item['HoldTime']             
            rockmagStep.StepType = item['StepType'] 
            rockmagStep.key = item['Key'] 
            rockmagStep.Remarks = item['Remarks']                     
            rockmagStep.Measure = item['Measure'] 
            rockmagStep.MeasureSusceptibility = item['MeasureSusceptibility ']              
            rockmagStep._Level = item['_Level'] 
            rockmagStep._DemagStepLabel = item['_DemagStepLabel'] 
            measurementSteps.Item.append(rockmagStep)
        
        return measurementSteps
    
    '''
    '''
    @classmethod
    def parseSample(cls, sample):
        sampleDict = {}
        sampleDict['SampleName'] = sample.Samplename
        sampleDict['SampleHole'] = sample.sampleHole
        sampleDict['IndexFile'] = sample.IndexFile
        sampleDict['SampleHeight'] = sample.SampleHeight
        sampleDict['Comment'] = sample.Comment 
        sampleDict['Susceptibility'] = sample.Susceptibility 
        
        sampleDict['Vol'] = sample.Vol 
        sampleDict['CorePlateStrike'] = sample.CorePlateStrike
        sampleDict['CorePlateDip'] = sample.CorePlateDip
        sampleDict['BeddingStrike'] = sample.CorePlateStrike
        sampleDict['BeddingDip'] = sample.CorePlateDip
        sampleDict['FoldAxis'] = sample.FoldAxis
        sampleDict['FoldPlunge'] = sample.FoldPlunge
        sampleDict['FoldRotation'] = sample.FoldRotation
        sampleDict['alreadyReadSpec'] = sample.alreadyReadSpec
                    
        return sampleDict
    
    '''
    '''
    @classmethod
    def parseSamples(cls, sampleSet):
        dataDict = {}
       
        dataDict['IndexFile'] = sampleSet.IndexFile        
        dataDict['Count'] = sampleSet.Count

        dataDict['Item'] = []
        for item in sampleSet.Item:
            sampleDict = cls.parseSample(item)
            dataDict['Item'].append(sampleDict)
        
        return dataDict

    '''
    '''
    @classmethod
    def loadSample(cls, dataDict):
        sample = Sample()            
        sample.Samplename = dataDict['SampleName'] 
        sample.sampleHole = dataDict['SampleHole'] 
        sample.IndexFile = dataDict['IndexFile'] 
        sample.SampleHeight = dataDict['SampleHeight']
        sample.Comment = dataDict['Comment']
        sample.Susceptibility = dataDict['Susceptibility']
        
        sample.Vol = dataDict['Vol']
        sample.CorePlateStrike = dataDict['CorePlateStrike']
        sample.CorePlateDip = dataDict['CorePlateDip']
        sample.BeddingStrike = dataDict['BeddingStrike']
        sample.BeddingDip = dataDict['BeddingDip']
        sample.FoldAxis = dataDict['FoldAxis']
        sample.FoldPlunge = dataDict['FoldPlunge']
        sample.FoldRotation = dataDict['FoldRotation']
        sample.alreadyReadSpec = dataDict['alreadyReadSpec']
        return sample             

    '''
    '''
    @classmethod
    def loadSamples(cls, dataDict, sampleSet):
        sampleSet.IndexFile = dataDict['IndexFile']         
        sampleSet.Count = dataDict['Count'] 

        sampleSet.Item = []
        for item in dataDict['Item']:
            sample = cls.loadSample(item)
            sampleSet.Item.append(sample)
            
        return sampleSet

    '''
    '''
    @classmethod
    def parseSampleIndexRegistration(cls, registry):
        if (registry == None):
            return None
        
        dataDict = {}
        dataDict['SampleCode'] = registry.SampleCode
        dataDict['FileDir'] = registry.filedir
        dataDict['FileName'] = registry.filename
        dataDict['Locality'] = registry.locality
        dataDict['BackupFileDir'] = registry.BackupFileDir
        dataDict['AvgSteps'] = registry.avgSteps             
        dataDict['SiteLat'] = registry.siteLat
        dataDict['SiteLong'] = registry.siteLong
        dataDict['MagDec'] = registry.magDec             
        dataDict['DoUp'] = registry.doUp
        dataDict['DoBoth'] = registry.doBoth
        dataDict['RockmagMode'] = registry.RockmagMode
        dataDict['CurrentDemag'] = registry._curDemag
        dataDict['CurrentDemagLong'] = registry._curDemagLong            

        dataDict['MeasurementSteps'] = cls.parseRockmagSteps(registry.measurementSteps)                        
        dataDict['SampleSet'] = cls.parseSamples(registry.sampleSet)

        return dataDict

    '''
    '''
    @classmethod
    def loadSampleIndexRegistration(cls, dataDict, registry, parent):
        registry.SampleCode = dataDict['SampleCode'] 
        registry.filedir = dataDict['FileDir'] 
        registry.filename = dataDict['FileName'] 
        registry.locality = dataDict['Locality'] 
        registry.BackupFileDir = dataDict['BackupFileDir'] 
        registry.avgSteps = dataDict['AvgSteps']              
        registry.siteLat = dataDict['SiteLat'] 
        registry.siteLong = dataDict['SiteLong'] 
        registry.magDec = dataDict['MagDec']              
        registry.doUp = dataDict['DoUp'] 
        registry.doBoth = dataDict['DoBoth'] 
        registry.RockmagMode = dataDict['RockmagMode'] 
        registry._curDemag = dataDict['CurrentDemag']
        registry._curDemagLong = dataDict['CurrentDemagLong']             
        
        registry.measurementSteps = cls.loadRockmagSteps(dataDict['MeasurementSteps'], registry.measurementSteps, parent)                        
        registry.sampleSet = cls.loadSamples(dataDict['SampleSet'], registry.sampleSet)
        
        return registry
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    @classmethod
    def loadSampleHolder(cls, dataDict, sampleHolder, parent):
        sampleHolder.Samplename = dataDict['SampleName'] 
        sampleHolder.sampleHole = dataDict['SampleHole']
        sampleHolder.IndexFile = dataDict['IndexFile'] 
        sampleHolder.SampleHeight = dataDict['SampleHeight'] 
        
        if (sampleHolder.parent != None):
            sampleHolder.parent = cls.loadSampleIndexRegistration(dataDict, sampleHolder.parent, parent)
        
        return sampleHolder
    
    '''
    '''
    @classmethod
    def parseSampleHolder(cls, sampleHolder):
        dataDict = {'DataType': 'SampleHolder'}
        dataDict['SampleName'] = sampleHolder.Samplename
        dataDict['SampleHole'] = sampleHolder.sampleHole
        dataDict['IndexFile'] = sampleHolder.IndexFile
        dataDict['SampleHeight'] = sampleHolder.SampleHeight
        
        if (sampleHolder.parent != None):            
            registryDict = cls.parseSampleIndexRegistration(sampleHolder.parent)
            dataDict.update(registryDict)
                                     
        return dataDict

    '''
        SampleIndexRegistrations
    '''
    @classmethod
    def loadSampleIndexRegistry(cls, dataDict, sampleIndexRegistry, parent):
        sampleIndexRegistry.SampleHolderIndex = cls.loadSampleIndexRegistration(dataDict['SampleHolderIndex'], sampleIndexRegistry.SampleHolderIndex, parent)
        sampleIndexRegistry.SampleHolderIndexTag = dataDict['SampleHolderIndexTag']
        
        for item in dataDict['Item']:
            registry = SampleIndexRegistration(parent)
            registry = cls.loadSampleIndexRegistration(item, registry, parent)
            sampleIndexRegistry.Item.append(registry)
                
        return sampleIndexRegistry

    '''
        SampleIndexRegistrations
    '''
    @classmethod
    def parseSampleIndexRegistry(cls, sampleIndexRegistry):
        dataDict = {'DataType': 'SampleIndexRegistry'}
        dataDict['SampleHolderIndex'] = cls.parseSampleIndexRegistration(sampleIndexRegistry.SampleHolderIndex)
        dataDict['SampleHolderIndexTag'] = sampleIndexRegistry.SampleHolderIndexTag
        
        dataDict['Item'] = []
        for item in sampleIndexRegistry.Item:
            sampleDict = cls.parseSampleIndexRegistration(item)            
            dataDict['Item'].append(sampleDict)
        
        return dataDict
