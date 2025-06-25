'''
Created on Jun 12, 2025

@author: hd.nguyen
'''

class AdwinAfOutputParameters():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Total_Output_Points = 0
        self.Total_Monitor_Points = 0
        self.Ramp_Up_Last_Point = 0
        self.Ramp_Down_First_Point = 0
        self.Measured_Peak_Monitor_Voltage = 0
        self.Max_Ramp_Voltage_Used = 0
        self.Actual_Slope_Down_Used = 0
        self.Time_Step_Between_Points = 0
        self.Number_Points_Per_Period = 0
        self.Coil = 'Unknown'
        
    '''
    '''
    def GetTotalRampDuration(self):
        if (self.Time_Step_Between_Points < 0):
            return 0
            
        num_points = self.Total_Monitor_Points
        if (num_points < 0):
            num_points = 0
            
        return num_points*self.Time_Step_Between_Points
        

'''
   ---------------------------------------------------------------------     
'''
class AdwinAfInputParameters():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Coil = 'Unknown'
        self.Slope_Up = 0.0
        self.Slope_Down = 0.0
        self.Peak_Monitor_Voltage = 0.0
        self.Resonance_Freq = 0.0
        self.Peak_Ramp_Voltage = 0.0
        self.Max_Ramp_Voltage = 0.0
        self.Max_Monitor_Voltage = 0.0
        
        self.ramp_mode = 0
        self.Output_Port_Number = 0
        self.Monitor_Port_Number = 0
        self.Process_Delay = 0
        self.Noise_Level = 0
        self.Number_Periods_Hang_At_Peak = 0
        self.Number_Periods_Ramp_Down = 0
        self.ramp_down_mode = 0
        
'''
   ---------------------------------------------------------------------     
'''
class AdwinAfRampStatus():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.WasSuccessful = True
        
        