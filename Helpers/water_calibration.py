#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 12:31:02 2021

@author: vincentbp
"""

# Calibrate the duration of solenoid valve opening to reward volumes and save it

import numpy as np
import hfb_lib as hfb
import socket
import os
# import time
import datetime
import matplotlib.pyplot as plt
import vbp

# Params
nTrials = 100 # Nb of repeat for each opening duration
dur2test = np.arange(0.01, 0.15, 0.015)

# Open communication with arduino  
ard = hfb.ardSetUp()
if ard == -1:
    sys.exit() 
    
# Initialize variables
valveID = 2;

# Load previous calibration
systName = socket.gethostname()
if os.path.isfile('Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy'):
    calibration = np.load('Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy',allow_pickle='TRUE').item()
    dur_prev = calibration["valveDurTested"]
    r_prev = calibration["rewardDelivered"]
else:
    print('No water calibration files found in "Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy"')
    calibration = {
        'valveID': 2,
        'valveDurTested': np.nan,
        'rewardDelivered': np.nan,
        'date': np.nan
        }
    dur_prev = np.nan
    r_prev = np.nan

rew = [] # To store value read at each calibration step


try: # In case user hits ctrl+c
    # Run through all duration tests
    for d in dur2test:
        
        # Some message
        print('\nTesting duration:'+"{0:.3f}".format(d)+ ' sec')
        input('Fill water and press ENTER')
        
        # Open valve for d seconds nTrials times
        for i in range(nTrials):
            ard.write(b'E') # Open valve
            vbp.pause(d) # Wait specified amoiunt of time
            ard.write(b'O') # Close valve 
            vbp.pause(0.1)
            
        # Query user for amount of reward in mL
        SATISFIED = False;
        while not(SATISFIED):
            x = float(input('Enter amount of water in mL: '))
            Q = input("You've entered "+"{0:.3f}".format(x)+" mL. Accept? [Y]/N: ")
            if Q == '' or Q == 'Y' or Q == 'y':
                SATISFIED = True
        
        # Append calibvration data        
        rew.append(x/nTrials*1000)
        
    # Plot data
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1) 
    l1 = ax.plot(dur_prev,r_prev,'kx',label = 'Previous calibration')
    l2 = ax.plot(dur2test,rew,'bx', label='New calibration')
    ax.legend()
    ax.set_xlabel('Valve opening duration (s)')
    ax.set_ylabel('Reward amount (uL)')
    plt.show()
    
    # Ask user if calibration is accepted
    Q = input('Accept calibration? [Y]/N: ')
    
    if Q == '' or Q == 'Y' or Q == 'y':
        # Update calibration data
        calibration['valveID'] = valveID
        calibration['valveDurTested'] = dur2test
        calibration['rewardDelivered'] = rew
        date = datetime.datetime.now()
        calibration['date'] = [date.year, date.month, date.day]
        
        # If a folder for this computer does not exist, create it
        systName = socket.gethostname()
        if not os.path.isdir('Calibration'+os.path.sep+systName):
            os.mkdir('Calibration'+os.path.sep+systName)
        
        # Save calibration data to this folder
        np.save('Calibration'+os.path.sep+systName+os.path.sep+'dataCalibration_valve'+str(valveID)+'.npy',calibration)
    else:
        print('Calibration data were not saved.')
        
        
except KeyboardInterrupt:
    print('Calibration was stopped before the end!')
    print('Calibration data were not saved.')
