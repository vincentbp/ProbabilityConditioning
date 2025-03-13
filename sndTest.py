#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 17:28:57 2021

@author: vincentbp
"""



# This is a script to test sound intensity

# Imports
import hfb_lib as hfb
import simpleaudio as sa
import time

durSound = 1;
sndFreq = [3000, 6000, 12000]
n = 5

# Initialize sounds
audio,a_fs = hfb.sndWavPROB(durSound,sndFreq)

time.sleep(1)
for x in range(n):
    for i in range(3):
        print('Tone = '+str(sndFreq[i]))
        # Play tone 
        play_obj = sa.play_buffer(audio[i,:], 1, 2, a_fs)
        
        time.sleep(5)

