'''
Created on Nov 8, 2024

@author: hungd
'''
from Process.ProcessData import ProcessData

class ModConfig():
    '''
    classdocs
    '''
    lastPositionRead = ''
    targetPosition = ''
    velocity = ''
    SampleHeight = 0.0
    
    processData = ProcessData()

    def __init__(self, process=None, config=None, queue=None):
        '''
        Constructor
        '''
        
        if (process != None):
            self.processData = process        
            self.parseConfig(self.processData.config)
        elif (config != None):
            self.parseConfig(config)
            
        self.queue = queue
        
    '''
        Read an integer value from INI file
    '''
    def getConfig_Int(self, config, section, label, default):
        try:
            value = int(config[section][label])
            return value
        
        except:
            return default         

    '''
        Read an integer value from INI file
    '''
    def getConfig_Float(self, config, section, label, default):
        try:
            value = float(config[section][label])
            return value
        
        except:
            return default         

    '''
       Read boolean value from INI file
    '''
    def getConfig_Bool(self, config, section, label, default):
        try:
            value = False
            if ('True'.lower() == config[section][label].lower()):
                value = True
            return value 
        
        except:
            return default         
                
    '''
        Set parameters from INI file
    '''
    def parseConfig(self, config):
        self.processData.config = config
        self.NoCommMode = self.getConfig_Bool(config, 'Program', 'NoCommMode', False)

        self.SlotMin = self.getConfig_Int(config, 'SampleChanger', 'SlotMin', 1)
        self.SlotMax = self.getConfig_Int(config, 'SampleChanger', 'SlotMax', 200)
        self.HoleSlotNum = self.getConfig_Int(config, 'SampleChanger', 'HoleSlotNum', 10)
        self.OneStep = self.getConfig_Float(config, 'SampleChanger', 'OneStep', -1010.1010101)

        self.DCMotorHomeToTop_StopOnTrue = self.getConfig_Bool(config, 'SteppingMotor', 'DCMotorHomeToTop_StopOnTrue', True)
        self.UpDownTorqueFactor = self.getConfig_Int(config, 'SteppingMotor', 'UpDownTorqueFactor', 40) 
        self.UpDownMaxTorque = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMaxTorque', 32000)   
        self.UpDownMotor1cm = self.getConfig_Int(config, 'SteppingMotor', 'UpDownMotor1cm', 10)    
        self.SampleBottom = self.getConfig_Int(config, 'SteppingMotor', 'SampleBottom', -2385)   
        self.SampleTop = self.getConfig_Int(config, 'SteppingMotor', 'SampleTop', -1979)
        self.LiftSpeedSlow = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedSlow', 4000000)    
        self.LiftSpeedNormal = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedNormal', 25000000)    
        self.LiftSpeedFast = self.getConfig_Int(config, 'SteppingMotor', 'LiftSpeedFast', 50000000)
        self.LiftAcceleration = self.getConfig_Int(config, 'SteppingMotor', 'LiftAcceleration', 90000)
        self.MeasPos = self.getConfig_Int(config, 'SteppingMotor', 'MeasPos', -30607)
        self.ChangerSpeed = self.getConfig_Int(config, 'SteppingMotor', 'ChangerSpeed', 31000)   
        self.SCurveFactor = self.getConfig_Int(config, 'SteppingMotor', 'SCurveFactor', 32767)
        self.SCoilPos = self.getConfig_Int(config, 'SteppingMotor', 'SCoilPos', -4202)
        self.AFPos = self.getConfig_Int(config, 'SteppingMotor', 'AFPos', -8405)
        self.ZeroPos = self.getConfig_Int(config, 'SteppingMotor', 'ZeroPos', -25886)
        self.PickupTorqueThrottle = self.getConfig_Float(config, 'SteppingMotor', 'PickupTorqueThrottle', 0.4)
        self.SampleHoleAlignmentOffset = self.getConfig_Float(config, 'SteppingMotor', 'SampleHoleAlignmentOffset', -0.02)

        self.UseXYTableAPS = self.getConfig_Bool(config, 'XYTable', 'UseXYTableAPS', False)        

        self.DoVacuumReset = self.getConfig_Bool(config, 'Vacuum', 'DoVacuumReset', False)

        self.EnableARM = self.getConfig_Bool(config, 'Modules', 'EnableARM', False)
        self.EnableAxialIRM = self.getConfig_Bool(config, 'Modules', 'EnableAxialIRM', False)
        
        self.AFUnits = config['AF']['AFUnits']
        
        self.IRMSystem = config['IRMPulse']['IRMSystem']        
        self.ApsIrm_DoRangeChange = self.getConfig_Bool(config, 'IRMPulse', 'ApsIrm_DoRangeChange', False)
        self.ApsIrm_RangeChangeLevel = self.getConfig_Int(config, 'IRMPulse', 'ApsIrm_RangeChangeLevel', 10000)   
        
        self.PulseAxialMax = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMax', 13080)
        self.PulseAxialMin = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMin', 50)
       
        self.MotorIDUpDown = config['MotorPrograms']['MotorIDUpDown']
        self.MotorIDChangerX = config['MotorPrograms']['MotorIDChanger']
        self.MotorIDChangerY = config['MotorPrograms']['MotorIDChangerY']
        self.MotorIDTurning = config['MotorPrograms']['MotorIDTurning']        

    '''
    '''
    def parseCommandExchange(self, exchangeStr):
        strList = exchangeStr.split(';')
        if (len(strList) == 3): 
            self.activeMotor = strList[0].strip()            
            self.outCommand = strList[1].strip()
            self.inResponse = strList[2].strip()
            
            if '@16 12 1' in self.outCommand:
                if (('UpDown' in self.activeMotor) or 
                    ('ChangerX' in self.activeMotor) or 
                    ('ChangerY' in self.activeMotor)):
                    
                    respList = self.inResponse.split()
                    if (len(respList) == 5):
                        upperWord = int(respList[3], 16)
                        lowerWord = int(respList[4], 16)
                        self.lastPositionRead = str(upperWord * 65536 + lowerWord)                     

    '''
    '''
    def parseMotorInfo(self, infoStr):
        strList = infoStr.split(';')
        
        for eachStr in strList:
            params = eachStr.strip().split()
            if (len(params) == 1):
                self.activeMotor = params[0]
            else:
                if 'Position' in params[0]:
                    self.targetPosition = params[1]
                elif 'Velocity' in params[0]:
                    self.velocity = params[1]
                    
    '''
        Get XY reading from XY Table
    '''
    def XYTablePositions(self, pos, axis):
        if (axis == 0):
            xyTableStr = 'XY' + str(pos) + 'X'
        elif (axis == 1):
            xyTableStr = 'XY' + str(pos) + 'Y'
        else:
            xyTableStr = 'XYHomeX'
        
        posCount = self.getConfig_Int(self.processData.config, 'XYTable', xyTableStr, 381830)
        
        return posCount

    '''
        update modConfig dictionarry
    '''
    def upDateXYTablePositions(self, pos, axis, value):
        if (axis == 0):
            xyTableStr = 'XY' + str(pos) + 'X'
        elif (axis == 1):
            xyTableStr = 'XY' + str(pos) + 'Y'
        else:
            xyTableStr = 'XYHomeX'
        
        self.processData.config['XYTable'][xyTableStr] = value        
        return
    
    '''
    '''
    def convertHoletoPosX(self, hole):
        self.XYTablePositions(hole, 0)

    '''
    '''
    def convertHoletoPosY(self, hole):
        self.XYTablePositions(hole, 1)
        


                    
        
    
            