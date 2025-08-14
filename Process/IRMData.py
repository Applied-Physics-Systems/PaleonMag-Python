'''
Created on Jul 16, 2025

@author: hd.nguyen
'''

dataPoint = {'deltaRate': 0,
            'readVoltage': 0,
            'timeStamp': 0}

class IrmDataPoint():
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.time_stamp = 0
        self.read_voltage = 0
        self.data_rate = 0

'''
    ---------------------------------------------------------------------------
'''
class IRMData():
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.mCol = []
        self.Count = 0
        self.num_total_points = 0 
        self.average_change_over_window = 0
        self.average_change_entire_charging_cycle = 0
        
        self.window_size = 20
        self.collection_size = 10 * self.window_size
        
        
    '''
    '''
    def Add(self, time, irm_read_voltage):
        irm_data_point = IrmDataPoint()
        irm_data_point.time_stamp = time
        irm_data_point.read_voltage = irm_read_voltage
        
        window_start = len(self.mCol) - self.window_size - 1
        
        if (len(self.mCol) > 1):            
            last_data_point = self.mCol[-1]
           
            delta_t = irm_data_point.time_stamp - last_data_point.time_stamp
            delta_v = irm_data_point.read_voltage - last_data_point.read_voltage
           
            if (delta_t != 0):                
                irm_data_point.delta_rate = delta_v / delta_t            
            else:            
                irm_data_point.delta_rate = 0
                        
        else:        
            irm_data_point.delta_rate = 0
                                                                                                                            
        self.average_change_entire_charging_cycle = self.average_change_entire_charging_cycle * self.num_total_points + \
                                                    irm_data_point.delta_rate
        
        self.average_change_entire_charging_cycle = self.average_change_entire_charging_cycle / (self.num_total_points + 1)
            
        
        if (window_start > 0):               
            window_start_point = self.mCol[window_start]                    
            self.average_change_over_window = self.average_change_over_window * self.window_size - \
                                              window_start_point.delta_rate + \
                                              irm_data_point.delta_rate                                                                                    
            self.average_change_over_window = self.average_change_over_window / self.window_size
        
        else:        
            self.average_change_over_window = self.average_change_entire_charging_cycle
                                
         
        self.mCol.append(irm_data_point)
        self.num_total_points = self.num_total_points + 1
        return
        