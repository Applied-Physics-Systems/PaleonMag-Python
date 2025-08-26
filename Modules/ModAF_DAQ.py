'''
Created on Apr 10, 2025

@author: hd.nguyen
'''
import os
import math
from Hardware.Device.DAQControl import DAQControl

class ModAF_DAQ(DAQControl):
    '''
    classdocs
    '''


    def __init__(self, path, parent = None, modConfig = None):
        '''
        Constructor
        '''
        DAQControl.__init__(self, path, parent = parent, modConfig = modConfig)
        self.parent = parent
        self.modConfig = modConfig

    '''
    '''
    def findField(self, MonVolt, paramList):        
        afCount = paramList[0]
        afArray = paramList[1]
        field = 0.0
        
        # Check to make sure afCount > 1
        if (afCount <= 1):
            messageStr = 'AF ERROR! Only one AF Coil calibration value has been set. '
            messageStr += 'Paleomag Code will now end.\n'
            messageStr += 'Please restart the code and go to the Settings Window '
            messageStr += 'to add more calibration values.'
            raise IOError(messageStr) 
         
        '''           
            Loop through the Axial coil calibration array
            Note: this may loop like an Off-By-One error, but the calibration array
                  is actually one row larger than AFAxialCount (the zeroth row
                  contains zero, zero)
        '''
        for i in range(1, afCount+1):
            # Check to see if MonVolt is equal to the X calibration value
            if (math.isclose(MonVolt, afArray[i, 0])):
                # Return the matching field value
                field = afArray[i, 1]
                
            # Now, check to see if we're in between the current and prior calibration values
            if ((MonVolt < afArray[i, 0]) and (MonVolt > afArray[i - 1, 0])):
                # User linear interpolation (Y = A*(MonVolt - X(i-1)) + Y(i-1)) to get the matching field value
                Slope = (afArray[i, 1] - afArray[i - 1, 1]) / (afArray[i, 0] - afArray[i - 1, 0])
                field = afArray[i - 1, 1] + Slope * (MonVolt - afArray[i - 1, 0])
                break
            
        # Check to see if MonVolt is greater than the larger X value in the calibration array
        if (MonVolt > afArray[afCount, 0]):
            i = afCount
            
            # Need to interpolate upward using last two points of the calibration array
            Slope = (afArray[i, 1] - afArray[i - 1, 1]) / (afArray[i, 0] - afArray[i - 1, 0])
            field = afArray[i, 1] + Slope * (MonVolt - afArray[i, 0])
        
        return field

    '''
    '''
    def FindFieldFromVolts(self, MonVolt, AFCoilSystem=-128):
        field = 0.0
        
        # Check for MonVolt <= 0
        if (MonVolt <= 0):
            return 0.0
        
        if (AFCoilSystem == self.modConfig.AxialCoilSystem):
            paramList = [self.modConfig.AFAxialCount,
                         self.modConfig.AFAxial]
            self.findField(MonVolt, paramList)
            
        elif (AFCoilSystem == self.modConfig.TransverseCoilSystem):
            paramList = [self.modConfig.AfTransCount,
                         self.modConfig.AfTrans]
            self.findField(MonVolt, paramList)
        
        return field
        
    '''
    '''
    def AnalogIn(self, channel):
        analogCount = self.cbAIn(channel)         
        analogValue = self.cbToEngUnits(analogCount)
        return analogValue
        
    '''
    '''
    def AnalogOut(self, channel, rangeType, EngUnits):
        DataValue = self.cbFromEngUnits(EngUnits)
        self.cbAOut(channel, rangeType, DataValue)
        
        return
    
    '''
    '''
    def DigitalIn(self, channel):
        print('TODO')
        return 0
    
    '''
    '''
    def DigitalOut(self, DigOut_Chan, SetHigh, OneChanOn = True):
        
        status = self.cbDConfigBit(DigOut_Chan)
        
        if (status != 0):
            print('Error: Failed to set Config bits')
            return status
        
        # Determine from the input whether to set the
        # port to the high value (1) or the low value (0)
        DataValue = 0
        if SetHigh:
            DataValue = 1
            
        status = self.cbDBitOut(DigOut_Chan, DataValue)
        
        return status
        
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            data = self.Get_ADC(0)
            print(data)            
        
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        currentPath = os.getcwd()
        daqUtil = ModAF_DAQ(currentPath)
        
        daqUtil.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))

    