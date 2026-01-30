'''
Created on Nov 3, 2025

@author: hd.nguyen
'''
import math

Pi = 3.141592653589

class Cartesian3D():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        
        self.rad = (Pi / 180)
        self.deg = (180 / Pi)
        
        self._mag = 0.0
        self._dec = 0.0
        self._inc = 0.0
        self._UnitVectorX = 0.0
        self._UnitVectorY = 0.0
        self._UnitVectorZ = 0.0
        
    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def dec(self):
        return self._dec
    
    @dec.getter
    def dec(self):
        self._dec = self.atan(self.X, self.Y) * self.deg
        return self._dec
    
    @property
    def inc(self):
        return self._inc
    
    @inc.getter
    def inc(self):
        p = self.X ** 2 + self.Y ** 2
        self._inc = self.atan(math.sqrt(p), self.Z) * self.deg
        return self._inc
        
    @property
    def mag(self):    
        return self._mag
    
    @mag.getter
    def mag(self):
        self._mag = math.sqrt(self.X ** 2 + self.Y ** 2 + self.Z ** 2)
        return self._mag
        
    @property
    def UnitVectorX(self):    
        return self._UnitVectorX
    
    @UnitVectorX.getter
    def UnitVectorX(self):
        M = self.mag
        
        if (M == 0):
            self._UnitVectorX = 1
        else:
            self._UnitVectorX = self.X / M
        
        return self._UnitVectorX
        
    @property
    def UnitVectorY(self):    
        return self._UnitVectorY
    
    @UnitVectorY.getter
    def UnitVectorY(self):
        M = self.mag
        
        if (M == 0):
            self._UnitVectorY = 0
        else:
            self._UnitVectorY = self.Y / M
        
        return self._UnitVectorY

    @property
    def UnitVectorZ(self):    
        return self._UnitVectorZ
    
    @UnitVectorZ.getter
    def UnitVectorZ(self):
        M = self.mag
        
        if (M == 0):
            self._UnitVectorZ = 0
        else:
            self._UnitVectorZ = self.Z / M
        
        return self._UnitVectorZ

    '''
        Internal Functions
    '''        
    def atan(self, X, Y):
        if (X > 0):
            if (Y > 0):
                atan = math.atan(Y / X)
            else:
                atan = 2 * Pi + math.atan(Y / X)
            
        elif (X < 0):
            atan = Pi + math.atan(Y / X)
            
        else:
            if (Y > 0):
                atan = Pi
            elif (Y < 0):
                atan = -Pi
            else:
                atan = 0
            
        return atan
    
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        test = Cartesian3D()
        test.X = 1.110233E-16
        test.Y = 1.110223E-16
        test.Z = -1.7182161040748
        print(test.dec)
        print(test.inc)
        
    except Exception as e:
        print(e)
    
    