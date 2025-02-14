'''
Created on Nov 8, 2024

@author: hungd
'''
from Process.ProcessData import ProcessData

CHANNEL = {'CH0': 0,
           'CH1': 1,
           'CH2': 2,
           'CH3': 3,
           'CH4': 4,
           'CH5': 5,
           'CH6': 6,
           'CH7': 7}

class Channel():
    ChanName = ''
    ChanNum = 0
    ChanType = ''
     
    def __init__(self, chanName, chanNum, chanType):
        self.ChanName = chanName
        self.ChanNum = chanNum
        self.ChanType = chanType

class ModConfig():
    '''
    classdocs
    '''
    lastPositionRead = ''
    targetPosition = ''
    velocity = ''
    SampleHeight = 0.0
    xPos = '0'
    yPos = '0'
    turningAngle = '0'
    
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
    '''
    def retrieveChannel(self, dataStr):
        dataList = dataStr.split('-')
        
        chanName = dataStr  
        chanNum = CHANNEL[dataList[2]]
        chanType = dataList[0] 
        
        channel = Channel(chanName, chanNum, chanType)
        
        return channel
        
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
        self.TurningMotorFullRotation = self.getConfig_Int(config, 'SteppingMotor', 'TurningMotorFullRotation', 2000)
        self.TurningMotor1rps = self.getConfig_Int(config, 'SteppingMotor', 'TurningMotor1rps', 16000000)
        self.TurnerSpeed = self.getConfig_Int(config, 'SteppingMotor', 'TurnerSpeed', 2000000)
        self.PickupTorqueThrottle = self.getConfig_Float(config, 'SteppingMotor', 'PickupTorqueThrottle', 0.4)
        self.SampleHoleAlignmentOffset = self.getConfig_Float(config, 'SteppingMotor', 'SampleHoleAlignmentOffset', -0.02)

        self.UseXYTableAPS = self.getConfig_Bool(config, 'XYTable', 'UseXYTableAPS', False)        

        self.DoVacuumReset = self.getConfig_Bool(config, 'Vacuum', 'DoVacuumReset', False)

        self.EnableARM = self.getConfig_Bool(config, 'Modules', 'EnableARM', False)
        self.EnableAxialIRM = self.getConfig_Bool(config, 'Modules', 'EnableAxialIRM', False)
        
        self.AFUnits = config['AF']['AFUnits']
        self.AxialRampUpVoltsPerSec = self.getConfig_Float(config, 'AF', 'AxialRampUpVoltsPerSec', 3.3)
        self.TransRampUpVoltsPerSec = self.getConfig_Float(config, 'AF', 'TransRampUpVoltsPerSec', 3.3)
        self.MinRampUpTime_ms = self.getConfig_Int(config, 'AF', 'MinRampUpTime_ms', 500)
        self.MaxRampUpTime_ms = self.getConfig_Int(config, 'AF', 'MaxRampUpTime_ms', 1500)
        self.RampDownNumPeriodsPerVolt = self.getConfig_Int(config, 'AF', 'RampDownNumPeriodsPerVolt', 200)
        self.MinRampDown_NumPeriods = self.getConfig_Int(config, 'AF', 'MinRampDown_NumPeriods', 500)
        self.MaxRampDown_NumPeriods = self.getConfig_Int(config, 'AF', 'MaxRampDown_NumPeriods', 5000)
        
        self.DegausserToggle = self.retrieveChannel(config['Channels']['DegausserToggle'])
        self.MotorToggle = self.retrieveChannel(config['Channels']['MotorToggle'])
        self.VacuumToggleA = self.retrieveChannel(config['Channels']['VacuumToggleA'])        
        
        self.EnableVacuum = self.getConfig_Bool(config, 'Modules', 'EnableVacuum', False)
        self.EnableDegausserCooler = self.getConfig_Bool(config, 'Modules', 'EnableDegausserCooler', False)
        
        self.IRMSystem = config['IRMPulse']['IRMSystem']        
        self.ApsIrm_DoRangeChange = self.getConfig_Bool(config, 'IRMPulse', 'ApsIrm_DoRangeChange', False)
        self.ApsIrm_RangeChangeLevel = self.getConfig_Int(config, 'IRMPulse', 'ApsIrm_RangeChangeLevel', 10000)   
        
        self.PulseAxialMax = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMax', 13080)
        self.PulseAxialMin = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMin', 50)
       
        self.MotorIDUpDown = config['MotorPrograms']['MotorIDUpDown']
        self.MotorIDChangerX = config['MotorPrograms']['MotorIDChanger']
        self.MotorIDChangerY = config['MotorPrograms']['MotorIDChangerY']
        self.MotorIDTurning = config['MotorPrograms']['MotorIDTurning']        

        self.AfAxialResFreq = self.getConfig_Float(config, 'AFAxial', 'AFAxialResFreq', 360)
        self.AfAxialRampMax = self.getConfig_Float(config, 'AFAxial', 'AFAxialRampMax', 5.5) 
        self.AfAxialMonMax = self.getConfig_Float(config, 'AFAxial', 'AFAxialMonMax', 5.5)
        
        self.AfTransResFreq = self.getConfig_Float(config, 'AFTrans', 'AFTransResFreq', 327)
        self.AfTransRampMax = self.getConfig_Float(config, 'AFTrans', 'AFTransRampMax', 5.3)
        self.AfTransMonMax = self.getConfig_Float(config, 'AFTrans', 'AFTransMonMax', 5.3)

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
    '''
    def parseMotorData(self, label, dataStr):
        if 'xPos' in label:
            self.xPos = dataStr
        elif 'yPos' in label:
            self.yPos = dataStr
        elif 'TurningAngle' in label:
            self.turningAngle = dataStr
                    
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
    def updateXYTablePositions(self, pos, axis, value):
        if (axis == 0):
            xyTableStr = 'XY' + str(pos) + 'X'
        elif (axis == 1):
            xyTableStr = 'XY' + str(pos) + 'Y'
        else:
            xyTableStr = 'XYHomeX'
        
        self.processData.config['XYTable'][xyTableStr] = str(value)        
        return
    
    '''
    '''
    def convertHoletoPosX(self, hole):
        posCount = self.XYTablePositions(hole, 0)
        return posCount

    '''
    '''
    def convertHoletoPosY(self, hole):
        posCount = self.XYTablePositions(hole, 1)
        return posCount


                    
        
    
            