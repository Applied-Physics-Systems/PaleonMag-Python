'''
Created on Jul 7, 2025

@author: hd.nguyen
'''

class GaussMeterControl():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.connectFlag = False
        
    '''--------------------------------------------------------------------------------------------
                        
                        Vacuum Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Disconnect(self):
        # TODO
        
        self.connectFlag = False
        return
       
    '''
    '''
    def cmdResetPeak_Click(self):
        print('TODO: GaussMeterControl.cmdResetPeak_Click')
        
        '''
        'Call gm0 shell function
        mod908AGaussmeter.resetpeak
        
        'Wait for new data
        mod908AGaussmeter.waitfordata mod908AGaussmeter.handle
        
        'Get new data
        mod908AGaussmeter.datacallback mod908AGaussmeter.handle
        
        Me.newdata
        '''
        return

    