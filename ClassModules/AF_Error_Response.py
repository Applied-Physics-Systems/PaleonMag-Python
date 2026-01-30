'''
Created on Nov 7, 2025

@author: hd.nguyen
'''
from enum import Enum
from ClassModules.AF_Ramp_Error import AFErrorTypeEnum
from Modules.modAF_DAQ import coil_type

class AFErrorActionEnum(Enum):
    ExpressError    = 0
    SuppressError   = 1

'''
    --------------------------------------------------------------------------------------
'''
class AF_Error_Response():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.ErrorType = AFErrorTypeEnum.NoError
        self.CoilType = coil_type.Axial
        self.CodeLevel = 'Green'
        self.ErrorAction = AFErrorActionEnum.ExpressError

        self.index = ''

'''
    --------------------------------------------------------------------------------------
'''
class AF_Error_Resp_Collection():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Class_Initialize()

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    def Class_Initialize(self):
        self.Item = []
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Clear(self):
        self.Class_Initialize()
        return
    
    '''
    '''
    def GenerateCollectionIndex(self, ErrorType, CoilType, CodeLevel):
        index = ""
            
        if (ErrorType == AFErrorTypeEnum.FatalError):            
            index += "Fatal_"
            
        elif (ErrorType == AFErrorTypeEnum.TargetOvershoot):        
            index += "Overshoot_"
        
        elif (ErrorType == AFErrorTypeEnum.TargetUndershoot):        
            index += "Undershoot_"
        
        elif (ErrorType == AFErrorTypeEnum.ZeroMonitorVoltage):    
            index += "Zero_"
        
        else:        
            index +="Other_"
                
    
        if (CoilType == coil_type.Axial):        
            index += "Axial_"
        
        if (CoilType == coil_type.Transverse):        
            index += "Transverse_"
                        
        else:        
            index += "NoCoil_"
                        
        generateCollectionIndex = index + CodeLevel
        return generateCollectionIndex 
   
    '''
    '''
    def Add(self, error_type, coil_type, code_level, error_action):
        # Create a new object
        objNewMember = AF_Error_Response()
    
        # Set the properties passed into the method
        objNewMember.ErrorType = error_type
        objNewMember.CoilType = coil_type
        objNewMember.CodeLevel = code_level
        objNewMember.ErrorAction = error_action
        
        index = self.GenerateCollectionIndex(error_type, coil_type, code_level)
        objNewMember.index = index
        
        # If index already exist, skip adding
        foundEntry = False
        for eachEntry in self.Item:
            if (index == eachEntry.index):
                foundEntry = True
        
        if not foundEntry:
            self.Item.append(objNewMember)
        return

    '''
    '''
    def SetItem(self, errorType, coilType, codeLevel, errorAction):        
        for i in range(0, len(self.Item)):
            if ((self.Item[i].ErrorType == errorType) and \
                (self.Item[i].CoilType == coilType) and \
                (self.Item[i].CodeLevel == codeLevel)):
                self.Item[i].ErrorAction = errorAction
        return
        