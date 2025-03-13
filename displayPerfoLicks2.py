#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 20:46:47 2021

@author: vincentbp
"""


# Read result and lick txt file and plot lick rate ETC

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import warnings
import os
import glob
import sys
import json



plt.style.use('dark_background')

fig = plt.figure()
ax0 = fig.add_subplot(2,2,1) #Plot anticipatory lick rate
ax1 = []
ax1.append(fig.add_subplot(2,4,5)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,6)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,7)) # Plot raster lick rate
ax1.append(fig.add_subplot(2,4,8)) # Plot raster lick rate
ax2 = fig.add_subplot(2,2,2) # Plot raster lick rate


np.seterr(all="ignore")

# File name folder name

# Define animal ID and user id
an = input('Please enter animal ID: ')
path = 'Data'+os.path.sep+an+os.path.sep
if not os.path.isdir(path): # Check if folder for animal exists
    print('Animal: '+an+' does not exist!')
    sys.exit()


def animate(i):
    # SOME CODING TO FIND LATEST FNAME TO LOAD DATA FROM
    list_of_files = glob.glob(path+'*lickRaster.csv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    fname = latest_file[:-14]
    
    # Load latest params
    f = open(fname+'Params.json','r')
    json_obj = f.read()
    params = json.loads(json_obj)
    f.close()
    
    # Determine timing of reward and window lick rasters
    # Parameters
    tRew = params['durPreReinf']
    win = [-1,tRew+2]
    
    # PLOT #1 ANTICIPATORY LICKING ===============
    # Load data
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        trialMTX = np.genfromtxt(fname+'trialMTX.csv', skip_header=1, delimiter=',')
    
    
    if len(trialMTX) > 0:
        
        # Case in which there is only one line
        if len(trialMTX.shape) < 2:
            trialMTX = np.array([trialMTX])
            
        # Extract trial type, trial #
        trType = trialMTX[:,1]
        trID = np.arange(len(trType))
        
        # Plot lick rate in pre
        ax0.clear()
        
        # Define list of color
        c = ['aqua', 'slateblue', 'darkorange', 'deeppink']
        lbl = []
        for i in range(4):
            lbl.append(trialMTX[trType == i, 2])
        
        # Plot separately for each trial type
        
        for i in range(4):
            lickPre = trialMTX[trType == i,8]
            if len(lickPre) >= 10:
                lickPreAVG = np.convolve(lickPre, np.ones(10), 'same')/10
            else:
                lickPreAVG = np.zeros(len(lickPre)) * np.nan
            tr = trID[trType == i]
            if len(lickPre) > 0:
                ax0.plot(tr,lickPre, 'o', color = c[i], ls='', label= 'Pr='+str(lbl[i][0]))
                ax0.plot(tr,lickPreAVG, color = c[i])
            if np.ceil(max(trialMTX[:,8])) > 0:
                ax0.set_ylim([0, np.ceil(max(trialMTX[:,8]))])
        ax0.set_ylabel('Lick rate (lick/s)')
        ax0.set_xlabel('Trial #')
        ax0.set_title('Anticipatory licking')
        ax0.legend()
        
        # PLOT #2 Raster lick ===============
        X = np.genfromtxt(fname+'lickRaster.csv', delimiter=',')
        t = X[0,:]
        lick = X[1:,:]
        if lick.shape[0] > len(trType):
            lick = lick[:len(trType),:]
            
        # Case in which there is only one line
        if len(lick.shape) < 2:
            lick = np.array([lick])
        
        
        # Create an event list for each trial type
        ax2.clear()
        for j in range(4):
            ev = []
            for i in range(lick.shape[0]):
                if trType[i] == j:
                    ev.append(t[lick[i,:] > 0])
            ax1[j].clear()
            ax1[j].plot([tRew,tRew],[-1, len(ev)],color='b')
            ax1[j].plot([0,0],[-1, len(ev)],color='r')
            ax1[j].eventplot(ev,color = c[j],linewidths=0.5)
            
            ax1[j].set_yticks([0,len(ev)-1])
            ax1[j].set_xticks([0, tRew])
            ax1[j].set_xlim(win)
            if j == 0:
                ax1[j].set_ylabel('Trial #')
                ax1[j].set_xlabel('Time from CS (s)')
                ax1[j].set_title('Lick raster')
            plt.tight_layout()
            
            # Convert licks to session average
            sr = len(t)/np.diff(win)
            v = np.ones(round(float(sr) /5))*5 # averaging window is 200 ms
            m = np.sum(lick[trType == j,:],axis = 0)/len(ev)
            
            mLick = np.convolve(m, v, mode='same');
            
            # Plot session average
            ax2.plot(t,mLick,color = c[j])
            
        yl = ax2.get_ylim()
        ax2.plot([0,0],yl,color = 'r')
        ax2.plot([params['durSound'],params['durSound']],yl,color = 'r',ls = ':')
        ax2.plot([tRew,tRew],yl,color = 'b')
        ax2.set_ylim(yl)
        ax2.set_xticks([0,tRew])
        ax2.set_xlabel('Time from CS (s)')
        ax2.set_ylabel('Lick rate (lick/s)')
        ax2.set_title('Session average')

    
ani = animation.FuncAnimation(fig, animate, interval=500)
plt.show()