'''
Created on Nov 14, 2025

@author: hd.nguyen
'''
import math

Pi = 3.1415926536
rad = (Pi / 180)
deg = (180 / Pi)

class modVector3d:
    '''
    classdocs
    '''
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Returns the angle from x clockwise to y, in radians.
        "xc" is in the x direction, "yc" is in the y direction.
    '''
    @classmethod
    def Atan2(cls, xC, yC):    
        if ((xC == 0) and (yC >= 0)):
            Atan2 = Pi / 2
        elif ((xC == 0) and (yC < 0)):
            Atan2 = 3 * Pi / 2
        else:
            Atan2 = math.atan(abs(yC / xC))
            if ((yC >= 0) and (xC > 0)):
                Atan2 = math.atan(abs(yC / xC))
            elif ((yC >= 0) and (xC < 0)):
                Atan2 = Pi - Atan2
            elif ((yC <= 0) and (xC < 0)):
                Atan2 = Pi + Atan2
            elif ((yC <= 0) and (xC > 0)):
                Atan2 = 2 * Pi - Atan2
                
        return Atan2
    
    '''
    '''
    @classmethod
    def RadToDeg(cls, ang, chVal = False):
        # This function returns an angle in degrees from some radian value
        RadToDeg = ang * deg
        if chVal:
            # We always want to return the declination between 0 and 360
            while (RadToDeg > 360):
                RadToDeg = RadToDeg - 360
            
            while (RadToDeg < 0):
                RadToDeg = RadToDeg + 360
            
        return RadToDeg
    
    '''
        This function returns an angle in radians from some degree value
    '''
    @classmethod
    def DegToRad(cls, ang):
        return ang * rad
    
    
    