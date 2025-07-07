'''
Created on Mar 24, 2025

@author: hd.nguyen
'''
import math

from Hardware.Device.SerialPortDevice import SerialPortDevice

class AF_2GControl(SerialPortDevice):
    '''
    classdocs
    '''


    def __init__(self, baudRate=None, pathName=None, comPort=None, Label=None, parent=None, modConfig=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.modConfig = modConfig
        if (comPort != None):
            SerialPortDevice.__init__(self, baudRate, 'AF_2GControl', pathName, comPort, Label, modConfig)
        
    '''
    ' Find X (input to AF) from field

    '-------------------------------------------------------------------------------------------------------------------------'
    '-------------------------------------------------------------------------------------------------------------------------'
    '
    '   Code Mod
    '   (July 2010, I Hilburn)
    '
    '   Changed code to match new array setup in modConfig and frmSettings used to store the AF and IRM calibration values
    '   Instead of two arrays per coil (X & Y), there's just one N x 2 array where col 0 = X, and col 1 = Y.
    '   Also, the array is now dynamic and can be larger than 25 elements (the auto-calibration routine makes it easy to generate
    '   long AF calibration arrays).
    '
    '   This function has otherwise been preserved as it was originally written.  Since the calibration array will be
    '   changed in frmSettings depending on the AF system, this one function can be used to convert field values to either
    '   2G numbers or Voltage double values for both the 2G and ADWIN AF systems. (Yay!)
    '
    '   To make this function useable by either 2G or ADWIN AF system, the return value has been changed to a Variant
    '''
    def FindXCalibValue(self, field, AFCoilSystem):
        xCalibValue = -1
        if (AFCoilSystem == self.modConfig.AxialCoilSystem):
            if (field > self.modConfig.AfAxialMax):
                field = self.modConfig.AfAxialMax
            elif (field < self.modConfig.AfAxialMin):
                field = self.modConfig.AfAxialMin
                
            # Check to make sure AFAxialCount > 1
            if (self.modConfig.AFAxialCount <= 1):
                errorMessage = "AF ERROR! Only one AF Axial Coil calibration value has been set."
                errorMessage += "Paleomag Code will now end.\n"
                errorMessage += "Please restart the code and go to the Settings Window "
                errorMessage += "to add more calibration values."
                raise ValueError(errorMessage)
            
            for i in range(1, self.modConfig.AFAxialCount+1):
                if (math.isclose(self.modConfig.AFAxial[i, 1], field)):
                    xCalibValue = self.modConfig.AFAxial[i, 0]
                    return xCalibValue
                
                elif ((self.modConfig.AFAxial[i - 1, 1] < field) and (self.modConfig.AFAxial[i, 1] > field)):
                    Slope = (self.modConfig.AFAxial[i, 0] - self.modConfig.AFAxial[i - 1, 0]) / (self.modConfig.AFAxial[i, 1] - self.modConfig.AFAxial[i - 1, 1])
                    xCalibValue = self.modConfig.AFAxial[i - 1, 0] + Slope * (field - self.modConfig.AFAxial[i - 1, 1])
                    break
                 
                elif (self.modConfig.AFAxial[self.modConfig.AFAxialCount, 1] < field):
                    # Field is larger than largest field in the calibration table
                    Slope = (self.modConfig.AFAxial[self.modConfig.AFAxialCount, 0] - self.modConfig.AFAxial[self.modConfig.AFAxialCount - 1, 0]) \
                            / (self.modConfig.AFAxial[self.modConfig.AFAxialCount, 1] - self.modConfig.AFAxial[self.modConfig.AFAxialCount - 1, 1])
                    xCalibValue = self.modConfig.AFAxial[self.modConfig.AFAxialCount, 0] + Slope * (field - self.modConfig.AFAxial[self.modConfig.AFAxialCount, 1])
                
        elif (AFCoilSystem == self.modConfig.TransverseCoilSystem):
            if (field > self.modConfig.AfTransMax):
                field = self.modConfig.AfTransMax
            elif (field < self.modConfig.AfTransMin):
                field = self.modConfig.AfTransMin
                
            # Check to make sure AfTransCount > 1
            if (self.modConfig.AfTransCount <= 1):
                errorMessage = "AF ERROR! Only one AF Trans Coil calibration value has been set."
                errorMessage += "Paleomag Code will now end.\n"
                errorMessage += "Please restart the code and go to the Settings Window "
                errorMessage += "to add more calibration values."
                raise ValueError(errorMessage)
            
            for i in range(1, self.modConfig.AfTransCount+1):
                if (math.isclose(self.modConfig.AfTrans[i, 1], field)):
                    xCalibValue = self.modConfig.AfTrans[i, 0]
                    return xCalibValue
                
                elif ((self.modConfig.AfTrans[i - 1, 1] < field) and (self.modConfig.AfTrans[i, 1] > field)):
                    Slope = (self.modConfig.AfTrans[i, 0] - self.modConfig.AfTrans[i - 1, 0]) / (self.modConfig.AfTrans[i, 1] - self.modConfig.AfTrans[i - 1, 1])
                    xCalibValue = self.modConfig.AfTrans[i - 1, 0] + Slope * (field - self.modConfig.AfTrans[i - 1, 1])
                    break
                 
                elif (self.modConfig.AfTrans[self.modConfig.AfTransCount, 1] < field):
                    # Field is larger than largest field in the calibration table
                    Slope = (self.modConfig.AfTrans[self.modConfig.AfTransCount, 0] - self.modConfig.AfTrans[self.modConfig.AfTransCount - 1, 0]) \
                            / (self.modConfig.AfTrans[self.modConfig.AfTransCount, 1] - self.modConfig.AfTrans[self.modConfig.AfTransCount - 1, 1])
                    xCalibValue = self.modConfig.AfTrans[self.modConfig.AfTransCount, 0] + Slope * (field - self.modConfig.AfTrans[self.modConfig.AfTransCount, 1])
        
        return xCalibValue
    
    '''
    '''
    def Disconnect(self):
        if self.PortOpen:
            self.PortOpen = False
            
        return
    
    