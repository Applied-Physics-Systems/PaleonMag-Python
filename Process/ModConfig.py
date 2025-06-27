'''
Created on Nov 8, 2024

@author: hungd
'''
import numpy as np
from Process.ProcessData import ProcessData

'''
    ---------------------------------------------------------------------------------------
'''
class Channel():
    ChanName = ''
    ChanNum = 0
    ChanType = ''
     
    def __init__(self, chanName, chanNum, chanType):
        self.ChanName = chanName
        self.ChanNum = chanNum
        self.ChanType = chanType

'''
    ---------------------------------------------------------------------------------------
'''
class WaveForm():
    def __init__(self):
        self.WaveININum = 0
        self.BoardUsed = 'ADWIN-light-16,1'
        self.Chan = 'AO-1-CH0'
        self.Channel = None 
        self.WaveName = ''
        self.StartPoint = 0
        self.MemAlloc = False
        self.DoDeallocate = False
        self.IO = 'OUTPUT'
        self.IORate = 50000
        self.RangeMax = 10
        self.RangeMin = -10
        self.Slope = 2.292696
        
        self.PeakVoltage = 0
        self.SineFreqMin = 0
        self.TimeStep = 0
        

'''
    ---------------------------------------------------------------------------------------
'''
class ModConfig():
    '''
    classdocs
    '''
    AxialCoilSystem = -1
    TransverseCoilSystem = 1
    IRMAxialCoilSystem = 2 
    NoCoilSystem = 0
    
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
        self.waveForms = {}
        if (process != None):
            self.processData = process        
            self.parseConfig(self.processData.config)
        elif (config != None):
            self.parseConfig(config)
            
        self.queue = queue
        
    '''
    '''
    def retrieveChannel(self, dataStr, config):
        dataList = dataStr.split('-')
        
        chanStr = config['Boards'][dataStr]
        paramList = chanStr.split(',') 
        chanTypeStr = dataList[0]
        
        channel = 0
        if 'AO' in chanTypeStr:
            channel = int(paramList[1])
            
        elif 'AI' in chanTypeStr:
            channel = int(paramList[1])
            
        elif 'DO' in chanTypeStr:
            channel = int(paramList[1])
            
        elif 'DI' in chanTypeStr:
            channel = int(paramList[1])     
                
        return Channel(paramList[0], channel, chanTypeStr)
        
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

    def getParam_Float(self, valueStr):
        try:
            if (valueStr == ''):
                value = 0.0
            else:
                value = float(valueStr)
            
        except:
            value = 0.0
            
        return value

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
    '''
    def getConfig_Array(self, config, section, label, rows):
        dataArray = np.zeros((rows, 2))
        for i in range(1, rows):
            dataArray[i, 0] = self.getConfig_Float(config, section, label + 'X' + str(i), 0.0) 
            dataArray[i, 1] = self.getConfig_Float(config, section, label + 'Y' + str(i), 0.0)
        
        return dataArray
    
    '''
    '''
    def getCoilSystem(self, coilLabel):
        AFCoilSystem = self.AxialCoilSystem
        if (coilLabel == 'Axial'):          
            AFCoilSystem = self.AxialCoilSystem
        elif (coilLabel == 'Transverse'):
            AFCoilSystem = self.TransverseCoilSystem
        elif (coilLabel == 'IRM Axial'):
            AFCoilSystem = self.IRMAxialCoilSystem
                                                    
        return AFCoilSystem
        
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
        self.EnableAF = self.getConfig_Bool(config, 'Modules', 'EnableAF', False)
        self.EnableAFAnalysis = self.getConfig_Bool(config, 'Modules', 'EnableAFAnalysis', False)
        self.EnableAxialIRM = self.getConfig_Bool(config, 'Modules', 'EnableAxialIRM', False)
        
        self.AFUnits = config['AF']['AFUnits'].strip()
        self.AFSystem = config['AF']['AFSystem'].strip()
        self.AxialRampUpVoltsPerSec = self.getConfig_Float(config, 'AF', 'AxialRampUpVoltsPerSec', 3.3)
        self.TransRampUpVoltsPerSec = self.getConfig_Float(config, 'AF', 'TransRampUpVoltsPerSec', 3.3)
        self.TSlope = self.getConfig_Float(config, 'AF', 'TSlope', 53.588)
        self.Toffset = self.getConfig_Float(config, 'AF', 'Toffset', 260.62)
        self.Thot = self.getConfig_Float(config, 'AF', 'Thot', 40.0)
        self.MinRampUpTime_ms = self.getConfig_Int(config, 'AF', 'MinRampUpTime_ms', 500)
        self.MaxRampUpTime_ms = self.getConfig_Int(config, 'AF', 'MaxRampUpTime_ms', 1500)
        self.RampDownNumPeriodsPerVolt = self.getConfig_Int(config, 'AF', 'RampDownNumPeriodsPerVolt', 200)
        self.MinRampDown_NumPeriods = self.getConfig_Int(config, 'AF', 'MinRampDown_NumPeriods', 500)
        self.MaxRampDown_NumPeriods = self.getConfig_Int(config, 'AF', 'MaxRampDown_NumPeriods', 5000)
        self.HoldAtPeakField_NumPeriods = self.getConfig_Int(config, 'AF', 'HoldAtPeakField_NumPeriods', 300)
        self.AFRelays_UseUpPosition = self.getConfig_Bool(config, 'AF', 'AFRelays_UseUpPosition', False)
        
        self.DegausserToggle = self.retrieveChannel(config['Channels']['DegausserToggle'], config)
        self.MotorToggle = self.retrieveChannel(config['Channels']['MotorToggle'], config)
        self.VacuumToggleA = self.retrieveChannel(config['Channels']['VacuumToggleA'], config)  
        self.AFAxialRelay = self.retrieveChannel(config['Channels']['AFAxialRelay'], config)       
        self.AFTransRelay = self.retrieveChannel(config['Channels']['AFTransRelay'], config)
        self.IRMRelay = self.retrieveChannel(config['Channels']['IRMRelay'], config)
        self.AnalogT1 = self.retrieveChannel(config['Channels']['AnalogT1'], config)
        self.AnalogT2 = self.retrieveChannel(config['Channels']['AnalogT2'], config)
        
        self.EnableVacuum = self.getConfig_Bool(config, 'Modules', 'EnableVacuum', False)
        self.EnableDegausserCooler = self.getConfig_Bool(config, 'Modules', 'EnableDegausserCooler', False)
        self.EnableT1 = self.getConfig_Bool(config, 'Modules', 'EnableT1', False)
        self.EnableT2 = self.getConfig_Bool(config, 'Modules', 'EnableT2', False)
        
        self.IRMSystem = config['IRMPulse']['IRMSystem']        
        self.ApsIrm_DoRangeChange = self.getConfig_Bool(config, 'IRMPulse', 'ApsIrm_DoRangeChange', False)
        self.ApsIrm_RangeChangeLevel = self.getConfig_Int(config, 'IRMPulse', 'ApsIrm_RangeChangeLevel', 10000)   
        
        self.PulseAxialMax = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMax', 13080)
        self.PulseAxialMin = self.getConfig_Int(config, 'IRMAxial', 'PulseAxialMin', 50)
       
        self.MotorIDUpDown = config['MotorPrograms']['MotorIDUpDown']
        self.MotorIDChangerX = config['MotorPrograms']['MotorIDChanger']
        self.MotorIDChangerY = config['MotorPrograms']['MotorIDChangerY']
        self.MotorIDTurning = config['MotorPrograms']['MotorIDTurning']        

        self.AfAxialMax = self.getConfig_Int(config, 'AFAxial', 'AfAxialMax', 2900)
        self.AfAxialMin = self.getConfig_Int(config, 'AFAxial', 'AFAxialMin', 10)
        self.AFAxialCount = self.getConfig_Int(config, 'AFAxial', 'AFAxialCount', 40)
        self.AfAxialResFreq = self.getConfig_Float(config, 'AFAxial', 'AFAxialResFreq', 360)
        self.AfAxialRampMax = self.getConfig_Float(config, 'AFAxial', 'AFAxialRampMax', 5.5) 
        self.AfAxialMonMax = self.getConfig_Float(config, 'AFAxial', 'AFAxialMonMax', 5.5)
        self.AFAxialCalDone = self.getConfig_Bool(config, 'AFAxial', 'AFAxialCalDone', False)
        self.AFAxial = self.getConfig_Array(config, 'AFAxial', 'AFAxial', self.AFAxialCount+1)
        
        self.AfTransMax = self.getConfig_Int(config, 'AFTrans', 'AFTransMax', 850)
        self.AfTransMin = self.getConfig_Int(config, 'AFTrans', 'AFTransMin', 10)
        self.AfTransCount = self.getConfig_Int(config, 'AFTrans', 'AFTransCount', 41)
        self.AfTransResFreq = self.getConfig_Float(config, 'AFTrans', 'AFTransResFreq', 327)
        self.AfTransRampMax = self.getConfig_Float(config, 'AFTrans', 'AFTransRampMax', 5.3)
        self.AfTransMonMax = self.getConfig_Float(config, 'AFTrans', 'AFTransMonMax', 5.3)
        self.AfTransCalDone = self.getConfig_Bool(config, 'AFTrans', 'AFTransCalDone', False)
        self.AfTrans = self.getConfig_Array(config, 'AFTrans', 'AFTrans', self.AfTransCount+1)
        
        self.AfRampDataPath = config['AFFileSave']['ADWINDataFileSaveBackupDir'].strip() 
        
        self.waveForms = self.getWaveForms(config)
        return

    '''
    '''
    def getWaveForms(self, config):
        waveForms = {}
        
        try:
            count = int(config['WaveForms']['WaveFormCount'])
            for index in range(0, count):
                waveForm = WaveForm()
                waveForm.WaveININum = self.getConfig_Int(config, 'WaveForms', 'WaveININum' + str(index), 0)
                waveForm.BoardUsed = config['WaveForms']['BoardUsed' + str(index)]
                waveForm.Chan = config['WaveForms']['Chan' + str(index)]
                waveForm.Channel = self.retrieveChannel(waveForm.Chan, config) 
                waveForm.WaveName = config['WaveForms']['WaveName' + str(index)]
                waveForm.StartPoint = self.getConfig_Int(config, 'WaveForms', 'StartPoint' + str(index), 0)
                waveForm.MemAlloc = self.getConfig_Bool(config, 'WaveForms', 'MemAlloc', False)
                waveForm.DoDeallocate = self.getConfig_Bool(config, 'WaveForms', 'DoDeallocate', False)
                waveForm.IO = config['WaveForms']['IO' + str(index)]
                waveForm.IORate = self.getConfig_Int(config, 'WaveForms', 'IORate' + str(index), 50000)
                waveForm.RangeMax = self.getConfig_Int(config, 'WaveForms', 'RangeMax' + str(index), 10)
                waveForm.RangeMin = self.getConfig_Int(config, 'WaveForms', 'RangeMin' + str(index), -10)
                waveForm.Slope = self.getConfig_Float(config, 'WaveForms', 'Slope', 2.292696)
                waveForms[waveForm.WaveName] = waveForm
            
            return waveForms
        
        except:
            return waveForms         

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


                    
        
    
            