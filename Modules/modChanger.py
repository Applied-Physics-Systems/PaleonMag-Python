'''
Created on Nov 12, 2024

@author: hd.nguyen
'''
import time

class ModChanger():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.modConfig = self.parent.modConfig
        self.curpos = 0

    '''--------------------------------------------------------------------------------------------
                        
                        Internal Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def GetCurrentChangerPos(self):
        if self.parent.currentPosInitialized:
            return
        
        rangeStr = str(self.parent.modConfig.SlotMin) + "-" + str(self.parent.modConfig.SlotMax)
        curHole = self.parent.motors.ChangerHole()
        
        if self.parent.modConfig.UseXYTableAPS:
            message = "Which XY cup is current under the quartz glass holder?;"
        else:
            message = "Which sample slot is now under "
            message += "the quartz glass holder " + rangeStr + "?;"
            
        message += "CAREFUL - A wrong answer "
        message += "here could BREAK THE SYSTEM!" 
        title =  "Important!"
        inputValue = curHole
        minValue = self.parent.modConfig.SlotMin
        maxValue =self.parent.modConfig.SlotMax
        newpos = self.parent.displayInputForm(message, title, inputValue, minValue, maxValue)

        self.parent.motors.SetChangerHole(int(newpos))
        self.parent.currentPosInitialized = True
        return
        
    '''
    '''
    def Find_NearestChangerHole(self):
        # If current position unknown, query user.
        self.GetCurrentChangerPos()
        
        lastPos = self.parent.motors.ChangerHole()
        self.curpos = lastPos
        
        if not self.parent.modConfig.UseXYTableAPS:
            #Using Chain Drive
            # Check for case where current position = nearest hole
            if self.isHole(self.curpos):
                return self.curpos
            
            # Find nearest hole by brute force.  I is the nearest hole above, K below
            i = self.curpos
            while not self.isHole(i):
                i = i + 1
                if (i > self.parent.modConfig.SlotMax):
                    i = i - self.parent.modConfig.SlotMax            
            
            k = self.curpos
            while not self.isHole(k):
                k = k - 1
                if (k < self.parent.modConfig.SlotMin):
                    k = k + self.parent.modConfig.SlotMax
            
          
            # Must worry about crossing the SLOTMAX barrier.
            upper = i - self.curpos
            if (upper < 0):
                upper = upper + self.parent.modConfig.SlotMax
            lower = self.curpos - k
            if (lower < 0):
                lower = lower + self.parent.modConfig.SlotMax
        
            if (upper <= lower):
                # Closest hole is a higher number:  Move it to the nearest hole!
                Find_NearestChangerHole = i
            else:
                Find_NearestChangerHole = k
            
        else:
            # Using XY Table            
            Find_NearestChangerHole = self.parent.modConfig.HoleSlotNum
        
        return Find_NearestChangerHole  
    
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        This function determines whether the slot at num is a
        valid slot.  It must be between SLOTMIN and SLOTMAX.
    '''
    def isValidStart(self, num):
        status = False
        
        try:
            if ((int(num) >= self.modConfig.SlotMin) and (int(num) <= self.modConfig.SlotMax)):
                status = True
        except:
            status = False
        
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
    
    '''
        This procedure moves the changer from the current position
        to the position specified.
    '''
    def Changer_MoveTo(self, target):
        self.parent.motors.ChangerMotortoHole(target)
        self.curpos = self.parent.motors.ChangerHole()           # Current position is changed
        return 
    
    '''
        This routine determines the location of the hole nearest to that
        of the present sample changer location, curPos, and moves the holder
        to it.  The last position moved from is stored in lastPos.
    '''
    def Changer_NearestHole(self):
        nearest_hole_pos = self.Find_NearestChangerHole()
        
        if (nearest_hole_pos == self.curpos):
            return
        
        self.Changer_MoveTo(nearest_hole_pos)
        return
    
    