#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 16:51:13 2021

@author: vincentbp
"""


# This is a script to do variable probability conditioning. Inspired by Fiorillo et al Science 2003
# It was based on the toneConditioningWIP.mat program in MATLAB

# V2 Jan 2022
# Main improvements:
# Data is saved differently (params in a .json file, trial matrix and lick results in a csv, arduino data in a .csv)
# Some issue with timing fixed so that tUS-tCS = durPreReinforcement

# V3 Apr 2022
# Main improvements:
# The user can put'variable' as a value for the water reward size parameter (amountReward). This option will deliver reward of different magnitudes, randomized for each trial.
# The way lick rasters are produced and saved is more stable. Uses a fixed sampling rate (200 Hz)
# Added option AN '00' for testing the script without an arduino connected. Will give random lick

# V5 March 2025
# Main improvements:
# Display of results is done within the same script. The user does not need to start a separate command for displaying results.

# Imports
import os
# import socket
import Helpers.hfb_lib as hfb
import sys
import numpy as np
import simpleaudio as sa
import time
import matplotlib.pyplot as plt
import datetime
# import scipy.io as io
import json
import pandas as pd
# %% To change all graphs
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['axes.spines.right'] = False
matplotlib.rcParams['axes.spines.top'] = False
matplotlib.rcParams['axes.linewidth'] = 0.5
matplotlib.rcParams['ytick.major.width'] = 0.5
matplotlib.rcParams['xtick.major.width'] = 0.5
plt.close('all')

# If MAC
# os.system('clear')
# IF WINDOWS
clear = lambda: os.system('cls')
clear()

# PARAMS =======================================

# Define animal ID and user id
an = input('Please enter animal ID: ')
# an = '01' # For testing the rig
# an = '00' # For testing without the rig. Will just choose randomly between left or right with random licking.
userID = input('Please enter your user ID: ')
if userID == '':
    userID = 'vbp'

# Define params specific for that animal
params = hfb.defineParams(an)
if params == -1:
    print('Params are not defined for animal #'+an)
    sys.exit()
    
# Ask for light cue (useful for linking with camera recording)
# The light cue turns for 1 sec after the reward consumption part
ask = input('Turn on light cues? [y]/n')
if ask == '':
    ask = 'y'
if ask == 'y':
    lightCue = True
    durLight = 0.5
else:
    lightCue = False

# Edit params that are behavior specific
params['BehaviorType'] = 'Prob. conditioning'
params['UserID'] = userID
params['DateTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
params['LightCues'] = lightCue


# Display animal params
print('\nParams for an# '+an+':\n')
for key, value in params.items() :
    print (key, value)

# N s ---
nTrials = params['nTrials']

# Amount reward
amountReward = params['amountReward']
if amountReward == 'variable':
    amountReward = [0.3,1,2.5,5,10]
else:
    amountReward = [amountReward]

# Durations ---
durITI = params['durITI']
durConsumption = params['durConsumption']
durPreReinforcement = params['durPreReinf']
durSess = params['durTotal']
durSound = params['durSound']

# Trial type selection --- 
fractEachTone = params["fractEachTone"] # Fraction of each tone presentation + fraction reward no tone position 4. Warning sum(fractEachTone) should be 1
probRew = np.array(params['probRew'])
probPun = np.array(params['probPun'])

if np.any((probPun+probRew) > 1):
    print('')
    print('P(rew)+P(punish.) <= 1 for each tone. Please revise parameters for an #'+an)
    sys.exit()    

# Sound freq
sndFreq = [3000, 6000, 12000]
params['SoundFrequencies'] = sndFreq

# Laser
# TBD

# Add parameters for calculation of BL and consumatory perfo.
durBL = 1;
durPost = 2;
params['durBaseline'] = durBL
params['durPostrew'] = durPost

# SETUP ========================================================================

# Randomize amount reward
amountRewList = np.array([])
while amountRewList.shape[0] < nTrials:
    amountRewList = np.concatenate((amountRewList,np.random.permutation(amountReward)))
amountRewList = amountRewList[:nTrials]

# Determine duration of solenoid valve opening for water reward from calibration data
durValve = np.zeros(nTrials)
for i in range(len(durValve)):

    durValve[i] = hfb.volReward2duration(amountRewList[i],2)
    if durValve[i] == -1:
        print('Something went wrong when determining valve opening durations')
        sys.exit()

print('1')
# Open communication with Arduino !!!!
if an == '00':
    ardIn = 'NoArduino'
else:
    ardIn = hfb.ardSetUp()

print('2')

ardIdx = 0;
if ardIn == -1:
    sys.exit() 

print('3')


# Initialize arduino data matrix
estSamplingRate = 260
estDur = 120 # minutes
nSamples = estSamplingRate*estDur*60
ardData = np.zeros((nSamples,7))*np.nan
print('DONE!\n')

# Initialize response MTX
responseMTXHeader = ['timeTrialStart','timeTone','timeReinforcement']
respMTX = np.zeros((nTrials,3))*np.nan


# Randomize trials and store them in trialTypeMTX
trialTypeMTX,trialTypeMTXHeader = hfb.randTrialsPROB(nTrials,fractEachTone,probRew,probPun,durITI)

# Initialize trial matrix
trmtx = pd.DataFrame(np.ones((nTrials,9))*np.nan,columns=['tone_id','reward','dur_iti','t_start','t_tone','t_reinf','bl_lickrate','anticip_lickrate','conso_lickrate'])

# Initialize lick raster
lickSR = 200
tR = np.arange(-durBL,durPreReinforcement+durPost,1/lickSR)
lick_ras = pd.DataFrame(np.ones((nTrials,len(tR))) * np.nan,columns=tR)

# Remove punishment on 10
nTrialRemovePunishment = 10
trialTypeMTX[np.where(trialTypeMTX[:nTrialRemovePunishment,2] < 0)[0],2] = 0

# Initialize sounds
audio,a_fs = hfb.sndWavPROB(durSound,sndFreq)

# Set up save folder and name 
if not os.path.isdir('Data'): # Check if folder 'Data' exists
    os.mkdir('Data')
if not os.path.isdir('Data'+os.path.sep+an): # Check if folder for animal exists
    os.mkdir('Data'+os.path.sep+an)
saveName = 'ProbCond_'+an+'_'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') # Make sure you do not overwrite previous data by creating a different save name by including date and time behavior was started

# Save params as .json
json = json.dumps(params) # create json object from dictionary
f = open('Data'+os.path.sep+an+os.path.sep+saveName+'_params.json',"w") # open file for writing, "w" 
f.write(json) # write json object to file
f.close() # close file

# Initialize files (lick raster and trial matrix) for saving results during behavior <--
lick_ras.to_csv('Data'+os.path.sep+an+os.path.sep+saveName+'_lickRaster.csv')
trmtx.to_csv('Data'+os.path.sep+an+os.path.sep+saveName+'_trialMTX.csv')

#%% Initialize figure

# Set up
plt.style.use('dark_background')
ls_col = ['aqua', 'slateblue', 'darkorange', 'deeppink']
fig = plt.figure(figsize=(10,6))

#Plot anticipatory lick rate
ax0 = fig.add_subplot(2,2,1) 
a = ax0
avg_anticip = []
for i in range(4):
    # l, = a.plot([],[],'o',color=ls_col[i])
    l, = a.plot([],[],'o',color=ls_col[i])
    avg_anticip.append(l)
a.set_ylim([-0.2,10])
a.set_ylabel('Lick rate (lick/s)')
a.set_xlabel('Trial #')
a.set_title('Anticipatory licking')

# Plot session average lick/s
ax2 = fig.add_subplot(2,2,2) # Plot raster lick rate
a = ax2
sessavg_lick = []
for i in range(4):
    l, = a.plot([],[],color = ls_col[i])
    sessavg_lick.append(l)
a.vlines(0,*[0,15],color = 'r')
a.vlines(durPreReinforcement,*[0,15],color = 'b')
a.vlines(durSound,*[0,15],color = 'w',ls=':')
a.set_xticks([0,durPreReinforcement])
a.set_xlabel('Time from CS (s)')
a.set_ylabel('Lick rate (lick/s)')
a.set_title('Session average')
a.set_xlim([-durBL,durPreReinforcement+durPost])
a.set_ylim([0,15])

# Rasters lick
ax1 = []
ax1.append(fig.add_subplot(2,4,5)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,6)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,7)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,8)) # Plot raster lick rate
lickrasplot = []
for i in range(4):
    a = ax1[i]
    a.vlines(0,*[-0.5,nTrials],color = 'r',lw=0.5)
    a.vlines(durPreReinforcement,*[-0.5,nTrials],color = 'b',lw=0.5)
    e = a.scatter(0,0,marker='|',color = ls_col[i],linewidths=0.5)
    lickrasplot.append(e)
    a.set_xticks([0, durPreReinforcement])
    a.set_xlim([-durBL,durPreReinforcement+durPost])
    a.set_ylim([-0.5,1.5])
    if i == 0:
        a.set_ylabel('Trial #')
        a.set_xlabel('Time from CS (s)')
        a.set_title('Lick rasters')

fig.tight_layout()
plt.pause(0.1)

#%%
# RUN TRIALS ====================================================================
AUTOSTOP = False
t0 = time.perf_counter()
totalReward = 0
N = 0

try:    
    while N+1 <= nTrials and time.perf_counter() - t0 < durSess:
        
        # Load params specific for each trial
        trType = int(trialTypeMTX[N,1])
        rewarded = trialTypeMTX[N,2]
        durITI = trialTypeMTX[N,3]
        
        # Display trial number & trial type
        print('Trial '+str(int(N+1))+':')
        # Time remaining
        tRemaining = (durSess - (time.perf_counter()-t0))/60
        print('Time remaining:'+"{0:.1f}".format(tRemaining)+' min')
        if trType < 3:
            print('Freq:'+"{0:.1f}".format(sndFreq[trType])+' P(rew):'+"{0:.1f}".format(probRew[trType])+" P(pun):{0:.1f}".format(probPun[trType])+' Reward:'+"{0:.1f}".format(rewarded*amountRewList[N])+" uL")
        else:
            print('Freq:none; P(rew):'+"{0:.1f}".format(probRew[trType])+" P(pun):{0:.1f}".format(probPun[trType])+' Reward:'+"{0:.1f}".format(rewarded*amountRewList[N])+" uL")
         
        # ITI ===========
        print('ITI: '+"{0:.2f}".format(durITI)+'sec')
        respMTX[N,0] = time.perf_counter() - t0 # Trial Start
        # Record arduino during ITI
        ardData, ardIdx = hfb.recMVT(ardIn,ardData,ardIdx,durITI,t0)
        
        
        # CONDITIONED STIM (CS) =======================
        if trType < 3:
            print('Tone')
            # Play tone 
            play_obj = sa.play_buffer(audio[int(trType),:], 1, 2, a_fs)
            # NOTE : Function is slow. The lag is 0.025 sec. Need to improve this and test other methods
        
        # Timing sound onset (CS). Note because it is unclear when the sound starts playing during the lag of the play_buffer function. It is better for accuracy of tUS to calculate tCS here.
        respMTX[N,1] = time.perf_counter() - t0 
        
        # PRE-REINFORCEMENT ==================      
        # Record arduino during pre-reinf
        ardData, ardIdx = hfb.recMVT(ardIn,ardData,ardIdx,durPreReinforcement,t0)
        
        # UNCONDITIONED STIMULUS (US) =======================
        respMTX[N,2] = time.perf_counter() - t0 # Timing US
        if rewarded == 1:
            print('REWARD')
            hfb.writeArduino(ardIn,b'E')
            totalReward += amountRewList[N]
        elif rewarded == -1:
            print('PUNISHMENT')
            hfb.writeArduino(ardIn,b'L')
        elif rewarded == 0:
            print('NO REINFORCEMENT!')
            
        # Record arduino during reward
        ardData, ardIdx = hfb.recMVT(ardIn,ardData,ardIdx,durValve[N],t0)
        
        # Close air or water solenoid
        hfb.writeArduino(ardIn,b'O')
        hfb.writeArduino(ardIn,b'M')
        
        # Post trial (consumption) ========
        ardData, ardIdx = hfb.recMVT(ardIn,ardData,ardIdx,durConsumption,t0)
        
        # Cue for camera recordings ==========
        if lightCue:
            hfb.writeArduino(ardIn,b'I') # TURN LED ON
            ardData, ardIdx = hfb.recMVT(ardIn,ardData,ardIdx,durLight,t0)
            hfb.writeArduino(ardIn,b'J') # TURN LED OFF
         

        # -----------------SAVING-----------------------------
        # Calculate licks for that trial and save -------------
        
        # Extract lick data and time
        t = ardData[:ardIdx,0]
        lick = np.concatenate([np.array([False]),np.diff(ardData[:ardIdx,2]) > 0]) # Define lick as onset of voltage change from the sensor
        
        # Crop data for trial only
        tCS = respMTX[N,1]
        tUS = respMTX[N,2]
        idxTrial = np.logical_and(t >= tCS - durBL, t <= tUS + durPost)
        
        # Extract lick data for that trial
        t = t[idxTrial]
        lick = lick[idxTrial]
        
        # Extract lick timestamps
        lick_ts = (t - t[0] - durBL)[lick > 0]
        
        # Binarized these timestamps
        lick4save = np.histogram(lick_ts,np.arange(-durBL-1/2/lickSR,durPreReinforcement+durPost+1/2/lickSR,1/lickSR))[0]
        
        # Add to lick raster
        lick_ras.iloc[N,:] = lick4save
        
        # Save lick raster
        lick_ras.to_csv('Data'+os.path.sep+an+os.path.sep+saveName+'_lickRaster.csv')
        
        # Trial info ------------------------------
        
        # Calculate average licking for this trial
        avgLick = np.zeros(3)

        # Calculate baseline lick rates
        idxBL = np.logical_and(t >= tCS-durBL, t <= tCS)
        avgLick[0] = np.sum(lick[idxBL])/durBL
        
        # Calculate anticipatory lick rates
        idxPre = np.logical_and(t >= tCS, t <= tUS)
        avgLick[1] = np.sum(lick[idxPre])/(tUS - tCS)
        
        # Calulcate consumatory lick rates
        idxPost = np.logical_and(t >= tUS, t <= tUS + durPost)
        avgLick[2] = np.sum(lick[idxPost])/durPost
        
        trmtx_line = np.concatenate((trialTypeMTX[N,1:],respMTX[N,:],avgLick))  
        trmtx_line[1] = amountRewList[N] * rewarded # Change rewarded to amount
        if trmtx_line[1] < 0: # If punishment make it -1
            trmtx_line[1] = -1
        
        # Append this line to trial matrix
        trmtx.iloc[N,:] = trmtx_line
        
        # Save trial matrix
        trmtx.to_csv('Data'+os.path.sep+an+os.path.sep+saveName+'_trialMTX.csv')
        
        # ------- PLOT RESULTS ---------------------------------------------
        
        # Note: It only updates the line for that trial type 'trType' (to save time!)
        
        # #Plot anticipatory lick rate
        x = np.arange(nTrials) + 1
        # if np.sum(trmtx['tone_id'] == trType) > 0:
        x = x[trmtx['tone_id'] == trType]
        y = trmtx['anticip_lickrate'][trmtx['tone_id'] == trType]
        avg_anticip[trType].set_data(x,y)
        ax0.set_xlim([0,N+2])
        
        # #Plot trial average lick rate
        # if np.sum(trmtx['tone_id'] == trType) > 0:
        l = lick_ras.loc[trmtx['tone_id'] == trType].to_numpy()
        l *= lickSR
        m_lick = np.nanmean(l,axis=0)
        m_lick = np.convolve(m_lick, np.ones(20)/20, mode='same')
        sessavg_lick[trType].set_data(tR,m_lick)
        
        # Update raster plot
        l = lick_ras.loc[trmtx['tone_id'] == trType].to_numpy()
        # Convert to event scatter
        y=  np.ones_like(l) * np.nan
        y[l > 0] = 1
        y = (y.T * np.arange(l.shape[0])).T
        y = y[y >= 0]
        
        x = np.ones_like(l) * np.nan
        x[l > 0] = 1
        x *= tR
        x = x[~np.isnan(x)]
        
        lickrasplot[trType].set_offsets(np.array([x,y]).T)
        ax1[trType].set_ylim([-0.5,np.max(y)+0.5])
    
        plt.pause(0.1)
        
        # End of trial, increment N ========
        # Display number of reward thus far
        print('Total volume of reward: '+str(totalReward)+' uL')
        print('')
        
        # Increment N, the trial index
        N += 1
        
except KeyboardInterrupt:
    print('')
    print('Exit behavior')

# CLEAN UP ============================
hfb.writeArduino(ardIn,b'J') # TURN LED OFF
# Close air or water solenoid
hfb.writeArduino(ardIn,b'O')
hfb.writeArduino(ardIn,b'M')

if ardIn != 'NoArduino':
    ardIn.close()

# SAVE arduino data
ardData = ardData[:ardIdx,:]

# Create header text
strHeader = 'TimeMATLAB, MVT, LICK1, LICK2, ACCX, ACCY, ACCZ'

# Save matrix info array into a csv
np.savetxt('Data'+os.path.sep+an+os.path.sep+saveName+'_ArdData.csv', ardData, 
           fmt='%f', 
           delimiter=',',
           header=strHeader)

# Save figure
fig.savefig('Data'+os.path.sep+an+os.path.sep+saveName+'_fig.png')

print('Data were saved properly!')


print('Done!')