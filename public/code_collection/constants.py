#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:35:06 2024

Keeps constants
    
@author: barisbozkurt
"""
import numpy as np
import json, os

# Constants
CENTS_IN_OCTAVE = 1200
reference_freq = 55 # 440/8

# Computing pitch histogram
num_notes_in_octave = 60
num_octaves_in_hist = 6

# Define analysis parameters for pitch extraction 
pitch_extraction_methods = ['pyin','crepe','makam']
pitch_params = {'sr':16000, # Sampling rate for reading files
          'F_min':55.0, # minimum frequency of interest in Hz
          'F_max':2000.0, # maximum frequency of interest in Hz        
          }
pitch_params['num_frames_per_sec'] = 100 #(corresponding to 10 msecs)
pitch_params['N'] = int(4*pitch_params['sr']/pitch_params['F_min']) # window size in samples
pitch_params['H'] = int(pitch_params['sr'] / pitch_params['num_frames_per_sec']) # hop size in samples 
pitch_params['thresholds_PYIN'] = np.arange(0.01, 1, 0.01)
pitch_params['R_PYIN'] = 10 # bin resolution in cents
pitch_params['conf_threshold_PYIN'] = 0.5 # confidence threshold between 0 and 1
pitch_params['methods'] = pitch_extraction_methods

dataFolder='../AudioCollection/CDsWithTags/'

# musicBrainz release id for 'Congrès de musique Arabe du Caire 1932'
musicbrainz_releaseid = "25d66aec-1463-4a0b-a331-d3bbe587e71c"

# Read region artists map from a JSON file created using create_region_artists.py
json_file_name = 'region_artists.json'
region_artists = {}
if os.path.exists(json_file_name):
    with open(json_file_name, 'r') as json_file:
        region_artists = json.load(json_file)
        
# mode name conversion map
mode_name_map = {
    'hijaz kar':'hicazkar',
    'husayn': 'husayni',
    'segah':'sikah',
    'rasd': 'rast',
    'kurdili hicaz kar':'kurdili hicazkar',
    'hijaz kar':'hicazkar',
    'bayat':'bayati'
    }