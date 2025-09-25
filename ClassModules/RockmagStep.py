'''
Created on Sep 9, 2025

@author: hd.nguyen
'''
from builtins import property

DEMAGLEN = 6

RockmagStepAFmax = "AFmax"
RockmagStepAFz = "AFz"
RockmagStepAF = "AF"
RockmagStepUAFX1 = "UAFX1"
RockmagStepUAFX2 = "UAFX2"
RockmagStepUAFZ1 = "UAFZ1"
RockmagStepaTAFX = "aTAFX" 
RockmagStepaTAFY = "aTAFY"
RockmagStepaTAFZ = "aTAFZ"
RockmagStepARM = "ARM"
RockmagStepVRM = "VRM"
RockmagStepPulseIRMAxial = "IRMz"
RockmagStepPulseIRMTrans = "IRMx"
RockmagStepRRM = "RRM"
RockmagStepRRMz = "RRMz"

class RockmagStep():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.BiasField = 0
        self.SpinSpeed = 0
        self.HoldTime = 0
        
        self.StepType = ''
        self.key = ''
        self.Remarks = ''
                
        self.Measure = False
        self.MeasureSusceptibility = False
        
        self._Level = 0
        self._DemagStepLabel = ''

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def DemagStepLabel(self):
        return self._DemagStepLabel
    
    @DemagStepLabel.getter
    def DemagStepLabel(self):
        self._DemagStepLabel = self.StepType
        
        if (len(self._DemagStepLabel) > DEMAGLEN):
            self._DemagStepLabel = self._DemagStepLabel[0:DEMAGLEN]
            
        numLength = DEMAGLEN - len(self._DemagStepLabel)
        if (self.StepType == RockmagStepARM): 
            setLevel = self.BiasField 
        else: 
            setLevel = self.Level
        
        if (setLevel != 0):
            self._DemagStepLabel = self._DemagStepLabel + str(setLevel).rjust(numLength)
        
        if (len(self._DemagStepLabel) < DEMAGLEN):
            for _ in range(len(self._DemagStepLabel), DEMAGLEN+1):
                self._DemagStepLabel += " "
        
        
        return self._DemagStepLabel
    
    @property
    def Level(self):
        return self._Level
    
    @Level.setter
    def Level(self, value):
        self._Level = value
        return
    
    @Level.getter
    def Level(self):
        mvarLevel = self._Level
        
        if (self.StepType == RockmagStepAF):
            if (self.parent.modConfig.AfAxialMax > self.parent.modConfig.AfTransMax):
                maxAcceptableLevel = self.parent.modConfig.AfTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            if (self.parent.modConfig.AfAxialMin < self.parent.modConfig.AfTransMin):
                minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            else: 
                minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepAFmax):
            if (self.parent.modConfig.AfAxialMax > self.parent.modConfig.AfTransMax):
                maxAcceptableLevel = self.parent.modConfig.AfTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            if (self.parent.modConfig.AfAxialMin < self.parent.modConfig.AfTransMin):
                minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            else: 
                minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
                
        elif (self.StepType == RockmagStepAFz):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFX1):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFX2):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepUAFZ1):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
                
        elif (self.StepType == RockmagStepaTAFX):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepaTAFY):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepaTAFZ):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin 
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepARM):
            maxAcceptableLevel = self.parent.modConfig.AfAxialMax
            minAcceptableLevel = self.parent.modConfig.AfAxialMin
            if not self.parent.modConfig.EnableARM:
                maxAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepPulseIRMAxial):
            if (self.parent.modConfig.PulseTransMax > self.parent.modConfig.PulseAxialMax):
                maxAcceptableLevel = self.parent.modConfig.PulseTransMax 
            else: 
                maxAcceptableLevel = self.parent.modConfig.PulseAxialMax
            if self.parent.modConfig.EnableIRMBackfield:
                minAcceptableLevel = -1*self.parent.modConfig.PulseAxialMax 
            else: 
                minAcceptableLevel = self.parent.modConfig.PulseAxialMin
            
            if not self.parent.modConfig.EnableAxialIRM:
                maxAcceptableLevel = 0
                minAcceptableLevel = 0
            
        elif (self.StepType == RockmagStepRRM):
            maxAcceptableLevel = self.parent.modConfig.AfTransMax
            minAcceptableLevel = self.parent.modConfig.AfTransMin
            if not self.parent.modConfig.EnableAF:
                maxAcceptableLevel = 0
            
        else:
            maxAcceptableLevel = 999999
            minAcceptableLevel = -999999
    
        if (self.StepType == RockmagStepAFmax):
            mvarLevel = maxAcceptableLevel
            
        elif (self._Level == 0):
            mvarLevel = 0
            
        elif (self._Level > maxAcceptableLevel):
            mvarLevel = maxAcceptableLevel
            
        elif (self._Level < minAcceptableLevel):
            mvarLevel = minAcceptableLevel
            
        else:
            mvarLevel = self._Level
        
        return mvarLevel
        
'''
    -----------------------------------------------------------------------------------------------
'''        
class RockmagSteps():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.CurrentStepIndex = 0
        self.nextStepID = 1
        self.Item = []
        
        self._Count = 0
        self._CurrentStep = RockmagStep()

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
    def CurrentStep(self):
        return self._CurrentStep
    
    @CurrentStep.getter
    def CurrentStep(self):
        self._CurrentStep = RockmagStep()
        self._CurrentStep.StepType = ''
        
        if (len(self.Item[0]) > self.CurrentStepIndex):
            self._CurrentStep = self.Item[0][self.CurrentStepIndex]
        
        return self._CurrentStep
    
    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    
   
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def AdvanceStep(self):
        self.CurrentStepIndex = (self.CurrentStepIndex + 1) % (self.Count)
        return
    
    '''
    '''
    def Remove(self, index):
        del self.Item[index]
        return
    
    '''
    '''
    def Add(self, StepType, 
                  Level= 0.0, 
                  BiasField = 0, 
                  SpinSpeed = 0, 
                  HoldTime = 0, 
                  Measure = True, 
                  MeasureSusceptibility = False, 
                  Remarks = '', 
                  BeforeStep = 0, 
                  AfterStep = 0):
        
        objNewMember = RockmagStep(self.parent)
        
        # set the properties passed into the method
        objNewMember.StepType = StepType
        objNewMember.Level = Level
        objNewMember.BiasField = BiasField
        objNewMember.SpinSpeed = SpinSpeed
        objNewMember.HoldTime = HoldTime
        objNewMember.Measure = Measure
        objNewMember.MeasureSusceptibility = MeasureSusceptibility
        objNewMember.Remarks = Remarks 
        objNewMember.key = "S" + str(self.nextStepID)
        
        if (BeforeStep > 0):
            self.Item.append([objNewMember, "S" + str(self.nextStepID), BeforeStep])
            
        elif (AfterStep > 0):
            self.Item.append([objNewMember, "S" + str(self.nextStepID),None, AfterStep]) 
            
        else:
            self.Item.append([objNewMember, "S" + str(self.nextStepID)])
        
        self.nextStepID = self.nextStepID + 1
        
        return objNewMember
    