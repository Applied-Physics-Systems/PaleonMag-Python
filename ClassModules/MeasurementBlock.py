'''
Created on Nov 3, 2025

@author: hd.nguyen
'''
import math
import numpy as np

from ClassModules.Cartesian3D import Cartesian3D

class MeasurementBlock():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.Baselines = []
        for _ in range(0, 2):
            sample = Cartesian3D()
            self.Baselines.append(sample)
            
        self.Sample = []
        for _ in range(0, 4):
            sample = Cartesian3D()
            self.Sample.append(sample)            
            
        self.Holder = []
        for _ in range(0, 4):
            sample = Cartesian3D()
            self.Holder.append(sample)
                
        self._AverageMagnitude = 0.0        
        self.Direction = 1
        self.sKey = ''
                
        self._isUp = True
        self._HolderFVal = 0.0
        self._FischerSD = 0.0
        self._Kappa = 0.0
        self._Average = Cartesian3D()
        self._sum = Cartesian3D()
        self._sumSqs = Cartesian3D()
        self._SumUnitVectors = Cartesian3D()
        self._VectSumInd = Cartesian3D()
        self._induced = Cartesian3D()
        self._driftc = Cartesian3D()
        self._ResultantVector = Cartesian3D()

    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def Average(self):    
        return self._Average

    @Average.getter
    def Average(self):
        workingvector = self.Sum
        self._Average = Cartesian3D()
                
        self._Average.X = workingvector.X / 4
        self._Average.Y = workingvector.Y / 4
        self._Average.Z = workingvector.Z / 4        
        return self._Average            

    @property
    def AverageMagnitude(self):    
        return self._AverageMagnitude

    @AverageMagnitude.getter
    def AverageMagnitude(self):        
        workingvector = self.Average        
        self._AverageMagnitude = math.sqrt(workingvector.X ** 2 + workingvector.Y ** 2 + workingvector.Z ** 2)
                
        return self._AverageMagnitude
        
    @property
    def isUp(self):    
        return self._isUp
    
    @isUp.getter
    def isUp(self):
        return self._isUp
    
    @isUp.setter
    def isUp(self, value):
        self._isUp = value
        if value:
            self.Direction = 1
        else:
            self.Direction = -1            
        return
    
    @property
    def induced(self):    
        return self._induced
    
    @induced.getter
    def induced(self):
        self._induced = Cartesian3D()
        
        for i in range(0, 4):
            workingvector = self.BaselineAdjustedSample(i)
            self._induced.X += workingvector.X / 4
            self._induced.Y += workingvector.Y / 4
            if (i > 2):
                self._induced.Z -= workingvector.Z / 4
            else:
                self._induced.Z += workingvector.Z / 4
            
        return self._induced

    @property
    def driftc(self):    
        return self._induced
    
    @driftc.getter
    def driftc(self):
        self._driftc = Cartesian3D()                    
        self._driftc.X = self.Baselines[1].X - self.Baselines[0].X
        self._driftc.Y = self.Baselines[1].Y - self.Baselines[0].Y
        self._driftc.Z = self.Baselines[1].Z - self.Baselines[0].Z                    
        return self._driftc
        
    @property
    def HolderFVal(self):    
        return self._HolderFVal
    
    @HolderFVal.getter
    def HolderFVal(self):
        self._HolderFVal = self.AverageHolder().mag
        return self._HolderFVal
                
    @property
    def Sum(self):    
        return self._sum
    
    @Sum.getter
    def Sum(self):
        self._sum = Cartesian3D()
        
        for i in range(0, 4):
            workingvector = self.CorrectedSample(i)
            self._sum.X += workingvector.X
            self._sum.Y += workingvector.Y
            self._sum.Z += workingvector.Z

        return self._sum
        
    @property
    def SumSqs(self):    
        return self._sumSqs
    
    @SumSqs.getter
    def SumSqs(self):
        self._sumSqs = Cartesian3D()
        
        for i in range(0, 4):
            workingvector = self.CorrectedSample(i)
            self._sumSqs.X += workingvector.X ** 2
            self._sumSqs.Y += workingvector.Y ** 2
            self._sumSqs.Z += workingvector.Z ** 2
            
        return self._sumSqs

    @property
    def SumUnitVectors(self):    
        return self._SumUnitVectors
    
    @SumUnitVectors.getter
    def SumUnitVectors(self):
        self._SumUnitVectors = Cartesian3D()
                
        for i in range(0, 4):
            workingvector = self.CorrectedSample(i)
            self._SumUnitVectors.X += workingvector.UnitVectorX
            self._SumUnitVectors.Y += workingvector.UnitVectorY
            self._SumUnitVectors.Z += workingvector.UnitVectorZ
        
        return self._SumUnitVectors

    @property
    def FischerSD(self):    
        return self._FischerSD
    
    '''
        returns theta-63
        this is circular SD from Fischer distribution
    '''
    @FischerSD.getter
    def FischerSD(self):        
        self._FischerSD = 81 / math.sqrt(self.Kappa)
        return self._FischerSD 

    @property
    def Kappa(self):    
        return self._Kappa
    
    @Kappa.getter
    def Kappa(self):
        N = 4
        r = self.SumUnitVectors.mag
        if (N == r):
            self._Kappa = 0.000000001
        else:
            self._Kappa = (N - 1) / (N - r)
        
        return self._Kappa

    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def AverageHolder(self):
        averageHolder = Cartesian3D()
        
        for i in range(0, 4):
            workingvector = self.CorrectedHolder(i)
            averageHolder.X += workingvector.X / 4
            averageHolder.Y += workingvector.Y / 4
            averageHolder.Z += workingvector.Z / 4
            
        return averageHolder
    
    '''
        Returns sample as corrected for angle and baseline adjusted
    '''
    def CorrectedHolder(self, i):
        X = self.Holder[i].X
        Y = self.Holder[i].Y
        Z = self.Holder[i].Z
        
        correctedHolder = Cartesian3D()
        if (i == 0):
            correctedHolder.X = X
            correctedHolder.Y = -Y
            correctedHolder.Z = Z
        elif (i == 1):
            correctedHolder.X = Y
            correctedHolder.Y = X
            correctedHolder.Z = Z
        elif (i == 2):
            correctedHolder.X = -X
            correctedHolder.Y = Y
            correctedHolder.Z = Z
        elif (i == 3):
            correctedHolder.X = -Y
            correctedHolder.Y = -X
            correctedHolder.Z = Z
            
        return correctedHolder 
   

    '''
    '''
    def CorrectedSample(self, i):
        # returns sample as corrected for angle and baseline adjusted
                
        workingvector = self.BaselineAdjustedSample(i)
        correctedSample = Cartesian3D()
        X = workingvector.X
        Y = workingvector.Y
        Z = workingvector.Z
        
        if (i == 0):
            correctedSample.X = X
            correctedSample.Y = -Y * self.Direction
            correctedSample.Z = Z * self.Direction
            
        elif (i == 1):
            correctedSample.X = Y
            correctedSample.Y = X * self.Direction
            correctedSample.Z = Z * self.Direction
            
        elif (i == 2):
            correctedSample.X = -X
            correctedSample.Y = Y * self.Direction
            correctedSample.Z = Z * self.Direction
            
        elif (i == 3):
            correctedSample.X = -Y
            correctedSample.Y = -X * self.Direction
            correctedSample.Z = Z * self.Direction
            
        return correctedSample

    '''
    '''    
    def BaselineAdjustedSample(self, i):
        sample = Cartesian3D()
        if ((i < 0) or (i > 3)):
            return sample
        
        BaselineFactor = [1 - (1 +i) / 5, (1 + i) / 5]    
        X1 = -BaselineFactor[0] * self.Baselines[0].X
        X2 = -BaselineFactor[1] * self.Baselines[1].X 
        X = X1 + X2 - self.Holder[i].X
        sample.X = self.Sample[i].X +  X
        
        Y1 = -BaselineFactor[0] * self.Baselines[0].Y
        Y2 = -BaselineFactor[1] * self.Baselines[1].Y 
        Y = Y1 + Y2 - self.Holder[i].Y
        sample.Y = self.Sample[i].Y + Y
        
        Z1 = -BaselineFactor[0] * self.Baselines[0].Z
        Z2 = -BaselineFactor[1] * self.Baselines[1].Z 
        Z = Z1 + Z2 - self.Holder[i].Z
        sample.Z = self.Sample[i].Z + Z
        
        return sample
    
    '''
    '''
    def SetBaseline(self, i, measurement):
        self.Baselines[i] = measurement
        return
    
    '''
    '''
    def SetHolder(self, i, vData):
        self.Holder[i] = vData
        return   
    
    '''
    '''
    def SetSample(self, i, measurement):
        self.Sample[i] = measurement
        return
            
'''
    ---------------------------------------------------------------------------------------------------------------------------------
'''            
class MeasurementBlocks():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.Item = []
        
        self._Count = 0
        self._Moment = 0.0
        self._SigDrift = 0.0
        self._SigNoise = 0.0
        self._SigHolder = 0.0
        self._SigInduced = 0.0
        self._HolderFVal = 0.0
        self._Kappa = 0.0
        self._FischerSD = 0.0
        
        self._Count = None
        self._VectSum = Cartesian3D()
        self._VectAvg = Cartesian3D()
        self._VectSD = Cartesian3D()
        self._VectInd = Cartesian3D()
        self._AverageBlock = MeasurementBlock()
            
    '''--------------------------------------------------------------------------------------------
                        
                        properties
                        
    --------------------------------------------------------------------------------------------'''
    @property
    def Count(self):    
        return self._Count
    
    @Count.getter
    def Count(self):
        self._Count = len(self.Item)
        return self._Count

    @property
    def Last(self):    
        return self._Last
    
    @Last.getter
    def Last(self):
        if (len(self.Item) > 0):
            self._Last = self.Item[-1]
            return self._Last
        else:
            return None

    @property
    def AverageBlock(self):    
        return self._AverageBlock
    
    @AverageBlock.getter
    def AverageBlock(self):
        sumMeasurements = []
        self._AverageBlock = MeasurementBlock()
        
        for j in range(0, 4):
            sumMeasurements.append(Cartesian3D())        
        
        cnt = self.Count
        if (cnt == 0):
            return self._AverageBlock
         
        for i in range(0, cnt):
                for j in range(0, 4):
                    workingvector = self.Item[i].BaselineAdjustedSample(j)
                    sumMeasurements[j].X += workingvector.X
                    sumMeasurements[j].Y += workingvector.Y
                    sumMeasurements[j].Z += workingvector.Z
        
        for i in range(0, 4):
            sumMeasurements[i].X /= cnt
            sumMeasurements[i].Y /= cnt
            sumMeasurements[i].Z /= cnt
            self._AverageBlock.SetSample(i, sumMeasurements[i])
        
        return self._AverageBlock

    @property
    def VectSum(self):    
        return self._VectSum
    
    @VectSum.getter
    def VectSum(self):
        self._VectSum = Cartesian3D()
        
        cnt = self.Count
        if (cnt == 0): 
            return
        
        for i in range(0, cnt):
            self._VectSum.X += self.Item[i].Sum.X
            self._VectSum.Y += self.Item[i].Sum.Y
            self._VectSum.Z += self.Item[i].Sum.Z
                
        return self._VectSum

    @property
    def VectSumSqs(self):    
        return self._VectSumSqs
    
    @VectSumSqs.getter
    def VectSumSqs(self):
        self._VectSumSqs = Cartesian3D()
        
        cnt = self.Count
        if (cnt == 0): 
            return self._VectSumSqs 
        
        for i in range(0, cnt):
            self._VectSumSqs.X += self.Item[i].SumSqs.X
            self._VectSumSqs.Y += self.Item[i].SumSqs.Y
            self._VectSumSqs.Z += self.Item[i].SumSqs.Z
        
        return self._VectSumSqs

    @property
    def VectSumInd(self):    
        return self._VectSumInd
    
    @VectSumInd.getter
    def VectSumInd(self):
        self._VectSumInd = Cartesian3D()
        
        cnt = self.Count
        if (cnt == 0): 
            return self._VectSumInd
         
        #With VectSumInd
        for i in range(0, cnt):
            self._VectSumInd.X += self.Item[i].induced.X
            self._VectSumInd.Y += self.Item[i].induced.Y
            self._VectSumInd.Z += self.Item[i].induced.Z

        return self._VectSumInd

    @property
    def VectAvg(self):    
        return self._VectAvg
    
    @VectAvg.getter
    def VectAvg(self):        
        workingvector = self.VectSum
        self._VectAvg = Cartesian3D()
        
        cnt = self.Count * 4
        if (cnt == 0): 
            return self._VectAvg
        
        self._VectAvg.X = workingvector.X / cnt
        self._VectAvg.Y = workingvector.Y / cnt
        self._VectAvg.Z = workingvector.Z / cnt        
        
        return self._VectAvg

    @property
    def VectSD(self):    
        return self._VectSD
    
    '''
         the standard deviation around each X,Y, & Z components
    '''
    @VectSD.getter
    def VectSD(self):                
        self._VectSD = Cartesian3D()
        
        cnt = self.Count * 4
        if (cnt == 0):
            return self._VectSD
        
        sumsq = self.VectSumSqs
        Sum = self.VectSum
        
        self._VectSD.X = math.sqrt(abs((sumsq.X * cnt - Sum.X ** 2) / (cnt * (cnt - 1))))
        self._VectSD.Y = math.sqrt(abs((sumsq.Y * cnt - Sum.Y ** 2) / (cnt * (cnt - 1))))
        self._VectSD.Z = math.sqrt(abs((sumsq.Z * cnt - Sum.Z ** 2) / (cnt * (cnt - 1))))
        
        return self._VectSD

    @property
    def VectInd(self):    
        return self._VectInd
    
    @VectInd.getter
    def VectInd(self):        
        workingvector = self.VectSumInd
        self._VectInd = Cartesian3D()
        
        cnt = self.Count
        if (cnt == 0): 
            return self._VectInd 
        
        self._VectInd.X = workingvector.X / cnt
        self._VectInd.Y = workingvector.Y / cnt
        self._VectInd.Z = workingvector.Z / cnt

        return self._VectInd
    
    @property
    def Moment(self):
        return self._Moment

    @Moment.getter
    def Moment(self):
        self._Moment = self.VectAvg.mag * self.parent.modConfig.RangeFact
        return self._Moment

    @property
    def HolderFVal(self):
        return self._HolderFVal

    @HolderFVal.getter
    def HolderFVal(self):
        cnt = self.Count
        if (cnt == 0): 
            return
        
        for i in range(0, cnt):
            self._HolderFVal += self.Item[i].HolderFVal / cnt
        
        return self._HolderFVal

    @property
    def SigDrift(self):
        return self._SigDrift
    
    @SigDrift.getter
    def SigDrift(self):        
        DriftMag = 0.0
        cnt = self.Count
        if (cnt > 0):
            for i in range(0, cnt):
                DriftMag += self.Item[i].driftc.mag / cnt
                    
        if (DriftMag == 0): 
            DriftMag = 0.000000001
            
        self._SigDrift = self.VectAvg.mag / DriftMag
        return self._SigDrift
    
    @property
    def SigNoise(self):
        return self._SigNoise
    
    @SigNoise.getter
    def SigNoise(self):
        noise = self.VectSD.mag
        if (noise == 0):
            noise = 0.000000001
        self._SigNoise = self.VectAvg.mag / noise
        return self._SigNoise

    @property
    def SigHolder(self):
        return self._SigHolder
    
    @SigHolder.getter
    def SigHolder(self):
        HolderMag = self.HolderFVal
        if (HolderMag == 0): 
            HolderMag = 0.000000001
        self._SigHolder = self.VectAvg.mag / HolderMag
        return self._SigHolder

    @property
    def SigInduced(self):
        return self._SigInduced
    
    @SigInduced.getter
    def SigInduced(self):
        induced = self.VectInd.mag
        if (induced == 0): 
            induced = 0.000000001
        self._SigInduced = self.VectAvg.mag / induced
        return self._SigInduced

    @property
    def FischerSD(self):
        return self._FischerSD
    
    '''
        returns theta-63
        this is circular SD from Fischer distribution
    '''
    @FischerSD.getter
    def FischerSD(self):        
        self._FischerSD = 81 / math.sqrt(self.Kappa)        
        return self._FischerSD
    
    @property
    def ResultantVector(self):
        return self._ResultantVector
    
    @ResultantVector.getter
    def ResultantVector(self):
        self._ResultantVector = Cartesian3D()
        
        cnt = self.Count
        if (cnt == 0):
            return self._ResultantVector 
        
        for i in range(0, cnt):
            workingvector = self.Item[i].SumUnitVectors
            self._ResultantVector.X += workingvector.X
            self._ResultantVector.Y += workingvector.Y
            self._ResultantVector.Z += workingvector.Z

        return self._ResultantVector

    @property
    def Kappa(self):
        return self._Kappa
    
    @Kappa.getter
    def Kappa(self):
        N = self.Count * 4
        r = self.ResultantVector.mag
        if (N == r):
            self._Kappa = 0.000000001
        else:
            self._Kappa = (N - 1) / (N - r)
        
        return self._Kappa
    
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Add(self, block, sKey=''):
        # Create a new object
        objNewMember = MeasurementBlock()
        
        for i in range(0, 4):
            objNewMember.SetSample(i, block.Sample[i])
            objNewMember.SetHolder(i, block.Holder[i])
        
        for i in range(0, 2):
            objNewMember.SetBaseline(i, block.Baselines[i])
        
        objNewMember.isUp = block.isUp        
    
        if (len(sKey) == 0):
            self.Item.append(objNewMember)
        else:
            objNewMember.sKey = sKey
            self.Item.append(objNewMember)
    
        # Return the object created        
        return objNewMember
                
    
        