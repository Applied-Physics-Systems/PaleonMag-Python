'''
Created on Oct 21, 2025

@author: hd.nguyen
'''
import math
import time

from datetime import datetime

import ClassModules.MeasurementBlock as MB

from Modules.modVector3d import modVector3d 

from ClassModules.Angular3D import Angular3D
from ClassModules.Cartesian3D import Cartesian3D

Magnet_SampleOrientationUp = -1
Magnet_SampleOrientationDown = 1
Measure_ARCDelay = 2.5

'''
    -----------------------------------------------------------------------------------------
'''
class Measure_Unfolded():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.S = Angular3D()
        self.c = Angular3D()
        self.g = Angular3D()

'''
    -----------------------------------------------------------------------------------------
'''
class Measure_AvgStats():
    '''
        This type is used to pass information from measurement
        of the sample to display on the screen, and output to
        a data file
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.unfolded = Measure_Unfolded()      # Unfolded measurement
        self.SigNoise = 0.0                     # Signal/Noise ratio
        self.SigHolder = 0.0                    # Signal/Holder ratio
        self.SigInduced = 0.0                   # Signal/Induced ratio
        self.momentvol = 0.0                    # Moment/vol ratio

'''
    -----------------------------------------------------------------------------------------
'''
class modMeasure():
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        self.parent = parent
        
        self.SampleNameCurrent = ''
        self.SampleStepCurrent = ''
        self.SampleOrientationCurrent = 0
        self.Meascount = 0
        self.DumpRawDataStats = True
        self.HolderMeasured = False
        
        self.frmMeasure_lblDemag = ''

    '''--------------------------------------------------------------------------------------------
                        
                        Susceptibility Meter Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def frmSusceptibilityMeter_LagTime(self):
        if not self.parent.modConfig.EnableSusceptibility:
            return
        
        self.parent.modConfig.queue.put('frmSusceptibilityMeter:Start Timer = Getting Response:Input Text = Calculating Lag Time ...')
                    
        responseStr = self.parent.susceptibility.makeMeasurement()
        
        self.parent.modConfig.queue.put('frmSusceptibilityMeter:Stop Timer:Status Text = ' + responseStr)
        
        return
    
    '''
    '''
    def frmSusceptibilityMeter_Measure(self):
        if not self.parent.modConfig.EnableSusceptibility:
            return
        
        self.parent.modConfig.queue.put('frmSusceptibilityMeter:Start Timer = Getting Response')
                    
        responseStr = self.parent.susceptibility.makeMeasurement()
        
        self.parent.modConfig.queue.put('frmSusceptibilityMeter:Stop Timer:Status Text = ' + responseStr)
        
        try:
            measureOut = float(responseStr) * self.parent.modConfig.SusceptibilityScaleFactor
        except:
            measureOut = 0.0
        
        return measureOut
    
    '''
    '''
    def frmSusceptibilityMeter_Zero(self):
        self.parent.susceptibility.zeroMeasurement()
        return

    '''
    '''
    def Susceptibility_Standardize(self, uncalibrated):
        
        susceptibility_Standardize = (uncalibrated - self.parent.SampleHolder.Susceptibility) * self.parent.modConfig.SusceptibilityMomentFactorCGS
        
        return susceptibility_Standardize

    '''
    '''
    def Susceptibility_Measure(self, processingSample, IsHolder = False):        
        processingSample.Susceptibility = 0
        if (self.parent.modConfig.COMPortSusceptibility < 1):
            return processingSample
        
        SCoilSampleCenterPos = int(self.parent.modConfig.SCoilPos + processingSample.SampleHeight / 2)
        if ((SCoilSampleCenterPos / abs(SCoilSampleCenterPos)) != (self.parent.modConfig.SCoilPos / abs(self.parent.modConfig.SCoilPos))):
            # crap... our sample is too large to put in the susceptibility coil!
            return processingSample
        
        if (abs(self.parent.motors.UpDownHeight()) > (0.5 * abs(self.parent.modConfig.SampleBottom))):
            self.parent.motors.HomeToTop()
        
        self.frmSusceptibilityMeter_Zero()
        self.parent.motors.UpDownMove(SCoilSampleCenterPos, 0) # (December 2008 K Bradley) Slow down the rod when it goes to the X coil to prevent breaking the rod
        measured = self.frmSusceptibilityMeter_Measure()
        
        if IsHolder:
            susceptibility_Measure = measured 
        else: 
            susceptibility_Measure = self.Susceptibility_Standardize(measured)
        processingSample.Susceptibility = susceptibility_Measure
        
        return processingSample

    '''--------------------------------------------------------------------------------------------
                        
                        Forms Updating Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def frmMeasure_SetFields(self, avgSteps, curDemagLong, doUp, doBoth, filename):
        messageStr = 'frmMeasure:SetFields:'
        messageStr += ':avgSteps = ' + str(avgSteps)
        messageStr += ':curDemagLong = ' + curDemagLong
        messageStr += ':doUp = ' + str(doUp)
        messageStr += ':doBoth = ' + str(doBoth)
        messageStr += ':filename = ' + filename
        self.parent.modConfig.queue.put(messageStr)
        return
    
    '''
    '''
    def frmMeasure_showData(self, X, Y, Z, num):
        messageStr = 'frmMeasure:showData:'
        messageStr += ':datX = ' + str(X)
        messageStr += ':datY = ' + str(Y)
        messageStr += ':datZ = ' + str(Z)
        messageStr += ':num = ' + str(num)
        messageStr += ':Meascount = ' + str(self.Meascount)
        self.parent.modConfig.queue.put(messageStr)
        return

    '''
    '''
    def frmMeasure_ShowAngDat(self, dec, inc, num):
        messageStr = 'frmMeasure:ShowAngDat:'
        messageStr += ':dec = ' + str(dec)
        messageStr += ':inc = ' + str(inc)
        messageStr += ':num = ' + str(num)
        self.parent.modConfig.queue.put(messageStr)
        return
    
    '''
    '''
    def frmMeasure_ShowStats(self, X, Y, Z,
                                   dec, inc, SigDrift,
                                   SigHold, SigInd, CSD):
        messageStr = 'frmMeasure:ShowStats:'
        messageStr += ':X = ' + str(X)
        messageStr += ':Y = ' + str(Y)
        messageStr += ':Z = ' + str(Z)
        messageStr += ':dec = ' + str(dec)
        messageStr += ':inc = ' + str(inc)
        messageStr += ':SigDrift = ' + str(SigDrift)
        messageStr += ':SigHold = ' + str(SigHold)
        messageStr += ':SigInd = ' + str(SigInd)
        messageStr += ':CSD = ' + str(CSD)
        self.parent.modConfig.queue.put(messageStr)
        return
    
    '''
    '''
    def frmMeasure_PlotEqualArea(self, dec, inc):
        messageStr = 'frmMeasure:PlotEqualArea'
        messageStr += ':dec = ' + str(dec)
        messageStr += ':inc = ' + str(inc)
        self.parent.modConfig.queue.put(messageStr)
        return

    '''
    '''
    def frmMeasure_updateStats(self, MaxX, MinX, MaxY, MinY, MaxZ, MinZ, Vol, momentvol):
        messageStr = 'frmMeasure:updateStats'
        messageStr += ':MaxX = ' + str(MaxX)
        messageStr += ':MinX = ' + str(MinX)
        messageStr += ':MaxY = ' + str(MaxY)
        messageStr += ':MinY = ' + str(MinY)
        messageStr += ':MaxZ = ' + str(MaxZ)
        messageStr += ':MinZ = ' + str(MinZ)
        messageStr += ':Vol = ' + str(Vol)
        messageStr += ':momentvol = ' + str(momentvol)
        self.parent.modConfig.queue.put(messageStr)
        return
    
    '''
    '''
    def frmMeasure_updateWidgets(self, widgetLabel, dataStr):
        messageStr = 'frmMeasure:' + widgetLabel + ' = ' + dataStr 
        self.parent.modConfig.queue.put(messageStr)
        return
    
    '''
        (August 2007 L Carporzen) Zijderveld diagram    
    '''
    def frmMeasure_ImportZijRoutine(self, FilePath, crdec, crinc, momentvol, refresh):
        print('TODO:modMeasure.frmMeasure_ImportZijRoutine') 
        return
   
    '''
    '''
    def frmMeasure_AveragePlotEqualArea(self, dec, inc, CSD):
        messageStr = 'frmMeasure:AveragePlotEqualArea'
        messageStr += ':dec = ' + str(dec)
        messageStr += ':inc = ' + str(inc)
        messageStr += ':CSD = ' + str(CSD)
        self.parent.modConfig.queue.put(messageStr)
        return

    '''--------------------------------------------------------------------------------------------
                        
                        Measure Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Measure_CalcStats(self, specimen, measblock):   
        measure_CalcStats = Measure_AvgStats()
        
        vect = measblock.VectAvg
        if (specimen.Vol > 0): 
            workingVol = specimen.Vol 
        else: 
            workingVol = 1
        measure_CalcStats.momentvol = measblock.Moment / workingVol
        # Generate signal/noise ratios - Large values imply good data
        measure_CalcStats.SigNoise = measblock.SigNoise         
        measure_CalcStats.SigHolder = measblock.SigHolder       
        measure_CalcStats.SigInduced = measblock.SigInduced     
        
        '''
            Calls subroutine to complete all unfolding, to give a
            structurally corrected declination and inclination.
        '''
        measure_CalcStats.unfolded = self.Measure_Unfold(specimen, vect.X, vect.Y, vect.Z, math.sqrt(vect.X ** 2 + vect.Y ** 2))
        
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
        if "aTAFX" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            measure_CalcStats.unfolded = self.Measure_Unfold(specimen, -vect.Z, vect.X, -vect.Y, math.sqrt(vect.Z ** 2 + vect.X ** 2))
        if "aTAFY" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            measure_CalcStats.unfolded = self.Measure_Unfold(specimen, vect.X, vect.Z, -vect.Y, math.sqrt(vect.X ** 2 + vect.Z ** 2))
        
        return measure_CalcStats
        
    '''
        Subroutine to perform the bedding-style rotations.  The direction
        to be rotated should be given in polar coordinates of DEC and INC
        (in degrees), while the direction of bedding dip (BA, not the
        strike!) and bedding dip (BD) are in radians.  The routine returns
        a new DEC and INC corresponding to the tilt-corrected directions.
    '''
    def Measure_Rotate(self, inc, dec, bA, bD):
        Measure_Rotate = Angular3D()
        
        Z = -math.sin(modVector3d.DegToRad(inc))
        X = math.cos(modVector3d.DegToRad(inc)) * math.cos(modVector3d.DegToRad(dec))
        Y = math.cos(modVector3d.DegToRad(inc)) * math.sin(modVector3d.DegToRad(dec))
        SA = -math.sin(bA)
        CA = math.cos(bA)
        CDP = math.cos(bD)
        SDP = math.sin(bD)
        xC = X * (SA * SA + CA * CA * CDP) + Y * (CA * SA * (1 - CDP)) - Z * SDP * CA
        yC = X * CA * SA * (1 - CDP) + Y * (CA * CA + SA * SA * CDP) + Z * SA * SDP
        zC = X * CA * SDP - Y * SDP * SA + Z * CDP
        # Corrected incl and decl
        Measure_Rotate.inc = -modVector3d.RadToDeg(math.atan(zC / math.sqrt(xC ** 2 + yC ** 2)))
        Measure_Rotate.dec = modVector3d.RadToDeg(modVector3d.Atan2(xC, yC), True)
        
        return Measure_Rotate 
        
    '''
        Subroutine to make the structural and fold corrections.
        This uses the strike of bedding, not the dip direction, given in
        a right-handed sense. If fold corrections are also going to be done,
        both the remanence direction and a normal vector to the local bedding
        planes are rotated such that the fold axis is horizontal. The new
        bedding direction is then used to tilt-correct the rotated remanence
        direction to the final structurally-corrected orientation, SDEC and
        SINC.
    '''    
    def Measure_Bedding(self, specimen, ginc, gdec):
        
        magDec = specimen.parent.magDec
        if not specimen.FoldRotation:
            # Do the simple garden-variety bedding correction.
            bA = modVector3d.DegToRad(specimen.BeddingStrike + magDec + 90)
            bD = modVector3d.DegToRad(specimen.BeddingDip)
            Measure_Bedding = self.Measure_Rotate(ginc, gdec, bA, bD)
        else:
            '''
                First, rotate the remanence direction through the amount
                necessary to make the fold axis horizontal.
            '''
            bA = modVector3d.DegToRad(specimen.FoldAxis + magDec)
            bD = modVector3d.DegToRad(specimen.FoldPlunge)
            firstval = self.Measure_Rotate(ginc, gdec, bA, bD)
            
            '''
                Now we must find the new orientation of the bedding planes after
                rotating the fold axis up to horizontal.  To do this, rotate the
                direction of the normal vector through the same matrix.  The
                DEC and INC values calculated in the next two statements should
                be a normal vector to the untilted plane, and the DEC and INC
                returned from ROTATE should correspond to the fold-corrected
                plane direction.
            '''
            dec = specimen.BeddingStrike + magDec - 90
            inc = 90 - specimen.BeddingDip            
            secondval = self.Measure_Rotate(inc, dec, bA, bD)
            
            '''
                Now we need to take the new normal vector to the bedding plane,
                DEC,INC, and compute the dip direction (BA) and plunge (BD,
                both in radians).  We can then re-generate the rotation matrix
                and finish the tilt correction process on SDEC and SINC.  Note
                that the rotated directions are given with respect to TRUE NORTH,
                and only the measurements taken in the field (with the Magnetic
                Declination offset on the compass set at ZERO) require the MAGDEC
                correction.
            '''
            bA = modVector3d.DegToRad((secondval.dec + 180))
            bD = modVector3d.DegToRad(90 - secondval.inc)
            # Put the intermediate direction back for the final rotation
            Measure_Bedding = self.Measure_Rotate(firstval.inc, firstval.dec, bA, bD)
            
        return Measure_Bedding
        
    '''
        A subroutine to feed in a direction in sample coordinates, and
        to unfold w.r.t. fold axes, bedding orientation, and sample
        orientation, to spit out a declination and inclination.  UNFOLD
        wants to be fed directions in sample coordinates, in variables
        XTEMP, YTEMP, and ZTEMP.
        COMPUTE DECL. AND INCL. IN SPECIMEN COORDINATES AS POSITIVE FROM +X
    '''
    def Measure_Unfold(self, specimen,
                       X, Y, Z,
                       HO = 0.0):
        
        ret = Measure_Unfolded()
        
        MT = math.sqrt(abs(X ** 2 + Y ** 2 + Z ** 2))
        ret.c.dec = modVector3d.RadToDeg(modVector3d.Atan2(X, Y), True)
        ret.c.inc = modVector3d.RadToDeg(math.atan(Z / (HO + 0.00001)))
        
        '''
            COORDINATE TRANSFORM FOR SAMPLE ORIENTATION IN FIELD
            CORRECT DIP DIRECTION FOR MAGNETIC DECLINATION,
            AND USE CALTECH ORIENTATION SYSTEM
        '''
        magDec = specimen.parent.magDec
        DD = specimen.CorePlateStrike + magDec - 90
        DP = modVector3d.DegToRad((90 - specimen.CorePlateDip))
        SD = math.sin(DP)
        CD = math.cos(DP)
        
        if (MT == 0):
            MT = 0.00001
        ax = X / MT
        ay = Y / MT
        aZ = Z / MT
        XP = ax * SD + aZ * CD
        BB = math.sqrt(XP ** 2 + ay ** 2)
        CC = aZ * SD - ax * CD
        if (BB == 0):
            BB = 0.00001
        ret.g.inc = modVector3d.RadToDeg(math.atan(CC / BB))
        # COMPUTE DEC = ARCTAN(Y/X)
        ret.g.dec = modVector3d.RadToDeg(modVector3d.Atan2(XP, ay) + modVector3d.DegToRad(DD), True)
        ret.S = self.Measure_Bedding(specimen, ret.g.inc, ret.g.dec)
        
        Measure_Unfold = ret        
        return Measure_Unfold
    
    '''
    '''
    def Measure_ReadSample_1(self, specimen, 
                           IsHolder = False,
                           isUp = True, 
                           AllowRemeasure = True):
        MaxX = -1000000000
        MaxY = -1000000000
        MaxZ = -1000000000
        MinX = 1000000000
        MinY = 1000000000
        MinZ = 1000000000

        measure_ReadSample = MB.MeasurementBlock()
        
        self.parent.modConfig.queue.put('frmMeasure:InitEqualArea')
        
        Holder = MB.MeasurementBlock()
        self.parent.modConfig.processData.SampleNameCurrent = specimen.Samplename
        measure_ReadSample.isUp = isUp
        if not IsHolder:
            for j in range(0, 4):
                measure_ReadSample.SetHolder(j, Holder.Sample[j])
            
        self.parent.motors.TurningMotorRotate(0)         
        self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 2)
        
        '''
            Before the first zero, reset and zero counter
            then wait for numbers to settle.
        '''
        self.parent.SQUID.CLP("A")
        self.parent.SQUID.ResetCount("A")
        
        self.parent.displayStatusBar("Resetting...")
        time.sleep(Measure_ARCDelay * 1)  # Briefly pause
        
        '''
            First zero measurement
            latch data from zero position
        '''
        self.parent.SQUID.latchVal("A", False)

        curMeas = self.parent.SQUID.getData(True)
        
        # Start move into SampleCenterPosition
        SampleCenterPosition = int(self.parent.modConfig.MeasPos + specimen.SampleHeight / 2)
        self.parent.motors.UpDownMove(SampleCenterPosition, 0, False)
        measure_ReadSample.SetBaseline(0, curMeas)
        self.frmMeasure_showData(curMeas.X, curMeas.Y, curMeas.Z, 0)
        
        '''
            Communication problem: Rescan the first zero if a 0 appears! (August 2007 L Carporzen)
            Lower to sense region and take first measurement
            remember to center the sample in the sense region ... SampleBottom is in the INI
            file, and the SampleTop value was set when the system picked it up initially.
            Note that both positions are measured with the TestAll function homing down, so
            the small distance that the turning rod moves up before the limit switch clicks
            should not influence the pushbutton position.
        '''
        self.parent.motors.UpDownMove(SampleCenterPosition, 0)
        self.parent.motors.TurningMotorRotate(0)    # (November 2009 L Carporzen)
        time.sleep(Measure_ARCDelay * 1)  # Briefly pause
        self.parent.SQUID.latchVal("A", True)
        curMeas = self.parent.SQUID.getData(True)
        measure_ReadSample.SetSample(0, curMeas)
        self.parent.motors.TurningMotorRotate(90, False)
        
        # Adjust to baseline - just for the display
        X = curMeas.X - measure_ReadSample.Baselines[0].X
        Y = curMeas.Y - measure_ReadSample.Baselines[0].Y
        Z = curMeas.Z - measure_ReadSample.Baselines[0].Z
        # Adjust to direction
        if isUp:
            # +X, -Y, +Z direction
            Y = -Y
        else:
            # +X, +Y, -Z direction
            Z = -Z
        
        unfolded = self.Measure_Unfold(specimen, X, Y, Z)
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
        if "aTAFX" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel:
            unfolded = self.Measure_Unfold(specimen, -Z, X, -Y)
        if "aTAFY" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, X, Z, -Y)
            
        if (X > MaxX):
            MaxX = X
        if (Y > MaxY): 
            MaxY = Y
        if (Z > MaxZ): 
            MaxZ = Z
        if (X < MinX):
            MinX = X
        if (Y < MinY): 
            MinY = Y
        if (Z < MinZ): 
            MinZ = Z
            
        self.frmMeasure_showData(X, Y, Z, 1)
        self.frmMeasure_ShowAngDat(unfolded.S.dec, unfolded.S.inc, 1)
        self.frmMeasure_PlotEqualArea(unfolded.S.dec, unfolded.S.inc)   # (August 2007 L Carporzen) Equal area plot
        
        # Move to +Y, +X Orientation and take measurement
        self.parent.motors.TurningMotorRotate(90)
        self.parent.SQUID.latchVal("A", True)
        curMeas = self.parent.SQUID.getData(True)
        self.parent.motors.TurningMotorRotate(180, False)
        measure_ReadSample.SetSample(1, curMeas)
        
        # Adjust to baseline - just for the display
        X = curMeas.Y - measure_ReadSample.Baselines[0].Y
        Y = curMeas.X - measure_ReadSample.Baselines[0].X
        Z = curMeas.Z - measure_ReadSample.Baselines[0].Z    # Adjust to direction
        if not isUp:
            # -Y, +X, -Z direction
            Y = -Y
            Z = -Z
        
        unfolded = self.Measure_Unfold(specimen, X, Y, Z)
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file        
        if "aTAFX" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, -Z, X, -Y)
            
        if "aTAFY" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, X, Z, -Y)
        
        if (X > MaxX): 
            MaxX = X
        if (Y > MaxY): 
            MaxY = Y
        if (Z > MaxZ): 
            MaxZ = Z
        if (X < MinX): 
            MinX = X
        if (Y < MinY): 
            MinY = Y
        if (Z < MinZ): 
            MinZ = Z
            
        self.frmMeasure_showData(X, Y, Z, 2)
        self.frmMeasure_ShowAngDat(unfolded.S.dec, unfolded.S.inc, 2)
        self.frmMeasure_PlotEqualArea(unfolded.S.dec, unfolded.S.inc)   # (August 2007 L Carporzen) Equal area plot
        
        # Move to -X, +Y Orientation and measure
        self.parent.motors.TurningMotorRotate(180)
        self.parent.SQUID.latchVal("A", True)
        curMeas = self.parent.SQUID.getData(True)
        self.parent.motors.TurningMotorRotate(270, False)
        measure_ReadSample.SetSample(2, curMeas)
        # Adjust to baseline - just for the display
        X = curMeas.X - measure_ReadSample.Baselines[0].X
        Y = curMeas.Y - measure_ReadSample.Baselines[0].Y
        Z = curMeas.Z - measure_ReadSample.Baselines[0].Z
        # Adjust to direction
        if isUp:
            # -X, +Y, +Z direction
            X = -X
        else:
            # -X, -Y, -Z direction
            X = -X
            Y = -Y
            Z = -Z
        
        unfolded = self.Measure_Unfold(specimen, X, Y, Z)
        
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
        if "aTAFX" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, -Z, X, -Y)
        if "aTAFY" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, X, Z, -Y)
        if (X > MaxX): 
            MaxX = X
        if (Y > MaxY): 
            MaxY = Y
        if (Z > MaxZ): 
            MaxZ = Z
        if (X < MinX): 
            MinX = X
        if (Y < MinY): 
            MinY = Y
        if (Z < MinZ): 
            MinZ = Z
            
        self.frmMeasure_showData(X, Y, Z, 3)
        self.frmMeasure_ShowAngDat(unfolded.S.dec, unfolded.S.inc, 3)
        self.frmMeasure_PlotEqualArea(unfolded.S.dec, unfolded.S.inc)   # (August 2007 L Carporzen) Equal area plot
        
        # Move to -Y, -X Orientation and measure
        self.parent.motors.TurningMotorRotate(270)
        self.parent.SQUID.latchVal("A", True)
        curMeas = self.parent.SQUID.getData(True)
        self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 0, False)
        self.parent.motors.TurningMotorRotate(360, False)
        measure_ReadSample.SetSample(3, curMeas)
        # Adjust to baseline - just for the display
        X = curMeas.Y - measure_ReadSample.Baselines[0].Y
        Y = curMeas.X - measure_ReadSample.Baselines[0].X
        Z = curMeas.Z - measure_ReadSample.Baselines[0].Z
        # Adjust to direction
        if isUp:
            # -Y, -X, +Z direction
            X = -X
            Y = -Y
        else:
            # +Y, -X, -Z direction
            X = -X
            Z = -Z
        
        unfolded = self.Measure_Unfold(specimen, X, Y, Z)
        # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
        if "aTAFX" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, -Z, X, -Y)
        if "aTAFY" in specimen.parent.measurementSteps.CurrentStep.DemagStepLabel: 
            unfolded = self.Measure_Unfold(specimen, X, Z, -Y)
        if (X > MaxX): 
            MaxX = X
        if (Y > MaxY): 
            MaxY = Y
        if (Z > MaxZ): 
            MaxZ = Z
        if (X < MinX): 
            MinX = X
        if (Y < MinY): 
            MinY = Y
        if (Z < MinZ): 
            MinZ = Z
        self.frmMeasure_showData(X, Y, Z, 4)
        self.frmMeasure_ShowAngDat(unfolded.S.dec, unfolded.S.inc, 4)
        self.frmMeasure_PlotEqualArea(unfolded.S.dec, unfolded.S.inc)   # (August 2007 L Carporzen) Equal area plot

        '''        
            Lift to zero and measure
            Rotate the sample back to start direction
        '''
        self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 0)
        # remember, on the new systems we keep the tube spinning in the same direction
        self.parent.motors.TurningMotorRotate(360)
        self.parent.motors.SetTurningMotorAngle(0)
        
        self.parent.SQUID.latchVal("A", True)
        curMeas = self.parent.SQUID.getData(True)
        measure_ReadSample.SetBaseline(1, curMeas)
        self.frmMeasure_showData(curMeas.X, curMeas.Y, curMeas.Z, 5)
        
        '''
            Communication problem: Rescan automatically the set of measurement if a 0 appears! (August 2007 L Carporzen)
            If Not NOCOMM_MODE And (curMeas.x = 0 Or curMeas.y = 0 Or curMeas.z = 0) Then Set Measure_ReadSample = Measure_ReadSample(specimen, isHolder, isUp, True)
        '''
        blocks = MB.MeasurementBlocks(self.parent)
        blocks.Add(measure_ReadSample)
        avstats = self.Measure_CalcStats(specimen, blocks)
        if self.parent.checkProgramHaltRequest():
            return

        '''        
                                       NEW PARAMETERS TO MONITOR THE SQUID NOISEs (August 2007 L Carporzen)
             Look at the homogeneity of each axis: it is only informative for the user, their is no automatic rescanof a bad value.
            The user sees the delta on each axis (in emu) as well as the ratio of this delta by the measured moment
            If the ratio is greater than 1, the boxes corresponding to the "bad" axis light in Orange
            If the ratio is greater than 5, the boxes corresponding to the "bad" axis light in Red
            Notice that X and Y axis share the SQUIDs X and Y.
        '''
        if self.parent.modConfig.processData.NOCOMM_MODE: 
            avstats.momentvol = 0.000000001            
        if (avstats.momentvol == 0): 
            avstats.momentvol = 0.000000001
            
        self.frmMeasure_updateStats(MaxX, MinX, MaxY, MinY, MaxZ, MinZ, specimen.Vol, avstats.momentvol)
        
        '''
                                       NEW PARAMETERS TO AVOID RECORD OF SQUID JUMPS (August 2007 L Carporzen)
            In the program, three new options are available in the Options menu:
            Above a certain moment, the initial criteria looking at the CSD and the Signal/Noise is apply
            Ian changed that value from 10-7 to 8.10-9 emu because of some unacceptable large CSD on weak samples
            "Critical moment (emu):" (default = 8.10-9 emu)
            If the measured moment is lower than 10-6 emu, the accepted differences between the zero measurements of each of the three SQUID is proportional to the measured moment.
            In case of very low moment, the possible drift of the SQUID may block this criteria. For that reason, you can change the "Jump sensitivity" (default = 1)
            In order to avoid infinite measurement, we put a limit above which the program will accept more easily a measurement.
            However, you can decide to accept only the good measurement which fit all the criteria by increasing the number of try to a much greater value.
            "Number of try:" (default = 5)
        
            If the zero measurements are too different we need to remeasure
        '''
        X = abs(curMeas.X - measure_ReadSample.Baselines[0].X)
        Y = abs(curMeas.Y - measure_ReadSample.Baselines[0].Y)
        Z = abs(curMeas.Z - measure_ReadSample.Baselines[0].Z)
        
        measure_ReadSampleDict = {'measure_ReadSample': measure_ReadSample,
                                  'avstats': avstats,
                                  'X': X,
                                  'Y': Y,
                                  'Z': Z}
        
        return measure_ReadSampleDict
   
 
    '''
        This procedure goes forward and measures the sample that
        is currently loaded in the magnetometer.  It starts with
        the sample in the zero position, and ends with the sample
        in the zero position
    '''
    def Measure_ReadSample(self, specimen, 
                           IsHolder = False,
                           isUp = True, 
                           AllowRemeasure = True):
        
        measure_ReadSampleDict = self.Measure_ReadSample_1(specimen, IsHolder, isUp, AllowRemeasure)
        measure_ReadSample = measure_ReadSampleDict['measure_ReadSample']
        avstats = measure_ReadSampleDict['avstats'] 
        X = measure_ReadSampleDict['X']
        Y = measure_ReadSampleDict['Y']
        Z = measure_ReadSampleDict['Z']
        
        '''
            To avoid repetitive measurements, "Number of try:" (Meascount) is the maximum try per measurement. You can change in the Options menu the "Number of try:" (default = 5)
            You can change in the Options menu the minimum moment ("Critical moment (emu):", default = 8.10-9 emu) where the CSD criteria is apply
        '''
        if (self.Meascount >= self.parent.modConfig.NbTry):
        #It sends an email when the measurement is accepted just to inform what were the zero differences
            if ((self.parent.modConfig.NbTry > 0) and \
               ((X > self.parent.modConfig.JumpThreshold) or \
               (Y > self.parent.modConfig.JumpThreshold) or \
               (Z > self.parent.modConfig.JumpThreshold))):
            
                mailNotification = "Measurement recorded even though... the difference between "
                mailNotification += "the two zero measurements is " + '{:.5f}'.format(X) + " on X, "
                mailNotification += '{:.5f}'.format(Y) + " on Y and " + '{:.5f}'.format(Z)
                mailNotification += " on Z; the moment is " + '{:.4f}'.format((specimen.Vol * avstats.momentvol))
                mailNotification += " emu and CSD=" + '{:.1f}'.format(measure_ReadSample.FischerSD)
                self.parent.sendEmailNotification(mailNotification)
                                                                
        # First, the CSD original criteria could be enough to rescan
        elif (AllowRemeasure and \
               ((specimen.Vol * avstats.momentvol) > self.parent.modConfig.MomMinForRedo) and \
               ((avstats.SigNoise < 1) or \
                (avstats.SigInduced < 1) or \
                (measure_ReadSample.FischerSD > self.parent.modConfig.RemeasureCSDThreshold))):
                
            self.frmMeasure_updateWidgets('lblRescan', "CSD " + '{:.1}'.format(measure_ReadSample.FischerSD))            
            self.Meascount = self.Meascount + 1
            
            '''
            '(March 9, 2011 - I Hilburn)
                Adding in modification to enable the user to separately set the remeasure Holder
                setting if the CSD is too high on a high-moment holder measurement
            '''
            if not (IsHolder and (self.Meascount > self.parent.modConfig.NbHolderTry)):
                '''
                    User setting allows the code to make another try at remeasuring the holder
            
                     For very strong moment, > StrongMom (default 2.10-2 emu), the SQUID response
                    will not enable this criteria, we look on the CSD original criteria.
                '''            
                if (((specimen.Vol * avstats.momentvol) > self.parent.modConfig.StrongMom) and (self.Meascount > 0)):                   
                    mailNotification = "Redoing the measurement because the CSD=" 
                    mailNotification += '{:.1f}'.format(measure_ReadSample.FischerSD) & _
                    mailNotification += " and the moment is " + '{:.4f}'.format((specimen.Vol * avstats.momentvol)) + " emu."
                    self.parent.sendEmailMailNotification(mailNotification)
                                                
                self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 0)
                
                time.sleep(Measure_ARCDelay * 1)  # Briefly pause
                
                measure_ReadSample = self.Measure_ReadSample(specimen, IsHolder, isUp, True)
                
            
        elif (AllowRemeasure and \
              ((specimen.Vol * avstats.momentvol) < self.parent.modConfig.StrongMom) and 
              ((X > self.parent.modConfig.JumpThreshold) or (Y > self.parent.modConfig.JumpThreshold) or (Z > self.parent.modConfig.JumpThreshold))):    
            # The CSD criteria has accepted the measurement
            # For moment below StrongMom (default 2.10-2 emu), we rescan if their is a jump > JumpThreshold (default 0.1x10-5 emu)
            # For moment > InterMom (default 10-6 emu), the difference between each of the three zero measurements
            # needs to be < JumpThreshold (default 0.1x10-5 emu)            
            if ((X > self.parent.modConfig.JumpThreshold) and (self.Meascount > 0)):            
                mailNotification = "X=" + '{:.5f}'.format(X) + " SQUID jump, "
                mailNotification += str(self.Meascount) + " redoing the measurement for a moment of " 
                mailNotification += '{:.4f}'.format(specimen.Vol * avstats.momentvol) 
                mailNotification += " emu, CSD=" + '{:.1f}'.format(measure_ReadSample.FischerSD)
                self.parent.sendEmailMailNotification(mailNotification)
            
            if ((Y > self.parent.modConfig.JumpThreshold) and (self.Meascount > 0)):
                mailNotification = "Y=" + '{:.5f}'.format(Y) + " SQUID jump, "
                mailNotification += str(self.Meascount) + " redoing the measurement for a moment of " 
                mailNotification += '{:.4f}'.format(specimen.Vol * avstats.momentvol) 
                mailNotification += " emu, CSD=" + '{:.1f}'.format(measure_ReadSample.FischerSD)
                self.parent.sendEmailMailNotification(mailNotification)
                            
            if ((Z > self.parent.modConfig.JumpThreshold) and (self.Meascount > 0)):
                mailNotification = "Z=" + '{:.5f}'.format(Z) + " SQUID jump, "
                mailNotification += str(self.Meascount) + " redoing the measurement for a moment of " 
                mailNotification += '{:.4f}'.format(specimen.Vol * avstats.momentvol) 
                mailNotification += " emu, CSD=" + '{:.1f}'.format(measure_ReadSample.FischerSD)
                self.parent.sendEmailMailNotification(mailNotification)
                
            '''
                Information mails when the measurement will be repeated because of a difference
                between the zero > JumpThreshold (default 0.1) (x10-5 emu)
            '''            
            self.frmMeasure_updateWidgets('lblRescan', "SQUID jumps") 
            self.Meascount = self.Meascount + 1
            
            self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 0)            
            time.sleep(Measure_ARCDelay * 1)  # Briefly pause
            
            measure_ReadSample = self.Measure_ReadSample(specimen, IsHolder, isUp, True)
        
        elif (AllowRemeasure and \
              ((specimen.Vol * avstats.momentvol) < self.parent.modConfig.IntermMom) and \
              ((specimen.Vol * avstats.momentvol) > self.parent.modConfig.MomMinForRedo) and \
              ((X / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)) or \
              (Y / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)) or \
              (Z / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)))):            
            '''        
                The large jump criteria has accepted the measurement
                For moment < InterMom (default 10-6 emu) and > MomMinForRedo (default 8.10-9 emu),
                the difference between each of the three zero measurements is controled by the measured moment:
                You can change in the Options menu the proportion of the moment ("Jump sensitivity", default = 1)
                which will be use to compare the zero measurements
            '''
            self.frmMeasure_updateWidgets('lblRescan', "Small jumps")
            self.Meascount = self.Meascount + 1
            
            self.parent.motors.UpDownMove(int(self.parent.modConfig.ZeroPos + specimen.SampleHeight / 2), 0)            
            time.sleep(Measure_ARCDelay * 1)    # Briefly pause            
            
            measure_ReadSample = self.Measure_ReadSample(specimen, IsHolder, isUp, True)
        
        self.frmMeasure_updateWidgets('lblRescan', "")      # Reset the rescan label
        
        # Label the small SQUID jumps in the Measure window:        
        if (((specimen.Vol * avstats.momentvol) < self.parent.modConfig.MomMinForRedo) and \
           ((X / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)) or \
            (Y / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)) or \
            (Z / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)))):
        
            if (X / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)):
                self.frmMeasure_updateWidgets('lblXSQUID', '{:.5f}'.format(X))                
            else:
                self.frmMeasure_updateWidgets('lblXSQUID', ' ')
            
            if (Y / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)):
                self.frmMeasure_updateWidgets('lblYSQUID', '{:.5f}'.format(Y))
            else:
                self.frmMeasure_updateWidgets('lblYSQUID', ' ')
            
            if (Z / (specimen.Vol * avstats.momentvol) > (self.parent.modConfig.JumpSensitivity / self.parent.modConfig.RangeFact)):
                self.frmMeasure_updateWidgets('lblZSQUID', '{:.5f}'.format(Z))
            else:
                self.frmMeasure_updateWidgets('lblZSQUID', ' ')
            
            self.frmMeasure_updateWidgets('lblRescan', "Small jumps")
            
        else:
            self.frmMeasure_updateWidgets('lblXSQUID', ' ')
            self.frmMeasure_updateWidgets('lblYSQUID', ' ')
            self.frmMeasure_updateWidgets('lblZSQUID', ' ')

        '''                    
            Code to remeasure Holder Measurements if Holder Moment is above a threshold set by the User
            Two Factors needed to enter this Logic:
             Sample = Holder
             Remeasure Holder above moment threshold = Enabled
        '''
        if (IsHolder and self.parent.modConfig.processData.EnableHolderMomentTooHighRemeasurements):    
            if ((specimen.Vol * avstats.momentvol) > self.parent.modConfig.HolderMomentTooHighThreshold):
                self.frmMeasure_updateWidgets('lblRescan', "Holder Moment too High.  Remeasuring...")                
                measure_ReadSample = self.Measure_ReadSample(specimen, IsHolder, isUp)
                self.frmMeasure_updateWidgets('lblRescan', "")
                        
        '''
            We've finished the measuring cycle
            So, now calculate the components, etc.
        '''        
        self.Meascount = 1
                
        # ADD Range switch code here if necessary. !!
        self.parent.modConfig.processData.SampleNameCurrent = ''
        
        return measure_ReadSample
    
    '''
        This function starts the averaging cycles for the up
        direction.  It measures two +X, two -X, two +Y, two -y,
        and four +Z components
    '''
    def Measure_Read(self, targetSample, RMStep, RockmagMode=False):
        isUp = False        
        readDats = MB.MeasurementBlocks(self.parent)
        Holder = MB.MeasurementBlock()
        
        IsHolder = (targetSample.Samplename == "Holder")
        self.parent.modConfig.processData.SampleNameCurrent = targetSample.Samplename
        self.parent.modConfig.processData.SampleStepCurrent = RMStep.DemagStepLabelLong
        
        # Initialize variables
        if self.parent.checkProgramHaltRequest():
            return
        
        if IsHolder:
            # Do initializations necessary for holder
            self.parent.SQUID.ChangeRange("A", "1")      # 1x read mode
            numAvgSteps = self.parent.SampQueue.maxAvgSteps            
        else:
            #With targetSample.Parent
            isUp = targetSample.parent.doUp
            doBoth = targetSample.parent.doBoth
            curDemag = targetSample.parent.curDemag
            numAvgSteps = targetSample.parent.avgSteps
            if (numAvgSteps < 1):
                numAvgSteps = 1
        
        # Begin
        for _ in range(0, numAvgSteps):
            # Do the initial zero measurement here
            readDats.Add(self.Measure_ReadSample(targetSample, IsHolder, isUp))
            for j in range(0, 4):
                readDats.Last.SetHolder(j, Holder.Sample[j])
            
            readDats.Last.isUp = isUp
            avg = readDats.VectAvg
            unfolded = self.Measure_Unfold(targetSample, avg.X, avg.Y, avg.Z)
            # (February 2010 L Carporzen) Measure the TAF and uncorrect them in sample file
            if ("aTAFX" in targetSample.parent.measurementSteps.CurrentStep.DemagStepLabel): 
                unfolded = self.Measure_Unfold(targetSample, -avg.Z, avg.X, -avg.Y)
                
            if ("aTAFY" in targetSample.parent.measurementSteps.CurrentStep.DemagStepLabel): 
                unfolded = self.Measure_Unfold(targetSample, avg.X, avg.Z, -avg.Y)
                
            self.frmMeasure_ShowStats(avg.X, avg.Y, avg.Z, unfolded.S.dec, unfolded.S.inc, 
                                      readDats.SigDrift, 
                                      readDats.SigHolder, 
                                      readDats.SigInduced, 
                                      readDats.FischerSD)
            
            if IsHolder:
                self.frmMeasure_AveragePlotEqualArea(unfolded.S.dec, unfolded.S.inc, readDats.FischerSD) # (August 2007 L Carporzen) Equal area plot
            avg = None

        if self.parent.checkProgramHaltRequest():
            return
        
        # Now we've done the measurements the avgSteps number of times
        if IsHolder:
            Holder = readDats.AverageBlock
        else:
            # Not a holder measurement
            if (isUp and doBoth):
                # We've measured the up direction, so save it to a temp file and leave
                targetSample.WriteUpMeasurements(readDats, curDemag)
                if self.DumpRawDataStats:
                    targetSample.WriteStatsTable(readDats, curDemag)
                avstats = self.Measure_CalcStats(targetSample, readDats)
                sdvect = readDats.VectSD
                self.frmStats_ShowErrors(readDats.FischerSD, 0, 0)
                self.frmStats.ShowAvgStats(sdvect.X, sdvect.Y, sdvect.Z, 
                                           avstats.unfolded.c.dec, avstats.unfolded.c.inc, 
                                           avstats.unfolded.g.dec, avstats.unfolded.g.inc, 
                                           avstats.unfolded.S.dec, avstats.unfolded.S.inc, 
                                           avstats.momentvol, avstats.SigNoise, 
                                           avstats.SigHolder, avstats.SigInduced)
                sdvect = None
                return
            
            if (doBoth and (not isUp)):
                readDats.Assimilate(targetSample.ReadUpMeasurements)
                UpToDn = readDats.UpToDown()
            
            ErrorAngle = readDats.FischerSD
            '''
                THE HORIZONTAL ERROR ANGLE, EH, IS NEGATIVE IF HOLDER SHOULD BE
                ROTATED TO THE LEFT, AND POSITIVE IF IT SHOULD GO TO THE RIGHT
            '''
            errorHoriz = readDats.ErrorHorizontal
            self.frmStats_ShowErrors(ErrorAngle, errorHoriz, UpToDn)
            sdvect = readDats.VectSD
            avstats = self.Measure_CalcStats(targetSample, readDats)
            self.frmStats_ShowAvgStats(sdvect.X, sdvect.Y, sdvect.Z, 
                                       avstats.unfolded.c.dec, avstats.unfolded.c.inc, 
                                       avstats.unfolded.g.dec, avstats.unfolded.g.inc, 
                                       avstats.unfolded.S.dec, avstats.unfolded.S.inc, 
                                       avstats.momentvol, avstats.SigNoise, 
                                       avstats.SigHolder, avstats.SigInduced)
            
            self.frmMeasure_ImportZijRoutine(self.frmMeasure_lblSampName, 
                                             avstats.unfolded.c.dec, avstats.unfolded.c.inc, 
                                             avstats.momentvol, False)      # (August 2007 L Carporzen) Zijderveld diagram
            self.frmMeasure_AveragePlotEqualArea(avstats.unfolded.S.dec, avstats.unfolded.S.inc, readDats.FischerSD)    # (August 2007 L Carporzen) Equal area plot
            unfolded = avstats.unfolded
            # Save the measurement if we're not measuring the holder
            targetSample.WriteData(curDemag, unfolded.g.dec, 
                                   unfolded.g.inc, unfolded.S.dec, unfolded.S.inc, 
                                   unfolded.c.dec, unfolded.c.inc, avstats.momentvol, 
                                   ErrorAngle, sdvect.X, sdvect.Y, sdvect.Z, readDats.UpToDown)
            
            if (RockmagMode or RMStep.MeasureSusceptibility):
                targetSample.WriteRockmagData(RMStep, 
                                              readDats.MomentVector.Z, 
                                              self.parent.modConfig.RangeFact * sdvect.Z, 
                                              readDats.MomentVector.X, 
                                              self.parent.modConfig.RangeFact * sdvect.X, 
                                              readDats.MomentVector.Y, 
                                              self.parent.modConfig.RangeFact * sdvect.Y, 
                                              unfolded.c.dec, 
                                              unfolded.c.inc, 
                                              avstats.momentvol, 
                                              ErrorAngle, 
                                              targetSample.SampleHeight)
                # multiply by rangefact to convert to emu
            
            if self.DumpRawDataStats:
                targetSample.WriteUpMeasurements(readDats, curDemag)
                targetSample.WriteStatsTable(readDats, curDemag)
            
            targetSample.BackupSpecFile
                
        self.parent.modConfig.processData.SampleNameCurrent = ''
        self.parent.modConfig.processData.SampleStepCurrent = ''
        return
    
    '''
        Measure_TreatAndRead
    
        This is the routine for taking care of AF demagnetization,
        susceptibility measurements, etc.
    '''
    def Measure_TreatAndRead(self, targetSample, useChanger = False):
        
        if self.parent.checkProgramHaltRequest():
            return
        
        self.parent.motors.TurningMotorAngleOffset(-self.parent.modConfig.TrayOffsetAngle)  # + 360 (November 2009 L Carporzen) change to 360 - instead of + because we changed the Sub TrayOffsetAngle
        
        RockmagMode = targetSample.parent.RockmagMode
        targetSample.parent.measurementSteps.CurrentStepIndex = 0
        doMeasure = targetSample.parent.measurementSteps.CurrentStep.Measure
        
        if ((targetSample.parent.measurementSteps.Count == 1) and (not targetSample.parent.RockmagMode)):
            doMeasure = True
        
        if RockmagMode:                
            targetSample.WriteRockmagInfoLine("Instrument: " + self.paren.modConfig.MailFromName)
            targetSample.WriteRockmagInfoLine("Time: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        while (targetSample.parent.measurementSteps.CurrentStepIndex > -1):
            
            if self.parent.checkProgramHaltRequest():   # (September 2007 L Carporzen) New version of the Halt button
                return
            
            LabelString = targetSample.Samplename + " @ " + targetSample.parent.curDemagLong
            
            if (targetSample.parent.measurementSteps.Count > 1):
                LabelString += " [" + str(targetSample.parent.measurementSteps.CurrentStepIndex) + \
                                "/" + str(targetSample.parent.measurementSteps.Count) + "]"
                
            self.parent.displayStatusBar("Measuring samples... (" + LabelString + ")")
            
            self.SampleNameCurrent = targetSample.Samplename
            self.SampleStepCurrent = targetSample.parent.measurementSteps.CurrentStep.DemagStepLabelLong
            
            if targetSample.parent.doUp:            
                self.SampleOrientationCurrent = Magnet_SampleOrientationUp                
            else:    
                self.SampleOrientationCurrent = Magnet_SampleOrientationDown
                            
            if ((targetSample.parent.measurementSteps.CurrentStep.MeasureSusceptibility) and \
                (targetSample.parent.doUp or (not targetSample.parent.doBoth))):                
                '''
                    (March 10, 2011 - I Hilburn)
                    This If ... then statement replaces the currently commented out code in SampleCommand.Execute
                    and in frmMagnetometerControl.cmdManHolder_Click.
                    This ensures that the susceptibility lag time is only calculated during holder measurements
                    if the user has selected for the susceptibility to be measured and should
                    eliminate the pause associated with all Holder measurements even when the user did not
                    want the susceptibility to be measured.
                '''
                if ((targetSample.Samplename == "Holder") and \
                   (self.parent.modConfig.COMPortSusceptibility > 0) and \
                   self.parent.modConfig.EnableSusceptibility):
                    '''
                        This is a holder measurement
                        Need to get the LagTime for the susceptibility measurement
                    '''
                    self.frmSusceptibilityMeter_LagTime()
                
                targetSample = self.Susceptibility_Measure(targetSample, (targetSample.Samplename == "Holder"))
                        
            targetSample.parent.measurementSteps.CurrentStep.PerformStep(targetSample)
            
            self.frmMeasure_SetFields(targetSample.parent.avgSteps, 
                                      targetSample.parent.curDemagLong, 
                                      targetSample.parent.doUp, 
                                      targetSample.parent.doBoth, 
                                      targetSample.parent.filename)            
            if doMeasure:                            
                self.Measure_Read(targetSample, 
                                  targetSample.parent.measurementSteps.CurrentStep, 
                                  RockmagMode)
                targetSample.parent.measurementSteps.AdvanceStep()
                
            elif RockmagMode:                
                targetSample.WriteRockmagData(targetSample.parent.measurementSteps.CurrentStep, 
                                              "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", 
                                              targetSample.SampleHeight,
                                              targetSample.parent.measurementSteps.AdvanceStep)            
                        
        if self.parent.checkProgramHaltRequest():   # (September 2007 L Carporzen) New version of the Halt button
            return

        self.parent.displayStatusBar("Measuring samples...")
        self.parent.motors.TurningMotorAngleOffset(self.parent.modConfig.TrayOffsetAngle)     # + 360 (November 2009 L Carporzen) change to 360 + instead of - because we changed the Sub TrayOffsetAngle
        
        self.SampleNameCurrent = ''
        self.SampleStepCurrent = ''
        self.SampleOrientationCurrent = 0
        return
        
    '''--------------------------------------------------------------------------------------------
                        
                        Public API Functions
                        
    --------------------------------------------------------------------------------------------'''
    '''
    '''
    def Manual_MeasureHolder(self):
        self.parent.modChanger.Changer_NearestHole()
                        
        self.parent.modConfig.queue.put('frmMagnetometerControl:Show frmMeasure:cmdManHolder_Click')
                    
        '''========================================================================================================
        '            '(March 10, 2011 - I Hilburn)
        '            'This code has been commented out as it is being applied even when the
        '            'user has not selected for the susceptibility measurements to be performed
        '            'New code has been added in MeasureTreatAndRead in
        '            'modMeasure to ensure that the susceptibility lagTime is set during the appropriate
        '            'Holder measurements
        ''--------------------------------------------------------------------------------------------------------
        '            If COMPortSusceptibility > 0 And EnableSusceptibility Then frmSusceptibilityMeter.LagTime
        ========================================================================================================'''
        
        # Reset SampleHolder step type to NRM, just in case
        self.parent.SampleHolder.parent.measurementSteps.Item[0].StepType = "NRM"
        self.parent.SampleHolder.parent.measurementSteps.Item[0].Level = 0
                    
        self.Measure_TreatAndRead(self.parent.SampleHolder, False)    # Read Holder
        
        self.parent.motors.UpDownMove(0, 2)
        self.HolderMeasured = True                       # Set the "holder measured" flag
                
        self.parent.displayStatusBar('')
        
        self.parent.SampleHolder.SampleHeight = 0
        
        self.parent.modConfig.queue.put('frmMagnetometerControl:cmdManHolder_End')
                
        return
    
    
        