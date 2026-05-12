'''
Created on Feb 25, 2026

@author: hd.nguyen
'''

class modProg():
    '''
    classdocs
    '''
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
        Now select the proper format for printing out this range
        information based on the TESTIT variable
    '''
    @classmethod
    def FormatNumber(cls, testit):
        if ((testit >= 1000000) or (testit <= -100000)):
            frmt = str(int(testit))  
        elif ((testit >= 100000) or (testit <= -10000)):
            frmt = '{:.1f}'.format(testit)
        elif ((testit >= 10000) or (testit <= -1000)):
            frmt = '{:.2f}'.format(testit)
        elif ((testit >= 1000) or (testit <= -100)):
            frmt = '{:.3f}'.format(testit)
        elif ((testit >= 100) or (testit <= -10)):
            frmt = '{:.4f}'.format(testit)
        elif ((testit >= 10) or (testit <= -1)):
            frmt = '{:.5f}'.format(testit)
        else:
            frmt = '{:.5f}'.format(testit)
        
        return frmt 
    
    '''
    '''
    @classmethod
    def getInt(cls, valueStr):
        try:
            valueInt = int(valueStr)
        except:
            valueInt = 0
            
        return valueInt

    '''
    '''
    @classmethod
    def getFloat(cls, valueStr):
        try:
            valueFloat = float(valueStr)
        except:
            valueFloat = 0.0
            
        return valueFloat

    '''
    '''
    @classmethod
    def getBool(cls, valueStr):
        if 'True' in valueStr:
            valueBool = True
        else:
            valueBool = False
            
        return valueBool

    '''
        Extract string from the request position on the left
    '''
    @classmethod
    def Left(cls, inStr, pos):
        outStr = inStr[:pos]
        return outStr 
    
    '''
        Extract string from the request position on the right
    '''
    @classmethod
    def Right(cls, inStr, pos):
        outStr = inStr[pos:]
        return outStr 

    '''
        Extract string from the request position in the middle
    '''
    @classmethod
    def Mid(cls, inStr, startPos, length):
        outStr = inStr[startPos:startPos+length]
        return outStr    
    