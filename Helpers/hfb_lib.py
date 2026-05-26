
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 19:18:08 2021

@author: vincentbp
"""

# !!! PROBABILITY CONDITIONING COPY

# Function library for HeadFixed Behavior (HFB)

import os
import socket
import numpy as np
import datetime as dt
import time
import sympy
import serial
import sys
import json

import Helpers.vbp as vbp

# This function is to set the system to the correct working directory. It returns the directory name as a string or -1
def setUpDir():
    # Get system name
    systName = socket.gethostname()
    
    # Increase this list with else ifs 
    if systName == "fin-de-semaine.crulrg.local x":
        d = "/Users/vincentbp/Desktop/Behavior2Python"
    elif systName == 'Scientifica-PC':
        d = r"C:\Users\Scientifica\Desktop\Behavior2Python\ProbabilityConditioning"        
    else:
        print('Please setup directory for behavior')
        return -1
    
    # Change working directory to "d"
    os.chdir(d);
    return d

def defineParams(an):
    # Check if param file exist
    if os.path.isfile('Data'+os.path.sep+an+os.path.sep+an+'_Params.json'):
        f = open('Data'+os.path.sep+an+os.path.sep+an+'_Params.json','r')
        json_obj = f.read()
        params = json.loads(json_obj)
        f.close()
        return params
    else:
        print('Params.json file does not exist for animal "'+an+'"\n')
        print('Please use "setParametersGUI" to create a Params.json file for that animal')
        return -1
    # # Check if param file exist
    # if os.path.isfile('Data'+os.path.sep+an+os.path.sep+an+'_params.npy'):
    #     params = np.load('Data'+os.path.sep+an+os.path.sep+an+'_params.npy', allow_pickle='TRUE').item()
    #     params['computerName'] = socket.gethostname()
    #     return params
    # else:
    #     print('params.npy file does not exist for animal "'+an+'"\n')
    #     print('Please use "createNewAnimal.npy" to create a params.npy file for that animal')
    #     return -1
    
def volReward2duration(rewAmount,valveID):
    # Function to obtain the duration the valve should be opened (durValve) in sec
    # for delivering a reward amount (rewAmount) in uL. Min is 2 uL.

    # Check if calibration file exists
    systName = socket.gethostname()
    if os.path.isfile('Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy'):
        calibration = np.load('Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy',allow_pickle='TRUE').item()
        dur = calibration["valveDurTested"]
        r = calibration["rewardDelivered"]
    else:
        print('No water calibration files found in "Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy"')
        durValve = 0
        return durValve
    
    # Check date
    dateCalib = calibration['date']
    today = dt.datetime.now()
    delta = dt.date(today.year,today.month,today.day) - dt.date(dateCalib[0],dateCalib[1],dateCalib[2])
    delta = delta.days
    if delta > 30:
        print('WARNING: Last time valve '+str(valveID)+' was calibrated is '+str(delta)+' days ago\n')
        print('Consider testing with "water_testCalibrationRL" function or calibrate!\n')
    
    # Check amount set from calibration
    if rewAmount < r[0]:
        print('Reward amount '+str(rewAmount)+' set too low for calibration data for valve '+str(valveID)+'.\n')
        return -1
    if rewAmount > r[-1]:
        print('Reward amount '+str(rewAmount)+' set too high for calibration data for valve '+str(valveID)+'.\n')
        return -1
    
    # Extrapolate duration valve opening
    # idx = find(rewAmount >= r,1,'last');
    r = np.array(r)
    idx = np.argwhere(rewAmount >= r)
    idx = int(idx[-1])
    durValve = dur[idx] + (rewAmount - r[idx])/(r[idx+1] - r[idx])*(dur[idx+1] - dur[idx])
    return durValve

def randomize_laser(params):
    
    # Shuffle with 0 and 1. Every 10th trial.
    to_shuffle = (np.arange(10) < np.round(params['laser']['fract_laseron']*10).astype(int)).astype(int)
    rng = np.random.default_rng(25)
    sequence = np.array([])
    while len(sequence) < params['nTrials']:
        rng.shuffle(to_shuffle)
        sequence = np.r_[sequence,to_shuffle] if len(sequence) > 0 else to_shuffle

    # Create a list of values
    if params['laser']['timing'] == 'both':
        values = ['cue','reinfo']
    else:
        values = [params['laser']['timing']]
    values = values * len(sequence)
    values = np.array(values)

    # Create a sequence with 0 or timing
    laser_sequence = np.zeros(len(sequence),dtype=object)
    laser_sequence[sequence > 0] = values[:np.sum(sequence > 0)]
    laser_sequence = laser_sequence[:params['nTrials']]
    
    # Turn off laser for n_omit
    laser_sequence[:params['laser']['n_trial_omit']] = 0
    
    return laser_sequence

def randTrialsPROB(params):
    
    # nTrials = 1000
    # fractTone = [0.4, 0.4, 0.1, 0.1] # FractTone[3] = absence of tone
    # probRew = [0.9, 0.1, 0, 0.9]
    # probPun = [0, 0, 0, 0.1]
    # distroITI = [10, 30]
    
    trialID = np.arange(params['nTrials'])
    
    ##### RANDOMIZE TONE SELECTION ##### 
    # Verify if sum of fractTone equal to 1
    if sum(params['fractEachTone']) != 1:
        print('Sum of fractTone should == 1')
        sys.exit()
        
    # Multiply fractTone by 20
    fractTone = np.round(np.array(params['fractEachTone']) * 20).astype(int)
    
    # Create an array with these proportions to randomly choose every 20 trials
    array_tone_select = []
    for i in range(len(fractTone)):
        for x in range(fractTone[i]):
            array_tone_select.append(i)
    array_tone_select = np.array(array_tone_select)
     
    # Randomize an array every 20 trials for N trials
    idx = vbp.vecOfRandPerm(len(array_tone_select),params['nTrials'])
     
    # Determine tone ID based on values of idx
    toneID = array_tone_select[idx]
         
    #### RANDOMIZE REWARD DELIVERY
    # Multiply probRew by 100
    probRew = np.round(np.array(params['probRew']) * 10)
    probPun = np.round(np.array(params['probPun']) * 10)
    
    # Randomize an an array every 100 trials for N trials
    idx = vbp.vecOfRandPerm(10,params['nTrials'])
    
    # Determine reward or not for each tone
    rew = np.zeros(params['nTrials'])
    for i in range(len(probRew)):
        idx = vbp.vecOfRandPerm(10,sum(toneID == i))
        x = np.zeros(len(idx))
        x[idx < probRew[i]] = 1
        x[idx >= 10-probPun[i]] = -1
        rew[toneID == i] = x;
    
    # For toneID == 3 always deliver reward
    # rew[toneID == 3] = 1;
    
    #### RANDOMIZE Inter Trial Interval (ITI) with an exponential distribution #######
    
    # Initialize durITI
    durITI = np.zeros(params['nTrials']) + params['durITI'][1]
    
    # Randomize duration ITI. If randomization yield values higher than distroITI[1], randomize those values
    while any(durITI >= params['durITI'][1]):
        idx = durITI >= params['durITI'][1]
        N = sum(idx)
        durITI[idx] = np.random.exponential(params['durITI'][0],N)
    
    # Round
    durITI = np.round(durITI,decimals=2)
        
    # Concatenate in one MTX
    trialTypeMTX = np.block([trialID, toneID, rew, durITI])
    trialTypeMTX.shape = (4,params['nTrials'])
    trialTypeMTX = trialTypeMTX.transpose()
    
    trialTypeMTXHeader = ['Trial#','ToneID','Reward?','ITI Duration']
    
    return trialTypeMTX, trialTypeMTXHeader

# To create a matrix with all sound waves (8 total for go no-go behavior)
def sndWavGNG(dur,freq):   
    # freq[0] = No-Go
    # freq[1] = Go
    
    
    # Get system name
    systName = socket.gethostname()
    
    # Sampling frequency and scaling factor to adjust amplitude of both tones
    # Note: Increase this list with elif with other systname 
    if systName == "fin-de-semaine.crulrg.local":
        scalingFact = [1, 1]
        fs = 44100;
    elif systName == 'Scientifica-PC':
        scalingFact = [1, 1]
        fs = 44100;        
    else:
        print('Sound scaling factors for '+systName+' are not defined. Revert to no scaling')
        scalingFact = [1, 1]
    
    # Create snd stim MTX which stores all freq, amplitude, and duration for each sound
    sndId = np.arange(8)
    sndFreq =  np.array([freq[0]]*4 + [freq[1]]*4)
    sndAmp =  np.array([scalingFact[0]]*4 + [scalingFact[1]]*4) * [1, 0.3163, 0.1, 0.0316, 1, 0.3163, 0.1, 0.0316]
    sndDur = np.array([dur] * 8)
    
    
    # Create array with each sound wave
    audio = np.array([])
    for i in range(8):
        # Create sound wave
        t = np.linspace(0, sndDur[i], int(round(sndDur[i] * fs)), False)
        s = np.sin(sndFreq[i] * t * 2 * np.pi)
        # Ensure that highest value is in 16-bit range and adjust amplitude
        s = s * (2**15 - 1) / np.max(np.abs(s)) * sndAmp[i]
        
        # Smooth onset/offset 
         # Parameters for smoothing
        durSm = 0.005
        nSm = round(durSm*fs)
        # Scaling factor
        scalingInOut = np.ones(len(s))
        scalingInOut[:nSm] = np.linspace(0,1,nSm)
        scalingInOut[-nSm:] = np.linspace(1,0,nSm)
        # Multiply scaling
        s = s * scalingInOut
        
        # Concatenate audio
        audio = np.block([audio, s])
    
    
    # Convert to 16-bit data
    audio = audio.astype(np.int16)
    
    # Reshape audio matrix for 8 sounds
    audio.shape = (8,int(round(sndDur[i] * fs)))

    return audio,fs

def sndWavPROB(dur,freq):   
 
    # Get system name
    systName = socket.gethostname()
    
    # Sampling frequency and scaling factor to adjust amplitude of both tones
    # Note: Increase this list with elif with other systname 
    if systName == "fin-de-semaine.crulrg.local":
        scalingFact = [1, 1, 1]
        fs = 44100
    elif systName == 'Scientifica-PC':
        scalingFact = [1, 1, 1]
        fs = 44100        
    else:
        print('Sound scaling factors for '+systName+' are not defined. Revert to no scaling')
        scalingFact = [1, 1, 1]
        fs = 44100
    
    # Create snd stim MTX which stores all freq, amplitude, and duration for each sound'
        
    sndId = np.arange(3)
    sndFreq = np.array(freq)
    sndAmp = np.array(scalingFact)
    sndDur = np.array([dur] * 3)
    
    
    
    # Create array with each sound wave
    audio = np.array([])
    for i in range(3):
        # Create sound wave
        t = np.linspace(0, sndDur[i], int(round(sndDur[i] * fs)), False)
        s = np.sin(sndFreq[i] * t * 2 * np.pi)
        # Ensure that highest value is in 16-bit range and adjust amplitude
        s = s * (2**15 - 1) / np.max(np.abs(s)) * sndAmp[i]
        
        # Smooth onset/offset 
         # Parameters for smoothing
        durSm = 0.005
        nSm = round(durSm*fs)
        # Scaling factor
        scalingInOut = np.ones(len(s))
        scalingInOut[:nSm] = np.linspace(0,1,nSm)
        scalingInOut[-nSm:] = np.linspace(1,0,nSm)
        # Multiply scaling
        s = s * scalingInOut
        
        # Concatenate audio
        audio = np.block([audio, s])
    
    
    # Convert to 16-bit data
    audio = audio.astype(np.int16)
    
    # Reshape audio matrix for 8 sounds
    audio.shape = (3,int(round(sndDur[i] * fs)))
    
    return audio,fs

def ardSetUp():
    # Get system name
    systName = socket.gethostname()
    
    # Define port based on system name
    if systName  == "fin-de-semaine.crulrg.local":
        portIn = '/dev/cu.usbmodem14101'
        portOut = ''
    elif systName == 'Scientifica-PC':
        # portIn = 'COM16'
        portIn = 'COM23'
        portOut = ''
    elif systName == 'DESKTOP-M408J26': # Behavior room computer #1
        portIn = 'COM7'
        portOut = ''
    elif systName == 'DESKTOP-15LB358' or systName == 'vbpbehavior2': # Behavior room computer #2
        portIn = 'COM6'
        portOut = ''
    elif systName == 'vbpbehavior3': # Behavior room computer #2
        portIn = 'COM3'
        portOut = ''
    elif systName == 'vbpbehavior4': # Behavior room computer #2
        portIn = 'COM3'
        portOut = ''
    elif systName == 'vbpbehavior5': # Behavior room computer #2
        portIn = 'COM3'
        portOut = ''
    elif systName == 'vbpbehavior6': # Behavior room computer #2
        portIn = 'COM3'
        portOut = ''
    elif systName == 'vbpbehavior2':
        portIn = 'COM7'
        portOut = ''
    else:
        print('Please define port for arduinos for this computer')
        portIn = -1
        portOut = -1
    
    try:
        # Open communication with Arduino IN
        ardIn = serial.Serial(port=portIn, baudrate=115200, timeout=.1)
    
        return ardIn
    except:
        print('Error while trying to connect to ARDUINO.')
        print('Are you sure it is plugged in?')       
        return -1

def readArduino(ardIn, t0=time.perf_counter()):
    # % d(0) = absolute time
    # % d(1) = lever value
    # % d(2) = lickspout1 value
    # % d(3) = lickspout2 value
    # % d(4) = accelerator X value
    # % d(5) = accelerator Y value
    # % d(6) = accelerator Z value

    # Create data d
    d = np.zeros(7)
    
    if ardIn != 'NoArduino':
        # Send byte to prepare arduino to read    
        ardIn.write(b'R')
        
        # Read line
        X = ardIn.readline()
        
        # Determine time
        d[0] = time.perf_counter()-t0
        
        if len(X) == 8:
            # % Determine lever value
            d[1] = X[0]*255 + X[1]
            d[1] = d[1] * -0.0049
            
            # % Determine lick value
            d[2] = (X[2] - 100) // 10
            d[3] = (X[2] - 100) % 10
    
            # Determine accelerometer
            d[4] = X[3]
            d[5] = X[4]
            d[6] = X[5]
        else:
            d[1:] = np.nan
    else:
        # Random lick rate for each port
        lickRate = 2
        sr = 0.002 
        # Determine time
        d[0] = time.perf_counter()-t0
        
        # Random lever mvt
        d[1] = np.random.rand(1)[0]       
        
        # Determine if lick or not based on lick rate and targeted sampling rate
        d[2] = np.random.rand(1)[0] < lickRate*sr
        d[3] = np.random.rand(1)[0] < lickRate*sr
        
        # Determine accelerometer
        d[4] = 0
        d[5] = 0
        d[6] = 0        
        
        # Pause for creating a delay similar to reading from a real arduino
        time.sleep(sr)
        
    return d

def writeArduino(ardIn,code):
    if ardIn != 'NoArduino':
        ardIn.write(code)
        

def refMVT(ardIn,nRef=100):
    if ardIn != 'NoArduino':
        FLAG = True
        k = 1
        while FLAG:
            
            # Measure baseline movement
            MVTBL = []
            for i in range(nRef):
                d = readArduino(ardIn)
                MVTBL.append(d[1])
            
            # 
            if np.std(MVTBL) < 0.05:
                FLAG = False
                m = np.mean(MVTBL)
                print('Measured BL lever movement: '+"{0:.2f}".format(m))
                if np.mean(MVTBL) < -4.9:
                    print('Lever voltage is off. Are you sure it is connected???')
            else:
                k += 1
                print('Try again BL measurements #'+str(k))
    else:
        MVTBL = 0
    
    return MVTBL

def detectMVT(ard,data,idx,params,t0=time.perf_counter()):
    # Params
    dur = params[0]
    mvt0 = params[1]
    thresh = params[2]
    
    # Set up
    deltaT = 0
    deltaMVT = 0
    tStart = time.perf_counter()
    
    # Measure movement for duration dur. Exit measurements if deltaMVT greater than set threshold
    while deltaT < dur and deltaMVT < thresh:
        data[idx,:] = readArduino(ard,t0)
        deltaT = time.perf_counter()-tStart
        idx += 1
        deltaMVT = np.absolute(data[idx-1,1]-mvt0)
        if np.isnan(deltaMVT):
            deltaMVT = 0
    
    # If MVT is detected return isMVT = True
    isMVT = True
    if deltaMVT < thresh:
        isMVT = False
    
    # Return recorded data, index of data and isMVT
    return data, idx, isMVT

def recMVT(ard,data,idx,dur,t0=time.perf_counter()):    
    # Set up
    deltaT = 0
    tStart = time.perf_counter()
    
    # Measure movement for duration dur
    while deltaT < dur:
        data[idx,:] = readArduino(ard,t0)
        deltaT = time.perf_counter()-tStart
        idx += 1

    # Return recorded data, index of data and isMVT
    return data, idx

def printPerfo(resp,trType,N):
    
    # Remove extra trials from response and trType MTX
    resp = resp[:N+1,:]
    trType = trType[:N+1,:]
    
    # Calculate nGo, nNo-GO, nH, nFA
    nH = sum(np.logical_and(trType[:,1] > 0 , resp[:,2] > 0))
    nGo = sum(np.logical_and(trType[:,1] > 0 , resp[:,5] < 1)) # Exclude early presses
    nFA = sum(np.logical_and(trType[:,1] < 1 , resp[:,2] > 0))
    nNoGo = sum(np.logical_and(trType[:,1] < 1 , resp[:,5] < 1)) # Exclude early presses
    
    # Determine hit and FA rates, and performance
    if nGo > 0:
        HR = nH/nGo * 100
    else:
        HR = -1
    
    if nNoGo > 0:
        FAR = nFA/nNoGo * 100
    else:
        FAR = -1
    Perfo = (nH + nFA)/(nGo + nNoGo) * 100 
    
    # Determine hit rate corrected to target response window
    targetRespWindow = 0.8 # Used to display HRate corrected
    rt = resp[:,3] - resp[:,1]
    nHCorr = sum(np.logical_and(trType[:,1] > 0, resp[:,2] > 0, rt < targetRespWindow))
    if nGo > 0:
        HRCorr = nHCorr/nGo * 100
    else:
        HRCorr = -1   
    
    # Print Performance
    print('AVERAGE PERFORMANCE:')
    print('H='+str(int(nH))+'\tM='+str(int(nGo-nH))+'\tFA='+str(int(nFA))+'\tCR='+str(int(nNoGo-nFA)))
    print('HR='+"{0:.1f}".format(HR)+'\tHRCorr='+"{0:.1f}".format(HRCorr)+'\tFAR='+"{0:.1f}".format(FAR)+'\tBOTH='+"{0:.1f}".format(Perfo))
    return nH, nGo, nFA, nNoGo