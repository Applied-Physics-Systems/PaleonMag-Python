'''
Created on Nov 12, 2024

@author: hd.nguyen
'''

class ModChanger():
    '''
    classdocs
    '''


    def __init__(self, modConfig):
        '''
        Constructor
        '''
        self.modConfig = modConfig
        
    '''
        This function determines whether the slot at num is a
        valid slot.  It must be between SLOTMIN and SLOTMAX.
    '''
    def isValidStart(self, num):
        status = False
        if ((int(num) >= self.modConfig.SlotMin) and (int(num) <= self.modConfig.SlotMax)):
            status = True
        
        return status
        
    '''
        This function returns true if 'num' identifies any hole in the
        sample changer.
    '''
    def isHole(self, num):
        Changer_isHole = False
        if self.modConfig.UseXYTableAPS:
            if (num == self.modConfig.HoleSlotNum):
                Changer_isHole = True
            else:
                Changer_isHole = False
        else:
            if ((num % self.modConfig.HoleSlotNum) == 0):
                Changer_isHole = True
            else:
                Changer_isHole = False

        return Changer_isHole
    