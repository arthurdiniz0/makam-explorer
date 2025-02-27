#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:35:06 2024

Retrieves metadata from MusicBrainz and adds to the content(dict) in 
the pickle files (two new keys: mb_metadata and mb_tags)

Running this script updates all pickle files and updates metadata 
retrieving it from MusicBrainz

@author: barisbozkurt
"""
import pickle
from MB_tools import get_musicbrainz_metadata, get_recording_tags
from common_tools import get_file_list
from constants import dataFolder        

pickle_file_list = get_file_list(dataFolder, extension='.pickle')

for index, pickle_file in enumerate(pickle_file_list, start=1):
    print(f"Processing file {index}/{len(pickle_file_list)}")
    # Load content from the pickle file
    with open(pickle_file, 'rb') as file:
        file_info = pickle.load(file)

    file_info['mb_metadata'] = get_musicbrainz_metadata(file_info['mbid'])
    file_info['mb_tags'] = get_recording_tags(file_info['mbid'])
    # Save extended content to the pickle file
    with open(pickle_file, 'wb') as file:
        pickle.dump(file_info, file)
