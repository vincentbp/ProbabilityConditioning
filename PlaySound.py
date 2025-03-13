#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 17:12:39 2022

@author: vbp
"""

# This is a script to play audio stim at various frequencies and time

# Imports
import hfb_lib as hfb
import simpleaudio as sa
import time


# PARAMS =======================================

# Display animal params
an = '01' #00 if not connected to an arduino; 01 if connected

# N s ---
nTrials = 30

# Durations ---
durBL = 5 #in second before starting stimulus
durITI = 15
durSound = 0.5

# Sound freq
sndFreq = [3000, 6000, 12000]


# SETUP ========================================================================

# Open communication with Arduino !!!!
if an == '00':
    ardIn = 'NoArduino'
else:
    ardIn = hfb.ardSetUp()
    
# Initialize sounds
audio,a_fs = hfb.sndWavPROB(durSound,sndFreq)

# Reset trigger off
hfb.writeArduino(ardIn,b'J') # TURN LED OFF
print('Loading...')
print('Total run time is '+"{0:.2f}".format(durBL+durITI*nTrials)+'sec')
time.sleep(2)


# RUN TRIALS ====================================================================

t0 = time.perf_counter()
N = 0
trType = 0

# Cue for camera recordings ==========
print('Triggered (PIN 12 HIGH)')
hfb.writeArduino(ardIn,b'I') # TURN LED ON

print('Baseline : '+"{0:.2f}".format(durBL)+'sec')
time.sleep(durBL)

try:    
    while N+1 <= nTrials:        
        
        # Display trial number & trial type
        print('Trial '+str(int(N+1))+'/'+str(int(nTrials))+':')
        print('Freq:'+"{0:.1f}".format(sndFreq[trType]))
        
        print('Tone')
        play_obj = sa.play_buffer(audio[int(trType),:], 1, 2, a_fs)
        
        
        # ITI ===========
        print('ITI: '+"{0:.2f}".format(durITI)+'sec')
        time.sleep(durITI)
        print()
        
        
        # Increment N, the trial index
        N += 1
        trType +=1
        if trType >= len(sndFreq):
            trType = 0

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


print('Done!')