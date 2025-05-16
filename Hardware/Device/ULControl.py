'''
Created on Mar 25, 2025

@author: hd.nguyen
'''
import UniversalLibrary as UL

BoardNum = 0
Gain = UL.BIP5VOLTS
Chan = 0

class ULControl():
    '''
    classdocs
    '''


    def __init__(self, parent=None, modConfig=None):
        '''
        Constructor
        '''
        self.parent = parent
        self.modConfig = modConfig
        
    '''
    '''
    def testUL(self):
        DataValue = UL.cbAIn(BoardNum, Chan, Gain)
        EngUnits = UL.cbToEngUnits(BoardNum, Gain, DataValue)
        print(EngUnits)
        return
    
    '''
    '''
    def runTask(self, taskID):
        if (taskID == 0):
            self.testUL()
    
#===================================================================================================
# Main Module
#---------------------------------------------------------------------------------------------------
if __name__=='__main__':
    try:    
        devControl = ULControl()
        devControl.runTask(0)
        
        print('Done !!!')
        
    except Exception as e:
        print('Error!! ' + str(e))
    
        