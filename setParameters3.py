#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 17:25:12 2022

@author: vbp
"""

# V3: with laser params

import sys
import os
import json
import Helpers.hfb_lib as hfb
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QRadioButton, QButtonGroup
from PyQt5.QtWidgets import QPushButton, QMessageBox
from PyQt5.QtCore import QSize    
from PyQt5.QtGui import QFont


# These are the default parameters 
params = {
    # AN id and syst name
    "animalID": '',
    "computerName": '',
    "BehaviorType": "N/D",
    
    # N s
    "nTrials": 1000,
    "amountReward": 5, # In uL. Run calibration 
    "fractEachTone": [0.5, 0, 0.5, 0], # Fraction of each tone presentation + fraction reward no tone position 4. Warning sum(fractEachTone) should be 1
    "probRew": [0, 0, 1, 1],
    "probPun": [0, 0, 0, 0],
        
    # Durations
    "durITI": [10 ,45],#[u max]
    "durConsumption": 4, #Time after reward delivery
    "durPreReinf": 1.5, # Includes sound duration
    "durTotal": 1800, # Duration in sec of the whole session
    "durSound": 1.5, # in sec
   
    # Laser
    "laser":{'fract_laseron':0, # between [0 and 1] in 0.1 increment
             'timing':'both', # values can be 1-'cue' 2-'reinf' 3-'both'
             'n_trial_omit': 5, # number of trial to omit at begining
             },
    }  
    
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(360, 410))    
        self.setWindowTitle("Edit conditioning parameters") 
        
        # AN ID
        H = 15
        self.labelANID = QLabel(self)
        self.labelANID.setText('ANIMAL ID:')
        self.labelANID.move(20, H)
        self.lineANID = QLineEdit(self)
        self.lineANID.move(120, H)
        self.lineANID.resize(200, 25)

        
        # Number of trials
        H +=30
        self.labelNTrials = QLabel(self)
        self.labelNTrials.setText('N Trials:')
        self.labelNTrials.move(20, H)
        self.lineNTrials = QLineEdit(self)
        self.lineNTrials.move(120, H)
        self.lineNTrials.resize(40, 25)
        self.lineNTrials.insert(str(params['nTrials']))
        
        # Amount of reward
        H += 30
        self.labelAmount = QLabel(self)
        self.labelAmount.setText('Amount reward:')
        self.labelAmount.move(20, H)        
        self.lineAmount = QLineEdit(self)
        self.lineAmount.move(120, H)
        self.lineAmount.resize(70, 25)
        self.lineAmount.insert(str(params['amountReward']))
        self.slabelAmount = QLabel(self)
        self.slabelAmount.setText('(uL); or variable')
        self.slabelAmount.setFont(QFont('Arial', 10))
        self.slabelAmount.move(190, H)
        
        # Fraction for each tone
        H += 30
        self.labelFraction = QLabel(self)
        self.labelFraction.setText('Fraction tone:')
        self.labelFraction.move(20, H)
        
        self.labelFraction1 = QLabel(self)
        self.labelFraction1.setText('3k')
        self.labelFraction1.move(150, H)
        self.labelFraction1.setFont(QFont('Arial', 10))
        self.lineFraction1 = QLineEdit(self)
        self.lineFraction1.move(120, H)
        self.lineFraction1.resize(30, 25)
        self.lineFraction1.insert(str(params['fractEachTone'][0]))
        
        self.labelFraction2 = QLabel(self)
        self.labelFraction2.setText('6k')
        self.labelFraction2.move(210, H)
        self.labelFraction2.setFont(QFont('Arial', 10))
        self.lineFraction2 = QLineEdit(self)
        self.lineFraction2.move(180, H)
        self.lineFraction2.resize(30, 25)
        self.lineFraction2.insert(str(params['fractEachTone'][1]))
        
        self.labelFraction3 = QLabel(self)
        self.labelFraction3.setText('12k')
        self.labelFraction3.move(270, H)
        self.labelFraction3.setFont(QFont('Arial', 10))
        self.lineFraction3 = QLineEdit(self)
        self.lineFraction3.move(240, H)
        self.lineFraction3.resize(30, 25)
        self.lineFraction3.insert(str(params['fractEachTone'][2]))
        
        self.labelFraction4 = QLabel(self)
        self.labelFraction4.setText('No')
        self.labelFraction4.move(330, H)
        self.labelFraction4.setFont(QFont('Arial', 10))
        self.lineFraction4 = QLineEdit(self)
        self.lineFraction4.move(300, H)
        self.lineFraction4.resize(30, 25)
        self.lineFraction4.insert(str(params['fractEachTone'][3]))
        
        # P(Reward) for each tone
        H += 30
        self.labelPRew = QLabel(self)
        self.labelPRew.setText('P(Reward):')
        self.labelPRew.move(20, H)
        
        self.labelPRew1 = QLabel(self)
        self.labelPRew1.setText('3k')
        self.labelPRew1.move(150, H)
        self.labelPRew1.setFont(QFont('Arial', 10))
        self.linePRew1 = QLineEdit(self)
        self.linePRew1.move(120, H)
        self.linePRew1.resize(30, 25)
        self.linePRew1.insert(str(params['probRew'][0]))
        
        self.labelPRew2 = QLabel(self)
        self.labelPRew2.setText('6k')
        self.labelPRew2.move(210, H)
        self.labelPRew2.setFont(QFont('Arial', 10))
        self.linePRew2 = QLineEdit(self)
        self.linePRew2.move(180, H)
        self.linePRew2.resize(30, 25)
        self.linePRew2.insert(str(params['probRew'][1]))
        
        self.labelPRew3 = QLabel(self)
        self.labelPRew3.setText('12k')
        self.labelPRew3.move(270, H)
        self.labelPRew3.setFont(QFont('Arial', 10))
        self.linePRew3 = QLineEdit(self)
        self.linePRew3.move(240, H)
        self.linePRew3.resize(30, 25)
        self.linePRew3.insert(str(params['probRew'][2]))
        
        self.labelPRew4 = QLabel(self)
        self.labelPRew4.setText('12k')
        self.labelPRew4.move(330, H)
        self.labelPRew4.setFont(QFont('Arial', 10))
        self.linePRew4 = QLineEdit(self)
        self.linePRew4.move(300, H)
        self.linePRew4.resize(30, 25)
        self.linePRew4.insert(str(params['probRew'][3]))
        
        # P(Punishment) for each tone
        H += 30
        self.labelPPun = QLabel(self)
        self.labelPPun.setText('P(Punish.):')
        self.labelPPun.move(20, H)
        
        self.labelPPun1 = QLabel(self)
        self.labelPPun1.setText('3k')
        self.labelPPun1.move(150, H)
        self.labelPPun1.setFont(QFont('Arial', 10))
        self.linePPun1 = QLineEdit(self)
        self.linePPun1.move(120, H)
        self.linePPun1.resize(30, 25)
        self.linePPun1.insert(str(params['probPun'][0]))
        
        self.labelPPun2 = QLabel(self)
        self.labelPPun2.setText('6k')
        self.labelPPun2.move(210, H)
        self.labelPPun2.setFont(QFont('Arial', 10))
        self.linePPun2 = QLineEdit(self)
        self.linePPun2.move(180, H)
        self.linePPun2.resize(30, 25)
        self.linePPun2.insert(str(params['probPun'][1]))
        
        self.labelPPun3 = QLabel(self)
        self.labelPPun3.setText('12k')
        self.labelPPun3.move(270, H)
        self.labelPPun3.setFont(QFont('Arial', 10))
        self.linePPun3 = QLineEdit(self)
        self.linePPun3.move(240, H)
        self.linePPun3.resize(30, 25)
        self.linePPun3.insert(str(params['probPun'][2]))
        
        self.labelPPun4 = QLabel(self)
        self.labelPPun4.setText('12k')
        self.labelPPun4.move(330, H)
        self.labelPPun4.setFont(QFont('Arial', 10))
        self.linePPun4 = QLineEdit(self)
        self.linePPun4.move(300, H)
        self.linePPun4.resize(30, 25)
        self.linePPun4.insert(str(params['probPun'][3]))
        
        # Duration ITI
        H += 30
        self.labelDurITI = QLabel(self)
        self.labelDurITI.setText('Dur. ITI (s):')
        self.labelDurITI.move(20, H)
        
        self.labelDurITI1 = QLabel(self)
        self.labelDurITI1.setText('mean')
        self.labelDurITI1.move(160, H)
        self.labelDurITI1.setFont(QFont('Arial', 10))
        self.lineDurITI1 = QLineEdit(self)
        self.lineDurITI1.move(120, H)
        self.lineDurITI1.resize(40, 25)
        self.lineDurITI1.insert(str(params['durITI'][0]))
        
        self.labelDurITI2 = QLabel(self)
        self.labelDurITI2.setText('max')
        self.labelDurITI2.move(230, H)
        self.labelDurITI2.setFont(QFont('Arial', 10))
        self.lineDurITI2 = QLineEdit(self)
        self.lineDurITI2.move(190, H)
        self.lineDurITI2.resize(40, 25)
        self.lineDurITI2.insert(str(params['durITI'][1]))
        
        # Duration trial
        H += 30
        self.labelDurTrial = QLabel(self)
        self.labelDurTrial.setText('Dur. trial (s):')
        self.labelDurTrial.move(20, H)
        
        self.labelDurTrial1 = QLabel(self)
        self.labelDurTrial1.setText('Snd.')
        self.labelDurTrial1.move(150, H)
        self.labelDurTrial1.setFont(QFont('Arial', 10))
        self.lineDurTrial1 = QLineEdit(self)
        self.lineDurTrial1.move(120, H)
        self.lineDurTrial1.resize(30, 25)
        self.lineDurTrial1.insert(str(params['durSound']))
        
        self.labelDurTrial2 = QLabel(self)
        self.labelDurTrial2.setText('Pre')
        self.labelDurTrial2.move(210, H)
        self.labelDurTrial2.setFont(QFont('Arial', 10))
        self.lineDurTrial2 = QLineEdit(self)
        self.lineDurTrial2.move(180, H)
        self.lineDurTrial2.resize(30, 25)
        self.lineDurTrial2.insert(str(params['durPreReinf']))
        
        self.labelDurTrial3 = QLabel(self)
        self.labelDurTrial3.setText('Post-rew')
        self.labelDurTrial3.move(270, H)
        self.labelDurTrial3.setFont(QFont('Arial', 10))
        self.lineDurTrial3 = QLineEdit(self)
        self.lineDurTrial3.move(240, H)
        self.lineDurTrial3.resize(30, 25)
        self.lineDurTrial3.insert(str(params['durConsumption']))
        
        # Total duration
        H +=30
        self.labelDurTotal = QLabel(self)
        self.labelDurTotal.setText('Dur. total (s):')
        self.labelDurTotal.move(20, H)
        self.lineDurTotal = QLineEdit(self)
        self.lineDurTotal.move(120, H)
        self.lineDurTotal.resize(60, 25)
        self.lineDurTotal.insert(str(params['durTotal']))
        
        # Fraction laser
        H += 30
        self.labelFractLas = QLabel(self)
        self.labelFractLas.setText('Fraction laser:')
        self.labelFractLas.move(20, H)
        
        self.lineFractLas1 = QLineEdit(self)
        self.lineFractLas1.move(120, H)
        self.lineFractLas1.resize(40, 25)
        self.lineFractLas1.insert(str(params['laser']['fract_laseron']))
        
        # N trial to omit laser
        self.labelFractOmit = QLabel(self)
        self.labelFractOmit.setText('N omit laser:')
        self.labelFractOmit.move(200, H)
        
        self.lineFractOmit1 = QLineEdit(self)
        self.lineFractOmit1.move(290, H)
        self.lineFractOmit1.resize(40, 25)
        self.lineFractOmit1.insert(str(params['laser']['n_trial_omit']))
        
        H+=30
        posX = [120,40]
        posX = [120,40]
        self.labelMVT = QLabel(self)
        self.labelMVT.setText('Timing opto:')
        self.labelMVT.move(posX[0]-100, H)
        
        self.radioLaser3a = QRadioButton(self)
        self.radioLaser3a.setText('Start')
        self.radioLaser3a.setFont(QFont('Arial', 10))
        self.radioLaser3a.setChecked(True)
        self.radioLaser3a.move(posX[0],H)
        
        posX = [200,40]
        self.radioLaser3b = QRadioButton(self)
        self.radioLaser3b.setText('Release')
        self.radioLaser3b.setFont(QFont('Arial', 10))
        self.radioLaser3b.move(posX[0],H)
        
        posX = [280,40]
        self.radioLaser3c = QRadioButton(self)
        self.radioLaser3c.setText('Both')
        self.radioLaser3c.setFont(QFont('Arial', 10))
        self.radioLaser3c.move(posX[0],H)
        
        if params["laser"]["timing"] == 'start':
            self.radioLaser3a.setChecked(True)
        elif params["laser"]["timing"] == 'release':
            self.radioLaser3b.setChecked(True)
        else:
            self.radioLaser3c.setChecked(True)
        

        # Button to load parameters
        H += 30
        pybutton = QPushButton('Load parameters', self)
        pybutton.clicked.connect(self.clickLoadMethod)
        pybutton.move(120, H) 
        pybutton.resize(200,32)
        
        # Button to save parameters
        H += 30
        pybutton = QPushButton('Save parameters', self)
        pybutton.clicked.connect(self.clickSaveMethod)
        pybutton.move(120, H)       
        pybutton.resize(200,32)

       
    
    # def textChangedMethod(self):
    #     self.sideLabel.setText(params[lsParams[0]])
    
    
    def clickLoadMethod(self):
        # Check ups ==========
        # Check if animal ID is not empty
        if not self.lineANID.text():
            # Future: make this a pop up window
            print('Please specify animal ID!')
            return
        
        print('Loading!')
        # Load params stored for that animal
        params = hfb.defineParams(self.lineANID.text())
        if params == -1:
            return
        
        if 'laser' not in params.keys(): # Patch so script works with older animals for which params were set with an old setParameters.py version (< v3)
            params['laser'] = {'timing': 'both' , # can be 'cue' 'reinfo' or 'both'               
                               'fract_laseron': 0,
                               'n_trial_omit':5,}
        
        # Update line text with loaded params
        self.lineNTrials.setText(str(params["nTrials"]))
        self.lineAmount.setText(str(params["amountReward"]))
        self.lineFraction1.setText(str(params["fractEachTone"][0]))
        self.lineFraction2.setText(str(params["fractEachTone"][1]))
        self.lineFraction3.setText(str(params["fractEachTone"][2]))
        self.lineFraction4.setText(str(params["fractEachTone"][3]))
        self.linePRew1.setText(str(params["probRew"][0]))
        self.linePRew2.setText(str(params["probRew"][1]))
        self.linePRew3.setText(str(params["probRew"][2]))
        self.linePRew4.setText(str(params["probRew"][3]))
        self.linePPun1.setText(str(params["probPun"][0]))
        self.linePPun2.setText(str(params["probPun"][1]))
        self.linePPun3.setText(str(params["probPun"][2]))
        self.linePPun4.setText(str(params["probPun"][3]))
        self.lineDurITI1.setText(str(params["durITI"][0]))
        self.lineDurITI2.setText(str(params["durITI"][1]))
        self.lineDurTrial1.setText(str(params["durSound"]))
        self.lineDurTrial2.setText(str(params["durPreReinf"]))
        self.lineDurTrial3.setText(str(params["durConsumption"]))
        self.lineDurTotal.setText(str(params["durTotal"]))
        self.lineFractLas1.setText(str(params['laser']['fract_laseron']))
        self.lineFractOmit1.setText(str(params['laser']['n_trial_omit']))
        
        if params["laser"]["timing"] == 'cue':
            self.radioLaser3a.setChecked(True)
        elif params["laser"]["timing"] == 'reinfo':
            self.radioLaser3b.setChecked(True)
        else:
            self.radioLaser3c.setChecked(True)

        print('Done!')
        
    def clickSaveMethod(self):
        # Check ups ==========
        # Check if animal ID is not empty
        an = self.lineANID.text()
        if not self.lineANID.text():
            # Future: make this a pop up window
            print('Data were not saved: Please specify animal ID!')
            return
        
        # Amount reward checkups and update
        txt = self.lineAmount.text()
        if txt == 'variable':
            amountRew = txt
        else:
            amountRew = float(self.lineAmount.text())

        
        # Check if sum(fract each tone) = 1
        s = sum([float(self.lineFraction1.text()), float(self.lineFraction2.text()), float(self.lineFraction3.text()), float(self.lineFraction4.text())])
        if s != 1:
            print('Data were not saved: Sum(fractEachTone) should be 1!')
            return
        
        # Check if amount reward is within a range
        if txt != 'variable':
            if float(self.lineAmount.text()) < 0.1 or float(self.lineAmount.text()) > 20:
                print('Data were not saved: Amount reward should min: 0.1 and max: 20 uL!')
                return
                    
        # Define laser timing type from radio button
        if self.radioLaser3a.isChecked():
            laser_timing = 'cue'
        if self.radioLaser3b.isChecked():
            laser_timing = 'reinfo'
        if self.radioLaser3c.isChecked():
            laser_timing = 'both' 
        
        # Update paramas with GUI input
        params = {
            "animalID": an,
            "nTrials": int(self.lineNTrials.text()),
            "amountReward": amountRew, # In uL. Run calibration 
            "fractEachTone": [float(self.lineFraction1.text()), float(self.lineFraction2.text()), float(self.lineFraction3.text()), float(self.lineFraction4.text())], # Fraction of each tone presentation + fraction reward no tone position 4. Warning sum(fractEachTone) should be 1
            "probRew": [float(self.linePRew1.text()), float(self.linePRew2.text()), float(self.linePRew3.text()), float(self.linePRew4.text())],
            "probPun": [float(self.linePPun1.text()), float(self.linePPun2.text()), float(self.linePPun3.text()), float(self.linePPun4.text())],
            "durITI": [float(self.lineDurITI1.text()), float(self.lineDurITI2.text())],#[u max]
            "durSound": float(self.lineDurTrial1.text()), # in sec
            "durPreReinf": float(self.lineDurTrial2.text()), # Includes sound duration
            "durConsumption": float(self.lineDurTrial3.text()), #Time after reward delivery
            "durTotal": float(self.lineDurTotal.text()) ,    # Duration in sec of the whole session   
            
            "laser":{
                'fract_laseron': float(self.lineFractLas1.text()),
                'n_trial_omit': int(self.lineFractOmit1.text()),
                'timing':laser_timing,
                }
            }
        
        # Check if folder 'Data' exists
        if not os.path.isdir('Data'):
            os.mkdir('Data')

        # Check if folder for animal exists
        if not os.path.isdir('Data'+os.path.sep+an):
            os.mkdir('Data'+os.path.sep+an)
        
        # Check if param file exists
        if not os.path.isfile('Data'+os.path.sep+an+os.path.sep+an+'_Params.json'):
            # Save params               
            json_obj = json.dumps(params) # create json object from dictionary
            f = open('Data'+os.path.sep+an+os.path.sep+an+"_Params.json","w") # open file for writing, "w" 
            f.write(json_obj) # write json object to file
            f.close() # close file
            print('"Data'+os.path.sep+an+os.path.sep+an+'_Params.json" was created.')
        else:
            # answer = input('Data'+os.path.sep+an+os.path.sep+an+'_Params.json already exist!\n Do you want to overwrite parameters (Y or [N])?\n')
            choice = QMessageBox.question(self,'Warning:', 
                                          'Data'+os.path.sep+an+os.path.sep+an+'_Params.json already exist!\n Do you want to overwrite parameters',
                                          QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:
                # Save params               
                json_obj = json.dumps(params) # create json object from dictionary
                f = open('Data'+os.path.sep+an+os.path.sep+an+"_Params.json","w") # open file for writing, "w" 
                f.write(json_obj) # write json object to file
                f.close() # close file
                
                print('"Data'+os.path.sep+an+os.path.sep+an+'_Params.json" was overwritten.')
            else:
                print('"Data'+os.path.sep+an+os.path.sep+an+'_Params.json" remains the same.')
                answer = 'n'

            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )