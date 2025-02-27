#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 09:54:43 2025
Data check tests

@author: z11164
"""
from constants import dataFolder
from common_tools import get_file_list
from mutagen.mp3 import MP3
import pickle

def check_pitch_frame_lens():
    mp3_files = get_file_list(dataFolder)
    for mp3_file in mp3_files:
        pickle_file = mp3_file.replace('.mp3','.pickle')
        # read pickle file
        with open(pickle_file, 'rb') as file:
            file_info = pickle.load(file)
        # get audio length
        audio_dur_secs = MP3(mp3_file).info.length
        # short name
        mp3_file = mp3_file.replace(dataFolder,'')
        if len(mp3_file) > 20:
            mp3_file = mp3_file[:20]
        # print
        print(round(audio_dur_secs*100), file_info['pitch_crepe'].shape[0], file_info['pitch_pyin'].shape[0], mp3_file)

check_pitch_frame_lens()        