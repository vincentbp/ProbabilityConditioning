# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 14:40:16 2022

@author: VBP-Behavior_2
"""

import numpy as np


X = np.load('G:/My Drive/Behavior/ProbabilityConditioning/Calibration/vbpbehavior2/dataCalibration_valve2.npy',allow_pickle=True).item()

X['valveDurTested'] = np.array([0.008, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09])
X['rewardDelivered'] = [0.25,0.5, 2.0, 4.0, 6.1, 9.000000000000002, 11.000000000000002, 15.5, 18.000000000000004, 20.499999999999996]

np.save('G:/My Drive/Behavior/ProbabilityConditioning/Calibration/vbpbehavior2/dataCalibration_valve2.npy',X)