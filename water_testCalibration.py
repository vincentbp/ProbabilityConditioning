#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 10:40:35 2021

@author: vincentbp
"""


# Imports

import hfb_lib as hfb
import sys
# import time
import vbp

# Params
n = 100

# User input
x = input('Enter reward size:' )
if x == '':
    print('Please enter valid reward size in uL')
    sys.exit()

rewSize = float(x)
if rewSize < 0.1 or rewSize > 30:
    print('Reward size value needs to be larger than 0.1 and smaller than 30 uL')
    sys.exit()
    
# Extract duration of valve opening
durValve = hfb.volReward2duration(rewSize,2)
if durValve == -1:
    print('Error while calculating valve duration')
    sys.exit()
    
# Open communication with Arduino !!!!
ardIn = hfb.ardSetUp()
ardIdx = 0;
if ardIn == -1:
    sys.exit() 

# Print and wait for user to fill reservoir
print('Testing reward size:'+"{0:.3f}".format(rewSize)+' uL')
input('Fill reservoir and press ENTER\n')

# Run test n times
for i in range(n):
    
    # Open valve
    ardIn.write(b'E')
    
    # Wait durValve seconds
    vbp.pause(durValve)
    
    # Close valve
    ardIn.write(b'O')
    
    # Wait 0.2 sec to reopen, for stability
    vbp.pause(0.1)

print('Total volume delivered = '+"{0:.3f}".format(rewSize*n*10**-3)+' mL')

# CLEAN UP ============================
ardIn.write(b'J') # TURN LED OFF
# Close air or water solenoid
ardIn.write(b'O')
ardIn.write(b'M')   
ardIn.close()

