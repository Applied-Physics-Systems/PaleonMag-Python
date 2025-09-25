'''
Created on Sep 24, 2025

@author: hd.nguyen
'''

commandMeasure = "Meas"
commandInitUp = "InitUp"
commandHolder = "Holder"
commandFlip = "Flip"
commandFin = "Fin"
commandGoto = "Goto"

class SampleCommand():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Key = ''
        self.commandType = ''
        self.FileID = ''
        self.Sample = ''
        self.Hole = ''

'''
    -----------------------------------------------------------------------------------
'''
class SampleCommands():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Item = []
        
    '''
    '''
    def Clear(self):
        self.Item = []
        return
        
        
