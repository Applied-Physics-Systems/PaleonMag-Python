'''
Created on Nov 14, 2025

@author: hd.nguyen
'''
import math

Pi = 3.141592653589
rad = (Pi / 180)
deg = (180 / Pi)

class Angular3D():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.dec = 0.0
        self.inc = 0.0
        self.mag = 0.0
        
        self._X = 0.0
        self._Y = 0.0
        self._Z = 0.0
        
    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def X(self):    
        return self._X
    
    @X.getter
    def X(self):
        p = math.cos(self.inc * rad)
        self._X = self.mag * p * math.cos(self.dec * rad)        
        return self._X
        
    @property
    def Y(self):    
        return self._Y
    
    @Y.getter
    def Y(self):
        p = math.cos(self.inc * rad)
        self._Y = self.mag * p * math.sin(self.dec * rad)        
        return self._Y

    @property
    def Z(self):    
        return self._Z
    
    @Z.getter
    def Z(self):
        self._Z = self.mag * math.sin(self.inc * rad)
        return self._Z
    
    
        