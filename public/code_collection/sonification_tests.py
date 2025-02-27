#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:35:06 2024

Sonification tests

@author: barisbozkurt
"""
import os
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import pickle

from constants import pitch_params, CENTS_IN_OCTAVE, num_notes_in_octave, num_octaves_in_hist, reference_freq
from MB_tools import read_musicbrainz_id
from common_tools import get_file_list, pure_sin_resynth, cents_to_hz

dataFolder = '../AudioCollection/CDsWithTags'

pickle_file = dataFolder + '/CD 4/02. Suite.pickle'
# Load content from the pickle file
with open(pickle_file, 'rb') as file:
    file_info = pickle.load(file)

num_frames_per_note = 100
sr = pitch_params['sr']
pitch_sca_fact = 4
dur_sca_fact = 1
maxima_locs_hz = cents_to_hz(file_info['maxima_locs_cent'], reference_frequency=reference_freq)

f0_series = []
for tone_hz in maxima_locs_hz:
    f0_series += [tone_hz] * num_frames_per_note
synth_signal = pure_sin_resynth(np.array(f0_series), sr, pitch_sca_fact, dur_sca_fact)

sf.write(pickle_file.replace('.pickle','.syn.wav'), synth_signal, sr)

