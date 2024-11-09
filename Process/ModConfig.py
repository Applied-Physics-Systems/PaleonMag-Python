'''
Created on Nov 8, 2024

@author: hungd
'''
from Process.ProcessData import ProcessData

class ModConfig():
    '''
    classdocs
    '''
    processData = ProcessData()

    def __init__(self, process=None, config=None, queue=None):
        '''
        Constructor
        '''
        
        if (process != None):
            self.processData = process        
            self.parseConfig(self.processData.config)
        elif (config != None):
            self.processData.config = config 
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
        self.NoCommMode = self.getConfig_Bool(config, 'Program', 'NoCommMode', False)
        
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

            
            